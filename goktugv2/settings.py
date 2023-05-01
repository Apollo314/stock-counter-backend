"""
Django settings for goktugv2 project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
LOCALE_PATHS = (BASE_DIR / "locale",)
# dotenv
for file in BASE_DIR.glob("*.env"):
    dotenv.load_dotenv(file)

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ["DEBUG"] == "True"
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split()
CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"].split()
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_ALL_ORIGINS = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # deps
    "rest_framework",
    "django_filters",
    "corsheaders",
    "simple_history",
    "drf_spectacular",
    "drf_standardized_errors",
    # auth
    "knox",
    "users.apps.UsersConfig",
    # apps
    "inventory.apps.InventoryConfig",
    "stakeholder.apps.StakeholderConfig",
    "invoice.apps.InvoiceConfig",
    "django_extensions",
]

MIDDLEWARE = [
    # "utilities.middleware.LogMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "goktugv2.urls"

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

WSGI_APPLICATION = "goktugv2.wsgi.application"
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    # "default": {
    #     "ENGINE": "django.db.backends.sqlite3",
    #     "NAME": "mydatabase",
    # }
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
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

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/admin/login/"

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "tr-tr"
# LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Istanbul"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "utilities.autoschema.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 5,
    "DEFAULT_RENDERER_CLASSES": (
        "drf_orjson_renderer.renderers.ORJSONRenderer",
        # "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "drf_orjson_renderer.parsers.ORJSONParser",
        # "rest_framework.parsers.JSONParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.TokenCookieAuthentication",
        # "knox.auth.TokenAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        # 'rest_framework.authentication.TokenAuthentication',
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "2/day",
    },
    "EXCEPTION_HANDLER": "utilities.exception_handler.extended_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "CurrencyEnum": "inventory.models.Currency.choices",
    },
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "docExpansion": None,
    },
    "ENFORCE_NON_BLANK_FIELDS": True,
    "TITLE": "drf",
    "SORT_OPERATION_PARAMETERS": False
    # "REDOC_DIST": "https://cdn.jsdelivr.net/npm/redoc@latest",
}


REST_KNOX = {
    "SECURE_HASH_ALGORITHM": "cryptography.hazmat.primitives.hashes.SHA512",
    "AUTH_TOKEN_CHARACTER_LENGTH": 64,
    "TOKEN_TTL": None,
    "USER_SERIALIZER": "knox.serializers.UserSerializer",
    "TOKEN_LIMIT_PER_USER": 10,
    "AUTH_HEADER_PREFIX": "Bearer",
    #   'AUTO_REFRESH': True,
}


CACHES = {
    # "default": {
    #     "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    # }
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://default:{os.environ['REDIS_PASSWORD']}@{os.environ['REDIS_HOST']}:6379",
    }
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # "filters": {
    #     "require_debug_true": {
    #         "()": "django.utils.log.RequireDebugTrue",
    #     }
    # },
    "handlers": {
        # "console": {
        #     "level": "DEBUG",
        #     # "filters": ["require_debug_true"],
        #     "class": "logging.StreamHandler",
        # }
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "warning.log",
        }
    },
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": ["file"],
        }
        # "django.db.backends": {
        #     "level": "DEBUG",
        #     "handlers": ["console"],
        # },
        # 'django': {
        #     'handlers': ['console'],
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        # }
    },
}
