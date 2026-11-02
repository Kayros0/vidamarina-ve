"""Registro, inicio y cierre de sesión."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from ..extensions import db
from ..forms import LoginForm, RegisterForm
from ..models import User

auth_bp = Blueprint("auth", __name__)


def _safe_next(target: str | None) -> str | None:
    """Evita redirecciones abiertas hacia otros dominios."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        existing = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()

        if existing:
            flash("Ese nombre de usuario o correo ya está registrado.", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash("¡Bienvenido! Tu cuenta fue creada correctamente.", "success")
            return redirect(_safe_next(request.args.get("next")) or url_for("main.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/entrar", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip()
        user = User.query.filter(
            or_(User.email == identity.lower(), User.username == identity)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Bienvenido de nuevo, {user.username}.", "success")
            return redirect(_safe_next(request.args.get("next")) or url_for("main.index"))

        flash("Correo/usuario o contraseña incorrectos.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/salir", methods=["POST"])
def logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("main.index"))
