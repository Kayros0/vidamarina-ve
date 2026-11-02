"""Modelos de la base de datos."""
import unicodedata
from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import event
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager

# Orden de rareza: mientras menor el número, más amenazada está la especie.
IUCN_ORDER = {"CR": 1, "EN": 2, "VU": 3, "NT": 4, "LC": 5, "DD": 6, "NE": 7}

IUCN_LABELS = {
    "CR": "En peligro crítico",
    "EN": "En peligro",
    "VU": "Vulnerable",
    "NT": "Casi amenazado",
    "LC": "Preocupación menor",
    "DD": "Datos insuficientes",
    "NE": "No evaluado",
}

GROUP_LABELS = {
    "pez": "Pez",
    "mamifero": "Mamífero",
    "reptil": "Reptil",
    "invertebrado": "Invertebrado",
    "ave": "Ave",
}

REGION_LABELS = {
    "caribe": "Caribe",
    "rios": "Ríos y aguas dulces",
    "ambas": "Caribe y ríos",
}


def normalize_text(value: str) -> str:
    """Minúsculas y sin tildes, para que 'delfin' encuentre 'Delfín'."""
    value = unicodedata.normalize("NFKD", value or "")
    return "".join(c for c in value if not unicodedata.combining(c)).lower().strip()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class Species(db.Model):
    __tablename__ = "species"

    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(120), nullable=False, index=True)
    scientific_name = db.Column(db.String(160), unique=True, nullable=False, index=True)
    group = db.Column(db.String(30), nullable=False, index=True)
    region = db.Column(db.String(20), nullable=False, index=True)
    habitat = db.Column(db.String(255), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")

    iucn_status = db.Column(db.String(2), nullable=False, default="NE", index=True)
    iucn_year = db.Column(db.Integer)
    described_year = db.Column(db.Integer)

    image_url = db.Column(db.String(500))
    image_author = db.Column(db.String(200))
    image_license = db.Column(db.String(120))
    source_url = db.Column(db.String(500))

    map_lat = db.Column(db.Float)
    map_lng = db.Column(db.Float)
    map_label = db.Column(db.String(160))

    search_key = db.Column(db.String(700), nullable=False, default="", index=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @property
    def rarity_rank(self) -> int:
        return IUCN_ORDER.get(self.iucn_status, 99)

    @property
    def iucn_label(self) -> str:
        return IUCN_LABELS.get(self.iucn_status, "No evaluado")

    @property
    def group_label(self) -> str:
        return GROUP_LABELS.get(self.group, self.group)

    @property
    def region_label(self) -> str:
        return REGION_LABELS.get(self.region, self.region)

    def refresh_search_key(self) -> None:
        parts = [
            self.common_name,
            self.scientific_name,
            self.habitat,
            self.group_label,
            self.region_label,
            self.iucn_label,
        ]
        self.search_key = normalize_text(" ".join(part for part in parts if part))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "common_name": self.common_name,
            "scientific_name": self.scientific_name,
            "group": self.group,
            "group_label": self.group_label,
            "region": self.region,
            "region_label": self.region_label,
            "habitat": self.habitat,
            "iucn_status": self.iucn_status,
            "iucn_label": self.iucn_label,
            "described_year": self.described_year,
            "image_url": self.image_url,
            "map_lat": self.map_lat,
            "map_lng": self.map_lng,
            "map_label": self.map_label,
        }

    def __repr__(self) -> str:
        return f"<Species {self.scientific_name}>"


@event.listens_for(Species, "before_insert")
@event.listens_for(Species, "before_update")
def _refresh_search_key(_mapper, _connection, target: Species) -> None:
    target.refresh_search_key()
