"""
Main Entry Point for Visual Automation Tool
Initializes the application, registers blocks, and launches the GUI.
"""

import sys
import logging
from pathlib import Path

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


def setup_application():
    """Initialize application and register all blocks"""
    logger.info("="*60)
    logger.info("Visual Automation Tool - Lite RPA Engine")
    logger.info("="*60)
    
    try:
        # Import block modules to register blocks
        from blocks.web_automation import register_web_blocks
        from blocks.logic import register_logic_blocks
        from blocks.http_requests import register_http_blocks
        
        # Register all blocks
        logger.info("Registering blocks...")
        register_web_blocks()
        register_logic_blocks()
        register_http_blocks()
        
        from core import BlockRegistry
        total_blocks = BlockRegistry.get_block_count()
        logger.info(f"Successfully registered {total_blocks} blocks")
        
        # Display registered categories
        categories = BlockRegistry.get_categories()
        logger.info(f"Available categories: {[cat.value for cat in categories]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup application: {e}")
        return False


def main():
    """Main application entry point"""
    try:
        # Setup application
        if not setup_application():
            logger.error("Application setup failed. Exiting.")
            sys.exit(1)
        
        # Launch GUI
        logger.info("Launching GUI...")
        from gui.main_window import MainWindow
        
        app = MainWindow()
        logger.info("Application started successfully")
        app.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Display banner
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     VISUAL AUTOMATION TOOL - LITE RPA ENGINE              ║
    ║                                                           ║
    ║     A Python-based drag-and-drop automation platform     ║
    ║                                                           ║
    ║     Version: 1.0.0                                       ║
    ║     License: Educational Use                             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    ⚠️  ETHICAL USE NOTICE:
    
    This tool is designed for legitimate automation purposes only.
    
    Please ensure you:
    • Have permission to automate any websites or APIs
    • Respect robots.txt and terms of service
    • Do not use for unauthorized access or data theft
    • Implement appropriate rate limiting
    • Use proper user-agent identification
    
    By using this tool, you agree to use it responsibly and ethically.
    
    Starting application...
    """)
    
    main()
