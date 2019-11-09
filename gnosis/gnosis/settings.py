"""
Django settings for gnosis project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6pph^ipk8sow@%nw)s!l@klg4q8lnar2k6k$&e=26pqrm(zg^a'

# SECURITY WARNING: don't run with debug turned on in production!
print(f"GNOSIS_DEBUG={os.environ.get('GNOSIS_DEBUG', False)}")
DEBUG = os.environ.get('GNOSIS_DEBUG', False)

ALLOWED_HOSTS = []

SESSION_SAVE_EVERY_REQUEST = True

# keys for reCaptcha v2 checkbox
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '6Ld6z7IUAAAAAC-qA5q5CC58YJx8Td_g6wPJs_Pk')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '6Ld6z7IUAAAAAPgCXtYcOjFMKo4CSx_WY2YAxIaC')

RECAPTCHA_PUBLIC_KEY_INV = os.environ.get('RECAPTCHA_PUBLIC_KEY_INV', '6LdbXLQUAAAAAGynHciK-BML9CthUvtrUm_Aim24')
RECAPTCHA_PRIVATE_KEY_INV = os.environ.get('RECAPTCHA_PRIVATE_KEY_INV', '6LdbXLQUAAAAACLkjt-f0tZ0mY1aXR6jghMg2tBw')

RECAPTCHA_PUBLIC_KEY_V3 = os.environ.get('RECAPTCHA_PUBLIC_KEY_V3', '6LfdR7UUAAAAAC9WK09i_tRLtNQq4aIaIQjWQ-4i')
RECAPTCHA_PRIVATE_KEY_V3 = os.environ.get('RECAPTCHA_PRIVATE_KEY_V3', '6LfdR7UUAAAAACkwrd0ae-3kkNWnRFgFcuU0m3Rv')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_forms',
    'allauth',
    'allauth.account',
    'el_pagination',
    'catalog.apps.CatalogConfig',
    'bookmark.apps.BookmarkConfig',
    'home.apps.HomeConfig',
    'recaptcha',
    'captcha',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gnosis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',  ## For EL-pagination
            ],
        },
    },
]

WSGI_APPLICATION = 'gnosis.wsgi.application'

# Increase this number when in production.
EL_PAGINATION_PER_PAGE = 3

# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gnosistest',  # gnosis_db
        'USER': 'gnosisuser',      # gnosis
        'PASSWORD': 'gnosis',
        'HOST': 'localhost',
        'PORT': os.environ.get('GNOSIS_DB_PORT', 5432),  #'5433',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# After user login and logout, she will be re-directed to home page instead of accounts/profile
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# This is for checking the password reset email when the email server is not configured
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = ( 
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Add notes app
INSTALLED_APPS += ['notes.apps.NotesConfig', ]

# django-allauth config
SITE_ID = 1