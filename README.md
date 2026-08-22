# NUAM — Mantenedor de Calificaciones Tributarias

Sistema web construido **100% en Python (venv) + Flask** con base de datos **MongoDB**, para que corredores de bolsa busquen, creen, modifiquen, eliminen y carguen en forma masiva calificaciones tributarias (DJ 1949 homologada a DJ 1922), con trazabilidad completa.

## Requisitos

- Python 3.10+ ([python.org](https://www.python.org/downloads/))
- MongoDB instalado y corriendo en `127.0.0.1:27017`

## Pasos a seguir

### 1. Instalar dependencias

Doble clic en `requerimientos.bat` (crea el venv si falta e instala todo), o manualmente:

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
```

### 2. Iniciar el sistema

Doble clic en `iniciar.bat`, o manualmente:

```powershell
.\venv\Scripts\python.exe app.py
```

Se abre solo el navegador en **http://127.0.0.1:5000**.
La primera vez la base de datos se crea y se siembran 5 registros de ejemplo automáticamente.

### 3. Iniciar sesión

| Correo | Clave |
|--------|-------|
| `ADMIN@mail.com` | `1234` |

### 4. Detener el servidor

Cierra la ventana o presiona `Ctrl + C`.

## Funcionalidades

- **Consultar calificaciones**: filtros por mercado (ACC/CFI/FMU), origen y ejercicio; grilla de resultados.
- **Ingresar / Modificar**: formulario completo; los factores tributarios (columnas 8–37) se recalculan automáticamente al guardar.
- **Eliminar**: con confirmación.
- **Carga masiva**: líneas CSV (`ejercicio, mercado, instrumento, fecha, secuenciaEvento, dividendo, valorHistorico, descripcion, isfut, factorActualizacion, origen`) con resumen insertados/errores por fila.
- **Trazabilidad**: bitácora de auditoría de cada acción (crear/modificar/eliminar/carga masiva).

## Reglas tributarias implementadas

- Factor de columna i: `factor = round8((dividendo × peso_i) / (valor_historico × actualización))`, clampeado a [0, 1].
- Pesos: `peso_i = 0.96^i` (i = 0..29) normalizados, redondeados a 8 decimales.
- `round8`: redondeo al 8vo decimal sin artefactos de coma flotante.
- Valor de referencia verificado: CMPC → factor columna 9 = **0.0052214**.

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/calificaciones?mercado=&origen=&ejercicio=` | Lista con filtros opcionales |
| POST | `/api/calificaciones` | Crear (201) · errores 400 `{"errores":[]}` |
| PUT | `/api/calificaciones/<id>` | Modificar (200) · 404 si no existe |
| DELETE | `/api/calificaciones/<id>` | Eliminar (204) · 404 si no existe |
| GET | `/api/calificaciones/catalogos` | Ejercicios disponibles sin duplicados |
| GET | `/api/calificaciones/auditoria` | Bitácora, más recientes primero |
| POST | `/api/calificaciones/masiva` | Carga masiva `{"lineas":[...]}` |

## Estructura del proyecto

```
NUAM-ANTO/
├── venv/                 # Entorno virtual
├── app.py                # Servidor Flask (puerto 5000) + API REST
├── db.py                 # Conexión MongoDB, índice único, seed inicial
├── dominio/
│   ├── factores.py       # Lógica tributaria pura (pesos, round8, factores)
│   └── validadores.py    # Validaciones de negocio (mensajes exactos)
├── templates/index.html  # Interfaz SPA (login + pantallas)
├── static/css/estilos.css
├── static/js/app.js      # Navegación por estado, fetch a la API
├── static/img/avatar.svg
├── iniciar.bat           # Activa venv, prepara BD y levanta servidor
├── requerimientos.bat    # Instala dependencias del venv
├── _actualizar.bat       # Atajo: git pull
├── _save.bat             # Atajo: git add + commit + push
├── _tests.py             # Pruebas de criterios de aceptación
└── requirements.txt
```

## Paleta de colores

| Color | Hex | Uso |
|-------|-----|-----|
| Antracita | `#2C3539` | Textos y títulos |
| Terracota | `#E64A19` | Acentos, tab superior, botones, ítems activos |
| Marfil | `#F7F8F7` | Fondos de tarjetas/sidebar |
| Blanco | `#FFFFFF` | Fondos de contenido |
| Borde | `#DDE2E5` | Bordes |
| Gris suave | `#5A666B` | Textos secundarios |
| Fondo pantalla | `#ECEFF1` | Fondo general |
| Rojo eliminar | `#C62828` | Solo eventos de eliminación |

## Pruebas

```powershell
.\venv\Scripts\python.exe _tests.py
```

Verifica los criterios de aceptación: redondeo exacto, factor CMPC = 0.0052214, catálogos `[2022, 2023, 2024]`, mensajes de validación exactos, CRUD con auditoría y carga masiva.
