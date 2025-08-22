#!/usr/bin/env python
"""
Setup script for the Dedalus Documentation MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="dedalus-docs-mcp-server",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "docs-mcp-server=server:main",
        ],
    },
)