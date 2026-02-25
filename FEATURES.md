# Funcionalidades y Pruebas

Este documento detalla las funcionalidades disponibles en el cliente MCP y cómo probar cada una de ellas utilizando `curl`.

## 1. Verificación de Estado (Health Check)

Este endpoint realiza un "Deep Health Check". No solo confirma que la API está funcionando, sino que también intenta verificar la conectividad con el servidor MCP y lista las herramientas disponibles.

### Cómo probar:
```bash
curl -X GET http://localhost:8000/healthcheck
```

### Respuesta esperada (Éxito):
```json
{
  "status": "ok",
  "mcp_server": {
    "connected": true,
    "url": "http://...",
    "available_tools": ["tool_batch_contracts", "..."]
  }
}
```

---

## 2. Listado de Herramientas (Tools)

Devuelve la lista completa de herramientas que el servidor MCP tiene publicadas. Es útil para verificar qué capacidades tiene el servidor en ese momento.

### Cómo probar:
```bash
curl -X GET http://localhost:8000/tools
```

### Respuesta esperada:
```json
{
  "tools": [
    {
      "name": "tool_batch_contracts",
      "description": "...",
      "inputSchema": { ... }
    }
  ]
}
```

---

## 3. Consulta de Carpetas (Folders Info)

Este endpoint consulta al servidor MCP las rutas físicas en el host de las carpetas de trabajo.

### Cómo probar:
```bash
curl -X GET http://localhost:8000/folders
```

### Respuesta esperada:
```json
{
  "input_folders": ["/ruta/host/entrada"],
  "processed_folder": "/ruta/host/procesado",
  "error_folder": "/ruta/host/error"
}
```

---

## 4. Procesamiento de Contratos (Process Contracts)

Este es el endpoint principal de negocio. Ejecuta el procesamiento por lotes de contratos en el servidor MCP configurado.

### Cómo probar:
```bash
curl -X POST http://localhost:8000/processcontract
```

### Notas:
- Este endpoint mapea internamente a la herramienta configurada en `.env` (variable `mcp_tool_name`, por defecto `tool_batch_contracts`).
- No requiere parámetros adicionales en el cuerpo de la petición actualmente, ya que el servidor MCP gestiona el origen de los archivos según su propia configuración.

### Respuesta esperada:
```json
{
  "results": [
    {
      "file": "contrato_1.pdf",
      "status": "success",
      "contract_id": 123,
      ...
    }
  ],
  "summary_text": "Procesamiento completado con éxito..."
}
```

---

## Resumen de Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/healthcheck` | Estado del cliente y conexión con el servidor MCP. |
| `GET` | `/tools` | Lista de herramientas disponibles en el servidor. |
| `GET` | `/folders` | Rutas de carpetas (entrada, procesados, errores) en el host. |
| `POST` | `/processcontract` | Ejecuta el procesamiento de contratos. |
