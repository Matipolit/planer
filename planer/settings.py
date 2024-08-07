"""
Django settings for planer project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-_sh4gb9fjl&)__j)l_8qi953mayo28umz4y6)wbmaq60x&0@nj"

# SECURITY WARNING: don't run with debug turned on in production!
env_debug = os.environ.get('PLANER_DEBUG')
if env_debug is None:
    DEBUG = False
elif env_debug == "True":
    print("Running in debug mode")
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "192.168.0.32", "sienkiewiczapi.duckdns.org",
                 "sienkiewicza114.wroclaw.pl"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "planer_app",
    "users_app",
    "django_celery_results"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "planer.middleware.HttpPostTunnelingMiddleware",
]

ROOT_URLCONF = "planer.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "planer.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DBENGINE', ''),
        'NAME': os.environ.get('DBNAME', ''),
        'USER': os.environ.get('DBUSER', ''),
        'PASSWORD': os.environ.get('DBPASSWORD', ''),
        'HOST': os.environ.get('DBHOST', ''),
        'PORT': os.environ.get('DBPORT', ''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/planer/"
STATIC_ROOT = "/var/www/html/static/planer"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379//'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = {'application/json'}
CELERY_TIMEZONE = 'Europe/Warsaw'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

email =os.environ.get('EMAIL', 'matipolit@gmail.com')
password = os.environ.get('EMAIL_PASS', '')
print("Host email: " + email)
print("Host password: " + password)
# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = email
EMAIL_HOST_PASSWORD = password
DEFAULT_FROM_EMAIL = f"<{email}>"
