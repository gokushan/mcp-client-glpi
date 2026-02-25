# Guía de Ejecución

Esta guía explica cómo levantar el cliente MCP en diferentes entornos.

## Requisitos Previos
- Python 3.10 o superior.
- El servidor MCP de GLPI debe estar accesible en la red.
- Archivo `.env` configurado (puedes copiar el `.env.example`).

---

### A. Configuración inicial (Solo la primera vez)
1. **Crear entorno virtual:**
   ```bash
   python3 -m venv .venv
   ```
2. **Instalar dependencias (Modo Editable):**
   ```bash
   .venv/bin/pip install -e .
   ```
   *El modo editable (`-e`) permite que los cambios en el código se reflejen al instante y añade el proyecto al path de Python de forma permanente en este entorno virtual.*

### B. Ejecución diaria (Desarrollo)
Una vez configurado, el entorno virtual ya reconoce la carpeta `src`. Solo necesitas ejecutar:
```bash
.venv/bin/uvicorn src.infrastructure.adapters.web.fastapi_app:app --reload --port 8000
```

## 2. Ejecución Standalone (Producción local)
Para ejecutar la aplicación como un proceso único estable.

```bash
.venv/bin/python -m src.main
```

## 3. Ejecución con Docker (Contenedor individual)
Si prefieres no instalar dependencias en tu máquina local.

1. **Construir la imagen:**
   ```bash
   docker build -t mcp-client-glpi .
   ```
2. **Ejecutar el contenedor:**
   ```bash
   docker run -p 8000:8000 --env-file .env mcp-client-glpi
   ```

## 4. Ejecución con Docker Compose (Recomendado)
Para gestionar el ciclo de vida, nombres y versiones de forma automática.

```bash
docker compose up -d
```
*Para ver los logs después de subirlo:* `docker compose logs -f mcp-client-glpi`
