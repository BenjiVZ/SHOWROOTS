"""
Django settings for Pulsar / SHOWROOTS - DJ Talent Marketplace
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env (dev local) — en prod las vars ya vienen del systemd EnvironmentFile
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-webdj-dev-key-change-in-production-2024'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')

# ALLOWED_HOSTS: en prod viene de env (coma-separado). En dev acepta todo.
_default_hosts = '*,backend.aplicacionesdamasco.com,frontend.aplicacionesdamasco.com,3000.masterslogic.com,3001.masterslogic.com,localhost'
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', _default_hosts).split(',') if h.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # Local apps
    'accounts',
    'talents',
    'bookings',
    'venues',
    'payments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.LastSeenMiddleware',
]

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# En prod: setear DB_ENGINE=postgres + DB_NAME/DB_USER/DB_PASSWORD/DB_HOST en .env
# En dev: SQLite por defecto
if os.environ.get('DB_ENGINE', '').lower() in ('postgres', 'postgresql'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'pulsar'),
            'USER': os.environ.get('DB_USER', 'pulsar_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    # Rate limiting — protección básica antes de Stripe
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '600/minute',
    },
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://im-pulsar.com',
    'https://www.im-pulsar.com',
    'https://api.im-pulsar.com',
    'https://frontend.aplicacionesdamasco.com',
    'http://frontend.aplicacionesdamasco.com',
    'https://backend.aplicacionesdamasco.com',
    'http://backend.aplicacionesdamasco.com',
    'https://3000.masterslogic.com',
    'https://3001.masterslogic.com',
    'http://localhost:3000',
    'http://localhost:3001',
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'https://im-pulsar.com',
    'https://www.im-pulsar.com',
    'https://api.im-pulsar.com',
    'https://frontend.aplicacionesdamasco.com',
    'https://backend.aplicacionesdamasco.com',
    'https://3000.masterslogic.com',
    'https://3001.masterslogic.com',
]

# ── Email Configuration ──
# Auto-detección: si hay credenciales SMTP, usa SMTP real; si no, imprime en consola.
import os

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# Timeout corto: si Gmail no responde en 10s, falla rápido en vez de colgar el worker.
# Combinado con el envío en thread (accounts/emails.py), un SMTP caído nunca produce 504.
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 10))

# Si el admin define un EMAIL_BACKEND explícito, respetarlo.
# Si no, usar SMTP cuando hay credenciales (EMAIL_HOST_USER + EMAIL_HOST_PASSWORD),
# o caer a consola en dev.
if os.environ.get('EMAIL_BACKEND'):
    EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
elif EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    f'Pulsar <{EMAIL_HOST_USER}>' if EMAIL_HOST_USER else 'Pulsar <no-reply@showroots.com>'
)

# Frontend URL for building reset links in emails
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://frontend.aplicacionesdamasco.com')

# ── Paguelofacil (pasarela de pagos) ──
PAGUELOFACIL_ENV = os.environ.get('PAGUELOFACIL_ENV', 'sandbox')
PAGUELOFACIL_CCLW = os.environ.get('PAGUELOFACIL_CCLW', '')
PAGUELOFACIL_ACCESS_TOKEN = os.environ.get('PAGUELOFACIL_ACCESS_TOKEN', '')
PAGUELOFACIL_RETURN_URL = os.environ.get(
    'PAGUELOFACIL_RETURN_URL',
    f'{FRONTEND_URL.rstrip("/")}/payment/return'
)
PAGUELOFACIL_WEBHOOK_URL = os.environ.get(
    'PAGUELOFACIL_WEBHOOK_URL',
    f'{FRONTEND_URL.rstrip("/")}/api/payments/paguelofacil/webhook/'
)
# HMAC-SHA256 del body con este secret debe matchear el header X-Paguelofacil-Signature.
# Si está vacío y estamos en sandbox: aceptamos sin validar. En prod: warning.
# Cuando soporte de PFL active el webhook, pedirles el secret y configurarlo acá.
PAGUELOFACIL_WEBHOOK_SECRET = os.environ.get('PAGUELOFACIL_WEBHOOK_SECRET', '')

# ── Production hardening ──
# Cuando DEBUG=False (prod) activamos SSL, HSTS, cookies seguras y proxy headers.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 días al principio; subir a 1 año cuando esté estable
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

# ── Spaces (S3-compatible) para MEDIA en producción ──
# Si USE_SPACES=True, los uploads van a DigitalOcean Spaces vía django-storages.
if os.environ.get('USE_SPACES', 'False') == 'True':
    INSTALLED_APPS += ['storages']
    AWS_ACCESS_KEY_ID = os.environ['SPACES_KEY']
    AWS_SECRET_ACCESS_KEY = os.environ['SPACES_SECRET']
    AWS_STORAGE_BUCKET_NAME = os.environ['SPACES_BUCKET']
    AWS_S3_ENDPOINT_URL = os.environ.get('SPACES_ENDPOINT', 'https://nyc3.digitaloceanspaces.com')
    AWS_S3_REGION_NAME = os.environ.get('SPACES_REGION', 'nyc3')
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # CDN opcional — si activás el CDN del Space, exponé media bajo ese hostname.
    SPACES_CDN = os.environ.get('SPACES_CDN', '')
    if SPACES_CDN:
        MEDIA_URL = f'https://{SPACES_CDN}/'
    else:
        MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
