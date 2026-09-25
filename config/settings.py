"""
Django settings for Desaint Stationeries platform.
Naito De Saint Enterprise (Sunyani, Ghana)
Engineered by SikaDev Software Engineering
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Defensive Environment Parsing (Guards against empty strings in Vercel console)
_raw_secret = (os.getenv('SECRET_KEY') or '').strip()
SECRET_KEY = _raw_secret if _raw_secret else 'django-insecure-desaint-stationeries-sunyani-enterprise-2026-key!'

_raw_debug = (os.getenv('DEBUG') or '').strip()
DEBUG = _raw_debug.lower() in ('true', '1', 'yes') if _raw_debug else True

# Universal ALLOWED_HOSTS (Accepts Vercel preview URLs & custom domains)
ALLOWED_HOSTS = ['*']
env_allowed = (os.getenv('ALLOWED_HOSTS') or '').strip()
if env_allowed and env_allowed != '*':
    ALLOWED_HOSTS.extend([h.strip() for h in env_allowed.split(',') if h.strip()])
ALLOWED_HOSTS.extend(['.vercel.app', '.now.sh', 'localhost', '127.0.0.1', 'desaintstationeries.com'])
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
    'https://*.desaintstationeries.com',
    'https://desaintstationeries.com',
    'http://127.0.0.1',
    'http://localhost',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Desaint Stationeries Core & Modules
    'core',
    'catalog',
    'inventory',
    'customizer',
    'orders',
    'invoices',
    'managerial',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.company_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration
IS_VERCEL = bool(
    'VERCEL' in os.environ or
    'AWS_LAMBDA_FUNCTION_NAME' in os.environ or
    'VERCEL_ENV' in os.environ or
    'VERCEL_REGION' in os.environ or
    'VERCEL_URL' in os.environ
)

DATABASE_URL = (os.getenv('DATABASE_URL') or '').strip()

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
        }
    except ImportError:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/tmp/db.sqlite3' if IS_VERCEL else BASE_DIR / 'db.sqlite3',
            }
        }
elif IS_VERCEL:
    try:
        from config.db_init import initialize_database
        initialize_database()
    except Exception as e:
        sys.stderr.write(f"Settings DB Init Notice: {e}\n")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
WHITENOISE_USE_FINDERS = True

# Media files (School Crests, Digital Proofs, Product Photos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Proxy & HTTPS Forwarding Settings for Vercel Edge
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Session & Authentication Settings
# Uses cryptographically signed cookies for serverless multi-container stateless sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400 * 7  # 7-day session validity
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from accessing session cookie
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

LOGIN_URL = 'managerial:staff_login'
LOGIN_REDIRECT_URL = 'managerial:dashboard'
