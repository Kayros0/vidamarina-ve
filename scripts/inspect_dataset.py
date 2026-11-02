"""Muestra un resumen del dataset generado."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

data = json.loads(
    (Path(__file__).resolve().parent.parent / "data" / "species.json").read_text(
        encoding="utf-8"
    )
)

print(f"Total: {len(data)} especies\n")
print(
    f"{'Nombre común':<30} {'UICN':<4} {'Año':<5} {'Desc.':<5} "
    f"{'Autor imagen':<24} {'Licencia':<20} {'Texto':>6}"
)
print("-" * 110)

for row in data:
    print(
        f"{row['common_name'][:29]:<30} {row['iucn_status']:<4} "
        f"{str(row['iucn_year'] or '—'):<5} {str(row['described_year'] or '—'):<5} "
        f"{str(row['image_author'] or '—')[:23]:<24} "
        f"{str(row['image_license'] or '—')[:19]:<20} "
        f"{len(row['description']):>6}"
    )

print("\nSin UICN:")
for row in data:
    if row["iucn_status"] == "NE":
        print("  -", row["common_name"], f"({row['scientific_name']})")

print("\nSin año de descripción:")
for row in data:
    if not row["described_year"]:
        print("  -", row["common_name"], f"({row['scientific_name']})")

print("\nEjemplo de ficha:")
print(json.dumps(data[0], ensure_ascii=False, indent=2))
