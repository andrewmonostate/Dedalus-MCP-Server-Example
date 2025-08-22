"""
Dedalus Documentation MCP Server
A Model Context Protocol server for serving and querying documentation
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables - try multiple locations
from pathlib import Path
env_path = Path('.') / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
load_dotenv()  # Also load .env if exists

from mcp.server.fastmcp import FastMCP
import mcp.types as types

mcp = FastMCP("Documentation Server")

# Configuration
# Check for docs in multiple locations (for Dedalus deployment compatibility)
possible_docs_dirs = [
    Path(os.getenv("DOCS_DIR", "./docs")),  # Environment variable
    Path("/app/docs"),  # Dedalus container path
    Path("./docs"),     # Local path
]

DOCS_DIR = None
for dir_path in possible_docs_dirs:
    if dir_path.exists():
        DOCS_DIR = dir_path
        break

# If no docs dir exists, use the first option and create it
if DOCS_DIR is None:
    DOCS_DIR = possible_docs_dirs[0]
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDINGS_CACHE = {}
METADATA_CACHE = {}


def get_doc_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract metadata from markdown files"""
    if file_path in METADATA_CACHE:
        return METADATA_CACHE[file_path]
    
    metadata = {
        "title": file_path.stem.replace("-", " ").title(),
        "path": str(file_path.relative_to(DOCS_DIR)),
        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        "size": file_path.stat().st_size,
        "hash": hashlib.md5(file_path.read_bytes()).hexdigest()
    }
    
    # Try to extract title from first # heading
    try:
        content = file_path.read_text()
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('# '):
                metadata["title"] = line[2:].strip()
                break
    except:
        pass
    
    METADATA_CACHE[file_path] = metadata
    return metadata


@mcp.resource("docs://{path}")
def get_documentation(path: str) -> str:
    """
    Serve markdown documentation files
    
    Args:
        path: Path to the documentation file relative to docs directory
    
    Returns:
        Content of the markdown file
    """
    file_path = DOCS_DIR / path
    
    if not file_path.exists():
        raise ValueError(f"Documentation file not found: {path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    if file_path.suffix not in ['.md', '.markdown', '.txt']:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    return file_path.read_text()


@mcp.tool()
def list_docs(directory: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all available documentation files
    
    Args:
        directory: Optional subdirectory to list (relative to docs root)
    
    Returns:
        List of document metadata
    """
    search_dir = DOCS_DIR
    if directory:
        search_dir = DOCS_DIR / directory
    
    if not search_dir.exists():
        return []
    
    docs = []
    for file_path in search_dir.rglob("*.md"):
        if file_path.is_file():
            docs.append(get_doc_metadata(file_path))
    
    return sorted(docs, key=lambda x: x["path"])


@mcp.tool()
def search_docs(
    query: str,
    max_results: int = 5,
    search_content: bool = True,
    search_titles: bool = True
) -> List[Dict[str, Any]]:
    """
    Search documentation using keyword matching (semantic search ready)
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        search_content: Whether to search in document content
        search_titles: Whether to search in document titles
    
    Returns:
        List of matching documents with relevance scores
    """
    query_lower = query.lower()
    results = []
    
    for file_path in DOCS_DIR.rglob("*.md"):
        if not file_path.is_file():
            continue
        
        score = 0
        metadata = get_doc_metadata(file_path)
        
        # Title matching
        if search_titles and query_lower in metadata["title"].lower():
            score += 10
        
        # Content matching
        if search_content:
            try:
                content = file_path.read_text().lower()
                # Count occurrences
                occurrences = content.count(query_lower)
                if occurrences > 0:
                    score += min(occurrences, 5)  # Cap at 5 points for content
                    
                    # Find snippet around first occurrence
                    idx = content.find(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 100)
                    snippet = content[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(content):
                        snippet = snippet + "..."
                    metadata["snippet"] = snippet
            except:
                pass
        
        if score > 0:
            metadata["relevance_score"] = score
            results.append(metadata)
    
    # Sort by relevance score
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return results[:max_results]


@mcp.tool()
def ask_docs(
    question: str,
    context_docs: Optional[List[str]] = None,
    max_context_length: int = 4000
) -> Dict[str, Any]:
    """
    Answer questions about documentation using AI
    
    Args:
        question: The question to answer
        context_docs: Optional list of document paths to use as context
        max_context_length: Maximum characters of context to include
    
    Returns:
        AI-generated answer with sources
    """
    # If no context docs specified, search for relevant ones
    if not context_docs:
        search_results = search_docs(question, max_results=3)
        context_docs = [result["path"] for result in search_results]
    
    # Gather context from documents
    context_parts = []
    sources = []
    total_length = 0
    
    for doc_path in context_docs:
        if total_length >= max_context_length:
            break
            
        try:
            file_path = DOCS_DIR / doc_path
            content = file_path.read_text()
            
            # Truncate if needed
            remaining = max_context_length - total_length
            if len(content) > remaining:
                content = content[:remaining] + "..."
            
            context_parts.append(f"--- {doc_path} ---\n{content}")
            sources.append(doc_path)
            total_length += len(content)
        except:
            continue
    
    if not context_parts:
        return {
            "answer": "I couldn't find relevant documentation to answer your question.",
            "sources": [],
            "confidence": "low"
        }
    
    full_context = "\n\n".join(context_parts)
    
    # Try to use OpenAI if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documentation. Only use information from the provided context."},
                    {"role": "user", "content": f"""Based on the following documentation, please answer this question: {question}

Documentation:
{full_context}

Please provide a clear, concise answer based only on the provided documentation."""}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                "answer": response.choices[0].message.content,
                "sources": sources,
                "context_length": total_length,
                "model": "gpt-4o-mini",
                "confidence": "high"
            }
        except Exception as e:
            # Fall back to context-only response if OpenAI fails
            return {
                "answer": f"Error using OpenAI: {str(e)}",
                "context": full_context[:500] + "..." if len(full_context) > 500 else full_context,
                "sources": sources,
                "context_length": total_length,
                "error": str(e)
            }
    
    # If no API key, return context for Dedalus deployment
    return {
        "question": question,
        "context": full_context[:500] + "..." if len(full_context) > 500 else full_context,
        "sources": sources,
        "context_length": total_length,
        "note": "No API key found. When deployed to Dedalus, this will use the platform's LLM integration via BYOK"
    }


@mcp.tool()
def index_docs(rebuild: bool = False) -> Dict[str, Any]:
    """
    Index or re-index all documentation for improved search
    
    Args:
        rebuild: Whether to rebuild the entire index from scratch
    
    Returns:
        Indexing statistics
    """
    if rebuild:
        METADATA_CACHE.clear()
        EMBEDDINGS_CACHE.clear()
    
    stats = {
        "files_indexed": 0,
        "total_size": 0,
        "errors": [],
        "timestamp": datetime.now().isoformat()
    }
    
    for file_path in DOCS_DIR.rglob("*.md"):
        try:
            if file_path.is_file():
                metadata = get_doc_metadata(file_path)
                stats["files_indexed"] += 1
                stats["total_size"] += metadata["size"]
                
                # Here you would generate embeddings for semantic search
                # EMBEDDINGS_CACHE[file_path] = generate_embeddings(content)
        except Exception as e:
            stats["errors"].append({
                "file": str(file_path),
                "error": str(e)
            })
    
    return stats


@mcp.tool()
def analyze_docs(
    task: str,
    docs: Optional[List[str]] = None,
    output_format: str = "summary"
) -> Dict[str, Any]:
    """
    Analyze documentation for specific tasks (foundation for agent handoffs)
    
    Args:
        task: Analysis task (e.g., "find_gaps", "generate_outline", "check_consistency")
        docs: Optional list of specific documents to analyze
        output_format: Output format (summary, detailed, structured)
    
    Returns:
        Analysis results ready for agent handoff
    """
    available_tasks = [
        "find_gaps",
        "generate_outline", 
        "check_consistency",
        "extract_examples",
        "identify_prerequisites",
        "suggest_improvements"
    ]
    
    if task not in available_tasks:
        return {
            "error": f"Unknown task. Available tasks: {', '.join(available_tasks)}",
            "available_tasks": available_tasks
        }
    
    # Gather documents to analyze
    if not docs:
        all_docs = list_docs()
        docs = [doc["path"] for doc in all_docs]
    
    # This is where different analysis agents would be invoked
    # Structure the response for easy handoff to specialized agents
    return {
        "task": task,
        "documents_analyzed": len(docs),
        "output_format": output_format,
        "results": {
            "summary": f"Analysis task '{task}' ready for processing",
            "documents": docs,
            "next_steps": [
                "Connect specialized agent for this task",
                "Process documents according to task requirements",
                "Return structured results"
            ]
        },
        "agent_handoff_ready": True,
        "suggested_model": "gpt-4" if task in ["find_gaps", "check_consistency"] else "claude-3-5-sonnet"
    }


@mcp.prompt()
def documentation_query(
    topic: str,
    detail_level: str = "medium"
) -> str:
    """
    Generate a prompt for querying documentation
    
    Args:
        topic: The topic to query about
        detail_level: Level of detail (brief, medium, comprehensive)
    
    Returns:
        A formatted prompt for documentation queries
    """
    prompts = {
        "brief": f"Provide a brief summary of {topic} from the documentation.",
        "medium": f"Explain {topic} with examples and key points from the documentation.",
        "comprehensive": f"Provide a comprehensive explanation of {topic} including all details, examples, and related concepts from the documentation."
    }
    
    return prompts.get(detail_level, prompts["medium"])


def main():
    """Main entry point for the MCP server"""
    import asyncio
    import sys
    
    # Ensure docs directory exists
    DOCS_DIR.mkdir(exist_ok=True)
    
    # Check if running in stdio mode (default for MCP)
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - just verify everything loads
        print(f"Documentation MCP Server loaded successfully")
        print(f"Docs directory: {DOCS_DIR.absolute()}")
        print(f"Tools available: list_docs, search_docs, ask_docs, index_docs, analyze_docs")
        print(f"Documents found: {len(list(DOCS_DIR.rglob('*.md')))}")
        return 0
    
    # Run the server in stdio mode (standard for MCP)
    # This is what Dedalus will call
    mcp.run()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())