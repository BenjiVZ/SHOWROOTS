from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0014_packbundle'),
    ]

    operations = [
        migrations.AddField(
            model_name='productionpack',
            name='includes_dj',
            field=models.BooleanField(
                default=False,
                help_text='Si el pack incluye DJ — turnkey: el cliente reserva sólo este pack y no necesita buscar DJ aparte.',
            ),
        ),
        migrations.AddField(
            model_name='productionpack',
            name='dj_name',
            field=models.CharField(
                max_length=120, blank=True,
                help_text='Nombre del DJ que viene con el pack (opcional). Si el aliado es DJ + equipo, normalmente es él mismo.',
            ),
        ),
    ]
