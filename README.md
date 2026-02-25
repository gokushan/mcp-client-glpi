# Cliente MCP GLPI

Este proyecto es un cliente basado en FastAPI diseñado para interactuar con el servidor MCP (Model Context Protocol) de GLPI.

## Documentación General

Para facilitar el uso y mantenimiento del proyecto, consulta los siguientes documentos:

- **[Guía de Ejecución](RUNNING.md)**: Cómo levantar el entorno virtual, instalar dependencias y ejecutar la app.
- **[Funcionalidades y Pruebas](FEATURES.md)**: Listado de endpoints disponibles y ejemplos de `curl` para probarlos.
- **[Arquitectura](ARCHITECTURE.md)**: Detalles sobre el diseño basado en arquitectura hexagonal y puertos/adaptadores.
- **[Despliegue con Docker](DEPLOYMENT.md)**: Instrucciones para entornos de producción y contenedores.

## Inicio Rápido

1. Crea tu archivo `.env` basado en `.env.example`.
2. Instala el proyecto en modo editable:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -e .
   ```
3. Ejecuta la aplicación:
   ```bash
   .venv/bin/uvicorn src.infrastructure.adapters.web.fastapi_app:app --reload
   ```
