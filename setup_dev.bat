@echo off
echo 🔧 CONFIGURANDO ENTORNO DE DESARROLLO
echo ========================================

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.9+ desde python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

echo 📦 Actualizando pip...
python -m pip install --upgrade pip

echo 📦 Instalando dependencias...
pip install -r requirements.txt

echo 📁 Creando directorios...
if not exist "data\cache" mkdir "data\cache"
if not exist "data\trading_data" mkdir "data\trading_data"
if not exist "data\user_portfolios" mkdir "data\user_portfolios"
if not exist "logs" mkdir "logs"

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✅ Archivo .env creado
    )
)

echo ✅ CONFIGURACIÓN COMPLETADA
echo Para ejecutar: run_app.bat
pause
