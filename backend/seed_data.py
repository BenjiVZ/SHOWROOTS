"""
Seed data script for WebDJ platform.
Run with: python manage.py shell < seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from talents.models import Genre, TalentProfile, TalentMedia, TalentExperience
from bookings.models import Booking, Review
from venues.models import Venue
from datetime import date, time

User = get_user_model()

print("🎧 Seeding WebDJ database...")

# ==========================================
# GENRES
# ==========================================
genres_data = [
    ('House', 'house', '🏠'),
    ('Techno', 'techno', '⚡'),
    ('EDM', 'edm', '🎛️'),
    ('Reggaeton', 'reggaeton', '🔥'),
    ('Salsa', 'salsa', '💃'),
    ('Merengue', 'merengue', '🎺'),
    ('Bachata', 'bachata', '🌹'),
    ('Hip Hop', 'hip-hop', '🎤'),
    ('R&B', 'rnb', '🎵'),
    ('Pop', 'pop', '⭐'),
    ('Rock', 'rock', '🎸'),
    ('Jazz', 'jazz', '🎷'),
    ('Latin Pop', 'latin-pop', '🌎'),
    ('Trap', 'trap', '💎'),
    ('Drum & Bass', 'drum-and-bass', '🥁'),
    ('Deep House', 'deep-house', '🌊'),
    ('Progressive House', 'progressive-house', '🔮'),
    ('Afrobeat', 'afrobeat', '🌍'),
    ('Cumbia', 'cumbia', '🪗'),
    ('Vallenato', 'vallenato', '🎹'),
    ('Electrónica', 'electronica', '💿'),
    ('Disco', 'disco', '🪩'),
    ('Funk', 'funk', '🕺'),
    ('Reggae', 'reggae', '🟢'),
]

genres = {}
for name, slug, icon in genres_data:
    genre, _ = Genre.objects.get_or_create(
        slug=slug, defaults={'name': name, 'icon': icon}
    )
    genres[slug] = genre

print(f"  ✅ {Genre.objects.count()} géneros creados")

# ==========================================
# ADMIN USER
# ==========================================
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@webdj.com',
        'first_name': 'Admin',
        'last_name': 'WebDJ',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("  ✅ Admin creado (admin / admin123)")

# ==========================================
# TALENT USERS + PROFILES
# ==========================================
talents_data = [
    {
        'username': 'djcarlos',
        'first_name': 'Carlos',
        'last_name': 'Mendoza',
        'email': 'carlos@webdj.com',
        'city': 'Caracas',
        'phone': '+58 412 1234567',
        'profile': {
            'talent_type': 'dj',
            'stage_name': 'DJ C-Mendz',
            'tagline': 'Haciendo vibrar Caracas desde 2015',
            'description': 'DJ profesional con más de 9 años de experiencia en eventos corporativos, bodas y fiestas privadas. Especialista en mezclas de reggaeton, EDM y house que mantienen la pista llena toda la noche.',
            'experience_years': 9,
            'price_min': 200,
            'price_max': 800,
            'equipment_own': True,
            'equipment_description': 'Pioneer DDJ-1000, JBL EON615 x2, iluminación LED completa',
            'city': 'Caracas',
            'is_featured': True,
            'is_available': True,
            'instagram': '@djcmendz',
            'genres': ['reggaeton', 'edm', 'house', 'latin-pop', 'trap'],
        }
    },
    {
        'username': 'djvaleria',
        'first_name': 'Valeria',
        'last_name': 'Torres',
        'email': 'valeria@webdj.com',
        'city': 'Valencia',
        'phone': '+58 414 7654321',
        'profile': {
            'talent_type': 'dj',
            'stage_name': 'ValeBeats',
            'tagline': 'El sonido que necesitas para tu evento perfecto',
            'description': 'Soy ValeBeats, DJ femenina apasionada por la música electrónica y los ritmos latinos. Mi estilo único fusiona deep house con sabores tropicales para crear una experiencia inolvidable en cada evento.',
            'experience_years': 6,
            'price_min': 150,
            'price_max': 600,
            'equipment_own': True,
            'equipment_description': 'Pioneer DDJ-800, QSC K12.2 x2, micrófono inalámbrico',
            'city': 'Valencia',
            'is_featured': True,
            'is_available': True,
            'instagram': '@valebeats',
            'genres': ['deep-house', 'reggaeton', 'latin-pop', 'pop', 'electronica'],
        }
    },
    {
        'username': 'djmarcelo',
        'first_name': 'Marcelo',
        'last_name': 'Díaz',
        'email': 'marcelo@webdj.com',
        'city': 'Maracaibo',
        'phone': '+58 424 9876543',
        'profile': {
            'talent_type': 'dj',
            'stage_name': 'Marcelo D',
            'tagline': 'Techno & House desde el Zulia para el mundo',
            'description': 'Productor y DJ con raíces en el underground de Maracaibo. Me especializo en techno melódico y progressive house, con sets que te llevan en un viaje sonoro único.',
            'experience_years': 12,
            'price_min': 300,
            'price_max': 1200,
            'equipment_own': True,
            'equipment_description': 'Pioneer CDJ-2000NXS2 x2, DJM-900NXS2, monitores KRK, controlador MIDI',
            'city': 'Maracaibo',
            'is_featured': True,
            'is_available': True,
            'instagram': '@marcelod_dj',
            'genres': ['techno', 'progressive-house', 'deep-house', 'electronica', 'house'],
        }
    },
    {
        'username': 'bandalamanga',
        'first_name': 'Ricardo',
        'last_name': 'Fernández',
        'email': 'lamanga@webdj.com',
        'city': 'Barquisimeto',
        'phone': '+58 416 1112233',
        'profile': {
            'talent_type': 'band',
            'stage_name': 'La Manga',
            'tagline': 'Salsa, merengue y gaitas para tu fiesta',
            'description': 'Somos La Manga, una banda de 7 músicos con más de 15 años llevando la mejor música tropical a eventos en todo el país. Desde una boda íntima hasta un festival masivo, ponemos a bailar a todos.',
            'experience_years': 15,
            'price_min': 500,
            'price_max': 2000,
            'equipment_own': True,
            'equipment_description': 'Equipo de sonido completo PA, instrumentos profesionales, iluminación de escenario',
            'city': 'Barquisimeto',
            'is_featured': True,
            'is_available': True,
            'instagram': '@lamangaband',
            'genres': ['salsa', 'merengue', 'cumbia', 'vallenato', 'latin-pop'],
        }
    },
    {
        'username': 'saxojuan',
        'first_name': 'Juan',
        'last_name': 'Martínez',
        'email': 'juan@webdj.com',
        'city': 'Caracas',
        'phone': '+58 412 5556677',
        'profile': {
            'talent_type': 'musician',
            'stage_name': 'Juan Sax',
            'tagline': 'El saxofón que enamora en tu evento',
            'description': 'Saxofonista profesional graduado del Conservatorio de Música. Toco en bodas, cenas románticas, cócteles corporativos y eventos de lujo. Mi repertorio incluye jazz, bossa nova, pop y música clásica.',
            'experience_years': 10,
            'price_min': 150,
            'price_max': 500,
            'equipment_own': True,
            'equipment_description': 'Saxofón alto Selmer Paris, saxofón tenor Yamaha, amplificador, micrófono',
            'city': 'Caracas',
            'is_featured': True,
            'is_available': True,
            'instagram': '@juansax',
            'genres': ['jazz', 'pop', 'rnb', 'latin-pop', 'funk'],
        }
    },
    {
        'username': 'djnightowl',
        'first_name': 'Andrés',
        'last_name': 'Ramírez',
        'email': 'nightowl@webdj.com',
        'city': 'Caracas',
        'phone': '+58 414 8889900',
        'profile': {
            'talent_type': 'dj',
            'stage_name': 'Night Owl',
            'tagline': 'Hip Hop y Trap para las noches más duras',
            'description': 'Night Owl es sinónimo de noches épicas. Con años de experiencia en los mejores clubs de Caracas, mis sets de hip hop, trap y reggaeton son la definición de fiesta.',
            'experience_years': 7,
            'price_min': 180,
            'price_max': 700,
            'equipment_own': True,
            'equipment_description': 'Pioneer DDJ-FLX6, scratching setup, PA system portátil',
            'city': 'Caracas',
            'is_available': True,
            'instagram': '@nightowl_dj',
            'genres': ['hip-hop', 'trap', 'reggaeton', 'rnb', 'afrobeat'],
        }
    },
    {
        'username': 'violinista_ana',
        'first_name': 'Ana',
        'last_name': 'García',
        'email': 'ana@webdj.com',
        'city': 'Mérida',
        'phone': '+58 416 3334455',
        'profile': {
            'talent_type': 'musician',
            'stage_name': 'Ana Strings',
            'tagline': 'Violín clásico y moderno para momentos únicos',
            'description': 'Violinista con formación clásica y pasión por la música moderna. Ofrezco shows con violín eléctrico LED para una experiencia visual y auditiva espectacular. Ideal para bodas, cócteles y eventos VIP.',
            'experience_years': 8,
            'price_min': 200,
            'price_max': 600,
            'equipment_own': True,
            'equipment_description': 'Violín acústico 4/4 luthier, violín eléctrico LED, amplificador Roland, looper',
            'city': 'Mérida',
            'is_available': True,
            'instagram': '@anastrings',
            'genres': ['pop', 'latin-pop', 'jazz', 'electronica', 'disco'],
        }
    },
    {
        'username': 'rockabilly_vzla',
        'first_name': 'Pedro',
        'last_name': 'Hernández',
        'email': 'rockbilly@webdj.com',
        'city': 'Maracay',
        'phone': '+58 424 1122334',
        'profile': {
            'talent_type': 'band',
            'stage_name': 'Los Rebeldes',
            'tagline': 'Rock nacional e internacional para tu evento',
            'description': 'Banda de rock con repertorio variado desde clásicos del rock en español hasta éxitos internacionales. Energía pura en el escenario con una puesta en escena profesional.',
            'experience_years': 11,
            'price_min': 400,
            'price_max': 1500,
            'equipment_own': True,
            'equipment_description': 'Backline completo, PA system, iluminación, técnico de sonido incluido',
            'city': 'Maracay',
            'is_available': True,
            'instagram': '@losrebeldes_ve',
            'genres': ['rock', 'pop', 'funk', 'disco', 'latin-pop'],
        }
    },
]

for talent_data in talents_data:
    profile_data = talent_data.pop('profile')
    genre_slugs = profile_data.pop('genres')

    user, created = User.objects.get_or_create(
        username=talent_data['username'],
        defaults={
            **{k: v for k, v in talent_data.items() if k != 'username'},
            'role': 'talent',
        }
    )
    if created:
        user.set_password('talent123')
        user.save()

    profile, _ = TalentProfile.objects.get_or_create(
        user=user,
        defaults=profile_data
    )
    profile.genres.set([genres[slug] for slug in genre_slugs])

print(f"  ✅ {TalentProfile.objects.count()} talentos creados")

# ==========================================
# CLIENT USERS
# ==========================================
clients_data = [
    {'username': 'maria_cliente', 'first_name': 'María', 'last_name': 'López', 'email': 'maria@test.com', 'city': 'Caracas'},
    {'username': 'jose_cliente', 'first_name': 'José', 'last_name': 'Rodríguez', 'email': 'jose@test.com', 'city': 'Valencia'},
    {'username': 'laura_cliente', 'first_name': 'Laura', 'last_name': 'Pérez', 'email': 'laura@test.com', 'city': 'Maracaibo'},
]

for client_data in clients_data:
    user, created = User.objects.get_or_create(
        username=client_data['username'],
        defaults={**{k: v for k, v in client_data.items() if k != 'username'}, 'role': 'client'}
    )
    if created:
        user.set_password('client123')
        user.save()

print(f"  ✅ {User.objects.filter(role='client').count()} clientes creados")

# ==========================================
# VENUES
# ==========================================
venues_data = [
    {
        'name': 'Hacienda La Colonial',
        'venue_type': 'hacienda',
        'description': 'Hermosa hacienda colonial con amplios jardines, ideal para bodas y eventos al aire libre. Capacidad para hasta 300 personas con estacionamiento privado.',
        'address': 'Km 15 Carretera Panamericana, Sector Los Teques',
        'city': 'Los Teques',
        'state': 'Miranda',
        'capacity_min': 50,
        'capacity_max': 300,
        'price_range': '$$$',
        'amenities': ['Estacionamiento', 'Catering', 'Jardines', 'Capilla', 'Suite Nupcial', 'Generador Eléctrico'],
        'phone': '+58 212 5551234',
        'is_verified': True,
    },
    {
        'name': 'Club Náutico Marina Bay',
        'venue_type': 'club',
        'description': 'Club frente al mar con vista espectacular al atardecer. Perfecto para fiestas, eventos corporativos y celebraciones exclusivas.',
        'address': 'Av. Principal Marina Bay, Sector Caraballeda',
        'city': 'La Guaira',
        'state': 'Vargas',
        'capacity_min': 100,
        'capacity_max': 500,
        'price_range': '$$$$',
        'amenities': ['Vista al mar', 'Piscina', 'Bar', 'DJ Booth', 'Estacionamiento VIP', 'Catering Premium'],
        'phone': '+58 212 5555678',
        'is_verified': True,
    },
    {
        'name': 'Salón Imperial',
        'venue_type': 'salon',
        'description': 'Salón de eventos elegante y moderno en el corazón de Caracas. Equipado con sonido profesional e iluminación de última generación.',
        'address': 'Av. Francisco de Miranda, Centro Comercial Lido, Nivel 5',
        'city': 'Caracas',
        'state': 'Distrito Capital',
        'capacity_min': 30,
        'capacity_max': 200,
        'price_range': '$$',
        'amenities': ['Sonido Profesional', 'Iluminación LED', 'Bar', 'Cocina', 'WiFi', 'Estacionamiento'],
        'phone': '+58 212 5559999',
        'is_verified': True,
    },
    {
        'name': 'Hotel Humboldt Rooftop',
        'venue_type': 'rooftop',
        'description': 'Terraza panorámica con vistas de 360° de Caracas desde el mítico Hotel Humboldt en el Ávila. Una experiencia única para eventos exclusivos.',
        'address': 'Cerro El Ávila, Parque Nacional Waraira Repano',
        'city': 'Caracas',
        'state': 'Distrito Capital',
        'capacity_min': 20,
        'capacity_max': 100,
        'price_range': '$$$$',
        'amenities': ['Vista Panorámica', 'Bar Premium', 'Catering Gourmet', 'Helipuerto', 'Suite VIP'],
        'phone': '+58 212 5550000',
        'is_verified': True,
    },
    {
        'name': 'Restaurante El Patio Criollo',
        'venue_type': 'restaurant',
        'description': 'Restaurante con ambiente acogedor y patio interior techado. Ideal para celebraciones íntimas, cumpleaños y cenas especiales con música en vivo.',
        'address': 'Calle 72 con Av. 3H, Sector Bellas Artes',
        'city': 'Maracaibo',
        'state': 'Zulia',
        'capacity_min': 20,
        'capacity_max': 80,
        'price_range': '$$',
        'amenities': ['Cocina Criolla', 'Bar', 'Escenario', 'Aire Acondicionado', 'Estacionamiento'],
        'phone': '+58 261 7778899',
    },
    {
        'name': 'Playa Parguito Beach Club',
        'venue_type': 'beach',
        'description': 'Beach club en la famosa Playa Parguito de Margarita. Eventos frente al mar con el mejor atardecer del Caribe.',
        'address': 'Playa Parguito, Municipio Antolín del Campo',
        'city': 'Isla de Margarita',
        'state': 'Nueva Esparta',
        'capacity_min': 50,
        'capacity_max': 400,
        'price_range': '$$$',
        'amenities': ['Playa Privada', 'Bar de Playa', 'DJ Booth', 'Parrillera', 'Toldos VIP', 'Duchas'],
        'phone': '+58 295 2634567',
    },
]

for venue_data in venues_data:
    Venue.objects.get_or_create(
        name=venue_data['name'],
        defaults=venue_data
    )

print(f"  ✅ {Venue.objects.count()} venues creados")

# ==========================================
# SAMPLE BOOKINGS & REVIEWS
# ==========================================
maria = User.objects.get(username='maria_cliente')
jose = User.objects.get(username='jose_cliente')
djcarlos_profile = TalentProfile.objects.get(stage_name='DJ C-Mendz')
valebeats_profile = TalentProfile.objects.get(stage_name='ValeBeats')

booking1, _ = Booking.objects.get_or_create(
    client=maria,
    talent=djcarlos_profile,
    event_date=date(2026, 5, 15),
    defaults={
        'event_type': 'wedding',
        'event_name': 'Boda de María y Roberto',
        'event_time_start': time(18, 0),
        'event_time_end': time(2, 0),
        'event_location': 'Hacienda La Colonial, Los Teques',
        'guest_count': 150,
        'description': 'Boda de 150 personas. Necesitamos música variada: cocktail con lounge/chill, luego reggaeton y pop para la fiesta.',
        'budget': 500,
        'quoted_price': 450,
        'status': 'completed',
    }
)

Review.objects.get_or_create(
    booking=booking1,
    defaults={
        'client': maria,
        'talent': djcarlos_profile,
        'rating': 5,
        'comment': '¡Espectacular! DJ C-Mendz hizo que nuestra boda fuera inolvidable. La pista estuvo llena toda la noche. 100% recomendado.',
    }
)

booking2, _ = Booking.objects.get_or_create(
    client=jose,
    talent=valebeats_profile,
    event_date=date(2026, 6, 20),
    defaults={
        'event_type': 'corporate',
        'event_name': 'Fiesta de Fin de Año Corporativa',
        'event_time_start': time(20, 0),
        'event_time_end': time(1, 0),
        'event_location': 'Salón Imperial, Caracas',
        'guest_count': 80,
        'description': 'Evento corporativo para 80 personas. Ambiente elegante al inicio, fiesta al final.',
        'budget': 400,
        'quoted_price': 350,
        'status': 'completed',
    }
)

Review.objects.get_or_create(
    booking=booking2,
    defaults={
        'client': jose,
        'talent': valebeats_profile,
        'rating': 5,
        'comment': 'ValeBeats superó todas las expectativas. Excelente selección musical y muy profesional. Ya la reservamos para el próximo año.',
    }
)

# Pending booking
Booking.objects.get_or_create(
    client=maria,
    talent=valebeats_profile,
    event_date=date(2026, 8, 10),
    defaults={
        'event_type': 'birthday',
        'event_name': 'Cumpleaños de Sofía',
        'event_time_start': time(19, 0),
        'event_time_end': time(23, 0),
        'event_location': 'Restaurante El Patio Criollo, Maracaibo',
        'guest_count': 40,
        'description': 'Fiesta de cumpleaños 30 de mi hija. Quiere música variada pero sobre todo reggaeton y pop.',
        'budget': 300,
        'status': 'pending',
    }
)

print(f"  ✅ {Booking.objects.count()} bookings creados")
print(f"  ✅ {Review.objects.count()} reviews creados")

print("\n🎉 ¡Seed completado exitosamente!")
print(f"   Admin: admin / admin123")
print(f"   Talentos: djcarlos, djvaleria, etc. / talent123")
print(f"   Clientes: maria_cliente, jose_cliente, laura_cliente / client123")
