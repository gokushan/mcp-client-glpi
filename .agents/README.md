# 🤖 Agentes Personalizados del Proyecto GLPI MCP

Este directorio contiene agentes personalizados especializados que pueden ser invocados para tareas específicas en el proyecto. Los agentes están organizados por categoría.

## 📚 Categorías de Agentes

### 🏗️ Development Architecture
- **backend-architect** - Diseña APIs REST, límites de microservicios y esquemas de base de datos. Revisa arquitectura para escalabilidad.
  - Uso: Crear nuevos servicios backend, diseñar APIs, optimizar arquitectura del sistema

### 🔐 Quality & Security
- **security-auditor** - Revisa código para vulnerabilidades, implementa autenticación segura, asegura cumplimiento OWASP.
  - Uso: Auditorías de seguridad, flujos de autenticación, corrección de vulnerabilidades

- **mcp-security-auditor** - Especialista en seguridad de servidores MCP, OAuth 2.1, RBAC y cumplimiento normativo.
  - Uso: Revisar implementaciones MCP, diseñar sistemas de autorización, auditorías de seguridad MCP

### 💻 Language Specialists
- **python-expert** - Escribe código Python idiomático, optimiza rendimiento, implementa patrones de diseño.
  - Uso: Refactorización Python, optimización de código, implementación de características avanzadas

### 🎨 Design & Experience
- **ui-ux-designer** - Diseña interfaces de usuario intuitivas y accesibles. Experto en sistemas de diseño y experiencia de usuario.
  - Uso: Diseño de UI/UX, sistemas de diseño, optimización de experiencia de usuario

### 🔧 Specialized Domains
- **mcp-expert** - Crea integraciones Model Context Protocol y configuraciones de servidor. Especialista en protocolo MCP.
  - Uso: Construir servidores MCP, configurar integraciones, diseñar implementaciones de protocolo

## 🚀 Cómo Usar los Agentes

Los agentes se pueden invocar:

### En Claude Code
Usa el comando `/invoke` seguido del nombre del agente:
```
/invoke backend-architect
/invoke python-expert
/invoke mcp-security-auditor
```

### Invocación Programática
Los agentes están disponibles para el sistema y pueden ser utilizados por Claude automáticamente cuando sea relevante para la tarea.

### Búsqueda de Agentes
Para encontrar el agente adecuado para tu tarea:
- ¿Necesitas revisar seguridad? → **security-auditor** o **mcp-security-auditor**
- ¿Trabajando con Python? → **python-expert**
- ¿Diseñando una API o servicio? → **backend-architect**
- ¿Construyendo un servidor MCP? → **mcp-expert**
- ¿Trabajando en UI/UX? → **ui-ux-designer**

## 📋 Resumen de Agentes Disponibles

| Agente | Categoría | Especialización | Casos de Uso |
|--------|-----------|-----------------|--------------|
| **backend-architect** | Development Architecture | APIs REST, Microservicios, Bases de Datos | Nuevos servicios, diseño de APIs, optimización |
| **security-auditor** | Quality & Security | Seguridad de Aplicaciones, OWASP | Auditorías, autenticación, vulnerabilidades |
| **mcp-security-auditor** | Quality & Security | Seguridad MCP, OAuth 2.1, RBAC | Servidores MCP, autorización, cumplimiento |
| **python-expert** | Language Specialists | Python avanzado, Patrones de Diseño | Refactorización, optimización, características |
| **ui-ux-designer** | Design & Experience | UI/UX, Diseño, Accesibilidad | Interfaces, sistemas de diseño, UX |
| **mcp-expert** | Specialized Domains | Protocol MCP, Integraciones | Servidores MCP, configuraciones, protocolo |

## 🔍 Estructura de Archivos

```
.agents/
├── README.md (este archivo)
├── development-architecture/
│   └── backend-architect.md
├── quality-security/
│   ├── security-auditor.md
│   └── mcp-security-auditor.md
├── language-specialists/
│   └── python-expert.md
├── design-experience/
│   └── ui-ux-designer.md
├── specialized-domains/
│   └── mcp-expert.md
├── rules/
│   └── ejemplo.md
└── workflows/
    └── ejemplo.md
```

## 💡 Tips para Aprovechar los Agentes

1. **Especificidad**: Sé específico en tu descripción del problema o tarea
2. **Contexto**: Proporciona contexto del proyecto y restricciones conocidas
3. **Combinación**: Algunos problemas pueden beneficiarse de múltiples agentes
4. **Iteración**: Los agentes pueden trabajar juntos para refinar soluciones

## 📝 Agregando Nuevos Agentes

Para agregar un nuevo agente personalizado:

1. Crea un archivo `.md` con la estructura:
```yaml
---
name: agent-name
description: Breve descripción del agente
category: category-name
---

Contenido del agente...
```

2. Colócalo en la carpeta de categoría correspondiente dentro de `.agents/`
3. Actualiza este README.md con la información del nuevo agente

---

**Última actualización:** Abril 2026
**Total de agentes:** 6
**Categorías:** 5
