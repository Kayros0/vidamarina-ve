"""Carga inicial de datos: especies y cuenta administradora."""
import json
from pathlib import Path

from flask import current_app

from .extensions import db
from .models import Species, User

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "species.json"


def seed_if_empty() -> None:
    """Carga el catálogo y el administrador solo si la base está vacía."""
    if Species.query.count() == 0 and DATA_FILE.exists():
        records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        for record in records:
            db.session.add(Species(**record))
        db.session.commit()

    if User.query.count() == 0:
        admin = User(
            username=current_app.config["ADMIN_USERNAME"],
            email=current_app.config["ADMIN_EMAIL"],
            is_admin=True,
        )
        admin.set_password(current_app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
