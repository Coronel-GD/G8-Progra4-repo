import os
from decouple import config

# === Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
)

from decouple import Config, RepositoryEnv
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    config = Config(RepositoryEnv(env_path))

# === Security ===
SECRET_KEY = config('SECRET_KEY')

INSTALLED_APPS = [
    # Django apps base
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Necesario para django-allauth

    # Librerías externas
    'import_export',
    'corsheaders',  # CORS
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'crispy_forms',
    'crispy_bootstrap5',


    # Apps locales
    'core',

    # API
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

REST_USE_JWT = True
JWT_AUTH_COOKIE = 'my-app-auth'
JWT_AUTH_REFRESH_COOKIE = 'my-refresh-token'
REST_AUTH_TOKEN_MODEL = None

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Agregado para soporte de idiomas
    "corsheaders.middleware.CorsMiddleware",  # CORS Middleware (antes de CommonMiddleware)
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True  # Permitir todos los orígenes (para desarrollo)

ROOT_URLCONF = 'djecommerce.urls'
WSGI_APPLICATION = 'djecommerce.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')

# Configuración de caché para mejor rendimiento
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Cachear consultas de SocialApp para OAuth más rápido
SOCIALACCOUNT_STORE_TOKENS = False  # No guardar tokens innecesarios

# Usar sesiones en caché para mejor rendimiento
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Configuración optimizada de OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',  # Más rápido, no pide refresh token
        },
        'FETCH_USERINFO': True,
    },
    'github': {
        'SCOPE': [
            'user:email',
        ],
    }
}

# Configuración de allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_AUTO_SIGNUP = True  # Registro automático con redes sociales

LOGIN_REDIRECT_URL = '/'

CRISPY_TEMPLATE_PACK = 'bootstrap5'

DEFAULT_CURRENCY = 'ARS'

MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY', default='')
MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN', default='')
MERCADOPAGO_SANDBOX = config('MERCADOPAGO_SANDBOX', default='True') == 'True'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
