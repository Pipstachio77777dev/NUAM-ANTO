@echo off
cd /d "%~dp0"
echo ============================================
echo   ACTUALIZAR: descargando cambios de Git...
echo ============================================
git pull
if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo actualizar. Revisa la conexion o el repositorio remoto.
)
echo.
pause
