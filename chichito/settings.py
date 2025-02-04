"""
Django settings for chichito project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'user.User' 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_HOST_USER="noreply.chichito.ir@gmail.com"
EMAIL_HOST_PASSWORD="hwgc fqfv yybl clbh"
EMAIL_USE_TLS=True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    

    'rest_framework_simplejwt.token_blacklist',
    'storages',
    
    'user',
    'category',
    'rest_framework',
    'drf_spectacular',
    'drf_yasg',
    'corsheaders',
    'product',
    'cart',
    'Order'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chichito.urls'

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

WSGI_APPLICATION = 'chichito.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
    
#     'default': {
#         'ENGINE': 'mysql.connector.django',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'LIARA_URL is not set.'),
            'USER': os.getenv('DB_USER', 'LIARA_URL is not set.'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'LIARA_URL is not set.'),
            'HOST': os.getenv('DB_HOST', 'LIARA_URL is not set.'),
            'PORT': os.getenv('DB_PORT', 'LIARA_URL is not set.'),
        }
    }




# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000", 
# ]
CORS_ALLOW_ALL_ORIGINS = True

STORAGES = {
  "default": {
      "BACKEND": "storages.backends.s3.S3Storage",
  },
  "staticfiles": {
      "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
  },
}
# settings.py
DEBUG = False
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),  
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),  
           
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',  # Outputs logs to stdout
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # Adjust log level to your needs (e.g., DEBUG, INFO, WARNING)
        },
        'user': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_HOST_USER="noreply.chichito.ir@gmail.com"
EMAIL_HOST_PASSWORD="hwgc fqfv yybl clbh"
EMAIL_USE_TLS=True


LIARA_ENDPOINT    = os.getenv("LIARA_ENDPOINT")
LIARA_BUCKET_NAME = os.getenv("LIARA_BUCKET_NAME")
LIARA_ACCESS_KEY  = os.getenv("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY  = os.getenv("LIARA_SECRET_KEY")
REDIS_URL = os.getenv("REDIS_URL")

AWS_ACCESS_KEY_ID       = LIARA_ACCESS_KEY
AWS_SECRET_ACCESS_KEY   = LIARA_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = LIARA_BUCKET_NAME
AWS_S3_ENDPOINT_URL     = LIARA_ENDPOINT
AWS_S3_REGION_NAME      = 'us-east-1' 


CACHE_TTL = 60 * 15
CACHES = {
    "default": {        
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,            
        },   
    },
}

