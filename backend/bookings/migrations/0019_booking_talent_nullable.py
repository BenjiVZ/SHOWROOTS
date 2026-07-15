import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Permite reservas de solo-servicios (sin DJ): Booking.talent pasa a NULL."""

    dependencies = [
        ('bookings', '0018_alter_gigoffer_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='talent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                help_text='Talento reservado. Puede ser NULL: reserva de solo-servicios (sin DJ).',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bookings',
                to='talents.talentprofile',
            ),
        ),
    ]
