from django.db import migrations


def activate_existing_partners(apps, schema_editor):
    """Usuarios con role='partner' arrancan con el flag activo y la oferta 'referral'."""
    User = apps.get_model('accounts', 'User')
    for u in User.objects.filter(role='partner'):
        u.is_partner_active = True
        if not u.partner_offers:
            u.partner_offers = ['referral']
        u.save(update_fields=['is_partner_active', 'partner_offers'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_is_partner_active_user_partner_offers'),
    ]

    operations = [
        migrations.RunPython(activate_existing_partners, noop_reverse),
    ]
