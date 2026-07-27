import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


PAYMENT_METHOD_CODE_CHOICES = [
    ('card', 'Tarjeta'),
    ('transfer', 'Transferencia'),
    ('paypal', 'PayPal'),
    ('cash', 'Efectivo'),
    ('other', 'Otro'),
]
PAYMENT_TYPE_CHOICES = [
    ('deposit', 'Abono/Depósito'),
    ('full', 'Pago Total'),
    ('balance', 'Saldo Restante'),
]


def seed_methods(apps, schema_editor):
    PaymentMethod = apps.get_model('bookings', 'PaymentMethod')
    defaults = [
        dict(
            name='Transferencia bancaria (ACH)',
            slug='transferencia-ach',
            kind='manual',
            is_active=True,
            display_order=1,
            instructions=(
                'Realiza la transferencia por el monto exacto a la cuenta indicada '
                'y sube el comprobante con el número de referencia.'
            ),
            account_holder='',
            bank_name='',
            account_number='',
            account_type='',
            requires_proof=True,
            payment_method_code='transfer',
        ),
        dict(
            name='Efectivo / otro',
            slug='efectivo',
            kind='manual',
            is_active=True,
            display_order=2,
            instructions=(
                'Coordina el pago con el equipo de ShowRoots y sube una foto del '
                'recibo/voucher como comprobante (opcional para efectivo).'
            ),
            requires_proof=False,
            payment_method_code='cash',
        ),
    ]
    for d in defaults:
        PaymentMethod.objects.get_or_create(slug=d['slug'], defaults=d)


def unseed_methods(apps, schema_editor):
    PaymentMethod = apps.get_model('bookings', 'PaymentMethod')
    PaymentMethod.objects.filter(slug__in=['transferencia-ach', 'efectivo']).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookings', '0019_booking_talent_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nombre visible: "Transferencia BAC", "Yappy", "Efectivo"…', max_length=80)),
                ('slug', models.SlugField(blank=True, help_text='Identificador único (se autogenera desde el nombre si se deja vacío).', max_length=90, unique=True)),
                ('kind', models.CharField(choices=[('manual', 'Manual (comprobante + revisión)'), ('automatic', 'Automático (pasarela)')], default='manual', max_length=10)),
                ('provider', models.CharField(blank=True, help_text="Para automáticos: 'paguelofacil'. Manuales: dejar vacío.", max_length=40)),
                ('is_active', models.BooleanField(default=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('instructions', models.TextField(blank=True, help_text='Instrucciones que ve el cliente para completar el pago.')),
                ('account_holder', models.CharField(blank=True, help_text='Titular de la cuenta / beneficiario.', max_length=120)),
                ('bank_name', models.CharField(blank=True, max_length=80)),
                ('account_number', models.CharField(blank=True, max_length=60)),
                ('account_type', models.CharField(blank=True, help_text='Ahorro / Corriente, etc.', max_length=40)),
                ('phone', models.CharField(blank=True, help_text='Teléfono para Yappy / Nequi.', max_length=40)),
                ('extra_info', models.CharField(blank=True, help_text='Cédula/RUC, email u otro dato de contacto.', max_length=200)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='payment_methods/')),
                ('requires_proof', models.BooleanField(default=True, help_text='El cliente debe subir comprobante (aplica a métodos manuales).')),
                ('payment_method_code', models.CharField(choices=PAYMENT_METHOD_CODE_CHOICES, default='transfer', help_text='Cómo se registra en el Payment al aprobar (transfer / cash / other…).', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Método de pago',
                'verbose_name_plural': 'Métodos de pago',
                'db_table': 'payment_methods',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ManualPaymentOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_type', models.CharField(choices=PAYMENT_TYPE_CHOICES, default='full', max_length=10)),
                ('reference', models.CharField(help_text='N° de referencia / confirmación que el cliente ingresa.', max_length=120)),
                ('receipt', models.ImageField(blank=True, null=True, upload_to='payments/receipts/')),
                ('client_note', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending_review', 'En revisión'), ('approved', 'Aprobada'), ('rejected', 'Rechazada'), ('cancelled', 'Cancelada')], default='pending_review', max_length=16)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_notes', models.TextField(blank=True)),
                ('rejection_reason', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manual_payments', to='bookings.booking')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manual_payment_orders', to=settings.AUTH_USER_MODEL)),
                ('method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='bookings.paymentmethod')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manual_order', to='bookings.payment')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_manual_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pago por revisar',
                'verbose_name_plural': 'Pagos por revisar',
                'db_table': 'manual_payment_orders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='manualpaymentorder',
            index=models.Index(fields=['status', 'created_at'], name='manualpay_status_created_idx'),
        ),
        migrations.RunPython(seed_methods, unseed_methods),
    ]
