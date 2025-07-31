# Guía de Instalación

## Requisitos
- Python 3.9+
- 4GB RAM
- 2GB espacio libre

## Windows
1. Ejecutar `setup_dev.bat`
2. Ejecutar `run_app.bat`

## Linux/macOS
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `streamlit run src/options_analyzer/main.py`

## Verificación
- Ejecutar `check_environment.bat` (Windows)
- Verificar http://localhost:8501 funciona
