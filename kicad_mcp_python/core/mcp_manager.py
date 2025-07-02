from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import AnyFunction, Resource


class ResourceManager:
    """
    Represents a resource with its properties and methods.
    """

    def __init__(self, mcp: FastMCP):
        self.mcp = mcp


    def add_resource(self, 
                    uri: str, 
                    name: str, 
                    description: Optional[str] = None,
                    mime_type: Optional[str] = None,
                    content: Optional[str] = None) -> None:
        """
        Adds a resource to the MCP with its URI, name and documentation.
        """
        resource = Resource(
            uri=uri,
            name=name,
            description=description,
            mimeType=mime_type
        )
        
        self.mcp.add_resource(resource)



class ToolManager:
    """
    Represents a tool with its properties and methods.
    """

    def __init__(self, mcp: FastMCP):
        self.mcp = mcp


    def add_tool(self, fn: AnyFunction):
        """
        Adds a tool to the MCP with its function name and documentation.
        """
        self.mcp.add_tool(fn, fn.__name__, fn.__doc__)
        return fn