# Deployment Guide

## How MCP Servers Work

MCP (Model Context Protocol) servers communicate via stdio (standard input/output) by default. When deployed to platforms like Dedalus, the platform handles:

1. **Installing dependencies** from `requirements.txt`
2. **Running the server** by calling the Python script
3. **Managing communication** between clients and the server
4. **Providing environment variables** for configuration

## Local Development

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional for AI features)
cp .env.example .env.local
# Add your OpenAI API key to .env.local
```

### Testing
```bash
# Test that server loads correctly
python src/server.py --test

# Run full test suite
python test_server.py

# Run server in stdio mode (how Dedalus runs it)
python src/server.py
```

## Dedalus Deployment

### Prerequisites
- Dedalus account
- API keys (OpenAI/Anthropic) for AI features

### Deployment Steps

1. **Prepare your server**:
   - Ensure `requirements.txt` includes all dependencies
   - Server must run via `python src/server.py`
   - Use environment variables for configuration

2. **Deploy to Dedalus**:
   ```bash
   dedalus deploy ./src/server.py --name "hackathon-docs-server"
   ```

3. **Configure environment variables** in Dedalus UI:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DOCS_DIR`: Optional custom docs directory

### How Dedalus Runs Your Server

When deployed, Dedalus:

1. Creates a container/environment with Python
2. Installs packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Runs your server:
   ```bash
   python src/server.py
   ```
4. Routes MCP protocol messages via stdio

### Using Your Deployed Server

```python
from dedalus_labs import AsyncDedalus, DedalusRunner

async def use_server():
    client = AsyncDedalus(api_key="your-api-key")
    runner = DedalusRunner(client)
    
    result = await runner.run(
        input="Your query here",
        model="openai/gpt-4o-mini",
        mcp_servers=["your-org/hackathon-docs-server"],
        stream=False
    )
    
    print(result.final_output)
```

## File Structure Requirements

```
your-mcp-server/
├── requirements.txt    # REQUIRED: Python dependencies
├── src/
│   └── server.py      # REQUIRED: Main server file
├── docs/              # Your documentation files
├── .env.example       # Example environment variables
└── README.md          # Documentation
```

## Key Points

1. **Dependencies**: All packages in `requirements.txt` are installed automatically
2. **Entry Point**: Server must be runnable via `python src/server.py`
3. **Environment**: Use `os.getenv()` for configuration
4. **Protocol**: MCP uses stdio for communication (handled by FastMCP)
5. **API Keys**: Provided via environment variables in Dedalus UI

## Troubleshooting

### Server doesn't start
- Check all imports are in `requirements.txt`
- Verify server runs locally with `python src/server.py --test`

### AI features not working
- Ensure `OPENAI_API_KEY` is set in Dedalus environment variables
- Check API key has sufficient credits

### Documents not found
- Verify `docs/` directory exists and contains `.md` files
- Check `DOCS_DIR` environment variable if using custom path

## Support

- [MCP Documentation](https://modelcontextprotocol.io)
- [Dedalus Documentation](https://docs.dedaluslabs.ai)
- [GitHub Issues](https://github.com/yourusername/dedalus-docs-mcp-server/issues)