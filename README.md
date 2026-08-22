# NUAM-ANTO

Proyecto Python con entorno virtual (`venv`) y servidor web Flask que se abre automáticamente en el navegador.

## Requisitos

- Python 3.10 o superior instalado ([python.org](https://www.python.org/downloads/))

## Pasos a seguir

### 1. Activar el entorno virtual

Cada vez que abras una terminal en esta carpeta, activa primero el `venv`:

```powershell
.\venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la ejecución de scripts, usa antes:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 2. Instalar las dependencias

Con el `venv` activado:

```powershell
pip install -r requirements.txt
```

### 3. Ejecutar el servidor

```powershell
python nuam-app.py
```

El navegador se abrirá solo en **http://127.0.0.1:5000**.
Si no se abre, copia esa dirección manualmente en tu navegador.

### 4. Detener el servidor

Presiona `Ctrl + C` en la terminal.

## Estructura del proyecto

```
NUAM-ANTO/
├── venv/             # Entorno virtual (no se sube a Git)
├── _actualizar.bat   # Atajo: git pull
├── _save.bat         # Atajo: git add + commit + push
├── main.py           # Script de prueba básico
├── nuam-app.py       # Servidor web Flask (abre el navegador)
├── requirements.txt  # Dependencias del proyecto
└── .gitignore        # Archivos excluidos de Git
```

## Atajos rápidos (.bat)

Doble clic en estos archivos desde el Explorador:

| Archivo | Qué hace |
|---------|----------|
| `_actualizar.bat` | Descarga los últimos cambios (`git pull`) |
| `_save.bat` | Guarda y sube tus cambios (`git add` + `git commit` + `git push`) |

> `_save.bat` te pedirá un mensaje para describir el cambio. Si presionas Enter usa "actualizacion automatica".

### Configurar GitHub por primera vez

Si aún no conectaste este proyecto con GitHub, ejecuta una sola vez:

```powershell
git remote add origin https://github.com/TU-USUARIO/NUAM-ANTO.git
git push -u origin main
```

## Agregar nuevas dependencias

```powershell
pip install <paquete>
pip freeze > requirements.txt
```
