#!/usr/bin/env python3
"""
KiCad MCP Python - A Model Context Protocol server for KiCad.
This server allows Claude and other MCP clients to interact with KiCad projects.
"""

from kicad_mcp_python.server import create_server


if __name__ == "__main__":
    # Create and run server
    server = create_server()
    server.run(transport='stdio')
