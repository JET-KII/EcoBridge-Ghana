import os
from pathlib import Path

from dotenv import load_dotenv

from .content import SITE_SETTINGS


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def database_url():
    value = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'ecobridge_dev.db'}")
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://") and "+psycopg" not in value:
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "app" / "static" / "uploads"))
    BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN", "")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 4 * 1024 * 1024))
    WTF_CSRF_TIME_LIMIT = None
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() in {"1", "true", "yes", "on"}
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "true").lower() in {"1", "true", "yes", "on"}
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", SITE_SETTINGS["site_public_email"])
    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", "30"))
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "false").lower() in {"1", "true", "yes", "on"}
    CONTACT_RECIPIENT = os.getenv("CONTACT_RECIPIENT", SITE_SETTINGS["site_public_email"])


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True


def get_config(config_object=None):
    if config_object:
        return config_object

    environment = os.getenv("FLASK_ENV", "development").lower()
    if environment == "testing":
        return TestingConfig
    return Config
