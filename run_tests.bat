@echo off
echo 🧪 EJECUTANDO SUITE DE TESTS
echo =============================

if exist "venv" (
    call venv\Scripts\activate.bat
)

python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando pytest...
    pip install pytest
)

echo 🔍 Ejecutando tests...
python -m pytest tests/ -v

echo Tests completados
pause
