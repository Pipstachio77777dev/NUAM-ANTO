@echo off
cd /d "%~dp0"
echo ============================================
echo   NUAM - Iniciando servidor Flask
echo ============================================
if not exist "venv\Scripts\python.exe" (
    echo [INFO] No existe el venv. Ejecuta primero requerimientos.bat
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python -c "import db, dominio.factores; db.init_db(dominio.factores.calcular_factores)"
python app.py
pause
