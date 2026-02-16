"""
HTTP Request Blocks
Provides blocks for making HTTP/API requests
"""

from core import (BlockDefinition, BlockPort, BlockParameter, BlockType, DataType, register_block)
import requests
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# GET REQUEST BLOCK
# ============================================================================

def execute_get_request(context: dict) -> dict:
    """Execute HTTP GET request"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    url = params.get("url", "")
    headers = params.get("headers", {})
    timeout = params.get("timeout", 30)
    
    if not url:
        raise ValueError("URL is required")
    
    # Parse headers if string
    if isinstance(headers, str):
        try:
            headers = json.loads(headers) if headers else {}
        except json.JSONDecodeError:
            headers = {}
    
    try:
        logger.info(f"GET request to: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
            "headers": dict(response.headers),
            "success": response.status_code < 400
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"GET request failed: {e}")
        raise


get_request_block = BlockDefinition(
    block_type="http_get",
    name="GET Request",
    category=BlockType.HTTP_REQUEST,
    description="Execute HTTP GET request",
    input_ports=[],
    output_ports=[
        BlockPort("status_code", DataType.NUMBER),
        BlockPort("text", DataType.STRING),
        BlockPort("json", DataType.OBJECT),
        BlockPort("headers", DataType.OBJECT),
        BlockPort("success", DataType.BOOLEAN)
    ],
    parameters=[
        BlockParameter("url", str, "", required=True, description="Request URL"),
        BlockParameter("headers", str, "{}", description="Headers (JSON format)"),
        BlockParameter("timeout", int, 30, description="Timeout in seconds")
    ],
    execute_func=execute_get_request,
    icon="📥",
    color="#88C0D0"
)


# ============================================================================
# POST REQUEST BLOCK
# ============================================================================

def execute_post_request(context: dict) -> dict:
    """Execute HTTP POST request"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    url = params.get("url", "")
    headers = params.get("headers", {})
    body = params.get("body", "")
    timeout = params.get("timeout", 30)
    
    if not url:
        raise ValueError("URL is required")
    
    # Parse headers
    if isinstance(headers, str):
        try:
            headers = json.loads(headers) if headers else {}
        except json.JSONDecodeError:
            headers = {}
    
    # Parse body
    if isinstance(body, str):
        try:
            body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            pass  # Keep as string
    
    try:
        logger.info(f"POST request to: {url}")
        
        if isinstance(body, dict):
            response = requests.post(url, json=body, headers=headers, timeout=timeout)
        else:
            response = requests.post(url, data=body, headers=headers, timeout=timeout)
        
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
            "headers": dict(response.headers),
            "success": response.status_code < 400
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"POST request failed: {e}")
        raise


post_request_block = BlockDefinition(
    block_type="http_post",
    name="POST Request",
    category=BlockType.HTTP_REQUEST,
    description="Execute HTTP POST request",
    input_ports=[],
    output_ports=[
        BlockPort("status_code", DataType.NUMBER),
        BlockPort("text", DataType.STRING),
        BlockPort("json", DataType.OBJECT),
        BlockPort("headers", DataType.OBJECT),
        BlockPort("success", DataType.BOOLEAN)
    ],
    parameters=[
        BlockParameter("url", str, "", required=True, description="Request URL"),
        BlockParameter("headers", str, "{}", description="Headers (JSON format)"),
        BlockParameter("body", str, "{}", description="Request body (JSON or text)"),
        BlockParameter("timeout", int, 30, description="Timeout in seconds")
    ],
    execute_func=execute_post_request,
    icon="📤",
    color="#88C0D0"
)


# ============================================================================
# PUT REQUEST BLOCK
# ============================================================================

def execute_put_request(context: dict) -> dict:
    """Execute HTTP PUT request"""
    params = context["parameters"]
    
    url = params.get("url", "")
    headers = params.get("headers", {})
    body = params.get("body", "")
    timeout = params.get("timeout", 30)
    
    if not url:
        raise ValueError("URL is required")
    
    # Parse headers and body
    if isinstance(headers, str):
        try:
            headers = json.loads(headers) if headers else {}
        except json.JSONDecodeError:
            headers = {}
    
    if isinstance(body, str):
        try:
            body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            pass
    
    try:
        logger.info(f"PUT request to: {url}")
        
        if isinstance(body, dict):
            response = requests.put(url, json=body, headers=headers, timeout=timeout)
        else:
            response = requests.put(url, data=body, headers=headers, timeout=timeout)
        
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
            "success": response.status_code < 400
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"PUT request failed: {e}")
        raise


put_request_block = BlockDefinition(
    block_type="http_put",
    name="PUT Request",
    category=BlockType.HTTP_REQUEST,
    description="Execute HTTP PUT request",
    input_ports=[],
    output_ports=[
        BlockPort("status_code", DataType.NUMBER),
        BlockPort("text", DataType.STRING),
        BlockPort("json", DataType.OBJECT),
        BlockPort("success", DataType.BOOLEAN)
    ],
    parameters=[
        BlockParameter("url", str, "", required=True, description="Request URL"),
        BlockParameter("headers", str, "{}", description="Headers (JSON format)"),
        BlockParameter("body", str, "{}", description="Request body"),
        BlockParameter("timeout", int, 30, description="Timeout in seconds")
    ],
    execute_func=execute_put_request,
    icon="🔄",
    color="#88C0D0"
)


# ============================================================================
# DELETE REQUEST BLOCK
# ============================================================================

def execute_delete_request(context: dict) -> dict:
    """Execute HTTP DELETE request"""
    params = context["parameters"]
    
    url = params.get("url", "")
    headers = params.get("headers", {})
    timeout = params.get("timeout", 30)
    
    if not url:
        raise ValueError("URL is required")
    
    if isinstance(headers, str):
        try:
            headers = json.loads(headers) if headers else {}
        except json.JSONDecodeError:
            headers = {}
    
    try:
        logger.info(f"DELETE request to: {url}")
        response = requests.delete(url, headers=headers, timeout=timeout)
        
        return {
            "status_code": response.status_code,
            "text": response.text,
            "success": response.status_code < 400
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"DELETE request failed: {e}")
        raise


delete_request_block = BlockDefinition(
    block_type="http_delete",
    name="DELETE Request",
    category=BlockType.HTTP_REQUEST,
    description="Execute HTTP DELETE request",
    input_ports=[],
    output_ports=[
        BlockPort("status_code", DataType.NUMBER),
        BlockPort("text", DataType.STRING),
        BlockPort("success", DataType.BOOLEAN)
    ],
    parameters=[
        BlockParameter("url", str, "", required=True, description="Request URL"),
        BlockParameter("headers", str, "{}", description="Headers (JSON format)"),
        BlockParameter("timeout", int, 30, description="Timeout in seconds")
    ],
    execute_func=execute_delete_request,
    icon="🗑️",
    color="#BF616A"
)


# ============================================================================
# PARSE JSON BLOCK
# ============================================================================

def execute_parse_json(context: dict) -> dict:
    """Parse JSON string"""
    inputs = context["inputs"]
    params = context["parameters"]
    
    json_text = inputs.get("text", params.get("json_text", ""))
    
    if not json_text:
        raise ValueError("JSON text is required")
    
    try:
        parsed = json.loads(json_text)
        logger.info("Parsed JSON successfully")
        
        return {
            "json": parsed,
            "type": type(parsed).__name__
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        raise ValueError(f"Invalid JSON: {e}")


parse_json_block = BlockDefinition(
    block_type="http_parse_json",
    name="Parse JSON",
    category=BlockType.DATA,
    description="Parse JSON string to object",
    input_ports=[
        BlockPort("text", DataType.STRING, required=False)
    ],
    output_ports=[
        BlockPort("json", DataType.OBJECT),
        BlockPort("type", DataType.STRING)
    ],
    parameters=[
        BlockParameter("json_text", str, "", description="JSON text to parse")
    ],
    execute_func=execute_parse_json,
    icon="📋",
    color="#EBCB8B"
)


# ============================================================================
# REGISTER ALL HTTP BLOCKS
# ============================================================================

def register_http_blocks():
    """Register all HTTP request blocks"""
    register_block(get_request_block)
    register_block(post_request_block)
    register_block(put_request_block)
    register_block(delete_request_block)
    register_block(parse_json_block)
    
    logger.info("Registered 5 HTTP request blocks")
