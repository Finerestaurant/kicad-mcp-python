import os
import subprocess
import tempfile
from PIL import Image
import cairosvg
import io
from dotenv import load_dotenv
import base64
from pathlib import Path

# Load .env file
load_dotenv()


class KiCadPCBConverter:
    def __init__(self):
        self.kicad_cli_path = os.getenv('KICAD_CLI_PATH')
        if not self.kicad_cli_path:
            raise ValueError("KICAD_CLI_PATH is not set in the .env file.")
        
        if not os.path.exists(self.kicad_cli_path):
            raise FileNotFoundError(f"KiCad CLI not found: {self.kicad_cli_path}")
    
    def pcb_to_jpg_via_svg(self, boardname, layers=None, cleanup=True):
        """Convert PCB to JPG via SVG and return temporary file path
        Return:
            dict: Base64 encoded data and metadata of the converted image
        """
        # Default layer settings (front and back)
        if layers is None:
            layers = ["F.Cu", "B.Cu", "F.SilkS", "B.SilkS", "F.Mask", "B.Mask"]
        try:
            pcb_path = self.get_pcb_path_by_name(boardname)
        except Exception as e:
            raise RuntimeError(f"Error occurred while finding board file, please write correct path in .env: {e}")
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as svg_temp:
            svg_path = svg_temp.name
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as jpg_temp:
            jpg_path = jpg_temp.name
        
        jpg_path_2 = 'test.jpg'            

        try:
            # Convert layers to comma-separated string
            layers_str = ",".join(layers)
            
            # Configure KiCad CLI command
            cmd = [
                self.kicad_cli_path, "pcb", "export", "svg",
                "--output", svg_path,
                "--layers", layers_str,  # Comma-separated layer list
                "--mode-single",  # Single file mode
                pcb_path
            ]
            
            print(f"Executing command: {' '.join(cmd)}")  # For debugging
            
            # Generate SVG with KiCad CLI
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Convert SVG to JPG
            png_data = cairosvg.svg2png(url=svg_path)
            image = Image.open(io.BytesIO(png_data))
            image.convert('RGB').save(jpg_path, 'JPEG')
            
            with open(jpg_path, 'rb') as f:
                jpg_data = f.read()
            
            # Encode to Base64
            base64_data = base64.b64encode(jpg_data).decode('utf-8')
            if cleanup:
                # Delete SVG temporary file
                os.unlink(svg_path)
                os.unlink(jpg_path)
                
            return base64_data

            
        except subprocess.CalledProcessError as e:
            # Clean up temporary files on failure
            if os.path.exists(svg_path):
                os.unlink(svg_path)
            if os.path.exists(jpg_path):
                os.unlink(jpg_path)
            
            # Print detailed error information
            print(f"Standard output: {e.stdout}")
            print(f"Standard error: {e.stderr}")
            raise RuntimeError(f"KiCad CLI execution error: {e}")
        except Exception as e:
            # Clean up temporary files on failure
            if os.path.exists(svg_path):
                os.unlink(svg_path)
            if os.path.exists(jpg_path):
                os.unlink(jpg_path)
            raise RuntimeError(f"Conversion error: {e}")
    

    def get_pcb_path_by_name(self, boardname):
        """
        Find and return the path corresponding to boardname from PCB_PATHS environment variable.
        
        Args:
            boardname (str): PCB board filename to find (including extension)
        
        Returns:
            str: Full path of the corresponding board, None if not found
        """
        # Get PCB_PATHS from environment variable
        pcb_paths = os.getenv('PCB_PATHS')
        
        if not pcb_paths:
            print("PCB_PATHS environment variable is not set.")
            return None
        
        # Convert comma-separated paths to list and remove whitespace
        paths = [path.strip() for path in pcb_paths.split(',')]
        
        # Check filename in each path
        for path in paths:
            if not path:  # Skip empty paths
                continue
                
            # Extract filename from path
            filename = Path(path).name
            
            # Check if filename matches
            if filename == boardname:
                return path
        
        print(f"File '{boardname}' not found.")
        return None