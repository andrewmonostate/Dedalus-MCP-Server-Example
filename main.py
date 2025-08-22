#!/usr/bin/env python
"""
Main entry point for Dedalus MCP server deployment
This file is required by Dedalus to start the MCP server
"""

import sys
import os

def main():
    """Main function for script entry point"""
    # Ensure we can import from src
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.main import main as server_main
        # Run the server's main function
        return server_main()
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()