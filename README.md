# Vida Marina VE

Catálogo web de la vida marina y de ríos de Venezuela. Proyecto de **Electiva 3
(Programación 3)**: permite explorar 46 especies del Caribe y de las cuencas del
Orinoco, buscar por nombre o hábitat, filtrar por grupo, región, rareza y año de
descripción, ver cada especie en un mapa interactivo y administrar el catálogo
desde un panel privado.

**Aplicación en producción:** <https://vidamarina-ve.onrender.com>

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Ejecutar en local](#ejecutar-en-local)
- [Paquete local para Windows](#paquete-local-para-windows)
- [Cuenta de administrador](#cuenta-de-administrador)
- [Rutas principales](#rutas-principales)
- [Modelo de datos](#modelo-de-datos)
- [Datos y fuentes](#datos-y-fuentes)
- [Pruebas automáticas](#pruebas-automáticas)
- [Despliegue público (Render + Neon)](#despliegue-público-render--neon)
- [Guion para la defensa](#guion-para-la-defensa)
- [Decisiones de seguridad](#decisiones-de-seguridad)
- [Limitaciones conocidas](#limitaciones-conocidas)

---

## Funcionalidades

| Requisito | Cómo se cumple |
| --- | --- |
| Registro e inicio de sesión | Flask-Login + contraseñas con hash (`scrypt` de Werkzeug). Sesión persistente con «Recordarme». |
| Búsqueda precisa | Búsqueda por nombre común, científico, hábitat, grupo, región y estado UICN, **sin distinguir mayúsculas ni tildes** (`delfin` encuentra `Delfín`). |
| Catálogo en tarjetas | Grid responsive con foto, nombre común, nombre científico, grupo, región, hábitat, año de descripción y badge UICN. |
| Filtros y orden | Región (Caribe / Ríos / Ambas), grupo taxonómico y orden por **A–Z**, **rareza (UICN)** o **último descrito**. |
| Ficha de especie | Imagen con crédito y licencia, descripción, ficha técnica, enlace a la fuente, mini-mapa y especies relacionadas. |
| Mapa interactivo | Leaflet + OpenStreetMap con 46 marcadores, filtro por región, lista lateral sincronizada y popups. |
| Base de datos y backend | Flask + SQLAlchemy. SQLite en local, PostgreSQL en producción. |
| Panel de administración | CRUD completo de especies, solo para usuarios `is_admin`. |
| API JSON | `/api/especies` con los mismos filtros y búsqueda que la web. |
| Despliegue público | `render.yaml` + Gunicorn, listo para Render; base de datos en Neon. |

Extras: diseño responsive, navegación por teclado, `prefers-reduced-motion`,
página de fuentes y licencias, y manejo de errores 403/404.

## Stack

- **Python 3.12** + **Flask 3.1**
- **Flask-SQLAlchemy** (SQLAlchemy 2.x) + **SQLite** / **PostgreSQL**
- **Flask-Login**, **Flask-WTF** (formularios + CSRF), **WTForms**
- **Jinja2** para las plantillas
- **Leaflet 1.9** + **OpenStreetMap** para el mapa
- **Gunicorn** en producción
- CSS y JavaScript propios, sin frameworks de frontend

## Estructura del proyecto

```
.
├── app/
│   ├── __init__.py          # fábrica de la app, blueprints, errores, seed
│   ├── extensions.py        # db, login_manager, csrf
│   ├── models.py            # User, Species, etiquetas y normalización
│   ├── forms.py             # formularios con validación en español
│   ├── seed.py              # carga inicial del catálogo y del admin
│   ├── routes/
│   │   ├── main.py          # catálogo, búsqueda, ficha, mapa, API
│   │   ├── auth.py          # registro, login, logout
│   │   └── admin.py         # CRUD protegido
│   ├── templates/           # base, catálogo, ficha, mapa, fuentes, auth, admin
│   └── static/              # CSS, JS y SVG de respaldo
├── data/
│   ├── species.json         # dataset curado (46 especies)
│   └── README.md            # documentación del dataset
├── scripts/
│   ├── build_dataset.py     # regenera el dataset desde Wikipedia/Wikidata/Commons
│   ├── build_local_zip.py   # arma dist/vidamarina-ve-local.zip
│   └── inspect_dataset.py   # resumen de control del dataset
├── tests/
│   └── test_app.py          # 13 pruebas automatizadas
├── dist/
│   ├── README.md            # instrucciones del paquete local
│   └── vidamarina-ve-local.zip
├── config.py                # configuración por variables de entorno
├── run.py                   # punto de entrada (dev y Gunicorn)
├── iniciar.py               # lanzador local que abre el navegador
├── Iniciar.bat              # doble clic para ejecutar en Windows
├── LEEME.txt                # instrucciones del paquete local
├── render.yaml              # blueprint de despliegue en Render
├── requirements.txt         # dependencias con versiones fijas
├── .env.example             # plantilla de variables de entorno
└── README.md
```

## Ejecutar en local

Requisitos: Python 3.10+ (recomendado 3.12) y Git.

```powershell
# 1. Clonar el repositorio
git clone https://github.com/Kayros0/vidamarina-ve.git
cd vidamarina-ve

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activar el entorno (PowerShell)
.\.venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear el archivo de variables de entorno
Copy-Item .env.example .env
#    y edita .env con una SECRET_KEY propia

# 6. Arrancar
python run.py
```

Abre <http://127.0.0.1:5000>.

La primera vez se crea `instance/vidamarina.db`, se cargan las 46 especies desde
`data/species.json` y se crea la cuenta administradora.

> En PowerShell, si la activación del entorno está bloqueada, ejecuta una vez:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## Paquete local para Windows

Si solo quieres ver la aplicación funcionando sin instalar nada a mano, descarga
el paquete y ejecútalo con doble clic:

**[Descargar `vidamarina-ve-local.zip`](https://github.com/Kayros0/vidamarina-ve/raw/main/dist/vidamarina-ve-local.zip)**

1. Descomprime el ZIP (queda la carpeta `vidamarina-ve-local`).
2. Haz doble clic en **`Iniciar.bat`**.
3. La primera vez crea el entorno virtual e instala las dependencias
   (1–2 minutos, necesita Internet). Las siguientes veces arranca en segundos.
4. El navegador se abre solo en `http://127.0.0.1:5000`; si el puerto está
   ocupado, usa el `5001`.

El paquete usa **SQLite**, así que no hace falta PostgreSQL ni cargar datos: la
base `instance/vidamarina.db` se crea y se llena con las 46 especies en el primer
arranque. Requiere Windows 10/11 y **Python 3.10+** instalado con la opción
«Add python.exe to PATH».

Cuenta de administrador de la demo local: `admin` / `Admin1234!`
(cámbiala en producción con `ADMIN_PASSWORD`).

Para regenerar el ZIP después de cambiar el código:

```powershell
python scripts/build_local_zip.py
```

El script excluye `.env`, `.venv/`, `instance/`, `.git/`, `__pycache__/`,
`*.pyc`, `*.db` y `dist/`. Más detalles en
[`dist/README.md`](dist/README.md).

## Cuenta de administrador

Se crea en el primer arranque con las variables `ADMIN_USERNAME`, `ADMIN_EMAIL`
y `ADMIN_PASSWORD`. Los valores por defecto para desarrollo son:

| Campo | Valor |
| --- | --- |
| Usuario | `admin` |
| Correo | `admin@vidamarina.ve` |
| Contraseña | `Admin1234!` |

**Cámbiala en producción** definiendo `ADMIN_PASSWORD` en el panel de Render
antes del primer despliegue. Las contraseñas se guardan con hash, nunca en texto
plano.

## Rutas principales

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/` | Catálogo con búsqueda, filtros y orden. |
| GET | `/especie/<id>` | Ficha completa de una especie. |
| GET | `/mapa` | Mapa interactivo. |
| GET | `/fuentes` | Fuentes, licencias y créditos. |
| GET | `/api/especies?q=&region=&grupo=&orden=` | API JSON del catálogo. |
| GET/POST | `/cuenta/registro` | Crear cuenta. |
| GET/POST | `/cuenta/entrar` | Iniciar sesión. |
| POST | `/cuenta/salir` | Cerrar sesión (CSRF). |
| GET | `/admin/` | Panel de administración (solo admin). |
| GET/POST | `/admin/nueva` | Crear especie. |
| GET/POST | `/admin/<id>/editar` | Editar especie. |
| POST | `/admin/<id>/eliminar` | Eliminar especie (CSRF). |

## Modelo de datos

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        bool is_admin
        datetime created_at
    }

    SPECIES {
        int id PK
        string common_name
        string scientific_name UK
        string group
        string region
        string habitat
        text description
        string iucn_status
        int iucn_year
        int described_year
        string image_url
        string image_author
        string image_license
        string source_url
        float map_lat
        float map_lng
        string map_label
        string search_key
        datetime created_at
        datetime updated_at
    }
```

`search_key` se recalcula automáticamente en cada `INSERT`/`UPDATE` (evento de
SQLAlchemy) y guarda el texto normalizado que usa la búsqueda. Así la búsqueda
sin tildes es una simple consulta `LIKE` parametrizada, sin funciones específicas
de cada motor de base de datos.

## Datos y fuentes

- **46 especies**: 30 del Caribe, 14 de ríos y 2 de ambas regiones.
- **36** con estado UICN real; el resto queda como `NE` (no evaluado).
- **44** con año de descripción científica.
- **46** con fotografía, autor y licencia.

Fuentes: Wikipedia en español (textos, CC BY-SA 4.0), Wikidata (UICN, año de
descripción e imágenes, CC0), Wikimedia Commons (fotografías con su licencia
individual), Lista Roja de la UICN, OpenStreetMap (ODbL) y Leaflet (BSD-2).

Los datos se generan una sola vez con `scripts/build_dataset.py` y quedan
guardados en `data/species.json`; la aplicación **no depende de Internet** para
mostrar el catálogo. En la página `/fuentes` se muestran los créditos.

## Pruebas automáticas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las 13 pruebas cubren: carga del catálogo, búsqueda sin tildes, filtro por
región, orden por rareza, ficha de especie, mapa, API JSON, 404, registro +
login, control de acceso al panel, CRUD de especies y hash de contraseñas.

## Despliegue público (Render + Neon)

La app necesita dos servicios gratuitos: **Neon** (PostgreSQL) y **Render**
(servidor web). El repositorio ya incluye `render.yaml` para desplegar con un
clic.

### 1. Subir el código a GitHub

```powershell
git init
git add .
git commit -m "Vida Marina VE: catálogo de especies con Flask"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/vidamarina-ve.git
git push -u origin main
```

Crea antes el repositorio vacío en <https://github.com/new> (sin README ni
`.gitignore`, para evitar conflictos). Git Credential Manager abrirá el navegador
para autenticarte la primera vez.

### 2. Crear la base de datos en Neon

1. Regístrate en <https://neon.tech> con tu cuenta de GitHub.
2. Crea un proyecto (región `AWS us-east-1` o la más cercana).
3. Copia la **connection string** (`postgresql://usuario:clave@host/db?sslmode=require`).

No necesitas crear tablas: la app ejecuta `db.create_all()` y carga el catálogo
al arrancar.

### 3. Desplegar en Render

1. Regístrate en <https://render.com> con GitHub.
2. **New → Blueprint** y elige el repositorio. Render leerá `render.yaml`.
3. Cuando pida las variables marcadas con `sync: false`:
   - `DATABASE_URL`: la cadena de conexión de Neon.
   - `ADMIN_PASSWORD`: la contraseña que quieras para el administrador.
4. Deploy. Al terminar tendrás una URL como
   `https://vidamarina-ve.onrender.com`.

> El plan gratuito de Render suspende el servicio tras unos minutos sin visitas;
> la primera carga puede tardar ~30 segundos. Es normal.

### 4. Verificar

- Abre la URL y comprueba que aparecen las 46 especies.
- Entra con el usuario `admin` y la contraseña que definiste.
- Prueba `/mapa`, `/api/especies?q=delfin` y una ficha.

## Guion para la defensa

1. **Portada**: explicar el objetivo (catálogo de biodiversidad acuática
   venezolana) y las dos regiones: Caribe y cuencas del Orinoco.
2. **Búsqueda**: escribir `delfin` sin tilde y mostrar que encuentra los tres
   delfines. Explicar la normalización de texto y `search_key`.
3. **Filtros**: elegir «Ríos y aguas dulces» + «Rareza (estado UICN)» y mostrar
   que el primero es el Caimán del Orinoco (`CR`).
4. **Ficha**: abrir una especie, mostrar imagen con licencia, ficha técnica,
   enlace a Wikipedia y mini-mapa.
5. **Mapa**: filtrar por región, hacer clic en un marcador y abrir la ficha.
6. **Cuentas**: registrarse, cerrar sesión y volver a entrar. Mostrar que la
   contraseña se guarda con hash (se puede enseñar la tabla `users`).
7. **Panel admin**: crear una especie, editarla y eliminarla.
8. **Backend**: enseñar `models.py`, `routes/`, el diagrama ER y ejecutar las
   pruebas (`python -m unittest discover -s tests -v`).
9. **Despliegue**: explicar Render + Neon y que la base es PostgreSQL en
   producción y SQLite en local, sin cambiar el código.

## Decisiones de seguridad

- Contraseñas con `generate_password_hash` / `check_password_hash` (scrypt).
- Todas las consultas usan el ORM de SQLAlchemy con parámetros: no hay SQL
  construido por concatenación, por lo que no hay inyección SQL.
- Formularios con **CSRF** en Flask-WTF y en los `POST` manuales (logout,
  eliminar especie).
- Validación de entrada en servidor (longitudes, email, rangos numéricos).
- Escapado automático de Jinja2 en todas las plantillas.
- Redirección `next` restringida a rutas internas (evita *open redirect*).
- Cookies `HttpOnly` y `SameSite=Lax`.
- `SECRET_KEY`, `DATABASE_URL` y credenciales fuera del repositorio (`.env` y
  variables de Render). `.env` está en `.gitignore`.
- Límite de 2 MB por formulario (`MAX_CONTENT_LENGTH`).
- Panel admin protegido por `login_required` + verificación de `is_admin`.

## Limitaciones conocidas

- `iucn_year` aparece como «—» porque Wikidata no incluye el año de evaluación
  como calificador en la mayoría de los taxones.
- Dos especies no tienen año de descripción en Wikidata: Barracuda
  (`Sphyraena barracuda`) y Caimán del Orinoco (`Crocodylus intermedius`).
- Diez especies figuran como `NE` (no evaluadas) porque Wikidata no tiene su
  estado UICN.
- Las imágenes se enlazan desde Wikimedia Commons; si Commons cambia una ruta,
  la tarjeta usa una imagen SVG de respaldo.
- El plan gratuito de Render suspende la instancia por inactividad.

---

Proyecto individual de **Electiva 3 · Programación 3**. Datos de biodiversidad
con fines académicos; cada imagen conserva su licencia original.
