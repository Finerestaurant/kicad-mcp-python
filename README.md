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



## What Can It Do?

With this MCP server, an AI model can perform tasks such as:

*   **Manipulate PCB Objects**:
    *   Create new items (footprints, tracks, etc.)
    *   Modify the properties of existing items
    *   Move and rotate items
    *   Delete unnecessary items
*   **Analyze PCBs**:
    *   Get a list of all items of a specific type on the board
    *   Query the overall status information of the board
*   **Visual Verification**:
    *   Generate PNG images of the entire board, routing layers, or component layers to visually inspect the design. This feature is planned for future implementation to enhance the verification process of PCB designs.

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

### 2. Install and Run the MCP Server

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

### 3. MCP Client Configuration

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
    *   `args`: Add `["main.py"]` to specify the script to run.


    **Configuration Example:**
    ```json
    {
      "servers": [
        {
          "name": "kicad-mcp-server",
          "command": "/pypoetry/virtualenvs/kicad-mcp-python-xxxxxxxx-py3.10/bin/python",
          "args": ["main.py"],

        }
      ]
    }
    ```

## Future Plans

*   **Schematic Support**: Currently developing APIs related to schematics in KiCad, and we plan to implement these features in the MCP as soon as development is complete.
*   **Simultaneous Multi-Item Editing/Moving**: We will implement functionality to select and modify or move multiple PCB items at once.

*   **Workflow Improvements**: We will improve the step-by-step flow of tools like item creation and modification to provide a more efficient and intuitive API.
*   **ScreenShot Verification**: We will implement a step to automatically verify the results after item manipulation to increase the reliability of operations.


## Changelog

### [0.2.0] (Planned)
*   Implement functionality to select and modify or move multiple PCB items at once.
*   Add a `verify_result` tool that uses screenshots for visual confirmation after operations.

### [0.1.0] - 2025-07-02
*   Initial release of the KiCad MCP server.
*   Support for basic PCB object manipulation (create, modify, move, delete).
*   Detailed setup instructions including `kicad-python` submodule installation.
