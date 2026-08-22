@echo off
cd /d "%~dp0"
echo ============================================
echo   GUARDAR Y SUBIR CAMBIOS A GIT
echo ============================================
set "MSG="
set /p MSG=Escribe un mensaje para el cambio (Enter = automatico): 
if "%MSG%"=="" set "MSG=actualizacion automatica"
echo.
echo Guardando todos los archivos...
git add .
git commit -m "%MSG%"
echo.
echo Subiendo a GitHub...
git push
if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo subir. Configura tu remoto con:
    echo         git remote add origin https://github.com/TU-USUARIO/NUAM-ANTO.git
)
echo.
pause
