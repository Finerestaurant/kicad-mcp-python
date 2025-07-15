from mcp.server.fastmcp import FastMCP
from kipy import KiCad

class PCBTool:
    """
    Represents a PCB module with its properties and methods.
    """

    def initialize_kicad(self):
        # TODO: Need to add logic to refresh the board.
        try:
            self.board = KiCad().get_board()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize the board: {str(e)}")
