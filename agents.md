# 🤖 AGENT_CONTEXT: GLPI MCP Client

Si eres un modelo de IA interactuando con este proyecto, este documento te ayudará a entender tu entorno, el flujo de trabajo y cómo este cliente se comunica con el servidor mcp-server.

## 📝 Resumen del Proyecto
El **mcp-client** es una aplicación FastAPI que actúa como un orquestador y cliente para el **GLPI MCP Server** (`mcp-server`). Su propósito principal es exponer una interfaz web (REST API) para automatizar el procesamiento de contratos en GLPI.

Este proyecto **no** realiza el procesamiento directamente, sino que delega las tareas pesadas (uso de LLMs, búsqueda en GLPI, etc.) al servidor MCP a través del protocolo Model Context Protocol.

## 🏗️ Arquitectura y Estándares
El cliente está diseñado siguiendo la **Arquitectura Hexagonal** (Puertos y Adaptadores):
- **Dominio (`src/domain/`)**: Define los modelos de datos y las interfaces (puertos) que el sistema necesita.
- **Aplicación (`src/application/`)**: Contiene los casos de uso (`ProcessContractsUseCase`, etc.) que orquestan el flujo entre los endpoints y el cliente MCP.
- **Infraestructura (`src/infrastructure/`)**:
    - **Adaptador Web**: FastAPI expone los endpoints.
    - **Adaptador MCP**: Implementa la comunicación con el `mcp-server` usando *Streamable HTTP*.
    - **Configuración**: Maneja las variables de entorno (`.env`) y la conexión al servidor.

## 🔗 Relación con mcp-server
Este proyecto es el **complemento directo** del `mcp-server`. 
- El `mcp-server` provee las herramientas (tools) para interactuar con GLPI.
- El `mcp-client` consume esas herramientas para automatizar procesos complejos, como el procesamiento por lotes de documentos.
- Generalmente, ambos proyectos residen en directorios hermanos dentro del mismo espacio de trabajo.

## 🛠️ Flujo de Operación
Cuando un usuario (o tú como agente) interactúa con el cliente:
1. Se recibe una petición en un endpoint de FastAPI (ej, `/processcontract`).
2. El cliente instancia un **Caso de Uso**.
3. El Caso de Uso utiliza el **Adaptador MCP** para llamar a una herramienta específica en el `mcp-server` (ej, `tool_batch_contracts`).
4. El cliente espera la respuesta estructurada del servidor y la devuelve al usuario de forma "pretty-printed".

## 📁 Configuración y Rutas
- La URL del servidor MCP se configura en la variable `MCP_SERVER_URL` del archivo `.env`.
- El cliente debe tener permisos de acceso a las carpetas de entrada/salida para informar correctamente sobre su estado, aunque la operación real sobre archivos la realiza el servidor.

## ⚠️ Manejo de Errores
El cliente propaga los códigos de error estandarizados desde el `mcp-server`:
- **105**: LLM Timeout o sesión cancelada (común si Ollama está saturado).
- Otros errores (100-104) relacionados con permisos de archivos y rutas.

## 📚 Documentación de Referencia
- `ARCHITECTURE.md`: Estructura detallada de las capas del proyecto.
- `FEATURES.md`: Guía de endpoints y ejemplos de uso con `curl`.
- `README.md`: Instrucciones de instalación y ejecución rápida.

---
*Este documento es la puerta de entrada para cualquier agente de IA que necesite entender cómo orquestar tareas usando este cliente mcp-client.*
