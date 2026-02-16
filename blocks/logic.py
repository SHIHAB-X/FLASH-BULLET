"""
Logic and Control Flow Blocks
Provides conditional logic, loops, delays, and variables
"""

from core import (BlockDefinition, BlockPort, BlockParameter, BlockType, DataType, register_block)
import logging
import time

logger = logging.getLogger(__name__)


# ============================================================================
# DELAY BLOCK
# ============================================================================

def execute_delay(context: dict) -> dict:
    """Wait for specified seconds"""
    params = context["parameters"]
    seconds = params.get("seconds", 1)
    
    logger.info(f"Waiting {seconds} seconds...")
    time.sleep(seconds)
    
    return {"waited": seconds}


delay_block = BlockDefinition(
    block_type="logic_delay",
    name="Delay",
    category=BlockType.CONTROL_FLOW,
    description="Pause execution for specified time",
    input_ports=[
        BlockPort("trigger", DataType.ANY, required=False)
    ],
    output_ports=[
        BlockPort("waited", DataType.NUMBER)
    ],
    parameters=[
        BlockParameter("seconds", float, 1.0, required=True, 
                      description="Seconds to wait")
    ],
    execute_func=execute_delay,
    icon="⏱️",
    color="#B48EAD"
)


# ============================================================================
# SET VARIABLE BLOCK
# ============================================================================

def execute_set_variable(context: dict) -> dict:
    """Set a global variable"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    var_name = params.get("variable_name", "")
    value = params.get("value", inputs.get("value", ""))
    
    if not var_name:
        raise ValueError("Variable name is required")
    
    # Store in shared context
    context["context"]["variables"][var_name] = value
    
    logger.info(f"Set variable {var_name} = {value}")
    
    return {
        "variable_name": var_name,
        "value": value
    }


set_variable_block = BlockDefinition(
    block_type="logic_set_variable",
    name="Set Variable",
    category=BlockType.VARIABLE,
    description="Store a value in a variable",
    input_ports=[
        BlockPort("value", DataType.ANY, required=False)
    ],
    output_ports=[
        BlockPort("variable_name", DataType.STRING),
        BlockPort("value", DataType.ANY)
    ],
    parameters=[
        BlockParameter("variable_name", str, "", required=True,
                      description="Variable name"),
        BlockParameter("value", str, "", required=False,
                      description="Value (or use input)")
    ],
    execute_func=execute_set_variable,
    icon="📌",
    color="#A3BE8C"
)


# ============================================================================
# GET VARIABLE BLOCK
# ============================================================================

def execute_get_variable(context: dict) -> dict:
    """Retrieve a global variable"""
    params = context["parameters"]
    var_name = params.get("variable_name", "")
    default_value = params.get("default_value", None)
    
    if not var_name:
        raise ValueError("Variable name is required")
    
    # Get from shared context
    variables = context["context"].get("variables", {})
    value = variables.get(var_name, default_value)
    
    if value is None:
        logger.warning(f"Variable {var_name} not found")
    else:
        logger.info(f"Retrieved variable {var_name} = {value}")
    
    return {
        "variable_name": var_name,
        "value": value
    }


get_variable_block = BlockDefinition(
    block_type="logic_get_variable",
    name="Get Variable",
    category=BlockType.VARIABLE,
    description="Retrieve a stored variable value",
    input_ports=[],
    output_ports=[
        BlockPort("variable_name", DataType.STRING),
        BlockPort("value", DataType.ANY)
    ],
    parameters=[
        BlockParameter("variable_name", str, "", required=True,
                      description="Variable name"),
        BlockParameter("default_value", str, None, required=False,
                      description="Default if not found")
    ],
    execute_func=execute_get_variable,
    icon="📍",
    color="#A3BE8C"
)


# ============================================================================
# PRINT/LOG BLOCK
# ============================================================================

def execute_print(context: dict) -> dict:
    """Print message to log"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    message = params.get("message", "")
    if not message and "text" in inputs:
        message = inputs["text"]
    
    logger.info(f"[OUTPUT] {message}")
    print(f"[Block Output] {message}")
    
    return {"message": message}


print_block = BlockDefinition(
    block_type="logic_print",
    name="Print/Log",
    category=BlockType.UTILITY,
    description="Print message to console/log",
    input_ports=[
        BlockPort("text", DataType.ANY, required=False)
    ],
    output_ports=[
        BlockPort("message", DataType.STRING)
    ],
    parameters=[
        BlockParameter("message", str, "", required=False,
                      description="Message to print")
    ],
    execute_func=execute_print,
    icon="🖨️",
    color="#D08770"
)


# ============================================================================
# IF/ELSE BLOCK
# ============================================================================

def execute_if_else(context: dict) -> dict:
    """Conditional execution"""
    params = context["parameters"]
    inputs = context["inputs"]
    
    condition = params.get("condition", "")
    left_value = inputs.get("left_value", params.get("left_value", ""))
    right_value = inputs.get("right_value", params.get("right_value", ""))
    operator = params.get("operator", "==")
    
    # Evaluate condition
    result = False
    try:
        if operator == "==":
            result = str(left_value) == str(right_value)
        elif operator == "!=":
            result = str(left_value) != str(right_value)
        elif operator == ">":
            result = float(left_value) > float(right_value)
        elif operator == "<":
            result = float(left_value) < float(right_value)
        elif operator == ">=":
            result = float(left_value) >= float(right_value)
        elif operator == "<=":
            result = float(left_value) <= float(right_value)
        elif operator == "contains":
            result = str(right_value) in str(left_value)
    except Exception as e:
        logger.error(f"Condition evaluation failed: {e}")
        result = False
    
    logger.info(f"Condition: {left_value} {operator} {right_value} = {result}")
    
    return {
        "result": result,
        "then": result,
        "else": not result
    }


if_else_block = BlockDefinition(
    block_type="logic_if_else",
    name="If/Else",
    category=BlockType.LOGIC,
    description="Conditional branching",
    input_ports=[
        BlockPort("left_value", DataType.ANY, required=False),
        BlockPort("right_value", DataType.ANY, required=False)
    ],
    output_ports=[
        BlockPort("result", DataType.BOOLEAN),
        BlockPort("then", DataType.BOOLEAN),
        BlockPort("else", DataType.BOOLEAN)
    ],
    parameters=[
        BlockParameter("left_value", str, "", description="Left value"),
        BlockParameter("operator", str, "==", 
                      options=["==", "!=", ">", "<", ">=", "<=", "contains"],
                      description="Comparison operator"),
        BlockParameter("right_value", str, "", description="Right value")
    ],
    execute_func=execute_if_else,
    icon="❓",
    color="#B48EAD"
)


# ============================================================================
# FOR LOOP BLOCK (Placeholder)
# ============================================================================

def execute_for_loop(context: dict) -> dict:
    """Execute loop (simplified version)"""
    params = context["parameters"]
    start = params.get("start", 0)
    end = params.get("end", 10)
    step = params.get("step", 1)
    
    # Note: Full loop implementation requires workflow engine support
    # This is a simplified placeholder
    
    iterations = []
    for i in range(start, end, step):
        iterations.append(i)
    
    logger.info(f"Loop: {start} to {end} (step {step}), {len(iterations)} iterations")
    
    return {
        "iterations": iterations,
        "count": len(iterations)
    }


for_loop_block = BlockDefinition(
    block_type="logic_for_loop",
    name="For Loop",
    category=BlockType.CONTROL_FLOW,
    description="Repeat actions in a loop (simplified)",
    input_ports=[],
    output_ports=[
        BlockPort("iterations", DataType.ARRAY),
        BlockPort("count", DataType.NUMBER)
    ],
    parameters=[
        BlockParameter("start", int, 0, description="Start value"),
        BlockParameter("end", int, 10, description="End value"),
        BlockParameter("step", int, 1, description="Step size")
    ],
    execute_func=execute_for_loop,
    icon="🔄",
    color="#B48EAD"
)


# ============================================================================
# REGISTER ALL LOGIC BLOCKS
# ============================================================================

def register_logic_blocks():
    """Register all logic and control flow blocks"""
    register_block(delay_block)
    register_block(set_variable_block)
    register_block(get_variable_block)
    register_block(print_block)
    register_block(if_else_block)
    register_block(for_loop_block)
    
    logger.info("Registered 6 logic blocks")
