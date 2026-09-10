"""
Django settings for lms_project project.
"""

from pathlib import Path
import os

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-r+)*^!$a2mbej@wis#dmxw+f4d_sc2xtdc()!fgrd#)j@@t(ea')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', '.onrender.com']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Site URL — dynamically switches to Render public HTTPS domain in production
if RENDER_EXTERNAL_HOSTNAME:
    SITE_URL = f'https://{RENDER_EXTERNAL_HOSTNAME}'
else:
    SITE_URL = os.environ.get('SITE_URL', 'https://sj-tech-classes.onrender.com').rstrip('/')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'crispy_forms',
    'crispy_bootstrap5',

    # Custom LMS Apps
    'accounts',
    'courses',
    'payments',
    'dashboard',
    'cloudinary_storage',
    'cloudinary',
]

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameBackend',
]



# Cloudinary Media & Video Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'c-bcaf5fdd742d64933349cef321defb'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.SingleDeviceLoginMiddleware',
    'accounts.middleware.HeadRequestMiddleware',
]

ROOT_URLCONF = 'lms_project.urls'

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
                'courses.context_processors.lms_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'lms_project.wsgi.application'

# Database Configuration - Neon PostgreSQL (Cloud Permanent) with SQLite dev fallback
RAW_DB_URL = (
    os.environ.get('DATABASE_URL') or
    os.environ.get('POSTGRES_URL') or
    os.environ.get('NEON_DATABASE_URL')
)

if RAW_DB_URL:
    RAW_DB_URL = RAW_DB_URL.strip()
    if RAW_DB_URL.startswith('postgres://'):
        RAW_DB_URL = RAW_DB_URL.replace('postgres://', 'postgresql://', 1)

DATABASES = {
    'default': dj_database_url.config(
        default=RAW_DB_URL or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=0,  # Recommended for serverless Neon Postgres to prevent stale closed connections
        conn_health_checks=True,  # Django 4.1+ tests connection vitality before queries and auto-reconnects
        ssl_require=True if (RAW_DB_URL and 'postgres' in RAW_DB_URL) else False,
    )
}

_active_engine = DATABASES['default'].get('ENGINE', '')
if 'postgres' in _active_engine:
    _db_host = DATABASES['default'].get('HOST', 'PostgreSQL Cloud')
    print(f"==> [DATABASE PERSISTENCE]: Connected to PostgreSQL (Neon Cloud: {_db_host}). Data and videos will persist permanently across sleep mode!")
else:
    print("==> [DATABASE WARNING]: Running on SQLite (Local Ephemeral Disk). Changes will be wiped on Render sleep mode unless DATABASE_URL is set in Render!")

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_MAX_AGE = 31536000  # 1 year static assets caching in user browser

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

if os.environ.get('CLOUDINARY_API_KEY') and os.environ.get('CLOUDINARY_API_SECRET'):
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'courses:home'

# Email Settings for Gmail OTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sunnywaghmode8@gmail.com'
EMAIL_HOST_PASSWORD = 'qnep owzh tznb baai'
DEFAULT_FROM_EMAIL = 'SJ TECH CLASSES <sunnywaghmode8@gmail.com>'
EMAIL_TIMEOUT = 5  # Prevents SMTP connections from hanging indefinitely

# HTTP Email API Keys (Bypasses Render Free Tier SMTP port blocking over HTTPS port 443)
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')



# Gemini AI Settings
GEMINI_API_KEY = 'AIzaSyD8a_I2ZDJMPkCro9OPnc7AWEhtx8h_so0'

# Security Settings & Protection Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB



