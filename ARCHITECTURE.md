# Arquitectura del Proyecto MCP Client GLPI

Este proyecto sigue los principios de la **Arquitectura Hexagonal** (también conocida como Puertos y Adaptadores) para mantener una separación clara entre la lógica de negocio y las dependencias externas.

## Estructura de Directorios

```text
src/
├── application/          # Casos de Uso (Lógica de aplicación)
├── domain/               # Entidades de negocio y Puertos (Interfaces)
└── infrastructure/       # Adaptadores (Implementaciones técnicas)
    ├── adapters/
    │   ├── mcp/          # Adaptador de cliente MCP (Maneja la comunicación)
    │   └── web/          # Adaptador de entrada (FastAPI)
    └── config.py         # Configuración y variables de entorno
```

## Componentes de la Arquitectura

### 1. Dominio (`src/domain/`)
Es el corazón de la aplicación. No depende de nada externo.
- **`models.py`**: Define las estructuras de datos (Pydantic) que utiliza todo el sistema.
- **`ports.py`**: Contiene las interfaces (Abstract Base Classes) que definen *qué* puede hacer el sistema, sin especificar *cómo*. Ejemplo: `ContractServicePort`.

### 2. Aplicación (`src/application/`)
Orquestra el flujo de datos entre el dominio y la infraestructura.
- **`use_cases.py`**: Contiene los casos de uso específicos. Cada clase representa una acción que el usuario puede realizar (ej. `ProcessContractsUseCase`). Estos dependen de los Puertos, no de los Adaptadores.

### 3. Infraestructura (`src/infrastructure/`)
Contiene los detalles técnicos y las implementaciones de los puertos.
- **Adaptador MCP (`src/infrastructure/adapters/mcp/client.py`)**: Implementa el puerto `ContractServicePort`. Sabe cómo hablar con el servidor MCP usando el transporte *Streamable HTTP*.
- **Adaptador Web (`src/infrastructure/adapters/web/fastapi_app.py`)**: Es el punto de entrada al sistema. Define los endpoints de FastAPI y llama a los Casos de Uso correspondientes.
- **Configuración (`src/infrastructure/config.py`)**: Centraliza el acceso a las variables de entorno usando `pydantic-settings`.

## Flujo de una petición
1. Una petición HTTP llega a **`fastapi_app.py`**.
2. El controlador instancia un **Caso de Uso** inyectándole el **Adaptador MCP** correspondiente.
3. El Caso de Uso ejecuta la lógica llamando a los métodos del **Puerto**.
4. El Adaptador MCP transforma la petición en una llamada de red al servidor externo y devuelve el resultado.
