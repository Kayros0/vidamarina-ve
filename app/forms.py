"""Formularios con validación y protección CSRF."""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
)

from .models import GROUP_LABELS, IUCN_LABELS, REGION_LABELS


class RegisterForm(FlaskForm):
    username = StringField(
        "Nombre de usuario",
        validators=[DataRequired(), Length(min=3, max=40)],
    )
    email = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(),
            Email(message="Ingresa un correo electrónico válido."),
            Length(max=120),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    confirm = PasswordField(
        "Repite la contraseña",
        validators=[
            DataRequired(),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    submit = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    identity = StringField(
        "Correo o usuario",
        validators=[DataRequired(), Length(max=120)],
    )
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember = BooleanField("Recordarme")
    submit = SubmitField("Entrar")


class SpeciesForm(FlaskForm):
    common_name = StringField(
        "Nombre común",
        validators=[DataRequired(), Length(max=120)],
    )
    scientific_name = StringField(
        "Nombre científico",
        validators=[DataRequired(), Length(max=160)],
    )
    group = SelectField(
        "Grupo",
        choices=[(key, label) for key, label in GROUP_LABELS.items()],
        validators=[DataRequired()],
    )
    region = SelectField(
        "Región",
        choices=[(key, label) for key, label in REGION_LABELS.items()],
        validators=[DataRequired()],
    )
    habitat = StringField("Hábitat", validators=[Optional(), Length(max=255)])
    description = TextAreaField("Descripción", validators=[Optional()])

    iucn_status = SelectField(
        "Estado de conservación (UICN)",
        choices=[(key, f"{key} · {label}") for key, label in IUCN_LABELS.items()],
        validators=[DataRequired()],
    )
    iucn_year = IntegerField(
        "Año de evaluación UICN",
        validators=[Optional(), NumberRange(min=1900, max=2100)],
    )
    described_year = IntegerField(
        "Año de descripción científica",
        validators=[Optional(), NumberRange(min=1700, max=2100)],
    )

    image_url = StringField("URL de la imagen", validators=[Optional(), Length(max=500)])
    image_author = StringField("Autor de la imagen", validators=[Optional(), Length(max=200)])
    image_license = StringField("Licencia de la imagen", validators=[Optional(), Length(max=120)])
    source_url = StringField("URL de la fuente", validators=[Optional(), Length(max=500)])

    map_lat = FloatField(
        "Latitud",
        validators=[Optional(), NumberRange(min=-90, max=90)],
    )
    map_lng = FloatField(
        "Longitud",
        validators=[Optional(), NumberRange(min=-180, max=180)],
    )
    map_label = StringField("Lugar de referencia", validators=[Optional(), Length(max=160)])

    submit = SubmitField("Guardar especie")
