from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0020_payment_methods'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                max_length=32,
                choices=[
                    ('new_request', 'Nueva Solicitud'),
                    ('request_accepted', 'Solicitud Aceptada'),
                    ('request_rejected', 'Solicitud Rechazada'),
                    ('payment_received', 'Pago Recibido'),
                    ('booking_confirmed', 'Reserva Confirmada'),
                    ('booking_completed', 'Reserva Completada'),
                    ('new_review', 'Nueva Reseña'),
                    ('new_message', 'Nuevo Mensaje'),
                    ('reminder', 'Recordatorio'),
                    ('event_reminder', 'Recordatorio de Evento'),
                    ('booking_expired', 'Reserva Expirada'),
                    ('booking_cancelled', 'Reserva Cancelada'),
                    ('system', 'Sistema'),
                    ('tier_upgrade', 'Subida de Tier'),
                    ('premium_invitation', 'Invitación Premium'),
                    ('flagged_warning', 'Advertencia de Mensaje'),
                    ('open_gig_available', 'Solicitud Abierta Disponible'),
                    ('open_gig_offer_received', 'Nueva Oferta Recibida'),
                    ('open_gig_offer_accepted', 'Oferta Aceptada'),
                    ('open_gig_offer_rejected', 'Oferta Rechazada'),
                    ('open_gig_expired', 'Solicitud Expirada'),
                ],
            ),
        ),
    ]
