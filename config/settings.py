import os
from pathlib import Path
import pymysql
from django.contrib.messages import constants as message_constants
from decouple import config

pymysql.version_info = (1, 4, 6, 'final', 0)
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'events',
    'orders',
    'additional',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

AUTH_USER_MODEL = 'authentication.AppUser'

SESSION_COOKIE_AGE = 100000

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart_item_count',
                'events.context_processors.random_categories',
                'events.context_processors.favorite_events',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


MESSAGE_LEVEL = message_constants.DEBUG

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

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

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
