# 🔗 Integración de Agentes en Claude

Este documento explica cómo integrar los agentes personalizados del proyecto de forma global en Claude Code y Claude Desktop.

## 📱 Claude Code (CLI)

### Opción 1: Configuración Local (Proyecto)
Los agentes están disponibles localmente en este proyecto. Para usarlos en Claude Code:

```bash
cd /home/gokushan/mcp-project

# Los agentes se cargan automáticamente desde .agents/
# Puedes invocarlos directamente en la sesión
```

### Opción 2: Configuración Global (Sistema)

Para que los agentes estén disponibles globalmente en Claude Code, crea o edita:

**`~/.claude/agents.json`** (o la ruta de configuración de Claude Code)

```json
{
  "agents": [
    {
      "path": "/home/gokushan/mcp-project/.agents/development-architecture/backend-architect.md",
      "name": "backend-architect",
      "category": "development-architecture"
    },
    {
      "path": "/home/gokushan/mcp-project/.agents/quality-security/security-auditor.md",
      "name": "security-auditor",
      "category": "quality-security"
    },
    {
      "path": "/home/gokushan/mcp-project/.agents/quality-security/mcp-security-auditor.md",
      "name": "mcp-security-auditor",
      "category": "quality-security"
    },
    {
      "path": "/home/gokushan/mcp-project/.agents/language-specialists/python-expert.md",
      "name": "python-expert",
      "category": "language-specialists"
    },
    {
      "path": "/home/gokushan/mcp-project/.agents/design-experience/ui-ux-designer.md",
      "name": "ui-ux-designer",
      "category": "design-experience"
    },
    {
      "path": "/home/gokushan/mcp-project/.agents/specialized-domains/mcp-expert.md",
      "name": "mcp-expert",
      "category": "specialized-domains"
    }
  ]
}
```

## 🖥️ Claude Desktop

Para integrar los agentes en Claude Desktop, edita:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Agrega los agentes bajo una sección personalizada (ejemplo):

```json
{
  "mcpServers": {
    "glpi-mcp-server": {
      "command": "python",
      "args": ["-m", "glpi_mcp_server.server"],
      "env": {
        "GLPI_API_URL": "https://your-glpi.com/apirest.php",
        "MCP_TRANSPORT": "streamable-http"
      }
    }
  },
  "customAgents": {
    "backend-architect": {
      "path": "/home/gokushan/mcp-project/.agents/development-architecture/backend-architect.md",
      "enabled": true
    },
    "python-expert": {
      "path": "/home/gokushan/mcp-project/.agents/language-specialists/python-expert.md",
      "enabled": true
    },
    "security-auditor": {
      "path": "/home/gokushan/mcp-project/.agents/quality-security/security-auditor.md",
      "enabled": true
    },
    "mcp-security-auditor": {
      "path": "/home/gokushan/mcp-project/.agents/quality-security/mcp-security-auditor.md",
      "enabled": true
    },
    "mcp-expert": {
      "path": "/home/gokushan/mcp-project/.agents/specialized-domains/mcp-expert.md",
      "enabled": true
    },
    "ui-ux-designer": {
      "path": "/home/gokushan/mcp-project/.agents/design-experience/ui-ux-designer.md",
      "enabled": true
    }
  }
}
```

## 📊 Agentes Disponibles

| Nombre | Ruta | Categoría | Descripción |
|--------|------|-----------|-------------|
| backend-architect | `.agents/development-architecture/` | Arquitectura | Diseña APIs y sistemas escalables |
| python-expert | `.agents/language-specialists/` | Lenguaje | Código Python idiomático y optimizado |
| security-auditor | `.agents/quality-security/` | Seguridad | Auditorías de seguridad de aplicaciones |
| mcp-security-auditor | `.agents/quality-security/` | Seguridad MCP | Auditorías de servidores MCP |
| mcp-expert | `.agents/specialized-domains/` | Dominios | Construcción de servidores MCP |
| ui-ux-designer | `.agents/design-experience/` | Diseño | Interfaces accesibles e intuitivas |

## 🔄 Verificar Agentes Disponibles

```bash
# Listar todos los agentes en el proyecto
find /home/gokushan/mcp-project/.agents -name "*.md" -type f

# Contar agentes por categoría
find /home/gokushan/mcp-project/.agents -type d | tail -n +2 | while read dir; do
  echo "$(basename "$dir"): $(ls "$dir"/*.md 2>/dev/null | wc -l)"
done
```

## 🎯 Casos de Uso por Agente

### backend-architect
- Diseño de nuevas APIs REST
- Definición de límites de microservicios
- Optimización de esquemas de base de datos
- Revisión de escalabilidad del sistema

### python-expert
- Refactorización de código Python
- Optimización de rendimiento
- Implementación de patrones de diseño
- Características avanzadas (decorators, async/await, etc.)

### security-auditor
- Auditoría de seguridad de código
- Implementación de autenticación segura
- Verificación de cumplimiento OWASP
- Corrección de vulnerabilidades

### mcp-security-auditor
- Auditoría de servidores MCP
- Diseño de sistemas de autorización
- Implementación de OAuth 2.1
- Cumplimiento normativo (SOC 2, GDPR)

### mcp-expert
- Construcción de servidores MCP
- Configuración de integraciones
- Optimización del protocolo MCP
- Documentación de configuraciones

### ui-ux-designer
- Diseño de interfaces de usuario
- Creación de sistemas de diseño
- Aseguranza de accesibilidad WCAG
- Optimización de experiencia de usuario

## 📝 Notas Importantes

1. **Rutas Absolutas**: Las rutas en la configuración deben ser absolutas (`/home/...`, no relativas)
2. **Permisos**: Asegúrate de que los archivos sean legibles (`chmod 644`)
3. **Actualización**: Si agregas nuevos agentes, actualiza esta configuración
4. **Sincronización**: Los cambios en los archivos `.md` se reflejan automáticamente

## 🔧 Troubleshooting

### Los agentes no aparecen en Claude
1. Verifica que la ruta en la configuración sea correcta
2. Asegúrate de que los archivos existan y sean legibles
3. Reinicia Claude Code o Claude Desktop
4. Comprueba que el archivo JSON de configuración sea válido (sin errores de sintaxis)

### Error: "Agente no encontrado"
1. Verifica el nombre exacto del agente (sensible a mayúsculas/minúsculas)
2. Confirma que el archivo `.md` existe en la ruta especificada
3. Recarga la configuración de Claude

---

**Última actualización:** Abril 2026
**Total de agentes configurables:** 6
