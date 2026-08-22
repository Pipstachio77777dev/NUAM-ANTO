@echo off
cd /d "%~dp0"
echo ============================================
echo   NUAM - Preparando dependencias del venv
echo ============================================
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo [OK] Dependencias instaladas. Ahora puedes usar iniciar.bat
pause
