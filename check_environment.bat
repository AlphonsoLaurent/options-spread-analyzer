@echo off
echo 🔍 VERIFICANDO ENTORNO
echo ======================

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado
) else (
    echo ✅ Python OK
    python --version
)

if exist "venv" (
    echo ✅ Entorno virtual OK
    call venv\Scripts\activate.bat
) else (
    echo ❌ Entorno virtual no encontrado
)

python -c "import streamlit; print('✅ Streamlit OK')" 2>nul || echo ❌ Streamlit faltante
python -c "import pandas; print('✅ Pandas OK')" 2>nul || echo ❌ Pandas faltante
python -c "import numpy; print('✅ NumPy OK')" 2>nul || echo ❌ NumPy faltante

if exist "src\options_analyzer\main.py" (echo ✅ Módulo principal OK) else (echo ❌ main.py faltante)

echo Verificación completada
pause
