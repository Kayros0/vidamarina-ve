# Dataset de especies

`species.json` es la fuente de datos que la aplicación carga en la base de datos
la primera vez que arranca (ver `app/seed.py`). No se consulta en tiempo de
ejecución: la web funciona aunque Wikipedia esté caída.

## Estructura

Cada registro tiene estos campos:

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `common_name` | texto | Nombre común en español. |
| `scientific_name` | texto | Nombre científico (único). |
| `group` | texto | `pez`, `mamifero`, `reptil`, `invertebrado` o `ave`. |
| `region` | texto | `caribe`, `rios` o `ambas`. |
| `habitat` | texto | Hábitat principal. |
| `description` | texto | Extracto descriptivo de Wikipedia. |
| `iucn_status` | texto | Código de la Lista Roja: `CR`, `EN`, `VU`, `NT`, `LC`, `DD` o `NE`. |
| `iucn_year` | entero o `null` | Año de evaluación UICN (normalmente no disponible en Wikidata). |
| `described_year` | entero o `null` | Año de descripción científica del taxón. |
| `image_url` | texto o `null` | Imagen en Wikimedia Commons. |
| `image_author` | texto o `null` | Autor de la fotografía. |
| `image_license` | texto o `null` | Licencia de la fotografía. |
| `source_url` | texto | Artículo de Wikipedia usado como fuente. |
| `map_lat`, `map_lng` | número o `null` | Punto de referencia en el mapa. |
| `map_label` | texto o `null` | Nombre del lugar de referencia. |

## Cómo se regenera

```powershell
.\.venv\Scripts\python.exe scripts\build_dataset.py
.\.venv\Scripts\python.exe scripts\inspect_dataset.py   # resumen de control
```

El script consulta las APIs públicas de Wikipedia (extractos), Wikidata (UICN,
año de descripción, imágenes) y Wikimedia Commons (autor y licencia). Respeta
los límites de las APIs con lotes de 20 títulos y reintentos ante HTTP 429.

> Si cambias el JSON después de que la base ya tiene especies, la app **no**
> vuelve a cargarlo: el seed solo actúa con la tabla vacía. Borra
> `instance/vidamarina.db` para forzar una recarga local.
