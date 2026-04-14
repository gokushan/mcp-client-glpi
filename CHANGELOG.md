# Changelog - MCP Client

All notable changes to this project will be documented in this file.

## [Unreleased]

### ✨ New Features

- **Custom Email Agents**: Added personalized email feature with CLAUDE.md configuration and custom agents for improved email processing workflows
- **IP Whitelist Control**: Implemented IP address allowed list configuration for enhanced security and access control
- **Client Host Configuration**: Added environment variable to specify client host or enable any connection mode for flexible deployment scenarios
- **Error Code Responses**: Enhanced API responses to include proper HTTP status codes for better error handling and debugging

### 🔧 Improvements

- **Environment Variable Documentation**: Comprehensive documentation added for IP control environment variables
- **Error Handling**: Updated model and responses to return proper error codes instead of generic responses
- **Configuration**: Added Docker ignore and Git ignore files for cleaner repository management
- **Agent Documentation**: Created agents.md file to guide AI agents through project structure and features

### 📚 Documentation

- Project documentation updated with latest features and deployment instructions
- Environment configuration examples provided (.env.example)
- Added FEATURES.md describing all available capabilities
- Created deployment guide (DEPLOYMENT.md)
- Architecture documentation available (ARCHITECTURE.md)

### 🚀 Version Updates

- Version bumped to 1.0.2

---

## [1.0.1] - Earlier Versions

### Initial Project Setup
- Project initialization with core MCP client functionality
- Docker containerization support
- Basic REST API proxy at port 8000
- Connection to FastMCP server at port 8081

---

## How to Contribute

We welcome contributions! Please follow these guidelines:

1. Keep commit messages clear and descriptive
2. Use conventional commit format when possible (feat:, fix:, docs:, etc.)
3. Test your changes before submitting
4. Update documentation for new features

## License

See LICENSE file for details.
