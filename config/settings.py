from pathlib import Path

import os

from dotenv import load_dotenv

import dj_database_url

from datetime import timedelta

import sys

sys.stdout.reconfigure(encoding='utf-8')



load_dotenv()



BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")



INSTALLED_APPS = [

    "django.contrib.admin",

    "django.contrib.auth",

    "django.contrib.contenttypes",

    "django.contrib.sessions",

    "django.contrib.messages",

    "django.contrib.staticfiles",



    "rest_framework",

    "rest_framework_simplejwt",

    "django_filters",



    "users",

    "hackathons",

    "teams",

    "projects",

    "judging",

    "announcements",

    "common",

    "frontend",

]



MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]



ROOT_URLCONF = "config.urls"



TEMPLATES = [

    {

        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [BASE_DIR / "templates"],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

            ],

        },

    },

]



WSGI_APPLICATION = "config.wsgi.application"



USE_SQLITE = os.getenv("USE_SQLITE", "False") == "True"



if USE_SQLITE:

    DATABASES = {

        "default": {

            "ENGINE": "django.db.backends.sqlite3",

            "NAME": BASE_DIR / "db.sqlite3",

        }

    }

else:

    DATABASES = {

        "default": {

            "ENGINE": "django.db.backends.postgresql",

            "NAME": "hackathondb",

            "USER": "postgres",

            "PASSWORD": os.getenv("DB_PASSWORD", "admin"),

            "HOST": "127.0.0.1",

            "PORT": "5432",

            "OPTIONS": {

                "client_encoding": "UTF8",

            },

        }

    }



DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True



MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"



AUTH_USER_MODEL = "users.User"



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



REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication.JWTAuthentication",

    ),

    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.IsAuthenticated",

    ),

    "DEFAULT_FILTER_BACKENDS": (

        "django_filters.rest_framework.DjangoFilterBackend",

    ),

}



SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "AUTH_HEADER_TYPES": ("Bearer",),

}



LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Asia/Bishkek"

USE_I18N = True

USE_TZ = True



STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static"]



DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



LOGIN_URL = "site_login"

LOGIN_REDIRECT_URL = "dashboard"

LOGOUT_REDIRECT_URL = "home"

