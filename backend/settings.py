"""
Django settings for ProManage backend project.
"""

from pathlib import Path
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from .env.backend
load_dotenv(dotenv_path=os.path.join(Path(__file__).resolve().parent.parent.parent, '.env.backend'))

BASE_DIR = Path(__file__).resolve().parent.parent

# Min 32 bytes required for HS256 (RFC 7518)
_DEFAULT_SECRET_KEY = 'django-insecure-promanage-dev-only-change-in-production-2026'


def _resolve_jwt_secret(raw_key):
    if len(raw_key.encode('utf-8')) >= 32:
        return raw_key
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()


SECRET_KEY = os.getenv('SECRET_KEY', _DEFAULT_SECRET_KEY)

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Anda bisa mengganti IP ini jika IP laptop Anda berubah
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://ie_web:8000').split(',')
CSRF_COOKIE_HTTPONLY = False

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'api' / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DATABASE_NAME', BASE_DIR / 'db' / 'db.sqlite3'),
        'USER': os.getenv('DATABASE_USER', ''),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', ''),
        'PORT': os.getenv('DATABASE_PORT', ''),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

# Internationalization
LANGUAGE_CODE = 'id-id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = BASE_DIR / os.getenv('STATIC_ROOT', 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'api' / 'static',
]

# Media files
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = BASE_DIR / os.getenv('MEDIA_ROOT', 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT Settings
JWT_SECRET_KEY = _resolve_jwt_secret(os.getenv('JWT_SECRET_KEY', SECRET_KEY))
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_DAYS = int(os.getenv('JWT_EXPIRATION_DAYS', '7'))

# File Upload Settings
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 5242880))  # 5MB
ALLOWED_IMAGE_TYPES = os.getenv('ALLOWED_IMAGE_TYPES', 'image/jpeg,image/png,image/jpg').split(',')

# Custom User Model
AUTH_USER_MODEL = 'api.User'

# Custom Cookie names
SESSION_COOKIE_NAME = 'pm_sessionid'
CSRF_COOKIE_NAME = 'pm_csrftoken'

# ─── Deployment Settings ───
import os as _os

_force_script = _os.environ.get('FORCE_SCRIPT_NAME', '')
if _force_script:
    FORCE_SCRIPT_NAME = _force_script
    STATIC_URL = _force_script + '/static/'
    MEDIA_URL = _force_script + '/media/'

if _os.environ.get('DEBUG', '1') == '0':
    DEBUG = False

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'http://38.47.94.194',
    'https://38.47.94.194',
    'http://localhost',
    'http://127.0.0.1',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
