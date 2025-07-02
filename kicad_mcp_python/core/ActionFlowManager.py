import logging
from typing import Any, Dict, Optional, Callable

from mcp.server.fastmcp import FastMCP
from kipy import KiCad

logger = logging.getLogger(__name__)


class ActionFlowManager:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp  # MCP instance
        self.action_flow = []  # Initialize action flow as a list
        self.mcp_tools = {}  # Store registered MCP tools
        self.flow_graph = {}  # Flow graph (information about the next function to execute)

    def _initialize_board(self):
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
        self._initialize_board()
        self.action_flow.append(func.__name__)

        # Register as an MCP tool (apply the actual mcp.tool decorator)
        try:
            mcp_registered_tool = self.mcp.tool(
                name=func.__name__,
                description=func.__doc__
            )(func)
            
        except Exception as e:
            # If registration fails, you can use the original function as is, or handle the error.
            # Here, we print a registration failure message and do not add it to mcp_tools,
            # or we can insert wrapped_func (a version not registered with mcp).
            # Currently, it is not added to mcp_tools upon registration failure.
            return # Exit the function upon registration failure
        
        # Store in the MCP tool dictionary
        self.mcp_tools[func.__name__] = mcp_registered_tool
        
    
    def get_mcp_tools(self) -> Dict[str, Callable]:
        """Returns the registered MCP tools"""
        return self.mcp_tools
    
    def __repr__(self):
        return f"ActionFlowManager(action_flow={self.action_flow})"
