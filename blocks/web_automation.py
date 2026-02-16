"""
Web Automation Blocks - Browser automation using Selenium
Provides blocks for web scraping, form filling, and browser interaction
"""

from core import (BlockDefinition, BlockPort, BlockParameter, BlockType, DataType, register_block)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time

logger = logging.getLogger(__name__)


# ============================================================================
# OPEN BROWSER BLOCK
# ============================================================================

def execute_open_browser(context: dict) -> dict:
    """Open a new browser instance"""
    params = context["parameters"]
    browser_type = params.get("browser", "chrome")
    headless = params.get("headless", False)
    
    try:
        if browser_type == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # User agent rotation for ethical scraping
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=options)
        elif browser_type == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser_type}")
        
        # Store browser instance in context
        browser_id = f"browser_{context['block_id']}"
        context["context"]["browser_instances"][browser_id] = driver
        
        logger.info(f"Opened {browser_type} browser (headless={headless})")
        
        return {
            "browser": driver,
            "browser_id": browser_id
        }
    
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        raise


open_browser_block = BlockDefinition(
    block_type="web_open_browser",
    name="Open Browser",
    category=BlockType.WEB_AUTOMATION,
    description="Open a new browser instance for automation",
    output_ports=[
        BlockPort("browser", DataType.BROWSER, description="Browser instance")
    ],
    parameters=[
        BlockParameter("browser", str, "chrome", options=["chrome", "firefox"],
                      description="Browser type"),
        BlockParameter("headless", bool, False, description="Run in headless mode")
    ],
    execute_func=execute_open_browser,
    icon="🌐",
    color="#5E81AC"
)


# ============================================================================
# NAVIGATE TO URL BLOCK
# ============================================================================

def execute_navigate(context: dict) -> dict:
    """Navigate to a URL"""
    params = context["parameters"]
    inputs = context["inputs"]
    url = params.get("url", "")
    
    if not url:
        raise ValueError("URL is required")
    
    # Get browser from input or context
    browser = inputs.get("browser")
    if not browser:
        # Try to get from context
        browser_instances = context["context"].get("browser_instances", {})
        if browser_instances:
            browser = list(browser_instances.values())[0]
        else:
            raise ValueError("No browser instance available")
    
    try:
        logger.info(f"Navigating to: {url}")
        browser.get(url)
        
        # Wait for page load
        time.sleep(2)
        
        return {
            "browser": browser,
            "url": url,
            "title": browser.title
        }
    
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        raise


navigate_block = BlockDefinition(
    block_type="web_navigate",
    name="Navigate to URL",
    category=BlockType.WEB_AUTOMATION,
    description="Navigate browser to a specific URL",
    input_ports=[
        BlockPort("browser", DataType.BROWSER, required=False)
    ],
    output_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("url", DataType.STRING),
        BlockPort("title", DataType.STRING)
    ],
    parameters=[
        BlockParameter("url", str, "", required=True, description="Target URL")
    ],
    execute_func=execute_navigate,
    icon="🔗",
    color="#5E81AC"
)


# ============================================================================
# FIND ELEMENT BLOCK
# ============================================================================

def execute_find_element(context: dict) -> dict:
    """Find an element on the page"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    selector = params.get("selector", "")
    selector_type = params.get("selector_type", "css")
    timeout = params.get("timeout", 10)
    
    if not selector:
        raise ValueError("Selector is required")
    
    browser = inputs.get("browser")
    if not browser:
        raise ValueError("Browser instance required")
    
    try:
        # Map selector types
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME,
            "tag": By.TAG_NAME
        }
        
        by = by_map.get(selector_type, By.CSS_SELECTOR)
        
        # Wait for element
        wait = WebDriverWait(browser, timeout)
        element = wait.until(EC.presence_of_element_located((by, selector)))
        
        logger.info(f"Found element: {selector}")
        
        return {
            "browser": browser,
            "element": element,
            "text": element.text,
            "visible": element.is_displayed()
        }
    
    except TimeoutException:
        logger.error(f"Element not found: {selector}")
        raise ValueError(f"Element not found within {timeout} seconds")
    except Exception as e:
        logger.error(f"Find element failed: {e}")
        raise


find_element_block = BlockDefinition(
    block_type="web_find_element",
    name="Find Element",
    category=BlockType.WEB_AUTOMATION,
    description="Find an element on the web page",
    input_ports=[
        BlockPort("browser", DataType.BROWSER)
    ],
    output_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("element", DataType.ELEMENT),
        BlockPort("text", DataType.STRING),
        BlockPort("visible", DataType.BOOLEAN)
    ],
    parameters=[
        BlockParameter("selector", str, "", required=True, description="Element selector"),
        BlockParameter("selector_type", str, "css", options=["css", "xpath", "id", "class", "name", "tag"]),
        BlockParameter("timeout", int, 10, description="Wait timeout in seconds")
    ],
    execute_func=execute_find_element,
    icon="🔍",
    color="#5E81AC"
)


# ============================================================================
# CLICK ELEMENT BLOCK
# ============================================================================

def execute_click(context: dict) -> dict:
    """Click an element"""
    inputs = context["inputs"]
    
    element = inputs.get("element")
    browser = inputs.get("browser")
    
    if not element:
        raise ValueError("Element is required")
    
    try:
        # Wait for element to be clickable
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable(element))
        
        element.click()
        time.sleep(1)  # Brief wait after click
        
        logger.info("Clicked element")
        
        return {
            "browser": browser,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Click failed: {e}")
        raise


click_block = BlockDefinition(
    block_type="web_click",
    name="Click Element",
    category=BlockType.WEB_AUTOMATION,
    description="Click on a web element",
    input_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("element", DataType.ELEMENT)
    ],
    output_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("success", DataType.BOOLEAN)
    ],
    parameters=[],
    execute_func=execute_click,
    icon="👆",
    color="#5E81AC"
)


# ============================================================================
# FILL INPUT BLOCK
# ============================================================================

def execute_fill_input(context: dict) -> dict:
    """Fill an input field"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    text = params.get("text", "")
    clear_first = params.get("clear_first", True)
    
    element = inputs.get("element")
    browser = inputs.get("browser")
    
    if not element:
        raise ValueError("Element is required")
    
    try:
        if clear_first:
            element.clear()
        
        element.send_keys(text)
        time.sleep(0.5)
        
        logger.info(f"Filled input with: {text}")
        
        return {
            "browser": browser,
            "element": element,
            "text": text
        }
    
    except Exception as e:
        logger.error(f"Fill input failed: {e}")
        raise


fill_input_block = BlockDefinition(
    block_type="web_fill_input",
    name="Fill Input",
    category=BlockType.WEB_AUTOMATION,
    description="Fill an input field with text",
    input_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("element", DataType.ELEMENT)
    ],
    output_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("element", DataType.ELEMENT),
        BlockPort("text", DataType.STRING)
    ],
    parameters=[
        BlockParameter("text", str, "", required=True, description="Text to enter"),
        BlockParameter("clear_first", bool, True, description="Clear field first")
    ],
    execute_func=execute_fill_input,
    icon="⌨️",
    color="#5E81AC"
)


# ============================================================================
# EXTRACT TEXT BLOCK
# ============================================================================

def execute_extract_text(context: dict) -> dict:
    """Extract text from element"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    attribute = params.get("attribute", None)
    
    element = inputs.get("element")
    browser = inputs.get("browser")
    
    if not element:
        raise ValueError("Element is required")
    
    try:
        if attribute:
            text = element.get_attribute(attribute)
        else:
            text = element.text
        
        logger.info(f"Extracted text: {text[:50]}...")
        
        return {
            "browser": browser,
            "text": text,
            "element": element
        }
    
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise


extract_text_block = BlockDefinition(
    block_type="web_extract_text",
    name="Extract Text",
    category=BlockType.WEB_AUTOMATION,
    description="Extract text or attribute from element",
    input_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("element", DataType.ELEMENT)
    ],
    output_ports=[
        BlockPort("browser", DataType.BROWSER),
        BlockPort("text", DataType.STRING),
        BlockPort("element", DataType.ELEMENT)
    ],
    parameters=[
        BlockParameter("attribute", str, None, required=False, 
                      description="Attribute to extract (leave empty for text)")
    ],
    execute_func=execute_extract_text,
    icon="📄",
    color="#5E81AC"
)


# ============================================================================
# CLOSE BROWSER BLOCK
# ============================================================================

def execute_close_browser(context: dict) -> dict:
    """Close browser instance"""
    inputs = context["inputs"]
    
    browser = inputs.get("browser")
    if not browser:
        raise ValueError("Browser instance required")
    
    try:
        browser.quit()
        logger.info("Closed browser")
        
        # Remove from context
        browser_instances = context["context"].get("browser_instances", {})
        browser_id = inputs.get("browser_id")
        if browser_id and browser_id in browser_instances:
            del browser_instances[browser_id]
        
        return {"success": True}
    
    except Exception as e:
        logger.error(f"Failed to close browser: {e}")
        raise


close_browser_block = BlockDefinition(
    block_type="web_close_browser",
    name="Close Browser",
    category=BlockType.WEB_AUTOMATION,
    description="Close the browser instance",
    input_ports=[
        BlockPort("browser", DataType.BROWSER)
    ],
    output_ports=[
        BlockPort("success", DataType.BOOLEAN)
    ],
    parameters=[],
    execute_func=execute_close_browser,
    icon="❌",
    color="#BF616A"
)


# ============================================================================
# REGISTER ALL WEB AUTOMATION BLOCKS
# ============================================================================

def register_web_blocks():
    """Register all web automation blocks"""
    register_block(open_browser_block)
    register_block(navigate_block)
    register_block(find_element_block)
    register_block(click_block)
    register_block(fill_input_block)
    register_block(extract_text_block)
    register_block(close_browser_block)
    
    logger.info("Registered 7 web automation blocks")
