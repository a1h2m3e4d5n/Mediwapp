import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
ENVIRONMENT = os.getenv("DJANGO_ENV", "local").lower()
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'demo-only-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'core',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'mediwapp.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'mediwapp.wsgi.application'

# Render provides DATABASE_URL for its PostgreSQL service. Keep the existing
# DB_* fallback for local SQL Server development.
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DB_ENGINE = os.getenv("DB_ENGINE", "mssql" if ENVIRONMENT != "production" else "postgresql").lower()
    if DB_ENGINE in {"postgres", "postgresql"}:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get("DB_NAME", ""),
                "USER": os.environ.get("DB_USER", ""),
                "PASSWORD": os.environ.get("DB_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", ""),
                "PORT": os.getenv("DB_PORT", ""),
            }
        }
    elif DB_ENGINE in {"mssql", "sqlserver"}:
        DATABASES = {
            "default": {
                "ENGINE": "mssql",
                "NAME": os.getenv("DB_NAME", "pp"),
                "USER": os.getenv("DB_USER", ""),
                "PASSWORD": os.getenv("DB_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", r"localhost\SQLEXPRESS02"),
                "PORT": os.getenv("DB_PORT", ""),
                "OPTIONS": {
                    "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
                    "extra_params": os.getenv("DB_EXTRA_PARAMS", "Trusted_Connection=yes"),
                },
            }
        }
    else:
        raise ImproperlyConfigured(f"Unsupported DB_ENGINE: {DB_ENGINE}")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = 'ar'
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Riyadh')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = Path(os.environ.get('STATIC_ROOT', str(BASE_DIR / 'staticfiles')))
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# PythonAnywhere keeps files under the user's home directory persistent between
# reloads. Set MEDIA_ROOT explicitly there if the project lives elsewhere.
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', str(BASE_DIR / 'media')))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = not DEBUG

WHATSAPP_ENABLED = os.environ.get('WHATSAPP_ENABLED', 'true').lower() == 'true'
META_WHATSAPP_TOKEN = os.environ.get('META_WHATSAPP_TOKEN', '')
META_PHONE_NUMBER_ID = os.environ.get('META_PHONE_NUMBER_ID', '')
META_API_VERSION = os.environ.get('META_API_VERSION', 'v21.0')
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '').rstrip('/')
WHATSAPP_TEMPLATE_LANGUAGE = os.environ.get('WHATSAPP_TEMPLATE_LANGUAGE', 'en_US')
WHATSAPP_WELCOME_TEMPLATE = os.environ.get('WHATSAPP_WELCOME_TEMPLATE', 'hello_world')
WHATSAPP_EXAM_TEMPLATE = os.environ.get('WHATSAPP_EXAM_TEMPLATE', 'hello_world')
