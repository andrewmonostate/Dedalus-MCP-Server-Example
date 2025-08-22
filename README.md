# Dedalus Documentation MCP Server

An open-source Model Context Protocol (MCP) server for serving and querying documentation, designed for deployment on [Dedalus Labs](https://dedaluslabs.ai).

## Features

- **Document Serving**: Serve markdown documentation files as MCP resources
- **Semantic Search**: Search across documentation with keyword and semantic matching
- **AI Q&A**: Answer questions about documentation using AI
- **Agent Handoffs**: Foundation for multi-model routing and agent collaboration
- **Metadata Extraction**: Automatic title and metadata extraction from documents
- **Extensible**: Easy to add new tools and capabilities

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dedalus-docs-mcp-server.git
cd dedalus-docs-mcp-server

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or use the setup script (Unix/Mac)
chmod +x setup.sh
./setup.sh
```

### Local Testing

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy and configure environment (for AI responses)
cp .env.example .env.local
# Edit .env.local and add your OpenAI API key

# Test the server
python test_server.py

# Run the server
python src/server.py

# Or with custom docs directory
DOCS_DIR=/path/to/your/docs python src/server.py
```

### Deploy to Dedalus Labs

```bash
# Deploy your MCP server to Dedalus
# The server uses 'mcp' package (in requirements.txt)
dedalus deploy ./src/server.py --name "hackathon-docs-server"
```

### Using the Deployed Server

```bash
# Install Dedalus client SDK
pip install dedalus-labs

# Use in your code (see examples/client.py)
mcp_servers=["your-org/hackathon-docs-server"]
```

## Usage Examples

### Using with Dedalus SDK

```python
import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner

async def query_docs():
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # Query your documentation
    result = await runner.run(
        input="How do I get started with MCP?",
        model="openai/gpt-4o-mini",
        mcp_servers=["your-org/docs-server"],
        stream=False
    )
    
    print(result.final_output)

asyncio.run(query_docs())
```

### Available Tools

#### `list_docs(directory?: string)`
List all available documentation files.

```python
# List all docs
docs = await mcp.call_tool("list_docs", {})

# List docs in subdirectory
docs = await mcp.call_tool("list_docs", {"directory": "guides"})
```

#### `search_docs(query: string, max_results?: number)`
Search documentation using keywords.

```python
results = await mcp.call_tool("search_docs", {
    "query": "agent handoffs",
    "max_results": 5
})
```

#### `ask_docs(question: string, context_docs?: list)`
Answer questions using AI based on documentation.

```python
answer = await mcp.call_tool("ask_docs", {
    "question": "How do I implement streaming responses?",
    "context_docs": ["advanced-tools.md"]
})
```

#### `analyze_docs(task: string, docs?: list)`
Analyze documentation for specific tasks (foundation for agent handoffs).

```python
analysis = await mcp.call_tool("analyze_docs", {
    "task": "find_gaps",
    "output_format": "detailed"
})
```

### Multi-Model Workflows

Example of using the server with agent handoffs:

```python
async def documentation_workflow(topic: str):
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # Stage 1: Search for relevant docs
    search_result = await runner.run(
        input=f"Search documentation for {topic}",
        model="openai/gpt-4o-mini",
        mcp_servers=["your-org/docs-server"],
    )
    
    # Stage 2: Deep analysis with Claude
    analysis = await runner.run(
        input=f"Analyze these docs and create a learning path: {search_result.final_output}",
        model="claude-3-5-sonnet-20241022",
        mcp_servers=["your-org/docs-server"],
    )
    
    return analysis.final_output
```

## Extending the Server

### Adding Custom Tools

```python
# In src/server.py

@mcp.tool()
def custom_analysis(
    doc_path: str,
    analysis_type: str
) -> dict:
    """Your custom analysis tool"""
    content = (DOCS_DIR / doc_path).read_text()
    
    # Your analysis logic
    result = perform_analysis(content, analysis_type)
    
    return {
        "document": doc_path,
        "analysis": result
    }
```

### Adding LLM Integration

To enable actual AI responses in the `ask_docs` tool:

```python
# Add your LLM client
from openai import AsyncOpenAI

client = AsyncOpenAI()

# Update ask_docs implementation
async def generate_answer(question: str, context: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Answer based on:\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content
```

### Adding Semantic Search

For production semantic search, integrate an embedding model:

```python
# Using sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(text: str) -> list[float]:
    return model.encode(text).tolist()

# Store embeddings for search
def index_document(doc_path: Path):
    content = doc_path.read_text()
    embedding = generate_embeddings(content)
    # Store in vector database
```

## Configuration

Environment variables:

- `DOCS_DIR`: Path to documentation directory (default: `./docs`)
- `MAX_CONTEXT_LENGTH`: Maximum context for AI queries (default: 4000)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)

## Project Structure

```
dedalus-docs-mcp-server/
├── src/
│   └── server.py           # Main MCP server implementation
├── docs/                    # Documentation files
│   ├── getting-started.md
│   ├── advanced-tools.md
│   └── agent-handoffs.md
├── examples/
│   ├── client.py           # Example Dedalus client
│   └── workflows.py        # Example workflows
├── tests/
│   └── test_server.py      # Server tests
├── pyproject.toml          # Package configuration
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- [Dedalus Labs Documentation](https://docs.dedaluslabs.ai)
- [MCP Specification](https://modelcontextprotocol.io)
- [GitHub Issues](https://github.com/yourusername/dedalus-docs-mcp-server/issues)

## Acknowledgments

Built with:
- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) by Anthropic
- [Dedalus Labs](https://dedaluslabs.ai) platform
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for simplified server creation