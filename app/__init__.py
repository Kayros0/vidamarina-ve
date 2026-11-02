"""Fábrica de la aplicación Flask."""
from pathlib import Path

from flask import Flask, render_template

from config import Config

from .extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/cuenta")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    with app.app_context():
        from . import models  # noqa: F401  (registra los modelos)

        db.create_all()

        from .seed import seed_if_empty

        seed_if_empty()

    return app
