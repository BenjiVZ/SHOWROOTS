from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_backfill_is_partner_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_seen_at',
            field=models.DateTimeField(
                blank=True, null=True,
                help_text='Última vez que el usuario hizo una petición autenticada. Usado para decidir si notificar por email.',
                verbose_name='Última actividad',
            ),
        ),
    ]
