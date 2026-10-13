"""
Configuración de Django para el proyecto sistHoraios.

Toda la configuración sensible se lee de variables de entorno (o de un
archivo ``.env`` en la raíz del proyecto, ver ``.env.example``).
Sin ninguna variable definida el proyecto arranca en modo desarrollo con
SQLite, de modo que ``python manage.py migrate`` funciona sin configuración.
"""

from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad -------------------------------------------------------------

DEBUG = config("DEBUG", default=False, cast=bool)

# En desarrollo se permite una clave por defecto; en producción es obligatoria.
_DEV_SECRET_KEY = "dev-only-insecure-key-no-usar-en-produccion"
SECRET_KEY = config("SECRET_KEY", default=_DEV_SECRET_KEY if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError(
        "Define la variable de entorno SECRET_KEY (o DEBUG=True para desarrollo local)."
    )

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

if not DEBUG:
    SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
    SECURE_CONTENT_TYPE_NOSNIFF = True

# --- Aplicaciones ----------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "generator",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sistHoraios.urls"

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

WSGI_APPLICATION = "sistHoraios.wsgi.application"

# --- Base de datos ---------------------------------------------------------
# SQLite por defecto. Para MySQL o PostgreSQL define DATABASE_URL, p. ej.:
#   mysql://usuario:contraseña@host:3306/sistemahorario
#   postgres://usuario:contraseña@host:5432/sistemahorario

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=config("DB_CONN_MAX_AGE", default=0, cast=int),
    )
}

# --- Autenticación ---------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# --- Internacionalización --------------------------------------------------

LANGUAGE_CODE = "es-mx"
TIME_ZONE = config("TIME_ZONE", default="America/Mexico_City")
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos ----------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
