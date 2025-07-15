import inspect

from typing import Any, Optional, get_origin, Dict

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import AnyFunction, Resource
from mcp.server.fastmcp.tools.base import Tool, func_metadata



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

    def response_formatter(
        self, 
        result: Any, 
        status: str = 'success', 
        error_type: Optional[str] = None
        ) -> Dict[str, Any]:
        
        return result # init function, will be use in ActionFlowmanager


    def add_tool(self, func: AnyFunction):
        """
        Adds a tool to the MCP with its function name and documentation.
        """
        try:

            def initialize_func(*args, **kwargs):
                """
                A wrapper function that calls the original function and formats the result.
                """
                self.initialize_kicad() 
                try:
                    result = func(*args, **kwargs)
                    return self.response_formatter(result)
                except Exception as e:
                    return self.response_formatter(str(e), status='error', error_type=type(e).__name__)
            
            # https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/tools/base.py#L40
            # The reason for directly using Tool.from_function to register the MCP tool
            # is because context_kwarg is required.
            context_kwarg = None
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if get_origin(param.annotation) is not None:
                    continue
                if issubclass(param.annotation, Context):
                    context_kwarg = param_name
                    break
                
            func_arg_metadata = func_metadata(
                func,
                skip_names=[context_kwarg] if context_kwarg is not None else [],
            )
            parameters = func_arg_metadata.arg_model.model_json_schema()

            tool = Tool(
                fn=initialize_func,
                name=func.__name__,
                title=None,
                description=func.__doc__,
                parameters=parameters,
                fn_metadata=func_arg_metadata,
                is_async=False,
                context_kwarg=context_kwarg,
                annotations=None,
            )
            self.mcp._tool_manager._tools[tool.name] = tool
            
            
        except Exception as e:
            raise RuntimeError(f"Failed to register tool {func.__name__}: {str(e)}")