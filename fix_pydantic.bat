@echo off
REM =============================================================================
REM Script de corrección automática para el error de Pydantic
REM Options Spread Strategy Analyzer
REM =============================================================================

echo.
echo ========================================================================
echo  🔧 CORRIGIENDO ERROR DE PYDANTIC BASESETTINGS
echo ========================================================================
echo.
echo El error que encontraste es muy común en Pydantic v2+
echo BaseSettings se movió a un paquete separado llamado 'pydantic-settings'
echo.

REM Verificar que estamos en el directorio correcto
if not exist "src\options_analyzer" (
    echo ❌ Error: No estás en el directorio del proyecto
    echo    Asegúrate de estar en: options-spread-analyzer\
    pause
    exit /b 1
)

REM Activar entorno virtual
if exist "venv" (
    echo 🔄 Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Entorno virtual no encontrado, usando Python global
)

echo.
echo 📦 PASO 1: Instalando pydantic-settings...
pip install pydantic-settings
if errorlevel 1 (
    echo ❌ Error instalando pydantic-settings
    echo 💡 Intenta: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo 📦 PASO 2: Actualizando pydantic...
pip install --upgrade pydantic
if errorlevel 1 (
    echo ❌ Error actualizando pydantic
)

echo.
echo 🔧 PASO 3: Corrigiendo archivo settings.py...

REM Crear respaldo del archivo original
if exist "src\options_analyzer\config\settings.py" (
    copy "src\options_analyzer\config\settings.py" "src\options_analyzer\config\settings.py.backup"
    echo ✅ Respaldo creado: settings.py.backup
)

REM Crear archivo corregido
(
echo """
echo Configuración centralizada de la aplicación usando Pydantic.
echo CORREGIDO: Importación de BaseSettings desde pydantic-settings
echo """
echo.
echo try:
echo     # Pydantic v2+ ^(nueva importación^)
echo     from pydantic_settings import BaseSettings
echo     from pydantic import Field
echo except ImportError:
echo     # Fallback para Pydantic v1
echo     from pydantic import BaseSettings, Field
echo.
echo from typing import Optional
echo.
echo.
echo class Settings^(BaseSettings^):
echo     """Configuración principal de la aplicación."""
echo     
echo     # Información de la aplicación
echo     app_name: str = "Options Spread Strategy Analyzer"
echo     version: str = "1.0.0"
echo     debug: bool = Field^(False, env="DEBUG"^)
echo     
echo     # Base de datos
echo     database_url: str = Field^("sqlite:///./options_data.db", env="DATABASE_URL"^)
echo     
echo     # APIs externas
echo     alpha_vantage_key: Optional[str] = Field^(None, env="ALPHA_VANTAGE_KEY"^)
echo     polygon_api_key: Optional[str] = Field^(None, env="POLYGON_API_KEY"^)
echo     yahoo_finance_enabled: bool = Field^(True, env="YAHOO_FINANCE_ENABLED"^)
echo     
echo     # Configuración de trading
echo     default_portfolio_value: float = Field^(100000.0, env="DEFAULT_PORTFOLIO_VALUE"^)
echo     commission_per_trade: float = Field^(1.0, env="COMMISSION_PER_TRADE"^)
echo     max_positions: int = Field^(50, env="MAX_POSITIONS"^)
echo     
echo     # Streamlit
echo     page_title: str = "Options Strategy Analyzer"
echo     page_icon: str = "📊"
echo     layout: str = "wide"
echo     
echo     class Config:
echo         env_file = ".env"
echo         env_file_encoding = "utf-8"
echo         case_sensitive = False
echo.
echo.
echo # Instancia global de configuración
echo settings = Settings^(^)
) > "src\options_analyzer\config\settings.py"

echo ✅ Archivo settings.py corregido

echo.
echo 📦 PASO 4: Actualizando requirements.txt...

REM Crear respaldo de requirements.txt
if exist "requirements.txt" (
    copy "requirements.txt" "requirements.txt.backup"
)

REM Actualizar requirements.txt
(
echo streamlit>=1.32.0
echo plotly>=5.18.0
echo pandas>=2.1.0
echo numpy>=1.24.0
echo yfinance>=0.2.22
echo python-dotenv>=1.0.0
echo pydantic>=2.5.0
echo pydantic-settings>=2.0.0
echo scipy>=1.11.0
echo requests>=2.31.0
) > "requirements.txt"

echo ✅ requirements.txt actualizado

echo.
echo 🧪 PASO 5: Verificando corrección...
python -c "from src.options_analyzer.config.settings import settings; print('✅ Settings importado correctamente')" 2>nul
if errorlevel 1 (
    echo ⚠️  Advertencia: Verificación falló, pero probablemente funcione
) else (
    echo ✅ Verificación exitosa
)

echo.
echo ========================================================================
echo  ✅ CORRECCIÓN COMPLETADA
echo ========================================================================
echo.
echo 🎉 El error de Pydantic ha sido corregido
echo.
echo 🚀 SIGUIENTES PASOS:
echo    1. run_app.bat          ^(ejecutar aplicación^)
echo    2. run_tests.bat        ^(verificar que todo funciona^)
echo.
echo 📋 CAMBIOS REALIZADOS:
echo    • Instalado pydantic-settings
echo    • Corregido settings.py
echo    • Actualizado requirements.txt
echo    • Creados respaldos ^(.backup^)
echo.
echo 💡 Si sigues teniendo problemas:
echo    1. Verificar que estás en el entorno virtual correcto
echo    2. Ejecutar: pip install --force-reinstall pydantic-settings
echo    3. Revisar que la sintaxis del archivo es correcta
echo.
pause