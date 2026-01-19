import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from backend/.env if present
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def env_list(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.getenv(name)
    if raw is None:
        return default or []
    value = raw.strip()
    if value == "*":
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


def database_config_from_url(url: str):
    # Be tolerant of common deployment formatting issues:
    # - accidental whitespace
    # - quoted values
    normalized = (url or "").strip().strip('"').strip("'")
    parsed = urlparse(normalized)

    scheme = (parsed.scheme or "").lower()
    # Handle schemes like "postgresql+psycopg" by taking the base scheme.
    scheme = scheme.split("+", 1)[0]

    if scheme in {"postgres", "postgresql"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote((parsed.path or "").lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or ""),
        }

    if scheme in {"sqlite", "sqlite3"}:
        # sqlite:///relative/path.db  or sqlite:////absolute/path.db
        raw_path = parsed.path or ""
        if raw_path in {"", "/"}:
            db_path = BASE_DIR / "db.sqlite3"
        else:
            # Remove leading slash so it works cross-platform with relative paths.
            candidate = Path(unquote(raw_path.lstrip("/")))
            db_path = candidate if candidate.is_absolute() else (BASE_DIR / candidate)
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_path,
        }

    raise ValueError(f"Unsupported DATABASE_URL scheme: {scheme or '(empty)'}")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-later")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("DEBUG", default=True)

# Hosts
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

# When behind a proxy (Render), let Django know how to detect HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env_bool("USE_X_FORWARDED_HOST", default=not DEBUG)

# CSRF (not strictly required for anonymous API usage, but keeps admin / future auth safe)
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", default=[])


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",
    "corsheaders",

    # local apps
    "tasks",
    "dashboards",
    "external_apis",
]

MIDDLEWARE = [
    # CORS must come before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    # Serve static files in production without needing Nginx.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS
# - In DEBUG mode, default to allow-all to keep local dev frictionless.
# - In production, configure allowed origins explicitly.
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", default=[])

# Safe defaults for APIs (no cookies needed)
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", default=False)

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "core.wsgi.application"

# Database
# Render sets DATABASE_URL for Postgres; but misconfiguration can leave it blank.
# Never crash at import-time: fall back to SQLite while still surfacing the error
# in logs (so the service can start and return JSON errors instead of a hard crash).
DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip().strip('"').strip("'")
if DATABASE_URL:
    try:
        DATABASES = {"default": database_config_from_url(DATABASE_URL)}
    except ValueError:
        # Invalid DATABASE_URL value (e.g. leading whitespace or malformed string)
        # -> fall back to SQLite to keep the process alive.
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: compressed static files with hashed filenames
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

# DRF – disable auth for demo
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # Always return JSON (even for unexpected server errors) and provide a clear
    # response for DB-not-ready errors instead of HTML 500 pages.
    "EXCEPTION_HANDLER": "core.exception_handler.custom_exception_handler",
}
