# Guía de Contribución

## Cómo Contribuir

1. Fork el repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Desarrollo

```bash
# Configurar entorno
setup_dev.bat  # Windows
python scripts/setup_dev.py  # Linux/macOS

# Ejecutar tests
run_tests.bat  # Windows
python -m pytest  # Linux/macOS

# Linting
python -m ruff check .
python -m black .
```

## Estándares

- Python 3.9+
- PEP 8 compliance
- Type hints requeridos
- Tests para nuevo código
- Documentación actualizada
