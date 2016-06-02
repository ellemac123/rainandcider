"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os, sys
from datetime import timedelta
import djcelery
djcelery.setup_loader()



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if 'OPENSHIFT_REPO_DIR' in os.environ:
    ON_OPENSHIFT = True
else:
    ON_OPENSHIFT = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ojzkkj+6x#(=4#=_5=6fjq8$@73t)#i(o&7*+#x)rz_tl-g21_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',
    'bootstrap3',
    'twython_django_oauth',
    'rcApp',
    'djcelery',
]

MIDDLEWARE_CLASSES = [
    #'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'


TEMPLATE_DIRS = (
     os.path.join(BASE_DIR, 'rcApp', 'templates'),
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'myproject.wsgi.application'


from kombu import Exchange, Queue
if ON_OPENSHIFT:
    LOG_DIR = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', ''))
    CELERYBEAT_SCHEDULE_FILENAME = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', ''),
                                                'celerybeat_schedule')
    CELERYBEAT_SCHEDULE_PIDFILE = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', ''),
                                           'celerybeat.pid')
    REDIS_URL = "redis://127.0.0.1:16379"
    # REDIS_URL = "redis://:{}@{}:{}".format(os.environ.get('OPENSHIFT_REDIS_PASSWORD', ''),
    #                                         os.environ.get('OPENSHIFT_REDIS_HOST', ''),
    #                                          os.environ.get('OPENSHIFT_REDIS_PORT', ''))
else:
    LOG_DIR = '.'
    CELERYBEAT_SCHEDULE_FILENAME = 'celerybeat_schedule'
    CELERYBEAT_SCHEDULE_PIDFILE = 'celerybeat.pid'
    REDIS_URL = "redis://127.0.0.1:16379"


BROKER_URL = REDIS_URL
CELERY_IMPORTS = ('rcApp.tasks')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_DEFAULT_QUEUE = 'rcApp'
CELERY_RESULT_EXCHANGE = 'rcAppresults'
CELERY_QUEUES = (
    Queue('rcApp', Exchange('rcApp'), routing_key='rcApp'),
)
CELERYBEAT_SCHEDULE = {
    'cache_data': {
        'task': 'update_cache',
        'schedule': timedelta(seconds=30),
        'options': {'expire': 30},
    },
}



#
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
#
# # Causes django to use Redis for session information
# SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
# SESSION_CACHE_ALIAS = "default"


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
if 'OPENSHIFT_REPO_DIR' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }



# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TWITTER_KEY = 'kkgJHe2AJCJ7TEumZa7WZ2pdR'
TWITTER_SECRET = 'z4fl2dFDDiLrV6w66Mpu2hu9lLSW0tEVkBAUTcyhgv2zaj4H6q'


LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers':{
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'app-root/logs/debug.log'
        },
    },
    'loggers': {
      'django': {
          'handlers': ['file'],
          'level': 'DEBUG',
          'propagate': True,
      },
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'rcApp', 'static')
STATIC_URL = '/static/'

