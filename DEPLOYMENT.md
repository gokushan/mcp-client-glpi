# Despliegue con Docker Compose

Docker Compose es la forma recomendada de desplegar el cliente MCP, especialmente si forma parte de un ecosistema de microservicios.

## Configuración

El archivo `docker-compose.yml` en la raíz del proyecto está configurado para:
- Construir la imagen localmente usando el `Dockerfile`.
- Mapear el puerto `8000` del contenedor al host.
- Cargar las variables de entorno desde el archivo `.env`.

## Comandos de Despliegue

### Levantar el servicio
Para iniciar el cliente en segundo plano:
```bash
docker compose up -d
```

### Ver logs
Para monitorizar la salida del cliente:
```bash
docker compose logs -f mcp-client-glpi
```

### Detener el servicio
```bash
docker compose down
```

### Aplicar cambios en Variables de Entorno (.env)
Si modificas el archivo `.env`, puedes aplicar los cambios recreando el contenedor sin necesidad de reconstruir la imagen:
```bash
docker compose up -d
```

### Re-construir tras cambios en el Código
Si realizas modificaciones en el código fuente de la aplicación, debes forzar la reconstrucción de la imagen:
```bash
docker compose up -d --build
```

---

## Variables de Entorno Críticas
Asegúrate de que tu archivo `.env` contenga los valores correctos antes de levantar el compose:

- `MCP_SERVER_URL`: Dirección completa del servidor MCP (ej. `http://192.168.1.10:8081/mcp`).
- `APP_PORT`: Puerto donde escuchará FastAPI (por defecto `8000`).
- `APP_VERSION`: Versión de la aplicación (por defecto `0.1.0`).
- `LOG_LEVEL`: Nivel de detalle de los logs (ej. `INFO`, `DEBUG`, `ERROR`).
- `mcp_initialize_on_startup`: `True` para validar la conexión al arrancar.
