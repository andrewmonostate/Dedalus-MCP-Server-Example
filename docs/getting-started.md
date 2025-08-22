# Getting Started with Dedalus MCP

Welcome to the Dedalus Model Context Protocol (MCP) documentation. This guide will help you get started with building and deploying MCP servers on the Dedalus platform.

## What is MCP?

The Model Context Protocol (MCP) is an open standard created by Anthropic that enables seamless communication between AI models and external tools, data sources, and services. It provides a standardized way to:

- Expose tools and functions to AI models
- Serve resources and documents
- Handle prompts and completions
- Enable agent-to-agent communication

## Quick Start

### 1. Installation

```bash
pip install dedalus-labs mcp
```

### 2. Create Your First MCP Server

```python
from mcp.server.fastmcp import FastMCP

# Create server instance
mcp = FastMCP("My First Server")

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### 3. Deploy to Dedalus

Deploy your MCP server to Dedalus Labs to make it accessible:

```bash
dedalus deploy ./your-server.py
```

## Core Concepts

### Tools
Tools are functions that AI models can call to perform actions:
- Data retrieval
- Calculations
- API calls
- File operations

### Resources
Resources are data that can be served to clients:
- Documentation files
- Configuration data
- Static content
- Dynamic data feeds

### Prompts
Prompts are templates that help structure AI interactions:
- Query templates
- Instruction formats
- Context builders

## Next Steps

- [Building Advanced Tools](./advanced-tools.md)
- [Agent Handoffs](./agent-handoffs.md)
- [Deployment Guide](./deployment.md)
- [API Reference](./api-reference.md)