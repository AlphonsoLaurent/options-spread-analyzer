@echo off
echo 🚀 EJECUTANDO OPTIONS SPREAD STRATEGY ANALYZER
echo ===============================================

if not exist "venv" (
    echo ❌ Entorno virtual no encontrado. Ejecuta setup_dev.bat primero
    pause
    exit /b 1
)

echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

echo ✅ Entorno verificado
echo 📊 Options Spread Strategy Analyzer
echo 🌐 La aplicación se abrirá en tu navegador
echo 🔗 URL: http://localhost:8501
echo ⏹️  Para detener: Ctrl+C

echo 🚀 Iniciando aplicación...
python -m streamlit run src/options_analyzer/main.py

echo 📴 Aplicación cerrada
pause
