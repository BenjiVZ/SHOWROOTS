"""
Endpoints de pagos con Paguelofacil (SDK + S2S API).

Frontend:
  POST /api/payments/paguelofacil/init/        → devuelve config para inicializar el SDK
  POST /api/payments/paguelofacil/confirm/     → verifica server-side tras onTxSuccess

Server-to-server (recibe de PFL):
  POST /api/payments/paguelofacil/webhook/     → notificación asincrónica

Consulta:
  GET  /api/payments/paguelofacil/status/<ref>/ → estado por internal_reference

Admin (payouts manuales a DJ/Aliado):
  GET  /api/payments/admin/payouts/            → lista
  POST /api/payments/admin/payouts/<id>/pay/   → marcar pagado
"""
import logging
from decimal import Decimal

from django.db import transaction as db_tx
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking, Payment

from .models import PaguelofacilTransaction, Payout
from .paguelofacil import (
    PaguelofacilAPIError,
    build_sdk_config,
    friendly_error,
    generate_internal_reference,
    parse_webhook,
    query_transaction,
    verify_webhook_signature,
)
from .serializers import (
    CreateCheckoutSerializer,
    PaguelofacilTransactionSerializer,
    PayoutSerializer,
)
from .services import create_payment_and_payouts, process_refund

logger = logging.getLogger(__name__)


def _first_tx_item(api_response):
    """El endpoint MerchantTransactions devuelve `data` como array (resultado de filtro).
    Toma el primer item — debería haber exactamente uno por codOper único."""
    raw = api_response.get('data', {}) if isinstance(api_response, dict) else {}
    if isinstance(raw, list):
        return raw[0] if raw else {}
    return raw if isinstance(raw, dict) else {}


def _extract_pfl_amount(api_data):
    """Extrae el monto realmente cobrado que PFL reporta (probando varias claves)."""
    for key in ('totalPay', 'total', 'netAmount', 'amount', 'requestPayAmount', 'montoTotal'):
        val = api_data.get(key)
        if val not in (None, ''):
            try:
                return Decimal(str(val))
            except (ValueError, TypeError):
                continue
    return None


# ─────────────────────────────────────────────────────────────────
# Frontend: inicializar SDK
# ─────────────────────────────────────────────────────────────────
class InitCheckoutView(APIView):
    """
    POST /api/payments/paguelofacil/init/

    Body: { booking_id, amount, payment_type }
    Response: { transaction_id, sdk_config: {...} }

    El frontend usa `sdk_config` para inicializar el PFScript.js.
    Crea la PaguelofacilTransaction en estado 'initiated'.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = CreateCheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        booking = get_object_or_404(Booking, pk=data['booking_id'])

        if booking.client_id != request.user.id:
            return Response(
                {'detail': 'No tienes permiso para pagar esta reserva.'},
                status=http_status.HTTP_403_FORBIDDEN,
            )

        # Whitelist en español (los códigos de status del modelo son en español).
        # El guard anterior usaba 'cancelled'/'completed' (inglés) que NUNCA
        # matcheaban → se podía iniciar el pago de una reserva cancelada (vuln I4).
        if booking.status not in ('aceptada', 'pendiente_pago'):
            return Response(
                {'detail': f'La reserva está {booking.get_status_display()}, no se puede pagar.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        amount = Decimal(str(data['amount']))
        if amount < Decimal('1.00'):
            return Response(
                {'detail': 'El monto mínimo es USD 1.00.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        max_payable = (booking.total_to_pay or Decimal('0')) - (booking.amount_paid or Decimal('0'))
        if amount > max_payable + Decimal('0.01'):
            return Response(
                {'detail': f'El monto excede el saldo pendiente (${max_payable:.2f}).'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        internal_ref = generate_internal_reference()
        # Reserva de solo-servicios: no hay DJ; describimos genéricamente.
        talent_name = (
            (booking.talent.stage_name or booking.talent.user.email)
            if booking.talent else 'Servicios de producción'
        )
        description = f"Pulsar | Reserva {booking.booking_code or booking.id} | {talent_name}"[:150]

        tx = PaguelofacilTransaction.objects.create(
            booking=booking,
            client=request.user,
            amount=amount,
            payment_type=data['payment_type'],
            description=description,
            internal_reference=internal_ref,
            status='initiated',
        )

        try:
            sdk_config = build_sdk_config(
                amount=amount,
                description=description,
                internal_reference=internal_ref,
                client_email=request.user.email,
                client_name=f'{request.user.first_name} {request.user.last_name}'.strip(),
            )
        except ValueError as e:
            tx.status = 'error'
            tx.last_error = str(e)
            tx.save(update_fields=['status', 'last_error', 'updated_at'])
            return Response(
                {'detail': str(e)},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        config_dict = sdk_config.to_dict()
        tx.request_payload = {
            'env': 'sandbox' if config_dict['use_sandbox'] else 'production',
            'amount': config_dict['amount'],
            'description': config_dict['description'],
            'internal_reference': config_dict['internal_reference'],
        }
        tx.save(update_fields=['request_payload', 'updated_at'])

        return Response({
            'transaction_id': tx.id,
            'internal_reference': tx.internal_reference,
            'sdk_config': config_dict,
        })


# ─────────────────────────────────────────────────────────────────
# Frontend: confirmar transacción tras onTxSuccess del SDK
# ─────────────────────────────────────────────────────────────────
class ConfirmCheckoutView(APIView):
    """
    POST /api/payments/paguelofacil/confirm/

    Body: { internal_reference, cod_oper }
    Verifica server-side contra PFL antes de marcar la transacción como aprobada.

    El SDK del frontend llama esto en onTxSuccess(data) con data.Oper.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        internal_ref = request.data.get('internal_reference', '').strip()
        cod_oper = request.data.get('cod_oper', '').strip()
        if not internal_ref or not cod_oper:
            return Response(
                {'detail': 'Faltan internal_reference y/o cod_oper.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        try:
            tx = PaguelofacilTransaction.objects.get(internal_reference=internal_ref)
        except PaguelofacilTransaction.DoesNotExist:
            return Response(
                {'detail': 'Transacción no encontrada.'},
                status=http_status.HTTP_404_NOT_FOUND,
            )

        if tx.client_id != request.user.id:
            return Response({'detail': 'Sin permisos.'}, status=http_status.HTTP_403_FORBIDDEN)

        # Idempotencia rápida (se re-verifica dentro del lock).
        if tx.status == 'approved':
            return Response(PaguelofacilTransactionSerializer(tx).data)

        # Verificar server-side contra PFL. La llamada de red va FUERA del lock DB
        # para no sostener un lock de fila durante un request HTTP.
        try:
            api_response = query_transaction(cod_oper)
        except PaguelofacilAPIError as e:
            tx.last_error = f'{e.code}: {e}'
            tx.save(update_fields=['last_error', 'updated_at'])
            logger.exception('PFL query falló para %s', cod_oper)
            return Response(
                {'detail': friendly_error(e.code) if e.code else f'No se pudo verificar el pago: {e}'},
                status=http_status.HTTP_502_BAD_GATEWAY,
            )

        api_data = _first_tx_item(api_response)
        is_approved = api_data.get('status') in (1, '1', True)
        reported_amount = _extract_pfl_amount(api_data)

        # Aprobación bajo lock de fila: evita doble Payment/Payout en carrera con el
        # webhook (RACE) y garantiza idempotencia real.
        with db_tx.atomic():
            tx = PaguelofacilTransaction.objects.select_for_update().get(pk=tx.pk)
            if tx.status == 'approved':
                return Response(PaguelofacilTransactionSerializer(tx).data)

            tx.response_payload = api_response
            tx.paguelofacil_id = cod_oper
            tx.paguelofacil_auth_code = str(api_data.get('authStatus', ''))

            if is_approved:
                # C1: el monto que PFL confirma DEBE cubrir el esperado. Si PFL
                # reporta menos (o no reporta monto), NO se confirma la reserva.
                if reported_amount is None or reported_amount < tx.amount - Decimal('0.01'):
                    tx.status = 'error'
                    tx.last_error = (
                        f'Monto verificado ${reported_amount} no cubre el esperado ${tx.amount}.'
                    )
                    tx.save()
                    logger.error(
                        'PFL amount mismatch tx=%s esperado=%s reportado=%s',
                        tx.internal_reference, tx.amount, reported_amount,
                    )
                    return Response(
                        {'detail': 'El monto verificado del pago no coincide con el de la '
                                   'reserva; no se confirmó. Contacta a soporte.'},
                        status=http_status.HTTP_409_CONFLICT,
                    )
                tx.status = 'approved'
                create_payment_and_payouts(tx)
            else:
                tx.status = 'declined'

            tx.save()

        return Response(PaguelofacilTransactionSerializer(tx).data)


# ─────────────────────────────────────────────────────────────────
# PFL → nosotros: webhook server-to-server
# ─────────────────────────────────────────────────────────────────
class WebhookView(APIView):
    """
    POST /api/payments/paguelofacil/webhook/
    Notificación asincrónica de PFL. Redundancia/backup del confirm.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # C2: leer el body CRUDO ANTES que request.data. Acceder a request.body
        # después de que DRF consumió el stream (request.data) lanza
        # RawPostDataException → el webhook devolvía 500 y nunca funcionaba.
        raw_body = request.body or b''

        payload = dict(request.data) if request.data else {}
        # Normalizar valores form-encoded (PFL puede mandar listas de 1 elemento)
        payload = {k: (v[0] if isinstance(v, list) and len(v) == 1 else v) for k, v in payload.items()}

        # PFL puede mandar la firma en distintos headers — los probamos en orden
        signature = (
            request.headers.get('X-Paguelofacil-Signature')
            or request.headers.get('X-PFL-Signature')
            or request.headers.get('X-Signature')
            or ''
        )

        # C2: en producción sin secret configurado, verify_webhook_signature ahora
        # RECHAZA (antes aceptaba forjas anónimas).
        if not verify_webhook_signature(payload, signature, raw_body):
            logger.warning('Webhook PFL con firma inválida/ausente: %s', payload)
            return Response({'ok': False, 'reason': 'invalid_signature'}, status=401)

        result = parse_webhook(payload)
        if not result.internal_reference and not result.cod_oper:
            logger.error('Webhook PFL sin identificador: %s', payload)
            return Response({'ok': False, 'reason': 'no_identifier'}, status=400)

        # Localizar la tx (sin lock) para saber si existe.
        tx = None
        if result.internal_reference:
            tx = PaguelofacilTransaction.objects.filter(
                internal_reference=result.internal_reference
            ).first()
        if not tx and result.cod_oper:
            tx = PaguelofacilTransaction.objects.filter(paguelofacil_id=result.cod_oper).first()

        if not tx:
            logger.error('Webhook PFL para tx desconocida: %s', payload)
            return Response({'ok': False, 'reason': 'unknown_tx'}, status=404)

        # RACE: procesar bajo lock de fila (el mismo que usa confirm/) → sin doble Payment.
        with db_tx.atomic():
            tx = PaguelofacilTransaction.objects.select_for_update().get(pk=tx.pk)
            tx.webhook_payloads = (tx.webhook_payloads or []) + [payload]

            # Idempotencia: ya aprobada → solo guardamos el payload.
            if tx.status == 'approved':
                tx.save(update_fields=['webhook_payloads', 'updated_at'])
                return Response({'ok': True, 'duplicate': True})

            tx.paguelofacil_id = result.cod_oper or tx.paguelofacil_id
            tx.paguelofacil_auth_code = result.auth_status or tx.paguelofacil_auth_code
            tx.status = result.status

            if result.status == 'approved' and not tx.payment_id:
                # C1 también en el webhook: el monto reportado debe cubrir el esperado.
                if result.amount is None or result.amount < tx.amount - Decimal('0.01'):
                    tx.status = 'error'
                    tx.last_error = (
                        f'Webhook: monto ${result.amount} no cubre el esperado ${tx.amount}.'
                    )
                    tx.save()
                    logger.error('Webhook PFL amount mismatch tx=%s', tx.internal_reference)
                    return Response({'ok': False, 'reason': 'amount_mismatch'}, status=409)
                create_payment_and_payouts(tx)

            tx.save()

        return Response({'ok': True, 'status': tx.status})


# ─────────────────────────────────────────────────────────────────
# Consulta de estado por el frontend (polling después del checkout)
# ─────────────────────────────────────────────────────────────────
class StatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, internal_reference):
        tx = get_object_or_404(
            PaguelofacilTransaction,
            internal_reference=internal_reference,
        )
        if tx.client_id != request.user.id and not request.user.is_staff:
            return Response({'detail': 'Sin permisos.'}, status=http_status.HTTP_403_FORBIDDEN)
        return Response(PaguelofacilTransactionSerializer(tx).data)


# ─────────────────────────────────────────────────────────────────
# Admin: payouts manuales a DJ/Aliados
# ─────────────────────────────────────────────────────────────────
class PayoutListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Payout.objects.select_related('booking', 'recipient').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(PayoutSerializer(qs[:200], many=True).data)


class PayoutMarkPaidView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        payout = get_object_or_404(Payout, pk=pk)
        if payout.status == 'paid':
            return Response({'detail': 'Ya estaba pagado.'}, status=http_status.HTTP_400_BAD_REQUEST)
        payout.status = 'paid'
        payout.method = request.data.get('method', payout.method)
        payout.reference = request.data.get('reference', '')
        payout.notes = request.data.get('notes', '')
        payout.created_by = request.user
        payout.paid_at = timezone.now()
        payout.save()
        return Response(PayoutSerializer(payout).data)


# ─────────────────────────────────────────────────────────────────
# Admin: reembolsos (parciales o totales)
# ─────────────────────────────────────────────────────────────────
class RefundView(APIView):
    """
    POST /api/payments/admin/refund/<tx_id>/
    Body: { amount: number, reason: string }
    """
    permission_classes = [IsAdminUser]

    def post(self, request, tx_id):
        tx = get_object_or_404(PaguelofacilTransaction, pk=tx_id)
        raw_amount = request.data.get('amount')
        reason = request.data.get('reason', '').strip()

        if raw_amount is None:
            return Response(
                {'detail': 'Falta el amount.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        try:
            amount = Decimal(str(raw_amount))
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Monto inválido.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        if amount <= 0:
            return Response(
                {'detail': 'El monto debe ser mayor a 0.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        # I5: chequeo acumulado (el enforcement autoritativo está en process_refund
        # bajo select_for_update; esto es solo para un mensaje temprano y claro).
        already = tx.refunded_amount or Decimal('0.00')
        if already + amount > tx.amount + Decimal('0.01'):
            disponible = tx.amount - already
            return Response(
                {'detail': f'El reembolso (${amount}) excede el saldo reembolsable (${disponible}). '
                           f'Ya reembolsado ${already} de ${tx.amount}.'},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        try:
            with db_tx.atomic():
                tx_locked = PaguelofacilTransaction.objects.select_for_update().get(pk=tx.pk)
                process_refund(tx_locked, amount, reason or f'Reembolso solicitado por {request.user.email}')
        except ValueError as e:
            return Response({'detail': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        except PaguelofacilAPIError as e:
            logger.exception('Refund PFL falló')
            return Response(
                {'detail': friendly_error(e.code) if e.code else f'PFL rechazó el reembolso: {e}'},
                status=http_status.HTTP_502_BAD_GATEWAY,
            )

        return Response(PaguelofacilTransactionSerializer(tx_locked).data)
