# Development Guide - Adding Custom Blocks

This guide explains how to create and register custom automation blocks in the Visual Automation Tool.

## Table of Contents
1. [Block Structure Overview](#block-structure-overview)
2. [Creating a Simple Block](#creating-a-simple-block)
3. [Advanced Block Features](#advanced-block-features)
4. [Testing Your Block](#testing-your-block)
5. [Best Practices](#best-practices)

## Block Structure Overview

Every block consists of three main components:

1. **Execution Function**: The Python function that runs when the block executes
2. **Block Definition**: Metadata describing the block's interface
3. **Registration**: Adding the block to the registry

## Creating a Simple Block

### Step 1: Create the Execution Function

```python
def execute_my_custom_block(context: dict) -> dict:
    """
    Execution function for your block.
    
    Args:
        context: Dictionary containing:
            - parameters: Block parameter values
            - inputs: Data from connected input blocks
            - block_id: Unique block instance ID
            - context: Shared workflow context
    
    Returns:
        Dictionary with output port values
    """
    # Get parameters
    params = context["parameters"]
    my_param = params.get("my_parameter", "default")
    
    # Get input data
    inputs = context["inputs"]
    input_value = inputs.get("input_port_name", None)
    
    # Perform your logic
    result = f"Processed: {input_value} with {my_param}"
    
    # Return outputs
    return {
        "output_port_name": result,
        "success": True
    }
```

### Step 2: Create the Block Definition

```python
from core import BlockDefinition, BlockPort, BlockParameter, BlockType, DataType

my_block = BlockDefinition(
    # Unique identifier (use prefix like "custom_")
    block_type="custom_my_block",
    
    # Display name
    name="My Custom Block",
    
    # Category (affects palette grouping)
    category=BlockType.UTILITY,
    
    # Description shown to users
    description="Does something awesome",
    
    # Input ports (data flowing INTO the block)
    input_ports=[
        BlockPort(
            name="input_port_name",
            data_type=DataType.STRING,
            required=True,
            description="Input data description"
        )
    ],
    
    # Output ports (data flowing OUT of the block)
    output_ports=[
        BlockPort(
            name="output_port_name",
            data_type=DataType.STRING,
            description="Output data description"
        ),
        BlockPort(
            name="success",
            data_type=DataType.BOOLEAN,
            description="Whether operation succeeded"
        )
    ],
    
    # Configuration parameters
    parameters=[
        BlockParameter(
            name="my_parameter",
            param_type=str,
            default_value="default",
            required=False,
            description="A configurable parameter"
        )
    ],
    
    # Link to execution function
    execute_func=execute_my_custom_block,
    
    # Visual properties
    icon="⭐",
    color="#A3BE8C"
)
```

### Step 3: Register the Block

```python
from core import register_block

# Register single block
register_block(my_block)

# Or create a registration function for multiple blocks
def register_my_blocks():
    """Register all custom blocks"""
    register_block(my_block)
    # register_block(another_block)
    # ...
```

### Step 4: Add to Application

In `main.py`, import and call your registration function:

```python
from blocks.my_custom_blocks import register_my_blocks

def setup_application():
    # ... existing code ...
    register_my_blocks()
    # ... rest of setup ...
```

## Advanced Block Features

### Working with Multiple Inputs

```python
def execute_combine_data(context: dict) -> dict:
    inputs = context["inputs"]
    
    # Get multiple inputs
    text1 = inputs.get("text1", "")
    text2 = inputs.get("text2", "")
    separator = context["parameters"].get("separator", " ")
    
    result = f"{text1}{separator}{text2}"
    
    return {"combined": result}

combine_block = BlockDefinition(
    block_type="custom_combine",
    name="Combine Text",
    category=BlockType.DATA,
    input_ports=[
        BlockPort("text1", DataType.STRING, required=True),
        BlockPort("text2", DataType.STRING, required=True)
    ],
    output_ports=[
        BlockPort("combined", DataType.STRING)
    ],
    parameters=[
        BlockParameter("separator", str, " ", description="Separator between texts")
    ],
    execute_func=execute_combine_data,
    icon="🔗"
)
```

### Accessing Shared Context

```python
def execute_with_context(context: dict) -> dict:
    # Access shared workflow context
    shared_context = context["context"]
    
    # Get/set global variables
    variables = shared_context.get("variables", {})
    my_var = variables.get("my_variable", None)
    
    # Access browser instances
    browser_instances = shared_context.get("browser_instances", {})
    
    # Store data for other blocks
    variables["computed_result"] = "some value"
    
    return {"result": my_var}
```

### Error Handling

```python
import logging

logger = logging.getLogger(__name__)

def execute_with_errors(context: dict) -> dict:
    params = context["parameters"]
    url = params.get("url", "")
    
    if not url:
        # Raise clear error messages
        raise ValueError("URL parameter is required")
    
    try:
        # Your logic here
        result = perform_operation(url)
        
        logger.info(f"Operation successful: {result}")
        return {"result": result, "success": True}
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        # Re-raise or return error state
        return {"result": None, "success": False, "error": str(e)}
```

### Parameter Validation

```python
def validate_positive_number(value):
    """Custom validation function"""
    return value > 0

my_param = BlockParameter(
    name="count",
    param_type=int,
    default_value=1,
    required=True,
    description="Must be positive",
    validation_func=validate_positive_number
)
```

### Dropdown Parameters

```python
BlockParameter(
    name="method",
    param_type=str,
    default_value="POST",
    options=["GET", "POST", "PUT", "DELETE"],
    description="HTTP method"
)
```

## Testing Your Block

### Unit Test Example

```python
import unittest
from core import BlockRegistry, create_block, BlockEngine

class TestMyBlock(unittest.TestCase):
    
    def setUp(self):
        """Register your block before tests"""
        from my_blocks import register_my_blocks
        register_my_blocks()
        self.engine = BlockEngine()
    
    def test_block_execution(self):
        """Test basic block execution"""
        # Create block instance
        block = create_block("custom_my_block")
        block.set_parameter("my_parameter", "test_value")
        
        # Add to engine
        self.engine.add_block(block)
        
        # Execute
        input_data = {"input_port_name": "test_input"}
        result = self.engine.execute_block(block, input_data)
        
        # Assert outputs
        self.assertIn("output_port_name", result)
        self.assertTrue(result["success"])
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        block = create_block("custom_my_block")
        
        # This should work
        block.set_parameter("my_parameter", "valid_value")
        
        # This should raise ValueError if validation fails
        with self.assertRaises(ValueError):
            block.set_parameter("invalid_param", "value")

if __name__ == "__main__":
    unittest.main()
```

### Manual Testing

1. Create your block file in `blocks/` directory
2. Register it in `main.py`
3. Run the application: `python main.py`
4. Find your block in the palette under its category
5. Drag to canvas and configure
6. Connect to other blocks and execute

## Best Practices

### 1. Naming Conventions
- Block types: `category_description` (e.g., `web_click`, `data_transform`)
- Parameter names: `snake_case` (e.g., `retry_count`, `timeout_seconds`)
- Output ports: descriptive names (e.g., `success`, `error_message`, `data`)

### 2. Documentation
- Always provide clear descriptions for blocks, ports, and parameters
- Use type hints in execution functions
- Add docstrings explaining purpose and behavior

### 3. Error Handling
- Validate inputs before processing
- Provide clear error messages
- Log important events using Python's logging module
- Don't swallow exceptions unless intentional

### 4. Data Types
Choose appropriate data types:
- `DataType.STRING` - Text data
- `DataType.NUMBER` - Numeric values
- `DataType.BOOLEAN` - True/False
- `DataType.OBJECT` - JSON objects, dictionaries
- `DataType.ARRAY` - Lists
- `DataType.ANY` - Accept any type
- `DataType.BROWSER` - Selenium browser instance
- `DataType.ELEMENT` - Web element reference

### 5. Resource Management
- Clean up resources (close files, connections, browsers)
- Use context managers where appropriate
- Store reusable resources in shared context

### 6. Performance
- Avoid blocking operations when possible
- Implement timeouts for external calls
- Consider adding progress indicators for long operations

### 7. Security
- Never hardcode credentials
- Validate and sanitize inputs
- Add warnings for potentially dangerous operations
- Respect rate limits and robots.txt

## Example: Complete Custom Block Module

```python
"""
Custom Email Blocks - Send automated emails
"""

from core import (BlockDefinition, BlockPort, BlockParameter, 
                  BlockType, DataType, register_block)
import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)


def execute_send_email(context: dict) -> dict:
    """Send an email"""
    params = context["parameters"]
    
    # Get parameters
    to_email = params.get("to_email", "")
    subject = params.get("subject", "")
    body = params.get("body", "")
    smtp_server = params.get("smtp_server", "smtp.gmail.com")
    smtp_port = params.get("smtp_port", 587)
    
    # Validate
    if not to_email or not subject:
        raise ValueError("Email and subject are required")
    
    try:
        # Note: This is simplified - real implementation needs auth
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = to_email
        
        # Would need credentials from context or secure storage
        # This is just a demonstration
        
        logger.info(f"Would send email to {to_email}")
        
        return {
            "sent": True,
            "recipient": to_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


send_email_block = BlockDefinition(
    block_type="email_send",
    name="Send Email",
    category=BlockType.UTILITY,
    description="Send an email via SMTP",
    input_ports=[
        BlockPort("body", DataType.STRING, required=False)
    ],
    output_ports=[
        BlockPort("sent", DataType.BOOLEAN),
        BlockPort("recipient", DataType.STRING)
    ],
    parameters=[
        BlockParameter("to_email", str, "", required=True),
        BlockParameter("subject", str, "", required=True),
        BlockParameter("body", str, ""),
        BlockParameter("smtp_server", str, "smtp.gmail.com"),
        BlockParameter("smtp_port", int, 587)
    ],
    execute_func=execute_send_email,
    icon="📧",
    color="#88C0D0"
)


def register_email_blocks():
    """Register all email blocks"""
    register_block(send_email_block)
    logger.info("Registered email blocks")
```

## Need Help?

- Check existing blocks in `blocks/` for reference implementations
- Review the core engine code in `core/block_engine.py`
- Test incrementally - start simple, add complexity gradually
- Use logging extensively during development

Happy automating! 🚀
