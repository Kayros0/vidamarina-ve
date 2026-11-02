# Paquete local para Windows

`vidamarina-ve-local.zip` es una copia del proyecto lista para ejecutarse con
doble clic en Windows. Usa SQLite, así que **no necesita PostgreSQL** ni cargar
datos a mano.

## Descargar

<https://github.com/Kayros0/vidamarina-ve/raw/main/dist/vidamarina-ve-local.zip>

También puedes descargarlo desde la página del repositorio:
<https://github.com/Kayros0/vidamarina-ve/blob/main/dist/vidamarina-ve-local.zip>

## Usar

1. Descomprime el ZIP (queda una carpeta `vidamarina-ve-local`).
2. Haz doble clic en `Iniciar.bat`.
3. La primera vez crea el entorno virtual e instala Flask (1–2 minutos,
   necesita Internet). Después arranca en segundos.
4. El navegador se abre solo en `http://127.0.0.1:5000` (o `5001` si el puerto
   está ocupado).
5. Para detener la app, cierra la ventana negra o pulsa `Ctrl+C`.

Requisitos: Windows 10/11 y Python 3.10 o superior con la opción
«Add python.exe to PATH» marcada al instalarlo.

Cuenta de administrador de la demo local: `admin` / `Admin1234!`.

Instrucciones completas dentro del ZIP: `LEEME.txt`.

## Regenerar el ZIP

Desde la raíz del repositorio:

```powershell
python scripts/build_local_zip.py
```

El script arma el paquete con `app/`, `data/`, `scripts/`, `tests/` y los
archivos de la raíz, y deja fuera `.env`, `.venv/`, `instance/`, `.git/`,
`__pycache__/`, `*.pyc`, `*.db` y `dist/`. Vuelve a ejecutarlo cada vez que
cambie el código para que la descarga esté al día.
