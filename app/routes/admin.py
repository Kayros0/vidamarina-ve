"""Panel de administración: CRUD de especies."""
from functools import wraps

from flask import (
    abort,
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import SpeciesForm
from ..models import Species, normalize_text

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _apply_form(species: Species, form: SpeciesForm) -> None:
    species.common_name = form.common_name.data.strip()
    species.scientific_name = form.scientific_name.data.strip()
    species.group = form.group.data
    species.region = form.region.data
    species.habitat = (form.habitat.data or "").strip()
    species.description = (form.description.data or "").strip()
    species.iucn_status = form.iucn_status.data
    species.iucn_year = form.iucn_year.data
    species.described_year = form.described_year.data
    species.image_url = (form.image_url.data or "").strip() or None
    species.image_author = (form.image_author.data or "").strip() or None
    species.image_license = (form.image_license.data or "").strip() or None
    species.source_url = (form.source_url.data or "").strip() or None
    species.map_lat = form.map_lat.data
    species.map_lng = form.map_lng.data
    species.map_label = (form.map_label.data or "").strip() or None


@admin_bp.route("/")
@login_required
@admin_required
def index():
    q = (request.args.get("q") or "").strip()
    query = Species.query
    if q:
        query = query.filter(Species.search_key.contains(normalize_text(q), autoescape=True))
    species = query.order_by(Species.common_name.asc()).all()
    return render_template("admin/index.html", species=species, q=q)


@admin_bp.route("/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = SpeciesForm()
    if form.validate_on_submit():
        scientific_name = form.scientific_name.data.strip()
        if Species.query.filter(Species.scientific_name == scientific_name).first():
            flash("Ya existe una especie con ese nombre científico.", "error")
        else:
            species = Species()
            _apply_form(species, form)
            db.session.add(species)
            db.session.commit()
            flash(f"«{species.common_name}» se agregó al catálogo.", "success")
            return redirect(url_for("admin.index"))

    return render_template("admin/form.html", form=form, species=None)


@admin_bp.route("/<int:species_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def edit(species_id: int):
    species = db.get_or_404(Species, species_id)
    form = SpeciesForm(obj=species)

    if form.validate_on_submit():
        scientific_name = form.scientific_name.data.strip()
        duplicate = Species.query.filter(
            Species.scientific_name == scientific_name,
            Species.id != species.id,
        ).first()
        if duplicate:
            flash("Otra especie ya usa ese nombre científico.", "error")
        else:
            _apply_form(species, form)
            db.session.commit()
            flash(f"«{species.common_name}» se actualizó correctamente.", "success")
            return redirect(url_for("admin.index"))

    return render_template("admin/form.html", form=form, species=species)


@admin_bp.route("/<int:species_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def delete(species_id: int):
    species = db.get_or_404(Species, species_id)
    name = species.common_name
    db.session.delete(species)
    db.session.commit()
    flash(f"«{name}» se eliminó del catálogo.", "success")
    return redirect(url_for("admin.index"))
