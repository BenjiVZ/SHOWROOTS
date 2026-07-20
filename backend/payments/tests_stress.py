"""
Regresión de seguridad de la pasarela de pagos.

Corre con:
    python manage.py test payments.tests_stress --keepdb -v 2

Cada test intenta EXPLOTAR una vulnerabilidad conocida y verifica que ahora
está CERRADA (el exploit ya NO funciona). Antes estos tests confirmaban que la
vuln existía; se invirtieron tras el hardening (C0/C1/C2/I4/I5).

NOTA sobre concurrencia: la DB de test es SQLite, que serializa escrituras y
trata select_for_update como no-op. Por eso el test de carrera es "best-effort":
en Postgres el lock por fila (confirm/ y webhook/) garantiza un solo Payment.
"""
import json
import threading
from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TransactionTestCase
from rest_framework.test import APIClient

from bookings.models import Booking, Payment
from talents.models import TalentProfile
from payments.models import PaguelofacilTransaction, Payout

User = get_user_model()

OK = '[OK] EXPLOIT BLOQUEADO:'   # ASCII only (Windows console = cp1252)


def _mk_world(quoted='500.00'):
    """Crea cliente, DJ y una reserva pagable."""
    import uuid
    tag = uuid.uuid4().hex[:8]
    client = User.objects.create_user(username=f'cli_{tag}', email=f'cli_{tag}@t.com', password='x')
    dj_user = User.objects.create_user(username=f'dj_{tag}', email=f'dj_{tag}@t.com', password='x', role='talent')
    talent = TalentProfile.objects.create(
        user=dj_user, talent_type='dj', talent_level='standard',
        stage_name='DJ Test', hourly_rate=Decimal('100.00'),
    )
    booking = Booking.objects.create(
        client=client, talent=talent,
        event_type='fiesta', event_date=date.today() + timedelta(days=30),
        event_time_start=time(20, 0), event_time_end=time(23, 0),
        event_location='Panama', quoted_price=Decimal(quoted),
        status='pendiente_pago',
    )
    return client, dj_user, talent, booking


def _init_tx(booking, client, amount='500.00', status='initiated'):
    return PaguelofacilTransaction.objects.create(
        booking=booking, client=client, amount=Decimal(amount),
        internal_reference=f'PLS-{booking.id:016X}', status=status,
    )


# PFL "aprobada" reportando un monto arbitrario (para el bypass de monto)
def _fake_pfl_response(amount):
    return {
        'success': True,
        'headerStatus': {'code': 200},
        'data': [{'status': 1, 'authStatus': '00', 'totalPay': str(amount), 'codOper': 'AUTH_CAP-FAKE'}],
    }


class PaymentGatewaySecurityRegression(TransactionTestCase):
    reset_sequences = True

    # ─────────────────────────────────────────────────────────────
    def test_C0_legacy_endpoint_eliminado(self):
        """C0 CERRADO: /payments/create/ ya no existe → no se puede marcar pagada sin pasarela."""
        client, dj, talent, booking = _mk_world()
        attacker = User.objects.create_user(username='atk', email='atk@t.com', password='x')

        c = APIClient()
        c.force_authenticate(user=attacker)              # NO es el cliente de la reserva
        resp = c.post('/api/payments/create/', {
            'booking': booking.id, 'amount': '0.01',
            'payment_type': 'full', 'payment_method': 'card',
        }, format='json')

        paid = Payment.objects.filter(booking=booking, payment_status='completed').exists()
        print(f'\n[C0] status={resp.status_code} pago_creado={paid}')
        self.assertFalse(paid, 'El endpoint legacy NO debe crear un pago (bypass C0).')
        self.assertIn(resp.status_code, (404, 405, 410),
                      'El endpoint legacy debe estar eliminado/deshabilitado.')
        print(f'[C0] {OK} endpoint legacy responde {resp.status_code}, sin pago creado.')

    # ─────────────────────────────────────────────────────────────
    def test_C1_confirm_verifica_monto(self):
        """C1 CERRADO: confirm/ NO aprueba si PFL reporta un monto menor al esperado."""
        client, dj, talent, booking = _mk_world(quoted='500.00')
        tx = _init_tx(booking, client, amount='500.00')

        c = APIClient()
        c.force_authenticate(user=client)
        with patch('payments.views.query_transaction', return_value=_fake_pfl_response('1.00')):
            resp = c.post('/api/payments/paguelofacil/confirm/', {
                'internal_reference': tx.internal_reference, 'cod_oper': 'AUTH_CAP-FAKE',
            }, format='json')

        tx.refresh_from_db()
        paid = Payment.objects.filter(booking=booking).exists()
        print(f'\n[C1] status={resp.status_code} tx.status={tx.status} (PFL reporto $1 sobre $500)')
        self.assertNotEqual(tx.status, 'approved', 'No debe aprobar con monto insuficiente.')
        self.assertFalse(paid, 'No debe crear Payment con monto insuficiente.')
        self.assertEqual(resp.status_code, 409, 'Debe responder 409 por mismatch de monto.')
        print(f'[C1] {OK} pago de $1 sobre reserva de $500 rechazado (tx.status={tx.status}).')

    # ─────────────────────────────────────────────────────────────
    def test_C2_webhook_forjado_rechazado_en_prod(self):
        """C2 CERRADO: en prod sin firma, un webhook forjado se rechaza (y no crashea)."""
        client, dj, talent, booking = _mk_world()
        tx = _init_tx(booking, client, amount='500.00', status='initiated')

        c = Client(raise_request_exception=False)
        forged = {'status': 1, 'PARM_1': tx.internal_reference,
                  'codOper': 'AUTH_CAP-FORGED', 'totalPay': '500.00'}
        # Simulamos PRODUCCIÓN (sin secret) → debe rechazar la forja.
        with patch('payments.paguelofacil.PaguelofacilConfig.is_sandbox', return_value=False):
            resp = c.post('/api/payments/paguelofacil/webhook/',
                          data=json.dumps(forged), content_type='application/json')

        tx.refresh_from_db()
        print(f'\n[C2] status={resp.status_code} tx.status={tx.status}')
        self.assertNotEqual(resp.status_code, 500,
                            'El webhook NO debe crashear (bug de lectura de body).')
        self.assertEqual(resp.status_code, 401, 'Webhook sin firma en prod debe rechazarse (401).')
        self.assertNotEqual(tx.status, 'approved', 'La forja no debe aprobar la transacción.')
        print(f'[C2] {OK} webhook forjado sin firma rechazado en prod (401), tx sin aprobar.')

    # ─────────────────────────────────────────────────────────────
    def test_I4_init_bloquea_reserva_cancelada(self):
        """I4 CERRADO: init/ NO deja iniciar pago de una reserva cancelada."""
        client, dj, talent, booking = _mk_world()
        booking.status = 'cancelada'
        booking.save()

        c = APIClient()
        c.force_authenticate(user=client)
        resp = c.post('/api/payments/paguelofacil/init/', {
            'booking_id': booking.id, 'amount': '500.00', 'payment_type': 'full',
        }, format='json')

        print(f'\n[I4] status={resp.status_code} sobre reserva CANCELADA')
        self.assertEqual(resp.status_code, 400, 'No debe dejar pagar una reserva cancelada.')
        print(f'[I4] {OK} pago de reserva cancelada bloqueado (400).')

    # ─────────────────────────────────────────────────────────────
    def test_I5_refund_con_tope_acumulado(self):
        """I5 CERRADO: los reembolsos parciales acumulados no pueden superar lo cobrado."""
        from payments.services import process_refund
        client, dj, talent, booking = _mk_world()
        tx = _init_tx(booking, client, amount='100.00', status='approved')
        tx.paguelofacil_id = 'AUTH_CAP-X'
        Payment.objects.create(booking=booking, client=client, amount=Decimal('100.00'),
                               payment_type='full', payment_status='completed', payment_method='card')
        tx.payment = Payment.objects.filter(booking=booking).first()
        tx.save()

        total_refunded = Decimal('0')
        blocked = False
        with patch('payments.paguelofacil.refund', return_value={'success': True}):
            for i in range(3):                          # intenta 3 x $60 = $180 sobre $100
                try:
                    process_refund(tx, Decimal('60.00'), reason=f'parcial {i}')
                    total_refunded += Decimal('60.00')
                    tx.refresh_from_db()
                except ValueError as e:
                    blocked = True
                    print(f'[I5] refund {i} bloqueado: {e}')
                    break

        print(f'\n[I5] total reembolsado=${total_refunded} sobre tx de $100')
        self.assertTrue(blocked, 'El tope acumulado debe bloquear el over-refund.')
        self.assertLessEqual(total_refunded, Decimal('100.00'),
                             'No debe reembolsarse mas de lo cobrado.')
        print(f'[I5] {OK} over-refund bloqueado; total reembolsado ${total_refunded} <= $100.')


class PaymentConcurrencyStress(TransactionTestCase):
    reset_sequences = True

    def test_double_payment_confirm_vs_webhook(self):
        """
        STRESS: confirm/ y webhook/ concurrentes sobre la MISMA tx.
        Con el lock por fila (select_for_update en ambos) debe generarse UN solo
        Payment/Payout. En SQLite el lock es no-op → best-effort (ver caveat).
        """
        client, dj, talent, booking = _mk_world()
        tx = _init_tx(booking, client, amount='500.00', status='initiated')
        barrier = threading.Barrier(2)
        errors = []

        def do_confirm():
            try:
                barrier.wait()
                with patch('payments.views.query_transaction', return_value=_fake_pfl_response('500.00')):
                    c = APIClient()
                    c.force_authenticate(user=client)
                    c.post('/api/payments/paguelofacil/confirm/',
                           {'internal_reference': tx.internal_reference, 'cod_oper': 'AUTH_CAP-FAKE'},
                           format='json')
            except Exception as e:
                errors.append(('confirm', repr(e)))

        def do_webhook():
            try:
                barrier.wait()
                with patch('payments.paguelofacil.PaguelofacilConfig.is_sandbox', return_value=True):
                    c = APIClient()
                    c.post('/api/payments/paguelofacil/webhook/',
                           {'status': 1, 'PARM_1': tx.internal_reference,
                            'codOper': 'AUTH_CAP-FAKE', 'totalPay': '500.00'},
                           format='json')
            except Exception as e:
                errors.append(('webhook', repr(e)))

        t1 = threading.Thread(target=do_confirm)
        t2 = threading.Thread(target=do_webhook)
        t1.start(); t2.start(); t1.join(); t2.join()

        n_payments = Payment.objects.filter(booking=booking).count()
        n_payouts = Payout.objects.filter(booking=booking).count()
        print(f'\n[RACE] Payments={n_payments} Payouts={n_payouts} errores={errors}')
        if n_payments > 1 or n_payouts > 1:
            print('[RACE] DOBLE registro (esperado 1 en Postgres con el lock).')
        else:
            print('[RACE] Un solo registro (correcto).')
        # SQLite serializa; en Postgres el lock garantiza 1. No hacemos assert duro.
        self.assertLessEqual(n_payments, 1)
