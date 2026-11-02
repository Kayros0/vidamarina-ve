"""Genera el paquete local para Windows (dist/vidamarina-ve-local.zip).

El ZIP contiene el proyecto listo para ejecutarse con doble clic en
`Iniciar.bat`, pero sin secretos, entorno virtual ni base de datos.

Uso:
    python scripts/build_local_zip.py
"""
from __future__ import annotations

import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"
ZIP_PATH = DIST_DIR / "vidamarina-ve-local.zip"
ROOT_IN_ZIP = "vidamarina-ve-local"

# Carpetas que se incluyen completas (se filtran los archivos temporales).
INCLUDE_DIRS = ["app", "data", "scripts", "tests"]

# Archivos sueltos de la raíz que sí forman parte del paquete.
INCLUDE_FILES = [
    ".env.example",
    ".gitignore",
    "Iniciar.bat",
    "LEEME.txt",
    "README.md",
    "config.py",
    "iniciar.py",
    "render.yaml",
    "requirements.txt",
    "run.py",
]

# Nunca deben viajar en el ZIP.
EXCLUDED_DIRS = {".git", ".venv", "venv", "instance", "__pycache__", "dist", ".idea", ".vscode"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".db", ".sqlite3", ".log"}
EXCLUDED_NAMES = {".env", ".DS_Store", "Thumbs.db"}


def _is_excluded(path: Path) -> bool:
    if path.name in EXCLUDED_NAMES:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    return any(part in EXCLUDED_DIRS for part in path.parts)


def iter_files() -> list[Path]:
    """Devuelve los archivos del proyecto que entran en el paquete."""
    files: list[Path] = []

    for name in INCLUDE_FILES:
        path = BASE_DIR / name
        if path.is_file():
            files.append(path)

    for dirname in INCLUDE_DIRS:
        root = BASE_DIR / dirname
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and not _is_excluded(path.relative_to(BASE_DIR)):
                files.append(path)

    return sorted(set(files))


def build() -> Path:
    files = iter_files()
    DIST_DIR.mkdir(exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            relative = path.relative_to(BASE_DIR)
            arcname = f"{ROOT_IN_ZIP}/{relative.as_posix()}"
            zf.write(path, arcname)

    return ZIP_PATH


def main() -> None:
    files = iter_files()
    print(f"Archivos a empaquetar: {len(files)}")
    for path in files:
        print(f"  + {path.relative_to(BASE_DIR).as_posix()}")

    zip_path = build()
    size_kb = zip_path.stat().st_size / 1024
    print()
    print(f"Listo: {zip_path.relative_to(BASE_DIR).as_posix()} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
