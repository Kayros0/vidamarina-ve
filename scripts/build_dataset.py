"""Construye data/species.json a partir de Wikipedia, Wikidata y Wikimedia Commons.

Uso:
    .venv\\Scripts\\python.exe scripts\\build_dataset.py

El resultado se guarda en data/species.json y luego la app lo carga en la base
de datos la primera vez que arranca (ver app/seed.py).
"""
import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "species.json"

SESSION = requests.Session()
SESSION.headers.update(
    {"User-Agent": "VidaMarinaVE/1.0 (proyecto universitario; contacto: estudiante)"}
)

IUCN_CODES = {
    "least concern": "LC",
    "near threatened": "NT",
    "vulnerable": "VU",
    "endangered": "EN",
    "critically endangered": "CR",
    "data deficient": "DD",
    "not evaluated": "NE",
    "extinct": "EX",
    "extinct in the wild": "EW",
}

# ---------------------------------------------------------------------------
# Catálogo curado: nombre común, grupo, región, hábitat y punto de referencia.
# El resto (descripción, UICN, año, imagen) se obtiene de las APIs.
# ---------------------------------------------------------------------------
SPECIES = [
    # --- Caribe -------------------------------------------------------------
    {
        "common_name": "Delfín nariz de botella",
        "scientific_name": "Tursiops truncatus",
        "group": "mamifero",
        "region": "caribe",
        "habitat": "Aguas costeras y oceánicas del Caribe venezolano",
        "map_lat": 10.98,
        "map_lng": -63.95,
        "map_label": "Isla de Margarita",
    },
    {
        "common_name": "Delfín moteado del Atlántico",
        "scientific_name": "Stenella frontalis",
        "group": "mamifero",
        "region": "caribe",
        "habitat": "Aguas profundas y costeras del Caribe",
        "map_lat": 11.2,
        "map_lng": -63.5,
        "map_label": "Archipiélago de Los Frailes",
    },
    {
        "common_name": "Ballena jorobada",
        "scientific_name": "Megaptera novaeangliae",
        "group": "mamifero",
        "region": "caribe",
        "habitat": "Aguas costeras del Caribe; migra desde el Atlántico Norte",
        "map_lat": 10.6,
        "map_lng": -66.9,
        "map_label": "Costa central de Venezuela",
    },
    {
        "common_name": "Cachalote",
        "scientific_name": "Physeter macrocephalus",
        "group": "mamifero",
        "region": "caribe",
        "habitat": "Aguas oceánicas profundas",
        "map_lat": 11.5,
        "map_lng": -62.0,
        "map_label": "Mar Caribe oriental",
    },
    {
        "common_name": "Orca",
        "scientific_name": "Orcinus orca",
        "group": "mamifero",
        "region": "caribe",
        "habitat": "Aguas oceánicas y costeras",
        "map_lat": 10.7,
        "map_lng": -63.0,
        "map_label": "Mar Caribe nororiental",
    },
    {
        "common_name": "Manatí antillano",
        "scientific_name": "Trichechus manatus",
        "group": "mamifero",
        "region": "ambas",
        "habitat": "Ríos, lagunas costeras y manglares",
        "map_lat": 8.0,
        "map_lng": -62.0,
        "map_label": "Delta del Orinoco",
    },
    {
        "common_name": "Tiburón ballena",
        "scientific_name": "Rhincodon typus",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas cálidas del Caribe",
        "map_lat": 11.0,
        "map_lng": -64.5,
        "map_label": "Isla de Margarita",
    },
    {
        "common_name": "Tiburón martillo",
        "scientific_name": "Sphyrna lewini",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas costeras y oceánicas",
        "map_lat": 10.5,
        "map_lng": -64.0,
        "map_label": "Costa nororiental",
    },
    {
        "common_name": "Mero guasa",
        "scientific_name": "Epinephelus itajara",
        "group": "pez",
        "region": "caribe",
        "habitat": "Arrecifes y cuevas submarinas",
        "map_lat": 10.9,
        "map_lng": -64.2,
        "map_label": "Isla de Cubagua",
    },
    {
        "common_name": "Pez loro guacamayo",
        "scientific_name": "Scarus guacamaia",
        "group": "pez",
        "region": "caribe",
        "habitat": "Arrecifes coralinos",
        "map_lat": 11.8,
        "map_lng": -66.2,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Pez ángel francés",
        "scientific_name": "Pomacanthus paru",
        "group": "pez",
        "region": "caribe",
        "habitat": "Arrecifes coralinos",
        "map_lat": 11.9,
        "map_lng": -66.8,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Pez cirujano azul",
        "scientific_name": "Acanthurus coeruleus",
        "group": "pez",
        "region": "caribe",
        "habitat": "Arrecifes coralinos",
        "map_lat": 11.7,
        "map_lng": -66.0,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Pez león",
        "scientific_name": "Pterois volitans",
        "group": "pez",
        "region": "caribe",
        "habitat": "Arrecifes y zonas rocosas; especie invasora",
        "map_lat": 10.6,
        "map_lng": -66.0,
        "map_label": "Costa central",
    },
    {
        "common_name": "Caballito de mar",
        "scientific_name": "Hippocampus erectus",
        "group": "pez",
        "region": "caribe",
        "habitat": "Praderas de pastos marinos y manglares",
        "map_lat": 10.8,
        "map_lng": -64.0,
        "map_label": "Isla de Margarita",
    },
    {
        "common_name": "Tortuga carey",
        "scientific_name": "Eretmochelys imbricata",
        "group": "reptil",
        "region": "caribe",
        "habitat": "Arrecifes y praderas marinas",
        "map_lat": 11.8,
        "map_lng": -66.5,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Tortuga verde",
        "scientific_name": "Chelonia mydas",
        "group": "reptil",
        "region": "caribe",
        "habitat": "Praderas de pastos marinos",
        "map_lat": 11.0,
        "map_lng": -64.0,
        "map_label": "Isla de Margarita",
    },
    {
        "common_name": "Tortuga cabezona",
        "scientific_name": "Caretta caretta",
        "group": "reptil",
        "region": "caribe",
        "habitat": "Aguas costeras y oceánicas",
        "map_lat": 10.5,
        "map_lng": -66.0,
        "map_label": "Costa central",
    },
    {
        "common_name": "Tortuga laúd",
        "scientific_name": "Dermochelys coriacea",
        "group": "reptil",
        "region": "caribe",
        "habitat": "Mar abierto; desova en playas del Caribe",
        "map_lat": 10.6,
        "map_lng": -63.0,
        "map_label": "Península de Paria",
    },
    {
        "common_name": "Coral cuerno de alce",
        "scientific_name": "Acropora cervicornis",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Arrecifes coralinos someros",
        "map_lat": 11.8,
        "map_lng": -66.2,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Coral cuerno de ciervo",
        "scientific_name": "Acropora palmata",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Arrecifes coralinos someros",
        "map_lat": 11.8,
        "map_lng": -66.3,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Langosta espinosa del Caribe",
        "scientific_name": "Panulirus argus",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Arrecifes y fondos rocosos",
        "map_lat": 11.0,
        "map_lng": -64.3,
        "map_label": "Isla de Cubagua",
    },
    {
        "common_name": "Caracol rosado",
        "scientific_name": "Lobatus gigas",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Praderas de pastos marinos y fondos arenosos",
        "map_lat": 11.9,
        "map_lng": -66.6,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Estrella de mar cojín",
        "scientific_name": "Oreaster reticulatus",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Arenas y pastos marinos",
        "map_lat": 11.5,
        "map_lng": -66.0,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Erizo de mar",
        "scientific_name": "Diadema antillarum",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Arrecifes coralinos",
        "map_lat": 11.6,
        "map_lng": -66.1,
        "map_label": "Archipiélago de Los Roques",
    },
    {
        "common_name": "Pulpo común",
        "scientific_name": "Octopus vulgaris",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Fondos rocosos y arenosos",
        "map_lat": 10.9,
        "map_lng": -64.1,
        "map_label": "Isla de Margarita",
    },
    {
        "common_name": "Medusa luna",
        "scientific_name": "Aurelia aurita",
        "group": "invertebrado",
        "region": "caribe",
        "habitat": "Aguas costeras y estuarios",
        "map_lat": 10.6,
        "map_lng": -64.8,
        "map_label": "Costa nororiental",
    },
    {
        "common_name": "Manta gigante",
        "scientific_name": "Mobula birostris",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas oceánicas y costeras",
        "map_lat": 11.3,
        "map_lng": -63.0,
        "map_label": "Mar Caribe oriental",
    },
    {
        "common_name": "Raya águila",
        "scientific_name": "Aetobatus narinari",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas costeras y arrecifes",
        "map_lat": 11.1,
        "map_lng": -64.2,
        "map_label": "Isla de Margarita",
    },
    {
        "common_name": "Dorado",
        "scientific_name": "Coryphaena hippurus",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas oceánicas y costeras",
        "map_lat": 10.8,
        "map_lng": -65.0,
        "map_label": "Costa central",
    },
    {
        "common_name": "Barracuda",
        "scientific_name": "Sphyraena barracuda",
        "group": "pez",
        "region": "caribe",
        "habitat": "Arrecifes y aguas costeras",
        "map_lat": 11.0,
        "map_lng": -64.4,
        "map_label": "Isla de Cubagua",
    },
    {
        "common_name": "Pez vela",
        "scientific_name": "Istiophorus platypterus",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas oceánicas",
        "map_lat": 11.2,
        "map_lng": -62.5,
        "map_label": "Mar Caribe oriental",
    },
    {
        "common_name": "Tiburón gato",
        "scientific_name": "Ginglymostoma cirratum",
        "group": "pez",
        "region": "caribe",
        "habitat": "Aguas costeras y arrecifes",
        "map_lat": 11.0,
        "map_lng": -64.0,
        "map_label": "Isla de Margarita",
    },
    # --- Ríos y aguas dulces ------------------------------------------------
    {
        "common_name": "Delfín rosado",
        "scientific_name": "Inia geoffrensis",
        "group": "mamifero",
        "region": "rios",
        "habitat": "Ríos y lagunas de la cuenca del Orinoco",
        "map_lat": 7.5,
        "map_lng": -65.5,
        "map_label": "Cuenca del Orinoco",
    },
    {
        "common_name": "Caimán del Orinoco",
        "scientific_name": "Crocodylus intermedius",
        "group": "reptil",
        "region": "rios",
        "habitat": "Ríos y caños de los Llanos",
        "map_lat": 8.5,
        "map_lng": -67.0,
        "map_label": "Río Cojedes",
    },
    {
        "common_name": "Caimán de la costa",
        "scientific_name": "Crocodylus acutus",
        "group": "reptil",
        "region": "ambas",
        "habitat": "Estuarios, manglares y ríos costeros",
        "map_lat": 10.5,
        "map_lng": -68.0,
        "map_label": "Costa de Falcón",
    },
    {
        "common_name": "Tortuga arrau",
        "scientific_name": "Podocnemis expansa",
        "group": "reptil",
        "region": "rios",
        "habitat": "Ríos y playas de la cuenca del Orinoco",
        "map_lat": 7.0,
        "map_lng": -66.0,
        "map_label": "Río Orinoco",
    },
    {
        "common_name": "Terecay",
        "scientific_name": "Podocnemis unifilis",
        "group": "reptil",
        "region": "rios",
        "habitat": "Ríos y lagunas del Orinoco y del Amazonas",
        "map_lat": 6.5,
        "map_lng": -66.5,
        "map_label": "Río Orinoco",
    },
    {
        "common_name": "Galápago llanero",
        "scientific_name": "Podocnemis vogli",
        "group": "reptil",
        "region": "rios",
        "habitat": "Lagunas y morichales de los Llanos",
        "map_lat": 8.0,
        "map_lng": -67.5,
        "map_label": "Llanos occidentales",
    },
    {
        "common_name": "Anguila eléctrica",
        "scientific_name": "Electrophorus electricus",
        "group": "pez",
        "region": "rios",
        "habitat": "Aguas turbias y de baja conductividad",
        "map_lat": 7.0,
        "map_lng": -64.0,
        "map_label": "Cuenca del Orinoco",
    },
    {
        "common_name": "Payara",
        "scientific_name": "Hydrolycus armatus",
        "group": "pez",
        "region": "rios",
        "habitat": "Ríos rápidos y caños",
        "map_lat": 6.0,
        "map_lng": -65.0,
        "map_label": "Río Caura",
    },
    {
        "common_name": "Piraña caribe",
        "scientific_name": "Pygocentrus cariba",
        "group": "pez",
        "region": "rios",
        "habitat": "Ríos y lagunas de los Llanos",
        "map_lat": 8.0,
        "map_lng": -66.0,
        "map_label": "Río Apure",
    },
    {
        "common_name": "Bagre rayado",
        "scientific_name": "Pseudoplatystoma tigrinum",
        "group": "pez",
        "region": "rios",
        "habitat": "Ríos y llanuras inundables",
        "map_lat": 7.0,
        "map_lng": -67.0,
        "map_label": "Río Apure",
    },
    {
        "common_name": "Pez sierra",
        "scientific_name": "Pristis pristis",
        "group": "pez",
        "region": "ambas",
        "habitat": "Estuarios y ríos; también aguas costeras",
        "map_lat": 8.0,
        "map_lng": -62.0,
        "map_label": "Delta del Orinoco",
    },
    {
        "common_name": "Raya de agua dulce",
        "scientific_name": "Potamotrygon motoro",
        "group": "pez",
        "region": "rios",
        "habitat": "Fondos arenosos de ríos",
        "map_lat": 6.5,
        "map_lng": -67.0,
        "map_label": "Río Orinoco",
    },
    {
        "common_name": "Pavón",
        "scientific_name": "Cichla ocellaris",
        "group": "pez",
        "region": "rios",
        "habitat": "Ríos y lagunas",
        "map_lat": 6.0,
        "map_lng": -64.0,
        "map_label": "Río Caura",
    },
    {
        "common_name": "Cachama",
        "scientific_name": "Colossoma macropomum",
        "group": "pez",
        "region": "rios",
        "habitat": "Ríos y lagunas del Orinoco y del Amazonas",
        "map_lat": 7.5,
        "map_lng": -65.0,
        "map_label": "Cuenca del Orinoco",
    },
]


def clean_text(value: str) -> str:
    value = value.replace("\u200b", "").replace("\u200e", "").replace("\u200f", "")
    value = value.replace("\ufeff", "")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def truncate(text: str, limit: int = 1400) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    sentence = max(cut.rfind(". "), cut.rfind(".\n"))
    if sentence > limit * 0.55:
        return cut[: sentence + 1].strip()
    return cut.rstrip() + "…"


def _request(params: dict, lang: str) -> dict:
    """Petición a la API de Wikipedia con reintentos ante límite de tasa."""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    response = None
    for attempt in range(4):
        response = SESSION.get(url, params=params, timeout=30)
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 3)) + attempt * 3
            print(f"  [429] límite alcanzado, esperando {wait}s…")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()
    if response is not None:
        response.raise_for_status()
    return {}


def wikipedia_batch(titles: list[str], lang: str = "es") -> dict:
    """Obtiene extractos de hasta 20 títulos por petición."""
    results: dict[str, dict] = {}
    unique = list(dict.fromkeys(titles))

    for start in range(0, len(unique), 20):
        chunk = unique[start : start + 20]
        data = _request(
            {
                "action": "query",
                "prop": "extracts|pageprops",
                "explaintext": 1,
                "exintro": 1,
                "exlimit": 20,
                "redirects": 1,
                "titles": "|".join(chunk),
                "format": "json",
                "ppprop": "wikibase_item",
            },
            lang,
        )
        query = data.get("query", {})
        normalized = {n["from"]: n["to"] for n in query.get("normalized", [])}
        redirects = {r["from"]: r["to"] for r in query.get("redirects", [])}
        pages = {p.get("title"): p for p in query.get("pages", {}).values()}

        for title in chunk:
            final = normalized.get(title, title)
            final = redirects.get(final, final)
            page = pages.get(final)
            if not page or "missing" in page:
                continue
            results[title] = {
                "title": page.get("title", final),
                "extract": clean_text(page.get("extract", "")),
                "qid": page.get("pageprops", {}).get("wikibase_item"),
                "lang": lang,
            }
        time.sleep(1.0)

    return results


def wikipedia_full(title: str, lang: str = "es") -> dict:
    """Trae el artículo completo (útil cuando la introducción es muy corta)."""
    data = _request(
        {
            "action": "query",
            "prop": "extracts|pageprops",
            "explaintext": 1,
            "redirects": 1,
            "titles": title,
            "format": "json",
            "ppprop": "wikibase_item",
        },
        lang,
    )
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    if not page or "missing" in page:
        return {}
    return {
        "title": page.get("title", title),
        "extract": clean_text(page.get("extract", "")),
        "qid": page.get("pageprops", {}).get("wikibase_item"),
        "lang": lang,
    }


def sparql(query: str) -> list:
    response = SESSION.get(
        "https://query.wikidata.org/sparql",
        params={"format": "json", "query": query},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()["results"]["bindings"]


def year_from_time(value: str | None):
    if not value:
        return None
    match = re.match(r"^[+-]?(\d{4})", value)
    return int(match.group(1)) if match else None


def fetch_wikidata(qids: list[str]) -> dict:
    if not qids:
        return {}
    values = " ".join(f"wd:{qid}" for qid in qids)
    query = f"""
    SELECT ?taxon ?iucnEn ?iucnYear ?describedYear ?image WHERE {{
      VALUES ?taxon {{ {values} }}
      OPTIONAL {{
        ?taxon p:P141 ?iucnStmt .
        ?iucnStmt ps:P141 ?iucn .
        OPTIONAL {{ ?iucnStmt pq:P585 ?iucnYear . }}
        OPTIONAL {{ ?iucn rdfs:label ?iucnEn . FILTER(LANG(?iucnEn) = "en") }}
      }}
      OPTIONAL {{
        ?taxon p:P225 ?nameStmt .
        ?nameStmt pq:P574 ?describedYear .
      }}
      OPTIONAL {{ ?taxon wdt:P18 ?image . }}
    }}
    """
    data: dict[str, dict] = {}
    for row in sparql(query):
        qid = row["taxon"]["value"].rsplit("/", 1)[-1]
        entry = data.setdefault(
            qid,
            {"iucn": None, "iucn_year": None, "described_year": None, "images": []},
        )
        label = row.get("iucnEn", {}).get("value", "").strip().lower()
        if label in IUCN_CODES and not entry["iucn"]:
            entry["iucn"] = IUCN_CODES[label]
        entry["iucn_year"] = entry["iucn_year"] or year_from_time(
            row.get("iucnYear", {}).get("value")
        )
        entry["described_year"] = entry["described_year"] or year_from_time(
            row.get("describedYear", {}).get("value")
        )
        image = row.get("image", {}).get("value")
        if image:
            entry["images"].append(image)
    return data


def commons_metadata(filenames: list[str]) -> dict:
    if not filenames:
        return {}
    result = {}
    for start in range(0, len(filenames), 40):
        batch = filenames[start : start + 40]
        titles = "|".join(f"File:{name}" for name in batch)
        response = SESSION.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "imageinfo",
                "iiprop": "extmetadata",
                "titles": titles,
                "format": "json",
            },
            timeout=45,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            title = page.get("title", "")
            meta = page.get("imageinfo", [{}])[0].get("extmetadata", {})
            artist = meta.get("Artist", {}).get("value", "")
            license_name = meta.get("LicenseShortName", {}).get("value", "")
            artist = re.sub(r"<[^>]+>", "", html.unescape(artist))
            artist = re.sub(r"\s+", " ", artist).strip()[:160]
            result[title] = {
                "author": artist,
                "license": clean_text(license_name)[:120],
            }
    return result


def filename_from_url(url: str) -> str:
    marker = "Special:FilePath/"
    if marker in url:
        return unquote(url.split(marker, 1)[1].split("?", 1)[0])
    return unquote(url.rsplit("/", 1)[-1])


def image_url(filename: str, width: int = 900) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + quote(filename)
        + f"?width={width}"
    )


def main() -> None:
    records = []
    missing_pages = []
    qids = []

    sci_names = [item["scientific_name"] for item in SPECIES]
    es_sci = wikipedia_batch(sci_names, "es")

    not_in_es = [item for item in SPECIES if item["scientific_name"] not in es_sci]
    es_common = wikipedia_batch([item["common_name"] for item in not_in_es], "es")

    still_missing = [
        item for item in not_in_es if item["common_name"] not in es_common
    ]
    en_sci = wikipedia_batch([item["scientific_name"] for item in still_missing], "en")

    still_missing = [
        item for item in still_missing if item["scientific_name"] not in en_sci
    ]
    en_common = wikipedia_batch([item["common_name"] for item in still_missing], "en")

    for item in SPECIES:
        scientific = item["scientific_name"]
        common = item["common_name"]

        wiki = (
            es_sci.get(scientific)
            or es_common.get(common)
            or en_sci.get(scientific)
            or en_common.get(common)
            or {}
        )

        if not wiki:
            missing_pages.append(scientific)
            print(f"[SIN WIKI] {common} ({scientific})")
            wiki = {"title": scientific, "extract": "", "qid": None, "lang": "es"}

        if wiki.get("extract") and len(wiki["extract"]) < 250:
            fuller = wikipedia_full(wiki["title"], wiki["lang"])
            if fuller.get("extract") and len(fuller["extract"]) > len(wiki["extract"]):
                wiki = fuller
            time.sleep(0.5)

        print(
            f"[{'OK' if wiki.get('qid') else '??'}] {common:<32} "
            f"{wiki['lang']} · {wiki.get('qid')} · "
            f"{len(wiki.get('extract', ''))} caracteres"
        )

        record = {**item}
        record["description"] = truncate(wiki.get("extract", "")) or (
            f"Ficha de {common} ({scientific})."
        )
        record["source_url"] = (
            f"https://{wiki['lang']}.wikipedia.org/wiki/"
            + quote(wiki["title"].replace(" ", "_"))
        )
        record["_qid"] = wiki.get("qid")
        if wiki.get("qid"):
            qids.append(wiki["qid"])
        records.append(record)

    wikidata = fetch_wikidata(qids)

    # Elegir una imagen que no sea un icono de estado UICN.
    chosen = {}
    filenames = []
    for record in records:
        entry = wikidata.get(record["_qid"], {})
        images = [
            url
            for url in entry.get("images", [])
            if not url.lower().endswith(".svg")
            and "status%20iucn" not in url.lower()
            and "status iucn" not in url.lower()
        ]
        if images:
            filename = filename_from_url(images[0])
            chosen[record["scientific_name"]] = filename
            filenames.append(filename)

    metadata = commons_metadata(filenames)

    output = []
    for record in records:
        entry = wikidata.get(record["_qid"], {})
        filename = chosen.get(record["scientific_name"])
        meta = metadata.get(f"File:{filename}", {}) if filename else {}

        output.append(
            {
                "common_name": record["common_name"],
                "scientific_name": record["scientific_name"],
                "group": record["group"],
                "region": record["region"],
                "habitat": record["habitat"],
                "description": record["description"],
                "iucn_status": entry.get("iucn") or "NE",
                "iucn_year": entry.get("iucn_year"),
                "described_year": entry.get("described_year"),
                "image_url": image_url(filename) if filename else None,
                "image_author": meta.get("author") or None,
                "image_license": meta.get("license") or None,
                "source_url": record["source_url"],
                "map_lat": record["map_lat"],
                "map_lng": record["map_lng"],
                "map_label": record["map_label"],
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print(f"Guardadas {len(output)} especies en {OUTPUT}")
    print(f"Con imagen: {sum(1 for row in output if row['image_url'])}")
    print(f"Con UICN:   {sum(1 for row in output if row['iucn_status'] != 'NE')}")
    print(f"Con año:    {sum(1 for row in output if row['described_year'])}")
    if missing_pages:
        print("\nSin página de Wikipedia:")
        for name in missing_pages:
            print("  -", name)


if __name__ == "__main__":
    main()
