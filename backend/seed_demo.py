"""
ShowRoots Demo Seed Script
Creates demo users, talents, and genres for testing the platform.
Run: python manage.py shell < seed_demo.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webdj.settings')
django.setup()

from django.contrib.auth import get_user_model
from talents.models import TalentProfile, Genre
from decimal import Decimal

User = get_user_model()

print("[*] Seeding ShowRoots demo data...")

# ── Genres ──
genre_names = [
    'House', 'Techno', 'Reggaeton', 'Salsa', 'Rock', 'Pop',
    'Jazz', 'Hip Hop', 'R&B', 'EDM', 'Tropical', 'Bachata',
    'Merengue', 'Vallenato', 'Cumbia', 'Funk', 'Soul', 'Latin Pop'
]

genres = {}
from django.utils.text import slugify
for name in genre_names:
    slug = slugify(name)
    g = Genre.objects.filter(name=name).first()
    if not g:
        g = Genre.objects.filter(slug=slug).first()
    if not g:
        g = Genre.objects.create(name=name, slug=slug)
    genres[name] = g
print(f"  [OK] {len(genres)} generos listos")

# ── Demo Users + Talent Profiles ──
talents_data = [
    {
        'username': 'djvoltex',
        'first_name': 'Carlos',
        'last_name': 'Mendoza',
        'email': 'carlos@showroots.com',
        'role': 'talent',
        'profile': {
            'stage_name': 'DJ Voltex',
            'talent_type': 'dj',
            'talent_level': 'premium',
            'description': 'DJ profesional con mas de 10 anos de experiencia en clubs y festivales internacionales. Especialista en House y Techno con sets que llenan cualquier pista.',
            'city': 'Caracas',
            'hourly_rate': Decimal('150.00'),
            'price_min': Decimal('500.00'),
            'price_max': Decimal('2000.00'),
            'experience_years': 10,
            'is_approved': True,
            'is_available': True,
            'rating_avg': Decimal('4.80'),
            'total_reviews': 24,
            'total_bookings': 156,
            'equipment_own': True,
            'equipment_description': 'Pioneer CDJ-3000 x2, DJM-900NXS2, Controlador Pioneer DDJ-1000',
            'genres': ['House', 'Techno', 'EDM'],
        }
    },
    {
        'username': 'mariafuego',
        'first_name': 'Maria',
        'last_name': 'Fuentes',
        'email': 'maria@showroots.com',
        'role': 'talent',
        'profile': {
            'stage_name': 'Maria Fuego',
            'talent_type': 'musician',
            'talent_level': 'premium',
            'description': 'Cantante y saxofonista con formacion clasica y pasion por el jazz moderno. Perfecta para eventos corporativos, cenas de gala y cocteles.',
            'city': 'Valencia',
            'hourly_rate': Decimal('120.00'),
            'price_min': Decimal('400.00'),
            'price_max': Decimal('1500.00'),
            'experience_years': 8,
            'is_approved': True,
            'is_available': True,
            'rating_avg': Decimal('4.90'),
            'total_reviews': 18,
            'total_bookings': 89,
            'equipment_own': True,
            'equipment_description': 'Saxofon Yamaha YAS-62, Sistema PA portatil QSC K12.2',
            'genres': ['Jazz', 'Soul', 'Latin Pop'],
        }
    },
    {
        'username': 'losvientos',
        'first_name': 'Roberto',
        'last_name': 'Herrera',
        'email': 'roberto@showroots.com',
        'role': 'talent',
        'profile': {
            'stage_name': 'Los Vientos del Caribe',
            'talent_type': 'band',
            'talent_level': 'premium',
            'description': 'Banda tropical con 6 integrantes que pone a bailar a cualquier audiencia. Especialistas en bodas, quinces y fiestas corporativas.',
            'city': 'Maracaibo',
            'hourly_rate': Decimal('250.00'),
            'price_min': Decimal('800.00'),
            'price_max': Decimal('3500.00'),
            'experience_years': 15,
            'is_approved': True,
            'is_available': True,
            'rating_avg': Decimal('4.70'),
            'total_reviews': 42,
            'total_bookings': 230,
            'equipment_own': True,
            'equipment_description': 'Sistema completo de sonido e iluminacion para hasta 500 personas',
            'genres': ['Salsa', 'Merengue', 'Tropical', 'Cumbia'],
        }
    },
    {
        'username': 'djnova',
        'first_name': 'Andrea',
        'last_name': 'Suarez',
        'email': 'andrea@showroots.com',
        'role': 'talent',
        'profile': {
            'stage_name': 'DJ Nova',
            'talent_type': 'dj',
            'talent_level': 'standard',
            'description': 'DJ emergente especializada en Reggaeton y musica urbana. Energia contagiosa y sets modernos que conectan con el publico joven.',
            'city': 'Caracas',
            'hourly_rate': Decimal('80.00'),
            'price_min': Decimal('250.00'),
            'price_max': Decimal('800.00'),
            'experience_years': 3,
            'is_approved': True,
            'is_available': True,
            'rating_avg': Decimal('4.50'),
            'total_reviews': 12,
            'total_bookings': 45,
            'equipment_own': True,
            'equipment_description': 'Pioneer DDJ-FLX6, MacBook Pro, PA system',
            'genres': ['Reggaeton', 'Hip Hop', 'Pop'],
        }
    },
    {
        'username': 'elmaestro',
        'first_name': 'Fernando',
        'last_name': 'Castillo',
        'email': 'fernando@showroots.com',
        'role': 'talent',
        'profile': {
            'stage_name': 'El Maestro Castillo',
            'talent_type': 'musician',
            'talent_level': 'standard',
            'description': 'Pianista clasico y contemporaneo. Ideal para bodas, eventos formales y sesiones acusticas intimas. Repertorio de Chopin hasta Ed Sheeran.',
            'city': 'Barquisimeto',
            'hourly_rate': Decimal('90.00'),
            'price_min': Decimal('300.00'),
            'price_max': Decimal('1000.00'),
            'experience_years': 12,
            'is_approved': True,
            'is_available': True,
            'rating_avg': Decimal('4.60'),
            'total_reviews': 8,
            'total_bookings': 67,
            'equipment_own': True,
            'equipment_description': 'Teclado Yamaha P-515, Sistema de amplificacion Bose L1',
            'genres': ['Jazz', 'Pop', 'R&B'],
        }
    },
    {
        'username': 'rockforce',
        'first_name': 'Luis',
        'last_name': 'Ramirez',
        'email': 'luis@showroots.com',
        'role': 'talent',
        'profile': {
            'stage_name': 'Rock Force',
            'talent_type': 'band',
            'talent_level': 'standard',
            'description': 'Banda de rock y pop con covers de los clasicos y exitos actuales. 4 musicos profesionales con mas de 100 shows en vivo.',
            'city': 'Merida',
            'hourly_rate': Decimal('180.00'),
            'price_min': Decimal('600.00'),
            'price_max': Decimal('2000.00'),
            'experience_years': 7,
            'is_approved': True,
            'is_available': True,
            'rating_avg': Decimal('4.40'),
            'total_reviews': 15,
            'total_bookings': 110,
            'equipment_own': True,
            'equipment_description': 'Backline completo: guitarras, bajo, bateria, PA 2000W',
            'genres': ['Rock', 'Pop', 'Funk'],
        }
    },
]

# Create a demo client user
client_user, created = User.objects.get_or_create(
    username='cliente_demo',
    defaults={
        'first_name': 'Juan',
        'last_name': 'Perez',
        'email': 'juan@cliente.com',
        'role': 'client',
    }
)
if created:
    client_user.set_password('demo1234')
    client_user.save()
    print("  [OK] Usuario cliente demo creado (cliente_demo / demo1234)")

# Create a demo partner user
partner_user, created = User.objects.get_or_create(
    username='partner_demo',
    defaults={
        'first_name': 'Ricardo',
        'last_name': 'Gomez',
        'email': 'ricardo@showroots.com',
        'role': 'partner',
    }
)
if created:
    partner_user.set_password('partner1234')
    partner_user.save()
    print("  [OK] Usuario partner demo creado (partner_demo / partner1234)")
else:
    print("  [--] Partner demo ya existe")

# Create talent users and profiles
for td in talents_data:
    profile_data = td.pop('profile')
    genre_names_list = profile_data.pop('genres')
    
    user, created = User.objects.get_or_create(
        username=td['username'],
        defaults={
            'first_name': td['first_name'],
            'last_name': td['last_name'],
            'email': td['email'],
            'role': td['role'],
        }
    )
    if created:
        user.set_password('talent1234')
        user.save()

    profile, _ = TalentProfile.objects.update_or_create(
        user=user,
        defaults=profile_data
    )
    
    # Assign genres
    genre_objs = [genres[g] for g in genre_names_list if g in genres]
    profile.genres.set(genre_objs)
    
    level_tag = '[PREMIUM]' if profile_data.get('talent_level') == 'premium' else '[STD]'
    print(f"  {level_tag} {profile_data['stage_name']} ({td['username']}) - {profile_data['city']}")

print(f"\n[DONE] Demo seed complete!")
print(f"   Client login:  cliente_demo / demo1234")
print(f"   Partner login: partner_demo / partner1234")
print(f"   Talent logins: [username] / talent1234")
print(f"   Admin:         admin / admin123")
