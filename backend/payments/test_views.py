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
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import PaguelofacilTransaction
from .paguelofacil import (
    PaguelofacilAPIError,
    PaguelofacilConfig,
    build_sdk_config,
    generate_internal_reference,
    query_transaction,
)

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

        context = {
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
