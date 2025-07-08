import logging
import inspect

from typing import Any, Dict, Optional, Callable, get_origin

from mcp.server.fastmcp import FastMCP, Context
from kipy import KiCad
from mcp.server.fastmcp.tools.base import Tool, func_metadata


logger = logging.getLogger(__name__)


class ActionFlowManager:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp  # MCP instance
        self.action_flow = []  # Initialize action flow as a list
        self.mcp_tools = {}  # Store registered MCP tools
        self.flow_graph = {}  # Flow graph (information about the next function to execute)
        
        
    def initialize_board(self):
        # TODO: Need to add logic to refresh the board.
        try:
            self.board = KiCad().get_board()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize the board: {str(e)}")


    def get_next_action(self, current_action: str) -> Optional[str]:
        """Returns the action to be executed after the current action"""
        try:
            current_index = self.action_flow.index(current_action)
            if current_index + 1 < len(self.action_flow):
                return self.action_flow[current_index + 1]
            return None
        except ValueError:
            return None

    def response_formatter(self, result: Any, status: str = 'success', error_type: Optional[str] = None) -> Dict[str, Any]:
        """Formats and returns the result"""
        if status == 'error':
            return {
                "result": result,
                "status": status,
                "error_type": error_type
            }
        else:
            next_action = self.get_next_action(self.action_flow[-1]) if self.action_flow else None
            return {
                "result": result,
                "status": status,
                "next_action": next_action,
                "next_action_info": f"Next execution: {next_action}" if next_action else "Flow complete"
            }
    
    
    def action_setter(self, func: Callable[..., Any]):
        """
        A function that adds a method to the action_flow list and registers it as an MCP tool.
        The registered function formats the result through self.response_formatter upon execution.
        """
        self.action_flow.append(func.__name__)

        # Register as an MCP tool (apply the actual mcp.tool decorator)
        try:

            def initialize_func(*args, **kwargs):
                """
                A wrapper function that calls the original function and formats the result.
                """
                self.initialize_board()
                try:
                    result = func(*args, **kwargs)
                    return self.response_formatter(result)
                except Exception as e:
                    logger.error(f"Error executing {func.__name__}: {e}")
                    return self.response_formatter(str(e), status='error', error_type=type(e).__name__)
            
            # https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/tools/base.py#L40
            # The reason for directly using Tool.from_function to register the MCP tool
            # is because context_kwarg is required.
            context_kwarg = None
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                print(param_name, param.annotation)
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
        
        # Store in the MCP tool dictionary
        self.mcp_tools[func.__name__] = func
        
    
    def get_mcp_tools(self) -> Dict[str, Callable]:
        """Returns the registered MCP tools"""
        return self.mcp_tools
    
    def __repr__(self):
        return f"ActionFlowManager(action_flow={self.action_flow})"
