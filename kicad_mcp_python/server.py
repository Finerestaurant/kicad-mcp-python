"""
MCP server creation and configuration
"""
import atexit
import os
import signal
import logging
import threading
from typing import Callable, List
from mcp.server.fastmcp import FastMCP

from kicad_mcp_python.pcb.tools import ManipulationTools, AnalyzeTools


# Import context management
def create_cleanup_registry() -> tuple[Callable[[Callable], Callable], Callable[[], None]]:
    """Creates a cleanup function registry.
    
    Returns:
        tuple: (register_cleanup function, execute_cleanup function)
    """
    cleanup_handlers: List[Callable] = []
    cleanup_executed = threading.Event()
    cleanup_lock = threading.Lock()
    
    def register_cleanup(handler: Callable) -> Callable:
        """Registers a cleanup handler.
        
        Args:
            handler: The function to execute on cleanup.
            
        Returns:
            The registered handler (for chaining).
        """
        if not cleanup_executed.is_set():
            cleanup_handlers.append(handler)
            logging.debug(f"Cleanup handler registered: {handler.__name__}")
        else:
            logging.warning(f"Cannot register handler {handler.__name__}: cleanup already executed")
        
        return handler
    
    def execute_cleanup() -> None:
        """Executes all registered cleanup handlers."""
        with cleanup_lock:
            if cleanup_executed.is_set():
                logging.debug("Cleanup already executed, skipping")
                return
            
            cleanup_executed.set()
            logging.info(f"Executing {len(cleanup_handlers)} cleanup handlers")
            
            errors = []
            for i, handler in enumerate(cleanup_handlers):
                try:
                    handler()
                    logging.debug(f"Cleanup handler {i+1}/{len(cleanup_handlers)} completed: {handler.__name__}")
                except Exception as e:
                    error_msg = f"Cleanup handler {handler.__name__} failed: {str(e)}"
                    errors.append(error_msg)
                    logging.error(error_msg, exc_info=True)
            
            if errors:
                logging.warning(f"Cleanup completed with {len(errors)} errors")
                for error in errors:
                    logging.warning(f"  - {error}")
            else:
                logging.info("All cleanup handlers completed successfully")
    
    return register_cleanup, execute_cleanup


def create_signal_handler(execute_cleanup: Callable[[], None]) -> Callable:
    """Creates a signal handler.
    
    Args:
        execute_cleanup: The function to execute cleanup tasks.
        
    Returns:
        The signal handler function.
    """
    shutdown_lock = threading.Lock()
    
    def handle_shutdown_signal(signum: int, frame) -> None:
        """Handles system signals and shuts down gracefully."""
        with shutdown_lock:  # Prevent duplicate execution
            logging.info(f"Received shutdown signal {signum}, initiating graceful shutdown")
            
            # Execute cleanup tasks
            execute_cleanup()
            
            # Log server shutdown
            logging.info("Graceful shutdown completed, exiting")
            
            # Force exit (to prevent stdio blocking)
            os._exit(0)
    
    return handle_shutdown_signal


def register_system_signals(signal_handler: Callable) -> List[int]:
    """Registers system signal handlers.
    
    Args:
        signal_handler: The signal handler function.
        
    Returns:
        A list of successfully registered signals.
    """
    target_signals = [signal.SIGINT, signal.SIGTERM]
    
    # Add SIGHUP if available
    if hasattr(signal, 'SIGHUP'):
        target_signals.append(signal.SIGHUP)
    
    registered_signals = []
    
    for sig in target_signals:
        try:
            signal.signal(sig, signal_handler)
            registered_signals.append(sig)
            logging.debug(f"Signal handler registered for {sig}")
        except (ValueError, AttributeError, OSError) as e:
            logging.warning(f"Cannot register signal {sig}: {str(e)}")
    
    if registered_signals:
        signal_names = [f"{sig}({sig.name if hasattr(sig, 'name') else str(sig)})" 
                       for sig in registered_signals]
        logging.info(f"Signal handlers registered for: {', '.join(signal_names)}")
    else:
        logging.warning("No signal handlers could be registered")
    
    return registered_signals


def setup_graceful_shutdown(server_instance: FastMCP) -> Callable[[Callable], Callable]:
    """Sets up graceful shutdown for the server.
    
    Args:
        server_instance: The server instance (optional).
        
    Returns:
        The cleanup handler registration function.
    """
    # Create cleanup registry
    register_cleanup, execute_cleanup = create_cleanup_registry()
    
    # Register server shutdown handler
    if server_instance:
        @register_cleanup
        def shutdown_server():
            """Shuts down the server instance safely."""
            try:
                logging.info("Shutting down server instance")
                # Add server-specific shutdown logic here
                logging.info("Server shutdown completed")
            except Exception as e:
                logging.error(f"Error during server shutdown: {str(e)}", exc_info=True)
    
    # Create and register signal handlers
    signal_handler = create_signal_handler(execute_cleanup)
    registered_signals = register_system_signals(signal_handler)
    
    if not registered_signals:
        logging.error("Failed to register any signal handlers - graceful shutdown may not work")
    
    # Register atexit handler
    atexit.register(execute_cleanup)
    logging.debug("atexit cleanup handler registered")
    
    return register_cleanup


def create_kicad_cleanup_handlers(register_cleanup: Callable[[Callable], Callable]) -> None:
    """Registers KiCad-related cleanup handlers.
    
    Args:
        register_cleanup: The cleanup handler registration function.
    """
    
    @register_cleanup
    def cleanup_kicad_instances():
        """Cleans up KiCad instances."""
        try:
            # KiCad-related cleanup logic
            logging.info("Cleaning up KiCad instances")
            # Implement actual KiCad cleanup code here
        except Exception as e:
            logging.error(f"KiCad cleanup failed: {str(e)}")
    
    @register_cleanup
    def cleanup_temporary_files():
        """Cleans up temporary files."""
        try:
            # Temporary file cleanup logic
            logging.info("Cleaning up temporary files")
            # Implement actual file cleanup code here
        except Exception as e:
            logging.error(f"Temporary file cleanup failed: {str(e)}")
    
    @register_cleanup
    def cleanup_resources():
        """Cleans up other resources."""
        try:
            # Other resource cleanup logic
            logging.info("Cleaning up miscellaneous resources")
            # Implement actual resource cleanup code here
        except Exception as e:
            logging.error(f"Resource cleanup failed: {str(e)}")


def create_server() -> FastMCP:
    """Creates and configures the KiCad MCP server.
    
    Returns:
        The configured FastMCP server instance.
    """
    # Create server instance
    mcp = FastMCP("KiCad")
    
    # Create tool managers
    ManipulationTools.register_tools(mcp)
    AnalyzeTools.register_tools(mcp)
    register_cleanup = setup_graceful_shutdown(mcp)
    
    # Register KiCad-related cleanup handlers
    create_kicad_cleanup_handlers(register_cleanup)
    
    # Example of registering an additional cleanup handler
    @register_cleanup
    def log_shutdown_completion():
        """Logs the completion of the shutdown."""
        logging.info("KiCad MCP Server shutdown process completed")
    
    logging.info("KiCad MCP Server created and configured successfully")
    
    return mcp
