from dotenv import load_dotenv

from ..pcbmodule import PCBTool
from ...core.ActionFlowManager import ActionFlowManager
from ...utils.kicad_cli import KiCadPCBConverter

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent

load_dotenv()


class VerifyFlowManager(ActionFlowManager):
    """A class that manages the step-by-step flow of remove Item"""
    
    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
        self.pcb_converter = KiCadPCBConverter()
        self.pcb_path = None
        self._register_tool()

    def _register_tool(self):
        self.action_setter(self.verify_pcb_step_1)
    
        
    def verify_pcb_step_1(self, layers: list):
        # TODO: Add more options for verifying PCB files.
        """ # verify_pcb_step_2
        
        Args:
            pcb_path (str): The path to the PCB file to be verified.
            layers (list): List of layers to be included in the verification.
            
        Returns:
            base64 (str): Base64 encoded string of the converted PCB image.
            
        Next action:
            get_board_status
        """
        base64_image = self.pcb_converter.pcb_to_jpg_via_svg(
            boardname=self.board.name,
            layers=layers
            )
        
        return ImageContent(
            type="image",
            data=base64_image,
            mimeType="image/jpeg"
        )
        
class VerifyTools:
    """A class that provides tools for verifying PCB files."""
    
    @classmethod
    def register_tools(self, mcp: FastMCP):
        '''
        Registers the verifying tools with the given MCP instance.
        
        Args:
            mcp (FastMCP): The MCP instance to register the tools with.
        '''
        # Register flow managers
        VerifyFlowManager(mcp) # TODO: name this flow manager