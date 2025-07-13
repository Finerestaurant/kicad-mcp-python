# KiCad MCP Server

This project is a Model Context Protocol (MCP) server for [KiCad](https://kicad.org). As MCP server that utilizes KiCad's official [IPC-API](https://gitlab.com/kicad/code/kicad-python), it provides the most stable and reliable way for AI models like Claude to interact with KiCad, automating and assisting with PCB design and schematic tasks.




## Key Features

*   **MCP Server Implementation**: Handles requests from MCP clients.
*   **KiCad Integration**: Communicates with a running KiCad session using the [`kicad-python`](https://gitlab.com/kicad/code/kicad-python) library.
*   **Automated Workflows**: Enables AI models to create, modify, and verify schematics and PCB layouts in KiCad projects.

### Wiring


https://github.com/user-attachments/assets/e2ba57e7-2c77-4c56-a911-c461c77307e4


### Move item


https://github.com/user-attachments/assets/de6c93dc-8808-4321-827e-ebad0556e7b1


### Enhanced Board Analysis and Action Verification




https://github.com/user-attachments/assets/0fea60de-d012-4b4d-bfa4-dd1b758b2c7f



This server features `AnalyzeTools` for enhanced board analysis. A key tool is `get_board_status`, which provides a comprehensive overview of the PCB layout, including screenshots.

To ensure robust and reliable operations, the server uses an `ActionFlowManager`. This manager orchestrates the execution of actions by automatically invoking `get_board_status` both before and after each action. This flow provides the AI model with critical context:

*   **Pre-Action Analysis**: By reviewing the board's state before an action, the model can make better-informed decisions.
*   **Post-Action Verification**: By comparing the board's state before and after the action, the model can visually confirm that the operation was successful and achieved the desired outcome.

This automated verification process significantly improves the accuracy and reliability of automated PCB design tasks.




## What Can It Do?

With this MCP server, an AI model can perform tasks such as:

*   **Manipulate PCB Objects**:
    *   Create new items (footprints, tracks, etc.)
    *   Modify the properties of existing items
    *   Move and rotate items
    *   Delete unnecessary items
*   **Analyze PCBs**:
    *   Get a list of all items of a specific type on the board.
    *   Query the overall status information of the board using `get_board_status` for comprehensive analysis.




## Getting Started

This project uses [Poetry](https://python-poetry.org/) to manage dependencies.

### 1. Prerequisite: Install `kicad-python`

This project uses the `kicad-python` library as a Git submodule. Therefore, you must build and install `kicad-python` before running this project.

1.  **Clone Repository and Initialize Submodules**:
    Run git submodule update --init to add kicad-python's source code as a submodule.
    ```bash
    git submodule update --init --depth 1
    ```

2.  **Build and Install `kicad-python`**:
    Navigate to the `kicad-python` directory and follow the instructions in that project's `COMPILING.md` file to build and install the library.

### 2. Configure Environment Variables

Before running the server, you need to create a `.env` file in the project's root directory (`KiCad-mcp-python/.env`). This file is crucial for tools that rely on KiCad's command-line interface (CLI), such as `get_board_status` which generates screenshots to provide visual context of the board. It stores the necessary environment variables for the server to function correctly.

Create a file named `.env` and add the following content, adjusting the paths to match your system configuration:

```
KICAD_CLI_PATH=/path/to/your/kicad-cli
PCB_PATHS=/path/to/your/project1.kicad_pcb,/path/to/your/project2.kicad_pcb
```

**Variable Explanations:**

*   `KICAD_CLI_PATH`: The absolute path to the KiCad command-line interface (CLI) executable.
    *   **macOS Example**: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`
    *   **Windows Example**: `C:\Program Files\KiCad\7.0\bin\kicad-cli.exe`
    *   **Linux Example**: `/usr/bin/kicad-cli`
*   `PCB_PATHS`: A comma-separated list of absolute paths to the `.kicad_pcb` files you want the MCP server to be able to access.


### 3. Install and Run the MCP Server

1.  **Install Dependencies**:
    Once `kicad-python` is installed, return to this project's root directory and run the following command to install the remaining dependencies:
    ```bash
    poetry install
    ```

2.  **Enable KiCad IPC Server**:
    Launch KiCad and enable the IPC server by selecting **Tools -> External Plugin -> Start Server**.

3.  **Start the MCP Server**:
    Start the MCP server with the following command:
    ```bash
    poetry run python main.py
    ```

The server is now waiting for a connection from an MCP client.

### 4. MCP Client Configuration

To use this server with an MCP client (e.g., a VSCode extension), you need to configure the server execution command correctly.

1.  **Find the Poetry Virtual Environment Interpreter Path**:
    Run the following command to find the full path to the Python interpreter installed in the current project's Poetry virtual environment:
    ```bash
    poetry env info --path
    ```
    Copy the path output by the command (e.g., `/pypoetry/virtualenvs/kicad-mcp-python-xxxxxxxx-py3.10`).

2.  **Add MCP Server Configuration**:
    Add the server information to your MCP client's configuration file (e.g., `mcp_servers.json`) as follows:

    *   `command`: Enter the full path to the interpreter by appending `/bin/python` to the path you copied above.
    *   `args`: Add `["/path/to/your/KiCad-mcp-python/main.py"]` to specify the script to run. Make sure to provide the full, absolute path to `main.py`.


    **Configuration Example:**
    ```json
    {
      "servers": [
        {
          "name": "kicad-mcp-server",
          "command": "/pypoetry/virtualenvs/kicad-mcp-python-xxxxxxxx-py3.10/bin/python",
          "args": ["/path/to/your/kicad-mcp-python/main.py"],

        }
      ]
    }
    ```

## Future Plans

*   **Schematic Support**: Currently developing APIs related to schematics in KiCad, and we plan to implement these features in the MCP as soon as development is complete.
*   **Simultaneous Multi-Item Editing/Moving**: We will implement functionality to select and modify or move multiple PCB items at once.

*   **Workflow Improvements**: We will improve the step-by-step flow of tools like item creation and modification to provide a more efficient and intuitive API.


## Changelog

### [0.2.0] (Planned)
*   Implement functionality to select and modify or move multiple PCB items at once.
*   Create a prompt section to serve as a guide for using the tools.
*   Updated `get_board_status` to include pre and post operation board information with screenshots for visual verification. ([0714 commit](https://github.com/Finerestaurant/kicad-mcp-python/commit/719715b6ef2bce4e4738a63439842929d22adacc))


### [0.1.0] - 2025-07-02
*   Initial release of the KiCad MCP server.
*   Support for basic PCB object manipulation (create, modify, move, delete).
*   Detailed setup instructions including `kicad-python` submodule installation.
