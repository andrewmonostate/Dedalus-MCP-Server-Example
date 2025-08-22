# Dedalus MCP Documentation Server

An MCP server for serving and querying documentation with AI capabilities. Built for the YC Agents Hackathon.

## Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure (optional for AI features)
cp config/.env.example .env.local

# Test
python tests/test_server.py

# Run
python src/server.py
```

## Deploy to Dedalus

```bash
dedalus deploy ./src/server.py --name "your-docs-server"
```

## Features

- Serve markdown documentation
- Search across docs
- AI-powered Q&A (with OpenAI)
- Ready for agent handoffs

## Tools Available

- `list_docs()` - List documentation files
- `search_docs()` - Search with keywords
- `ask_docs()` - AI answers from docs
- `index_docs()` - Index documents
- `analyze_docs()` - Analyze for tasks

## Documentation

See `docs/` directory for:
- [Getting Started Guide](docs/guides/getting-started.md)
- [Hackathon Information](docs/hackathon/yc-agents-hackathon.md)
- [Deployment Guide](docs/guides/deployment.md)
- [Examples](examples/)

## License

MIT