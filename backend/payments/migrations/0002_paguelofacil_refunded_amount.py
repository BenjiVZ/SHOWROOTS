from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    """Tope acumulado de reembolsos (vuln I5): guarda cuánto se reembolsó ya."""

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paguelofaciltransaction',
            name='refunded_amount',
            field=models.DecimalField(
                max_digits=10, decimal_places=2, default=Decimal('0.00'),
                help_text='Suma de todos los reembolsos ya procesados sobre esta transacción.',
            ),
        ),
    ]
