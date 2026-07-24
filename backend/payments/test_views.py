"""
Página de pruebas de Paguelofacil.

Solo accesible por administradores autenticados. Sirve para verificar que la
integración funciona sin necesidad de hacer todo el flujo desde el frontend.

Rutas montadas en payments/urls.py:
  GET  /api/payments/pfl-test/                 → HTML con panel de pruebas
  POST /api/payments/pfl-test/init/            → devuelve SDKConfig sin crear tx real
  POST /api/payments/pfl-test/query/           → consulta un codOper en PFL
  POST /api/payments/pfl-test/sim-webhook/     → simula un webhook
"""
import json
import logging
from datetime import date, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import PaguelofacilTransaction, Payout
from .paguelofacil import (
    PaguelofacilAPIError,
    PaguelofacilConfig,
    build_sdk_config,
    first_tx_item,
    generate_internal_reference,
    query_transaction,
)
from .services import apply_confirmation

logger = logging.getLogger(__name__)


def _mask(value: str, keep: int = 6) -> str:
    """Enmascara secretos para mostrarlos en la UI sin exponerlos completos."""
    if not value:
        return '— sin configurar —'
    if len(value) <= keep * 2:
        return value[:keep] + '…'
    return f"{value[:keep]}…{value[-keep:]}"


@method_decorator(staff_member_required, name='dispatch')
class PflTestPageView(View):
    """Renderiza el panel HTML de pruebas."""

    def get(self, request):
        cfg = PaguelofacilConfig
        access_token = cfg.access_token()
        cclw = cfg.cclw()

        # ¿está bien configurado?
        config_ok = bool(access_token and cclw)

        # ── KPIs ──
        tx_qs = PaguelofacilTransaction.objects.all()
        approved = tx_qs.filter(status='approved')
        revenue = approved.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        refunded = tx_qs.aggregate(t=Sum('refunded_amount'))['t'] or Decimal('0.00')
        payouts_pending = Payout.objects.filter(status='pending')
        payouts_pending_amount = payouts_pending.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        kpis = [
            {'label': 'Cobrado (aprobado)', 'value': f'${revenue:,.2f}', 'accent': True},
            {'label': 'Transacciones', 'value': tx_qs.count()},
            {'label': 'Aprobadas', 'value': approved.count()},
            {'label': 'Reembolsado', 'value': f'${refunded:,.2f}'},
            {'label': 'Payouts pendientes', 'value': payouts_pending.count()},
            {'label': 'A liquidar', 'value': f'${payouts_pending_amount:,.2f}'},
        ]

        context = {
            'kpis': kpis,
            'env': cfg.env(),
            'is_sandbox': cfg.is_sandbox(),
            'host': cfg.host(),
            'api_host': cfg.api_host(),
            'management_host': cfg.management_host(),
            'sdk_script_url': cfg.sdk_script_url(),
            'return_url': cfg.return_url(),
            'webhook_url': cfg.webhook_url(),
            'cclw_masked': _mask(cclw, 8),
            'access_token_masked': _mask(access_token, 10),
            'config_ok': config_ok,
            'default_from_email': settings.DEFAULT_FROM_EMAIL,
            'recent_tx': PaguelofacilTransaction.objects.select_related('booking', 'client')[:20],
            'init_url': reverse('pfl-test-init'),
            'query_url': reverse('pfl-test-query'),
            'sim_webhook_url': reverse('pfl-test-sim-webhook'),
            'real_webhook_url': reverse('pfl-webhook'),
            'checkout_init_url': reverse('pfl-test-checkout-init'),
            'test_confirm_url': reverse('pfl-test-confirm'),
        }
        return render(request, 'payments/pfl_test.html', context)


@method_decorator([csrf_exempt, staff_member_required], name='dispatch')
class PflTestInitView(View):
    """
    Devuelve una SDKConfig para probar el SDK de PFL sin crear una transacción real.
    No graba nada en la DB — es solo para probar que el iframe carga bien.
    """

    def post(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        try:
            amount = Decimal(str(body.get('amount', '1.00')))
        except Exception:
            return JsonResponse({'error': 'Monto inválido'}, status=400)

        if amount < Decimal('1.00'):
            return JsonResponse({'error': 'El monto mínimo es USD 1.00'}, status=400)

        description = str(body.get('description') or 'Prueba PFL Pulsar')[:120]
        client_email = str(body.get('client_email') or request.user.email or '')
        client_name = str(body.get('client_name') or request.user.get_full_name() or 'Test User')

        internal_ref = generate_internal_reference('TEST')

        try:
            sdk_cfg = build_sdk_config(
                amount=amount,
                description=description,
                internal_reference=internal_ref,
                client_email=client_email,
                client_name=client_name,
            )
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'sdk_config': sdk_cfg.to_dict(),
            'internal_reference': internal_ref,
            'note': 'Esto NO crea transacción en la DB — es solo para probar el iframe del SDK.',
        })


@method_decorator([csrf_exempt, staff_member_required], name='dispatch')
class PflTestQueryView(View):
    """Consulta el estado de una transacción PFL por codOper."""

    def post(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        cod_oper = str(body.get('cod_oper') or '').strip()
        if not cod_oper:
            return JsonResponse({'error': 'Falta codOper'}, status=400)

        try:
            data = query_transaction(cod_oper)
            return JsonResponse({'ok': True, 'data': data})
        except PaguelofacilAPIError as e:
            return JsonResponse({
                'ok': False,
                'error': str(e),
                'code': e.code,
                'response': e.response,
            }, status=200)  # 200 para que el frontend renderice el error


@method_decorator([csrf_exempt, staff_member_required], name='dispatch')
class PflTestSimWebhookView(View):
    """
    Simula un webhook de PFL — hace un POST al endpoint real /webhook/ con un
    payload editable por el admin. Sirve para probar que el parser + la lógica
    de post-procesado funcionan sin depender de PFL.
    """

    def post(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        payload = body.get('payload')
        if not isinstance(payload, dict):
            return JsonResponse({'error': 'payload debe ser un objeto JSON'}, status=400)

        # Importar parse_webhook y correrlo directo, en vez de hacer POST HTTP
        # (así el test no depende de que el server esté aceptando su propio POST).
        from .paguelofacil import parse_webhook
        try:
            result = parse_webhook(payload)
            return JsonResponse({
                'ok': True,
                'parsed': {
                    'internal_reference': result.internal_reference,
                    'cod_oper': result.cod_oper,
                    'status': result.status,
                    'amount': str(result.amount) if result.amount is not None else None,
                    'auth_status': result.auth_status,
                },
                'note': (
                    'Solo se parseó el payload — no se ejecutó la lógica de post-procesado. '
                    'Para probar el flujo completo, haz un POST real al endpoint del webhook.'
                ),
            })
        except Exception as e:
            logger.exception('Error simulando webhook')
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@method_decorator([csrf_exempt, staff_member_required], name='dispatch')
class PflTestCheckoutInitView(View):
    """
    Inicia una prueba de checkout REAL de sandbox.

    Crea una reserva de PRUEBA (solo-servicios, sin DJ, marcada 'PRUEBA PFL') a nombre
    del staff, y una PaguelofacilTransaction real en estado 'initiated'. Devuelve la
    SDKConfig para que el panel cargue el iframe del SDK y se pague con tarjeta de prueba.

    Al pagar, el panel llama a pfl-test-confirm, que verifica server-side y crea el
    Payment — el flujo completo init→SDK→confirm, sin tocar reservas reales.
    """

    def post(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        try:
            amount = Decimal(str(body.get('amount', '1.00')))
        except Exception:
            return JsonResponse({'error': 'Monto inválido'}, status=400)
        if amount < Decimal('1.00'):
            return JsonResponse({'error': 'El monto mínimo es USD 1.00'}, status=400)

        from bookings.models import Booking

        # Reserva de prueba (solo-servicios). Queda clara para poder borrarla luego.
        booking = Booking.objects.create(
            client=request.user,
            talent=None,
            event_type='other',
            event_name='PRUEBA PFL (sandbox)',
            event_date=date.today() + timedelta(days=7),
            event_time_start=time(20, 0),
            event_time_end=time(23, 0),
            event_location='PRUEBA — generada por el tester de pagos',
            quoted_price=amount,
            status='pendiente_pago',
        )

        internal_ref = generate_internal_reference('PLS')
        description = f'PRUEBA Pulsar | Reserva {booking.booking_code or booking.id}'[:120]

        tx = PaguelofacilTransaction.objects.create(
            booking=booking,
            client=request.user,
            amount=amount,
            payment_type='full',
            description=description,
            internal_reference=internal_ref,
            status='initiated',
        )

        try:
            sdk_cfg = build_sdk_config(
                amount=amount,
                description=description,
                internal_reference=internal_ref,
                client_email=request.user.email,
                client_name=request.user.get_full_name() or 'Staff Test',
            )
        except ValueError as e:
            tx.status = 'error'
            tx.last_error = str(e)
            tx.save(update_fields=['status', 'last_error', 'updated_at'])
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'internal_reference': internal_ref,
            'tx_id': tx.id,
            'booking_id': booking.id,
            'sdk_config': sdk_cfg.to_dict(),
        })


@method_decorator([csrf_exempt, staff_member_required], name='dispatch')
class PflTestConfirmView(View):
    """
    Confirma una transacción de prueba tras pagar en el SDK (verificación server-side).

    Usa la MISMA lógica endurecida que producción (apply_confirmation): consulta PFL,
    verifica el monto (C1) y aprueba bajo lock. Solo staff.
    """

    def post(self, request):
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        internal_ref = str(body.get('internal_reference') or '').strip()
        cod_oper = str(body.get('cod_oper') or '').strip()
        if not internal_ref or not cod_oper:
            return JsonResponse({'error': 'Faltan internal_reference y/o cod_oper'}, status=400)

        try:
            tx = PaguelofacilTransaction.objects.get(internal_reference=internal_ref)
        except PaguelofacilTransaction.DoesNotExist:
            return JsonResponse({'error': 'Transacción no encontrada'}, status=404)

        if tx.status == 'approved':
            return JsonResponse({'ok': True, 'status': 'approved', 'result': 'already',
                                 'payment_id': tx.payment_id})

        try:
            api_response = query_transaction(cod_oper)
        except PaguelofacilAPIError as e:
            return JsonResponse({'ok': False, 'error': str(e), 'code': e.code,
                                 'response': e.response}, status=200)

        api_data = first_tx_item(api_response)
        result, detail = apply_confirmation(tx, cod_oper, api_data, api_response)
        tx.refresh_from_db()
        return JsonResponse({
            'ok': result in ('approved', 'already'),
            'result': result,
            'status': tx.status,
            'detail': detail,
            'payment_id': tx.payment_id,
            'booking_id': tx.booking_id,
        })
