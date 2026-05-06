"""
Reset Users Script — ShowRoots (Pulsar)
Borra TODOS los usuarios excepto admin y recrea usuarios demo.
Ejecutar: python manage.py shell < reset_users.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from talents.models import TalentProfile, Genre

# ══════════════════════════════════════════════
# 1. Borrar todos los usuarios EXCEPTO admin
# ══════════════════════════════════════════════
deleted_count = User.objects.exclude(is_superuser=True).delete()
print(f"[OK] Eliminados: {deleted_count}")

# ══════════════════════════════════════════════
# 2. Asegurar géneros existentes
# ══════════════════════════════════════════════
genres_data = [
    ('Electrónica', 'electronica', '⚡'),
    ('House', 'house', '🏠'),
    ('Techno', 'techno', '🤖'),
    ('Reggaetón', 'reggaeton', '🔥'),
    ('Salsa', 'salsa', '💃'),
    ('Pop', 'pop', '🎤'),
    ('Rock', 'rock', '🎸'),
    ('Jazz', 'jazz', '🎷'),
    ('Hip-Hop', 'hip-hop', '🎙️'),
    ('Merengue', 'merengue', '🥁'),
    ('Bachata', 'bachata', '🌹'),
    ('Clásica', 'clasica', '🎻'),
    ('Tropical', 'tropical', '🌴'),
    ('R&B', 'rnb', '🎵'),
    ('Funk', 'funk', '🕺'),
]
genre_objs = {}
for name, slug, icon in genres_data:
    try:
        g = Genre.objects.get(slug=slug)
    except Genre.DoesNotExist:
        try:
            g = Genre.objects.get(name=name)
        except Genre.DoesNotExist:
            g = Genre.objects.create(name=name, slug=slug, icon=icon)
    genre_objs[slug] = g

print(f"[OK] Generos listos: {len(genre_objs)}")

# ══════════════════════════════════════════════
# 3. Crear Talentos
# ══════════════════════════════════════════════
PASSWORD = 'Show2026!'

talents_data = [
    {
        'username': 'djvoltex',
        'first_name': 'Carlos',
        'last_name': 'Mendoza',
        'email': 'carlos@showroots.com',
        'city': 'Caracas',
        'phone': '+58 412-5551001',
        'talent': {
            'stage_name': 'DJ Voltex',
            'talent_type': 'dj',
            'talent_level': 'premium',
            'tagline': 'Electrizando cada pista desde 2015',
            'description': 'DJ profesional con más de 10 años de experiencia en festivales y eventos corporativos. Especialista en sesiones de Electrónica, House y Techno. Equipado con Pioneer CDJ-3000 y DJM-900NXS2.',
            'experience_years': 10,
            'hourly_rate': 150.00,
            'price_min': 500,
            'price_max': 2000,
            'equipment_own': True,
            'equipment_description': 'Pioneer CDJ-3000 x2, DJM-900NXS2, QSC K12.2 x2',
            'city': 'Caracas',
            'is_available': True,
            'is_approved': True,
            'is_featured': True,
            'instagram': '@djvoltex',
            'spotify': 'https://open.spotify.com/artist/voltex',
            'genres': ['electronica', 'house', 'techno'],
        }
    },
    {
        'username': 'mariafuego',
        'first_name': 'María',
        'last_name': 'Fuentes',
        'email': 'maria@showroots.com',
        'city': 'Valencia',
        'phone': '+58 414-5552002',
        'talent': {
            'stage_name': 'María Fuego',
            'talent_type': 'musician',
            'talent_level': 'premium',
            'tagline': 'La voz que enciende las noches de Venezuela',
            'description': 'Cantante y saxofonista con formación en el Conservatorio de Valencia. Fusiono jazz, soul y ritmos latinos para crear experiencias musicales únicas. Disponible para eventos privados, bodas y festivales.',
            'experience_years': 8,
            'hourly_rate': 120.00,
            'price_min': 400,
            'price_max': 1500,
            'equipment_own': True,
            'equipment_description': 'Saxofón alto Yamaha YAS-62, micrófono Shure SM58, PA portátil',
            'city': 'Valencia',
            'is_available': True,
            'is_approved': True,
            'is_featured': True,
            'instagram': '@mariafuego',
            'soundcloud': 'https://soundcloud.com/mariafuego',
            'genres': ['jazz', 'pop', 'salsa'],
        }
    },
    {
        'username': 'losvientos',
        'first_name': 'Roberto',
        'last_name': 'Herrera',
        'email': 'roberto@showroots.com',
        'city': 'Maracaibo',
        'phone': '+58 416-5553003',
        'talent': {
            'stage_name': 'Los Vientos del Caribe',
            'talent_type': 'band',
            'talent_level': 'premium',
            'tagline': 'El sabor tropical que necesita tu evento',
            'description': 'Agrupación de 6 músicos especializada en salsa, merengue y tropical. Más de 500 eventos realizados en todo el país. Repertorio amplio que incluye clásicos y éxitos actuales.',
            'experience_years': 15,
            'hourly_rate': 300.00,
            'price_min': 1000,
            'price_max': 5000,
            'equipment_own': True,
            'equipment_description': 'Equipo completo de sonido e iluminación para hasta 500 personas',
            'city': 'Maracaibo',
            'is_available': True,
            'is_approved': True,
            'is_featured': True,
            'instagram': '@losvientosdelcaribe',
            'genres': ['salsa', 'merengue', 'tropical'],
        }
    },
    {
        'username': 'djnova',
        'first_name': 'Andrea',
        'last_name': 'Suárez',
        'email': 'andrea@showroots.com',
        'city': 'Caracas',
        'phone': '+58 412-5554004',
        'talent': {
            'stage_name': 'DJ Nova',
            'talent_type': 'dj',
            'talent_level': 'standard',
            'tagline': 'Beats frescos para una nueva generación',
            'description': 'DJ emergente con estilo fresco y enérgico. Especialista en sesiones de reggaetón, hip-hop y electrónica urbana. Residente en principales clubs de Caracas.',
            'experience_years': 4,
            'hourly_rate': 80.00,
            'price_min': 250,
            'price_max': 800,
            'equipment_own': True,
            'equipment_description': 'Pioneer DDJ-1000, MacBook Pro, Monitores KRK',
            'city': 'Caracas',
            'is_available': True,
            'is_approved': True,
            'is_featured': False,
            'instagram': '@djnova_ve',
            'genres': ['reggaeton', 'hip-hop', 'electronica'],
        }
    },
    {
        'username': 'elmaestro',
        'first_name': 'Fernando',
        'last_name': 'Castillo',
        'email': 'fernando@showroots.com',
        'city': 'Barquisimeto',
        'phone': '+58 414-5555005',
        'talent': {
            'stage_name': 'El Maestro Castillo',
            'talent_type': 'musician',
            'talent_level': 'standard',
            'tagline': 'Violín clásico con alma venezolana',
            'description': 'Violinista con 12 años de trayectoria en orquestas y eventos. Graduado del Sistema de Orquestas. Ideal para bodas, cenas de gala y eventos corporativos.',
            'experience_years': 12,
            'hourly_rate': 100.00,
            'price_min': 350,
            'price_max': 1200,
            'equipment_own': True,
            'equipment_description': 'Violín profesional, amplificación acústica portátil',
            'city': 'Barquisimeto',
            'is_available': True,
            'is_approved': True,
            'is_featured': False,
            'instagram': '@maestrocastillo',
            'spotify': 'https://open.spotify.com/artist/castillo',
            'genres': ['clasica', 'jazz', 'pop'],
        }
    },
    {
        'username': 'rockforce',
        'first_name': 'Luis',
        'last_name': 'Ramírez',
        'email': 'luis@showroots.com',
        'city': 'Mérida',
        'phone': '+58 416-5556006',
        'talent': {
            'stage_name': 'Rock Force',
            'talent_type': 'band',
            'talent_level': 'standard',
            'tagline': 'Rock con energía que sacude el escenario',
            'description': 'Banda de rock alternativo con 4 integrantes. Covers y material original. Experiencia en festivales universitarios, bares y eventos privados en los Andes venezolanos.',
            'experience_years': 6,
            'hourly_rate': 200.00,
            'price_min': 600,
            'price_max': 2500,
            'equipment_own': True,
            'equipment_description': 'Backline completo, PA de 2000W, iluminación LED',
            'city': 'Mérida',
            'is_available': True,
            'is_approved': True,
            'is_featured': False,
            'instagram': '@rockforce_ve',
            'genres': ['rock', 'pop', 'funk'],
        }
    },
]

for td in talents_data:
    talent_info = td.pop('talent')
    genre_slugs = talent_info.pop('genres')
    
    user = User.objects.create_user(
        username=td['username'],
        email=td['email'],
        password=PASSWORD,
        first_name=td['first_name'],
        last_name=td['last_name'],
        role='talent',
        phone=td.get('phone', ''),
        city=td.get('city', ''),
        country='Venezuela',
        is_verified=True,
    )
    
    profile = TalentProfile.objects.create(user=user, **talent_info)
    profile.genres.set([genre_objs[s] for s in genre_slugs if s in genre_objs])
    
    level = '[P]' if talent_info.get('talent_level') == 'premium' else '[S]'
    print(f"  {level} Talento: {user.get_full_name()} ({profile.stage_name})")

print(f"[OK] {len(talents_data)} talentos creados")

# ══════════════════════════════════════════════
# 4. Crear Clientes
# ══════════════════════════════════════════════
clients_data = [
    {
        'username': 'cliente_ana',
        'first_name': 'Ana',
        'last_name': 'Martínez',
        'email': 'ana@cliente.com',
        'city': 'Caracas',
        'phone': '+58 412-7771001',
    },
    {
        'username': 'cliente_jose',
        'first_name': 'José',
        'last_name': 'Rodríguez',
        'email': 'jose@cliente.com',
        'city': 'Valencia',
        'phone': '+58 414-7772002',
    },
    {
        'username': 'cliente_laura',
        'first_name': 'Laura',
        'last_name': 'Pérez',
        'email': 'laura@cliente.com',
        'city': 'Maracaibo',
        'phone': '+58 416-7773003',
    },
]

for cd in clients_data:
    user = User.objects.create_user(
        username=cd['username'],
        email=cd['email'],
        password=PASSWORD,
        first_name=cd['first_name'],
        last_name=cd['last_name'],
        role='client',
        phone=cd.get('phone', ''),
        city=cd.get('city', ''),
        country='Venezuela',
        is_verified=True,
    )
    print(f"  [C] Cliente: {user.get_full_name()}")

print(f"[OK] {len(clients_data)} clientes creados")

# ══════════════════════════════════════════════
# 5. Crear Partner
# ══════════════════════════════════════════════
partner = User.objects.create_user(
    username='partner_ricardo',
    email='ricardo@showroots.com',
    password=PASSWORD,
    first_name='Ricardo',
    last_name='Gómez',
    role='partner',
    phone='+58 412-8881001',
    city='Caracas',
    country='Venezuela',
    is_verified=True,
)
print(f"  [PR] Partner: {partner.get_full_name()}")

print("\n" + "=" * 50)
print("[OK] RESET COMPLETO")
print(f"   Contraseña única para todos: {PASSWORD}")
print(f"   Admin preservado (sin cambios)")
print("=" * 50)
