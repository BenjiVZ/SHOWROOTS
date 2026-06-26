"""
Verifica si las credenciales Paguelofacil son de sandbox o producción.

Uso:
    python manage.py pfl_check

Hace una llamada AUTH chica (USD 1.00) con tarjeta de prueba contra sandbox.
- Si responde "approved" → tus credenciales SON de sandbox.
- Si responde "MERCHANT NOT VALID" (600) → son de producción (probarlas en sandbox falla).
- Si responde "INVALID CARD" o similar → son de producción y la tarjeta de test no aplica.

NO hace cobros reales — solo pre-autorización (AUTH), no captura.
Después de probar, NO hace falta reversar porque la pre-auth expira sola en ~7 días.
"""
import json

import requests
from django.core.management.base import BaseCommand

from payments.paguelofacil import PaguelofacilConfig

# Tarjeta de prueba "Aprobada" que dan los docs
TEST_CARD = {
    'cardNumber': '5038460000000019',
    'expMonth': '04',
    'expYear': '99',
    'cvv': '475',
    'firstName': 'Pulsar',
    'lastName': 'Test',
    'cardType': 'MASTERCARD',
}


class Command(BaseCommand):
    help = 'Verifica si las credenciales Paguelofacil son sandbox o producción.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            choices=['sandbox', 'production'],
            default='sandbox',
            help='Contra qué entorno probar (default: sandbox).',
        )

    def handle(self, *args, **opts):
        target = opts['target']
        host = (
            'https://sandbox.paguelofacil.com'
            if target == 'sandbox'
            else 'https://secure.paguelofacil.com'
        )
        url = f'{host}/rest/processTx/AUTH'

        cclw = PaguelofacilConfig.cclw()
        token = PaguelofacilConfig.access_token()
        if not cclw or not token:
            self.stdout.write(self.style.ERROR(
                'FALTAN PAGUELOFACIL_CCLW o PAGUELOFACIL_ACCESS_TOKEN en el .env.'
            ))
            return

        payload = {
            'cclw': cclw,
            'amount': 1.00,
            'taxAmount': 0.00,
            'email': 'test@im-pulsar.com',
            'phone': '60000000',
            'concept': 'pulsar-cred-check',
            'description': 'Verificación de credenciales',
            'cardInformation': TEST_CARD,
        }

        self.stdout.write(f'\n>> Probando contra: {url}')
        self.stdout.write(f'>> CCLW: {cclw[:12]}…{cclw[-4:]}')
        self.stdout.write(f'>> Token: {token[:8]}…{token.split("|")[-1][-4:]}\n')

        try:
            r = requests.post(
                url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': token,
                },
                timeout=30,
            )
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Conexión falló: {e}'))
            return

        try:
            data = r.json()
        except ValueError:
            self.stdout.write(self.style.ERROR(
                f'Respuesta no-JSON ({r.status_code}): {r.text[:500]}'
            ))
            return

        self.stdout.write(f'HTTP {r.status_code}')
        self.stdout.write(json.dumps(data, indent=2, ensure_ascii=False))

        header = data.get('headerStatus', {})
        code = header.get('code')
        desc = header.get('description', '')
        success = data.get('success', False)

        self.stdout.write('\n' + '─' * 50)
        if success:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Credenciales VÁLIDAS en {target}.'
            ))
            if target == 'sandbox':
                self.stdout.write('   → Las credenciales son de SANDBOX (test).')
                self.stdout.write('   → Podés cobrar con tarjetas de prueba sin riesgo.')
            else:
                self.stdout.write('   → Las credenciales son de PRODUCCIÓN (real).')
                self.stdout.write(
                    self.style.WARNING(
                        '   ⚠️  Esta transacción de test es REAL — '
                        'reversarla con REVERSE_AUTH si fue una tarjeta real.'
                    )
                )
        elif code in (600, '600') or 'MERCHANT NOT VALID' in desc.upper():
            self.stdout.write(self.style.ERROR(
                f'\n❌ Credenciales NO válidas en {target}.'
            ))
            if target == 'sandbox':
                self.stdout.write(
                    self.style.WARNING(
                        '   → Probablemente son de PRODUCCIÓN. '
                        'Volvé a correr con --target production.'
                    )
                )
            else:
                self.stdout.write(
                    '   → Las credenciales no son válidas tampoco en prod. '
                    'Verificá con tu cliente.'
                )
        else:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️ Respuesta inesperada (code={code}): {desc}'
            ))
            self.stdout.write('   Revisá el JSON arriba para más contexto.')
