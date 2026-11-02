"""Configuración central de la aplicación."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

# Render entrega la URL como postgres://, pero SQLAlchemy espera postgresql://
_database_url = os.environ.get("DATABASE_URL", "").strip()
if _database_url.startswith("postgres://"):
    _database_url = _database_url.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = _database_url or f"sqlite:///{INSTANCE_DIR / 'vidamarina.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB por formulario

    # Cuenta administradora creada en el primer arranque.
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin").strip()
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@vidamarina.ve").strip().lower()
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin1234!")
