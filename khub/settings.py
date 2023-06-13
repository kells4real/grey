from pathlib import Path
import os
import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f@+7ghgh(+ccadoz(i$8pzi-ahounc7-o4xyt0r#aq_ccms4#x'

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
    'authentication',
    'account',
    'social_auth',
    'wallet',
    'investment',
    'loan',
    'configuration',
    'piggyvest',
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'notifications',
    'notifications_rest',
    'django_crontab',
    'rest_framework_simplejwt.token_blacklist',
    'fcm_django'
]

FCM_DJANGO_SETTINGS = {
        # authentication to Firebase
        "FCM_SERVER_KEY": "AAAAOHqteEo:APA91bF_bwGq8YRJ_rxV5ro1P72L6RrsVVHaQi1bdqQ6RMcYomKh_8vURVHWQuaBC4vHZhbAYsK9IC3XorTghOWYEZFuZzIKBZwKlDVWzKcp4dNgjK4urjpDzN4h_Pze7IEzJL43AN13",
        # true if you want to have only one active device per registered user at a time
        # default: False
        "ONE_DEVICE_PER_USER": False,
        # devices to which notifications cannot be sent,
        # are deleted upon receiving error response from FCM
        # default: False
        "DELETE_INACTIVE_DEVICES": True,
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/media/cache',
        'TIMEOUT': 432000000
        # 'OPTIONS': {
        #     'MAX_ENTRIES': 1000
        # }
    }
}

AUTH_USER_MODEL = 'authentication.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'UNICODE_JSON': True,
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'error',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=13065),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=17020),
}

ROOT_URLCONF = 'khub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:9000",
    "https://cighedge.com"
]

# CSRF_TRUSTED_ORIGINS = [
#     '',
# ]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.edufy\.school$",
]

WSGI_APPLICATION = 'khub.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / "db.sqlite3"),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'OPTIONS': {
#             'sql_mode': 'traditional'},
#         'NAME': 'cig',
#         'USER': "root",
#         'PASSWORD': "Stalking26",
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#         'STORAGE_ENGINE': 'MyISAM'
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FROM_EMAIL = "Trix Swift <noreply@trixswift.com>"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.trixswift.com'
EMAIL_PORT = 26
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "noreply@trixswift.com"
EMAIL_HOST_PASSWORD = "NewEmailPassword2022"