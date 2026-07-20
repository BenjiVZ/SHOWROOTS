"""
Cliente Paguelofacil para Pulsar.

Arquitectura:
  - Frontend usa el SDK JavaScript "PagueloFacil App" (PFScript.js) → inputs de tarjeta
    en iframe hosteado por PFL → CERO PCI para nosotros.
  - Backend usa la API Server-to-Server (/rest/processTx/...) SOLO para:
      · Consultar el estado de una transacción
      · Procesar reembolsos
      · Recibir webhooks asincrónicos

  Header de auth para la API:
    Authorization: PUBLIC_KEY|PRIVATE_KEY
  El access token de PFL viene ya en ese formato — solo lo pasamos tal cual.

Docs:
  https://developers.paguelofacil.com/guias                                (SDK)
  https://developers.paguelofacil.com/es/server-to-server-integration      (API)
"""
from __future__ import annotations

import re
import secrets
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

INTERNAL_REF_PATTERN = re.compile(r'(?:^|\s|=)(PLS-[A-F0-9]{16})\b', re.IGNORECASE)


# Mapeo de códigos de error PFL a mensajes amigables.
# Lista completa en: https://developers.paguelofacil.com/es/server-to-server-integration
PFL_ERROR_MESSAGES = {
    300: 'Error en la pasarela. Reintentá en unos minutos.',
    500: 'Sesión inválida. Vuelve a iniciar el pago.',
    600: 'Comercio no válido — credenciales o CCLW incorrectos.',
    601: 'Comercio suspendido (sin actividad en los últimos 90 días).',
    602: 'Faltan datos obligatorios.',
    603: 'El monto es menor al mínimo permitido (USD 1.00).',
    604: 'El monto excede el máximo permitido.',
    605: 'Número de tarjeta inválido.',
    606: 'Código de seguridad (CVV) inválido.',
    607: 'Tipo de tarjeta no aceptada.',
    608: 'Email inválido.',
    609: 'Nombre demasiado corto o largo.',
    610: 'Apellido demasiado corto o largo.',
    611: 'Teléfono inválido.',
    612: 'Demasiados intentos en poco tiempo. Esperá 5 minutos.',
    613: 'Se alcanzó el límite mensual de transacciones.',
    614: 'Se alcanzó el límite diario de transacciones.',
    621: 'Transacción rechazada por el banco emisor.',
    626: 'Se agotó el tiempo para reembolsar esta transacción.',
    627: 'Fondos insuficientes para reembolso.',
    629: 'Tarjeta no admitida.',
    631: 'Fraude detectado.',
    651: 'Fecha de expiración inválida.',
    654: 'Tarjeta inválida.',
    660: 'Pago bloqueado por reglas de fraude.',
    661: 'Transacción ya anulada.',
    662: 'Servicio del comercio deshabilitado.',
    60002: 'Transacción denegada.',
    60003: 'Transacción pendiente.',
    60007: 'Esta transacción ya fue procesada.',
}


def friendly_error(code) -> str:
    """Devuelve un mensaje user-facing para un código de error PFL."""
    try:
        return PFL_ERROR_MESSAGES.get(int(code), f'Error PFL {code}')
    except (ValueError, TypeError):
        return f'Error PFL ({code})'


# ─────────────────────────────────────────────────────────────────
# Configuración de entorno (sandbox / producción)
# ─────────────────────────────────────────────────────────────────
class PaguelofacilConfig:
    """Lee la config de Django settings (que a su vez lee del .env)."""

    @staticmethod
    def env() -> str:
        return getattr(settings, 'PAGUELOFACIL_ENV', 'sandbox').lower()

    @staticmethod
    def is_sandbox() -> bool:
        return PaguelofacilConfig.env() != 'production'

    @staticmethod
    def cclw() -> str:
        return getattr(settings, 'PAGUELOFACIL_CCLW', '')

    @staticmethod
    def access_token() -> str:
        """Formato: PUBLIC_KEY|PRIVATE_KEY"""
        return getattr(settings, 'PAGUELOFACIL_ACCESS_TOKEN', '')

    @staticmethod
    def return_url() -> str:
        return getattr(
            settings, 'PAGUELOFACIL_RETURN_URL',
            'https://im-pulsar.com/payment/return'
        )

    @staticmethod
    def webhook_url() -> str:
        return getattr(
            settings, 'PAGUELOFACIL_WEBHOOK_URL',
            'https://im-pulsar.com/api/payments/paguelofacil/webhook/'
        )

    @classmethod
    def host(cls) -> str:
        """Host raíz del checkout/admin."""
        if cls.is_sandbox():
            return 'https://sandbox.paguelofacil.com'
        return 'https://secure.paguelofacil.com'

    @classmethod
    def api_host(cls) -> str:
        """Host de la API server-to-server (transacciones nuevas: AUTH/AUTH_CAPTURE)."""
        if cls.is_sandbox():
            return 'https://api-sand.pfserver.net'
        return 'https://api.pfserver.net'

    @classmethod
    def management_host(cls) -> str:
        """
        Host del servicio de Management (consulta de transacciones existentes).
        Distinto del checkout host — usa el dominio 'admin' en producción.
        """
        if cls.is_sandbox():
            return 'https://sandbox.paguelofacil.com'
        return 'https://admin.paguelofacil.com'

    @classmethod
    def sdk_script_url(cls) -> str:
        """URL del PFScript.js — el SDK que carga el frontend."""
        return f"{cls.host()}/HostedFields/vendor/scripts/WALLET/PFScript.js"


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────
def generate_internal_reference(prefix: str = 'PLS') -> str:
    """Identificador único interno: PLS-AB12CD34EF56789A"""
    return f"{prefix}-{secrets.token_hex(8).upper()}"


# ─────────────────────────────────────────────────────────────────
# Config del SDK para el frontend
# ─────────────────────────────────────────────────────────────────
@dataclass
class SDKConfig:
    """Lo que el backend devuelve al frontend para inicializar el SDK."""
    script_url: str
    api_key: str           # access token (PUBLIC|PRIVATE)
    cclw: str
    use_sandbox: bool
    amount: float          # PFL usa float, no string
    description: str
    internal_reference: str
    return_url: str
    client_email: str = ''
    client_name: str = ''

    def to_dict(self) -> dict:
        return {
            'script_url': self.script_url,
            'api_key': self.api_key,
            'cclw': self.cclw,
            'use_sandbox': self.use_sandbox,
            'amount': self.amount,
            'description': self.description,
            'internal_reference': self.internal_reference,
            'return_url': self.return_url,
            'client_email': self.client_email,
            'client_name': self.client_name,
        }


def build_sdk_config(
    *,
    amount: Decimal,
    description: str,
    internal_reference: str,
    client_email: str = '',
    client_name: str = '',
) -> SDKConfig:
    """Arma la config que el frontend usa para inicializar PFScript.js."""
    cclw = PaguelofacilConfig.cclw()
    api_key = PaguelofacilConfig.access_token()
    if not cclw or not api_key:
        raise ValueError(
            'PAGUELOFACIL_CCLW y/o PAGUELOFACIL_ACCESS_TOKEN no configurados. '
            'Revisa el .env del droplet.'
        )

    # Embebemos el internal_reference en la descripción con marcador 'ref='
    # para poder recuperarlo desde el webhook (que no soporta customFieldValues
    # vía el SDK confiablemente).
    desc_with_ref = f'{description} | ref={internal_reference}'[:150]

    return SDKConfig(
        script_url=PaguelofacilConfig.sdk_script_url(),
        api_key=api_key,
        cclw=cclw,
        use_sandbox=PaguelofacilConfig.is_sandbox(),
        amount=float(amount),
        description=desc_with_ref,
        internal_reference=internal_reference,
        return_url=PaguelofacilConfig.return_url(),
        client_email=client_email,
        client_name=client_name,
    )


# ─────────────────────────────────────────────────────────────────
# Llamadas server-to-server a la API de PFL
# ─────────────────────────────────────────────────────────────────
class PaguelofacilAPIError(Exception):
    """Error de la API de PFL — incluye código y respuesta cruda."""
    def __init__(self, message: str, code: int = 0, response: dict = None):
        super().__init__(message)
        self.code = code
        self.response = response or {}


def _auth_headers() -> dict:
    token = PaguelofacilConfig.access_token()
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': token,
    }


def _post_processtx(tx_type: str, payload: dict, timeout: int = 30) -> dict:
    """
    POST genérico a /rest/processTx/{type}.
    tx_type ∈ {AUTH, AUTH_CAPTURE, CAPTURE, RECURRENT, REVERSE_AUTH, REVERSE_CAPTURE}
    """
    url = f"{PaguelofacilConfig.host()}/rest/processTx/{tx_type}"
    logger.info('PFL POST %s', url)
    try:
        r = requests.post(url, json=payload, headers=_auth_headers(), timeout=timeout)
    except requests.RequestException as e:
        raise PaguelofacilAPIError(f'Conexión a PFL falló: {e}') from e

    try:
        data = r.json()
    except ValueError:
        raise PaguelofacilAPIError(
            f'PFL devolvió HTTP {r.status_code} no-JSON: {r.text[:300]}',
            code=r.status_code,
        )

    if r.status_code >= 400 or not data.get('success', False):
        header = data.get('headerStatus', {}) if isinstance(data, dict) else {}
        msg = header.get('description') or data.get('message') or 'Error desconocido'
        code = header.get('code') or r.status_code
        raise PaguelofacilAPIError(msg, code=code, response=data)

    return data


def query_transaction(cod_oper: str) -> dict:
    """
    Consulta el estado de una transacción por su codOper.

    Endpoint oficial (docs "Consultar Transacciones"):
      GET https://admin.paguelofacil.com/PFManagementServices/api/v1/MerchantTransactions
          ?filter=codOper::{codOper}

    En sandbox: https://sandbox.paguelofacil.com/...

    Devuelve un payload con headerStatus, success, y data (array con la(s) tx).
    """
    base = PaguelofacilConfig.management_host()
    url = f'{base}/PFManagementServices/api/v1/MerchantTransactions'
    params = {'filter': f'codOper::{cod_oper}'}

    try:
        r = requests.get(url, params=params, headers=_auth_headers(), timeout=15)
    except requests.RequestException as e:
        raise PaguelofacilAPIError(f'Error consultando PFL: {e}') from e

    try:
        data = r.json()
    except ValueError:
        raise PaguelofacilAPIError(
            f'Respuesta no-JSON ({r.status_code}): {r.text[:300]}',
            code=r.status_code,
        )

    if r.status_code >= 400 or not data.get('success', False):
        header = data.get('headerStatus', {}) if isinstance(data, dict) else {}
        msg = header.get('description') or 'No se pudo consultar la transacción.'
        code = header.get('code') or r.status_code
        raise PaguelofacilAPIError(msg, code=code, response=data)

    return data


def refund(cod_oper: str, amount: Decimal) -> dict:
    """Reembolso parcial o total. tx_type = REVERSE_CAPTURE."""
    payload = {
        'cclw': PaguelofacilConfig.cclw(),
        'codOper': cod_oper,
        'amount': float(amount),
    }
    return _post_processtx('REVERSE_CAPTURE', payload)


# ─────────────────────────────────────────────────────────────────
# Webhook parsing — confirma transacciones asincrónicamente
# ─────────────────────────────────────────────────────────────────
@dataclass
class WebhookResult:
    """Resultado normalizado de un webhook de Paguelofacil."""
    internal_reference: str
    cod_oper: str            # equivale a paguelofacil_id (codOper)
    status: str              # nuestro status normalizado
    amount: Optional[Decimal]
    auth_status: str         # código ISO de la marca (VISA/MC)
    raw: dict = field(default_factory=dict)


def parse_webhook(payload: dict) -> WebhookResult:
    """
    Normaliza el payload del webhook. PFL puede mandar el evento bajo distintas
    claves según la versión — probamos varias para ser tolerantes.
    """
    def get(*keys, default=''):
        # Buscar en el root y bajo 'data'
        for k in keys:
            if k in payload and payload[k] not in (None, ''):
                return payload[k]
        data = payload.get('data') or {}
        if isinstance(data, dict):
            for k in keys:
                if k in data and data[k] not in (None, ''):
                    return data[k]
        return default

    cod_oper = str(get('codOper', 'CodOper', 'operationCode', 'cod_oper', default=''))

    # 'status' en respuestas PFL: 1=aprobada, 0=declinada, 3=reembolsada, 4=anulada
    pfl_status = get('status', 'Status', 'state', default=None)
    auth_status = str(get('authStatus', 'auth_status', default=''))

    if pfl_status in (1, '1', True, 'true', 'approved', 'aprobada'):
        status = 'approved'
    elif pfl_status in (0, '0', False, 'false', 'declined', 'rechazada'):
        status = 'declined'
    elif pfl_status in (3, '3', 'refunded', 'reembolsada'):
        status = 'refunded'
    elif pfl_status in (4, '4', 'voided', 'anulada', 'cancelled'):
        status = 'cancelled'
    elif pfl_status in ('pending', 'processing'):
        status = 'processing'
    else:
        status = 'processing' if cod_oper else 'error'

    amount_raw = get('totalPay', 'amount', 'requestPayAmount', default='')
    try:
        amount = Decimal(str(amount_raw)) if amount_raw else None
    except (ValueError, TypeError):
        amount = None

    # Buscar internal_reference. Estrategia en cascada:
    # 1. Campo explícito (poco probable que PFL lo mande)
    # 2. customFieldValues (si el SDK los reenvía)
    # 3. Regex 'ref=PLS-XXX' embebida en description (siempre debería estar)
    internal_ref = str(get('internalReference', 'PARM_1', default=''))
    if not internal_ref or not internal_ref.startswith('PLS-'):
        cfv = payload.get('customFieldValues') or get('customFieldValues', default=[])
        if isinstance(cfv, list):
            for f in cfv:
                if isinstance(f, dict) and f.get('id') == 'internalReference':
                    internal_ref = f.get('value', '')
                    break
    if not internal_ref or not internal_ref.startswith('PLS-'):
        desc = str(get('description', default=''))
        m = INTERNAL_REF_PATTERN.search(desc)
        if m:
            internal_ref = m.group(1).upper()

    return WebhookResult(
        internal_reference=internal_ref,
        cod_oper=cod_oper,
        status=status,
        amount=amount,
        auth_status=auth_status,
        raw=payload,
    )


def verify_webhook_signature(payload, signature_header: str, raw_body: bytes = b'') -> bool:
    """
    Verificación de firma del webhook.

    Estrategia (a confirmar con soporte PFL cuando activen el webhook):
      1. Si hay PAGUELOFACIL_WEBHOOK_SECRET configurado → calcular HMAC-SHA256
         del raw_body con ese secret y comparar contra `signature_header`.
      2. Si no hay secret y estamos en sandbox → aceptar (DEV).
      3. Si no hay secret y estamos en producción → RECHAZAR (vuln C2). Antes se
         aceptaba, lo que permitía forjar webhooks anónimos y marcar pagos como
         aprobados. El confirm/ server-side sigue siendo el camino principal; el
         webhook solo funciona cuando el secret está configurado.

    Acepta tanto la cadena en signature_header con prefijo 'sha256=' como sin él.
    """
    import hashlib
    import hmac

    secret = getattr(settings, 'PAGUELOFACIL_WEBHOOK_SECRET', '') or ''

    if secret:
        if not raw_body:
            logger.warning('verify_webhook_signature: no raw_body — no se puede verificar.')
            return False
        if not signature_header:
            logger.warning('verify_webhook_signature: falta signature_header.')
            return False

        expected = hmac.new(
            secret.encode('utf-8'),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        provided = signature_header.strip()
        if provided.lower().startswith('sha256='):
            provided = provided.split('=', 1)[1]

        is_valid = hmac.compare_digest(expected, provided)
        if not is_valid:
            logger.warning(
                'verify_webhook_signature: HMAC no coincide. '
                'Esperado=%s… Recibido=%s…',
                expected[:8], provided[:8],
            )
        return is_valid

    # Sin secret configurado
    if PaguelofacilConfig.is_sandbox():
        # En sandbox no hay dinero real: aceptamos para poder probar el flujo.
        return True
    # PRODUCCIÓN sin secret → rechazar (C2). Un webhook sin firma no es confiable.
    logger.error(
        'Webhook PFL en PRODUCCIÓN sin PAGUELOFACIL_WEBHOOK_SECRET: se RECHAZA. '
        'Configura el secret HMAC en el .env para habilitar el webhook.'
    )
    return False
