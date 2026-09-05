from pathlib import Path
import secrets
import environ
import os
import cloudinary
import dj_database_url
from celery.schedules import crontab
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
DEBUG = env.bool('DEBUG', default=not bool(RENDER_EXTERNAL_HOSTNAME))

SECRET_KEY = env('SECRET_KEY', default='')
if not SECRET_KEY and not DEBUG:
    raise ImproperlyConfigured('SECRET_KEY must be configured when DEBUG=0')
SECRET_KEY = SECRET_KEY or secrets.token_urlsafe(50)
if RENDER_EXTERNAL_HOSTNAME and (
    len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-')
):
    raise ImproperlyConfigured(
        'SECRET_KEY debe ser larga y aleatoria en el entorno de producción.'
    )

default_allowed_hosts = ['localhost', '127.0.0.1']
if RENDER_EXTERNAL_HOSTNAME:
    default_allowed_hosts.append(RENDER_EXTERNAL_HOSTNAME)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=default_allowed_hosts)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'django.contrib.humanize',

    # apps propias
    'users',
    'customer',
    'workorder',
    'pumpingreport',
    'generalreport',
    'electricalreport',
    'notification',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.PrivateResponseHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ayc_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ayc_api.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=env(
            'DATABASE_URL',
            default=env('URL_DB', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        )
    )
}

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.authentication.CookieJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'login': '5/minute',
        'refresh': '30/minute',
        'bootstrap': '3/hour',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = env('CSRF_COOKIE_SAMESITE', default='Lax' if DEBUG else 'None')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'users.validators.StrongPasswordValidator'},
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=25)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'no-reply@localhost')
default_frontend_url = (
    f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if RENDER_EXTERNAL_HOSTNAME
    else 'http://localhost:5173'
)
FRONTEND_URL = env('FRONTEND_URL', default=default_frontend_url)
BOOTSTRAP_ADMIN_TOKEN = env('BOOTSTRAP_ADMIN_TOKEN', default='')
AUTH_COOKIE_SAMESITE = env('AUTH_COOKIE_SAMESITE', default='Lax' if DEBUG else 'None')
AUTH_COOKIE_SECURE = env.bool('AUTH_COOKIE_SECURE', default=not DEBUG)
if AUTH_COOKIE_SAMESITE.lower() == 'none' and not AUTH_COOKIE_SECURE:
    raise ImproperlyConfigured(
        'AUTH_COOKIE_SAMESITE=None requiere AUTH_COOKIE_SECURE=1.'
    )
default_frontend_origins = [default_frontend_url]
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=default_frontend_origins,
)
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=default_frontend_origins,
)
CORS_ALLOW_CREDENTIALS = True
if '*' in CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured(
        'CORS_ALLOWED_ORIGINS no puede usar * cuando se envían credenciales.'
    )
if RENDER_EXTERNAL_HOSTNAME:
    configured_origins = set(CORS_ALLOWED_ORIGINS + CSRF_TRUSTED_ORIGINS)
    insecure_origins = {
        origin for origin in configured_origins
        if not origin.startswith('https://')
    }
    if insecure_origins:
        raise ImproperlyConfigured(
            'En producción, CORS_ALLOWED_ORIGINS y CSRF_TRUSTED_ORIGINS deben usar HTTPS.'
        )

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=not DEBUG)
SECURE_HSTS_SECONDS = env.int(
    'SECURE_HSTS_SECONDS',
    default=31536000 if not DEBUG else 0,
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS',
    default=False,
)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = env('SECURE_REFERRER_POLICY', default='same-origin')
X_FRAME_OPTIONS = 'DENY'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False
if CSRF_COOKIE_SAMESITE.lower() == 'none' and not CSRF_COOKIE_SECURE:
    raise ImproperlyConfigured(
        'CSRF_COOKIE_SAMESITE=None requiere una cookie CSRF segura.'
    )

cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME', default=env('CLOUD_NAME', default='')),
    api_key=env('CLOUDINARY_API_KEY', default=env('API_KEY', default='')),
    api_secret=env('CLOUDINARY_API_SECRET', default=env('API_SECRET', default='')),
)

CLOUDINARY_CLOUD_NAME = env(
    'CLOUDINARY_CLOUD_NAME',
    default=env('CLOUD_NAME', default=''),
)
CLOUDINARY_LOGO_PUBLIC_ID = env('CLOUDINARY_LOGO_PUBLIC_ID', default='')
CLOUDINARY_LOGO_URL = ''
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_LOGO_PUBLIC_ID:
    CLOUDINARY_LOGO_URL = (
        f'https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload/'
        f'f_png,q_auto/{quote(CLOUDINARY_LOGO_PUBLIC_ID, safe="/")}.png'
    )

PUSHER_CONFIG = {
    'app_id': env('APP_ID', default=''),
    'key': env('KEY', default=''),
    'secret': env('SECRET', default=''),
    'cluster': env('CLUSTER', default=''),
    'ssl': True,
}
PUSHER_ENABLED = env.bool('PUSHER_ENABLED', default=False)

CELERY_ENABLED = env.bool('CELERY_ENABLED', default=bool(os.getenv('CELERY_BROKER_URL')))
if CELERY_ENABLED:
    CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)
else:
    # Permite probar la API gratis sin un Redis ni un worker ejecutandose.
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'
CELERY_TASK_ALWAYS_EAGER = not CELERY_ENABLED
CELERY_TASK_EAGER_PROPAGATES = True

CELERY_BEAT_SCHEDULE = {
    'recordatorio_trabajos_del_dia': {
        'task': 'workorder.tasks.enviar_recordatorio_trabajos_dia',
        'schedule': crontab(hour=7, minute=0),
    },
}

DATA_UPLOAD_MAX_MEMORY_SIZE = env.int('DATA_UPLOAD_MAX_MEMORY_SIZE', default=10485760)
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int('FILE_UPLOAD_MAX_MEMORY_SIZE', default=10485760)
