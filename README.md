# 📊 Options Spread Strategy Analyzer

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Un analizador profesional de estrategias de opciones con sistema de paper trading integrado.

## 🚀 Instalación Rápida

### Windows (Un Solo Comando)
```cmd
cd options-spread-analyzer
setup_dev.bat
run_app.bat
```

### Linux/macOS
```bash
cd options-spread-analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/options_analyzer/main.py
```

## ✨ Características

- 📊 **Análisis Completo**: Bull Call, Iron Condor, Bear Put Spreads
- 💼 **Paper Trading**: Sistema de simulación completo
- 📈 **Visualizaciones**: Gráficos interactivos con Plotly
- 🔄 **Datos Reales**: Integración con Yahoo Finance
- 🧪 **Testing**: Suite completa de pruebas

## 🖥️ Scripts Windows

| Script | Función |
|--------|---------|
| `setup_dev.bat` | Configuración completa |
| `run_app.bat` | Ejecutar aplicación |
| `run_tests.bat` | Ejecutar pruebas |
| `check_environment.bat` | Verificar entorno |

## 📊 Uso Básico

1. **Ejecutar**: `run_app.bat`
2. **Navegar a**: http://localhost:8501
3. **Análisis**: Ir a página "Análisis"
4. **Configurar**: Símbolo + estrategia + parámetros
5. **Analizar**: Ver resultados y gráficos

## 🏗️ Estructura

```
src/options_analyzer/
├── core/              # Lógica de negocio
├── data/              # Acceso a datos
├── ui/                # Interfaz Streamlit
├── visualization/     # Gráficos
└── config/           # Configuración
```

## ⚠️ Disclaimer

Solo para fines educativos. No constituye asesoramiento financiero.

## 📄 Licencia

MIT License - Ver LICENSE para detalles.
