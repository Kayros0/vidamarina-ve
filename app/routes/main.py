"""Rutas públicas: catálogo, búsqueda, ficha, mapa y API."""
from flask import Blueprint, jsonify, render_template, request, url_for
from sqlalchemy import case, func

from ..extensions import db
from ..models import (
    GROUP_LABELS,
    IUCN_ORDER,
    REGION_LABELS,
    Species,
    normalize_text,
)

main_bp = Blueprint("main", __name__)

SORT_OPTIONS = {
    "nombre": "Orden alfabético (A–Z)",
    "rareza": "Rareza (estado UICN)",
    "reciente": "Último descrito (más reciente)",
}


def _filtered_species():
    """Aplica búsqueda, filtros y orden según los parámetros de la URL."""
    q = (request.args.get("q") or "").strip()
    region = (request.args.get("region") or "").strip()
    group = (request.args.get("grupo") or "").strip()
    sort = (request.args.get("orden") or "nombre").strip()

    query = Species.query

    if q:
        key = normalize_text(q)
        if key:
            query = query.filter(Species.search_key.contains(key, autoescape=True))

    if region in REGION_LABELS:
        query = query.filter(Species.region == region)

    if group in GROUP_LABELS:
        query = query.filter(Species.group == group)

    if sort == "rareza":
        rank = case(IUCN_ORDER, value=Species.iucn_status, else_=99)
        query = query.order_by(rank.asc(), Species.common_name.asc())
    elif sort == "reciente":
        query = query.order_by(
            Species.described_year.desc().nullslast(),
            Species.common_name.asc(),
        )
    else:
        sort = "nombre"
        query = query.order_by(Species.common_name.asc())

    filters = {"q": q, "region": region, "grupo": group, "orden": sort}
    return query.all(), filters


@main_bp.route("/")
def index():
    species, filters = _filtered_species()

    stats = {
        "total": db.session.query(func.count(Species.id)).scalar() or 0,
        "caribe": Species.query.filter(
            Species.region.in_(["caribe", "ambas"])
        ).count(),
        "rios": Species.query.filter(Species.region.in_(["rios", "ambas"])).count(),
        "amenazadas": Species.query.filter(
            Species.iucn_status.in_(["CR", "EN", "VU"])
        ).count(),
    }

    return render_template(
        "index.html",
        species=species,
        filters=filters,
        stats=stats,
        sort_options=SORT_OPTIONS,
        group_labels=GROUP_LABELS,
        region_labels=REGION_LABELS,
    )


@main_bp.route("/especie/<int:species_id>")
def species_detail(species_id: int):
    species = db.get_or_404(Species, species_id)
    related = (
        Species.query.filter(
            Species.group == species.group,
            Species.id != species.id,
        )
        .order_by(func.random())
        .limit(3)
        .all()
    )
    return render_template(
        "species_detail.html",
        species=species,
        related=related,
    )


@main_bp.route("/mapa")
def map_view():
    species = Species.query.order_by(Species.common_name.asc()).all()
    items = [
        {
            **item.to_dict(),
            "url": url_for("main.species_detail", species_id=item.id),
        }
        for item in species
    ]
    return render_template("map.html", species=items)


@main_bp.route("/fuentes")
def sources():
    return render_template("sources.html")


@main_bp.route("/api/especies")
def api_species():
    """API JSON del catálogo (misma búsqueda y filtros que la web)."""
    species, filters = _filtered_species()
    return jsonify(
        {
            "count": len(species),
            "filters": filters,
            "results": [
                {
                    **item.to_dict(),
                    "url": url_for("main.species_detail", species_id=item.id),
                }
                for item in species
            ],
        }
    )
