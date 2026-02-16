"""
Demo Version - Visual Automation Tool
This version demonstrates the core functionality without requiring external dependencies.
For full functionality, install dependencies: pip install -r requirements.txt
"""

import sys
import os
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_tool.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    
    try:
        import customtkinter
    except ImportError:
        missing.append('customtkinter')
    
    try:
        import selenium
    except ImportError:
        missing.append('selenium')
    
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    return missing


def setup_demo_blocks():
    """Setup minimal blocks for demo without external dependencies"""
    from core import (BlockDefinition, BlockPort, BlockParameter, 
                     BlockType, DataType, register_block)
    import time
    
    # Simple delay block
    def execute_delay(context: dict) -> dict:
        seconds = context["parameters"].get("seconds", 1)
        time.sleep(seconds)
        return {"waited": seconds}
    
    delay_block = BlockDefinition(
        block_type="demo_delay",
        name="Delay",
        category=BlockType.CONTROL_FLOW,
        description="Wait for specified seconds",
        output_ports=[BlockPort("waited", DataType.NUMBER)],
        parameters=[BlockParameter("seconds", float, 1.0, required=True)],
        execute_func=execute_delay,
        icon="⏱️",
        color="#B48EAD"
    )
    
    # Simple print block
    def execute_print(context: dict) -> dict:
        message = context["parameters"].get("message", "")
        print(f"[DEMO OUTPUT] {message}")
        logger.info(f"[DEMO OUTPUT] {message}")
        return {"message": message}
    
    print_block = BlockDefinition(
        block_type="demo_print",
        name="Print Message",
        category=BlockType.UTILITY,
        description="Print a message",
        input_ports=[BlockPort("text", DataType.STRING, required=False)],
        output_ports=[BlockPort("message", DataType.STRING)],
        parameters=[BlockParameter("message", str, "Hello World!")],
        execute_func=execute_print,
        icon="🖨️",
        color="#D08770"
    )
    
    # Variable blocks
    def execute_set_var(context: dict) -> dict:
        var_name = context["parameters"].get("variable_name", "")
        value = context["parameters"].get("value", "")
        context["context"]["variables"][var_name] = value
        logger.info(f"Set {var_name} = {value}")
        return {"variable_name": var_name, "value": value}
    
    set_var_block = BlockDefinition(
        block_type="demo_set_var",
        name="Set Variable",
        category=BlockType.VARIABLE,
        description="Store a variable",
        output_ports=[BlockPort("value", DataType.ANY)],
        parameters=[
            BlockParameter("variable_name", str, "", required=True),
            BlockParameter("value", str, "", required=True)
        ],
        execute_func=execute_set_var,
        icon="📌",
        color="#A3BE8C"
    )
    
    # Register blocks
    register_block(delay_block)
    register_block(print_block)
    register_block(set_var_block)
    
    logger.info("Registered 3 demo blocks")


def main():
    """Main demo entry point"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     VISUAL AUTOMATION TOOL - DEMO MODE                   ║
    ║                                                           ║
    ║     Lite RPA Engine - Core Functionality Demo            ║
    ║                                                           ║
    ║     Version: 1.0.0 (Demo)                                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    logger.info("="*60)
    logger.info("Visual Automation Tool - DEMO MODE")
    logger.info("="*60)
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"\nTo install all dependencies, run:")
        print(f"    pip install -r requirements.txt\n")
        print(f"Running in DEMO mode with limited blocks...\n")
        
        # Setup demo blocks instead
        try:
            setup_demo_blocks()
            logger.info("Demo blocks registered successfully")
        except Exception as e:
            logger.error(f"Failed to setup demo blocks: {e}")
            return
    else:
        # Full mode - import all blocks
        try:
            from blocks.web_automation import register_web_blocks
            from blocks.logic import register_logic_blocks
            from blocks.http_requests import register_http_blocks
            
            register_web_blocks()
            register_logic_blocks()
            register_http_blocks()
            
            logger.info("All blocks registered successfully")
        except Exception as e:
            logger.error(f"Failed to register blocks: {e}")
            return
    
    # Launch GUI
    try:
        logger.info("Launching GUI...")
        from gui.main_window import MainWindow
        
        app = MainWindow()
        logger.info("Application started successfully")
        app.mainloop()
        
    except ImportError as e:
        logger.error(f"GUI dependencies missing: {e}")
        print(f"\n❌ Cannot start GUI: {e}")
        print(f"\nPlease install CustomTkinter:")
        print(f"    pip install customtkinter")
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\n❌ Application error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nApplication closed by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
