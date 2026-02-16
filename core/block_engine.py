"""
Block Engine - Core execution engine for visual automation blocks
This module handles block definitions, validation, and execution logic.
"""

from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockType(Enum):
    """Enumeration of block categories"""
    WEB_AUTOMATION = "web_automation"
    HTTP_REQUEST = "http_request"
    LOGIC = "logic"
    DATA = "data"
    CONTROL_FLOW = "control_flow"
    VARIABLE = "variable"
    UTILITY = "utility"


class DataType(Enum):
    """Data types for block inputs/outputs"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    ANY = "any"
    ELEMENT = "element"  # Web element reference
    BROWSER = "browser"  # Browser instance
    RESPONSE = "response"  # HTTP response


@dataclass
class BlockPort:
    """Represents an input or output port on a block"""
    name: str
    data_type: DataType
    required: bool = True
    description: str = ""
    default_value: Any = None


@dataclass
class BlockParameter:
    """Configuration parameter for a block"""
    name: str
    param_type: type
    default_value: Any = None
    required: bool = False
    description: str = ""
    validation_func: Optional[Callable] = None
    options: Optional[List[Any]] = None  # For dropdown selections


@dataclass
class BlockDefinition:
    """
    Defines the structure and behavior of an automation block.
    This is the template used to create block instances.
    """
    block_type: str
    name: str
    category: BlockType
    description: str = ""
    
    # Ports
    input_ports: List[BlockPort] = field(default_factory=list)
    output_ports: List[BlockPort] = field(default_factory=list)
    
    # Parameters (configuration)
    parameters: List[BlockParameter] = field(default_factory=list)
    
    # Execution function
    execute_func: Optional[Callable] = None
    
    # Visual properties
    color: str = "#2E3440"
    icon: str = "⚙️"
    
    # Metadata
    version: str = "1.0.0"
    author: str = "System"
    
    def validate(self) -> bool:
        """Validate block definition"""
        if not self.name or not self.block_type:
            raise ValueError("Block must have name and type")
        if not self.execute_func:
            raise ValueError(f"Block {self.name} missing execute function")
        return True


@dataclass
class BlockInstance:
    """
    A specific instance of a block in the workflow.
    Contains runtime state and connections.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    definition: BlockDefinition = None
    
    # Position on canvas
    x: float = 0
    y: float = 0
    
    # Configuration values
    parameter_values: Dict[str, Any] = field(default_factory=dict)
    
    # Connections to other blocks
    connections: Dict[str, List[str]] = field(default_factory=dict)  # {output_port: [target_block_ids]}
    
    # Runtime state
    executed: bool = False
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def set_parameter(self, param_name: str, value: Any):
        """Set a parameter value with validation"""
        param_def = next((p for p in self.definition.parameters if p.name == param_name), None)
        
        if not param_def:
            raise ValueError(f"Parameter {param_name} not found in block definition")
        
        # Type validation
        if not isinstance(value, param_def.param_type) and value is not None:
            try:
                value = param_def.param_type(value)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid type for {param_name}. Expected {param_def.param_type}")
        
        # Custom validation
        if param_def.validation_func and not param_def.validation_func(value):
            raise ValueError(f"Validation failed for parameter {param_name}")
        
        self.parameter_values[param_name] = value
        logger.debug(f"Block {self.id}: Set {param_name} = {value}")
    
    def get_parameter(self, param_name: str) -> Any:
        """Get parameter value or default"""
        if param_name in self.parameter_values:
            return self.parameter_values[param_name]
        
        param_def = next((p for p in self.definition.parameters if p.name == param_name), None)
        return param_def.default_value if param_def else None
    
    def connect_to(self, output_port: str, target_block_id: str):
        """Connect this block's output to another block's input"""
        if output_port not in [p.name for p in self.definition.output_ports]:
            raise ValueError(f"Output port {output_port} not found")
        
        if output_port not in self.connections:
            self.connections[output_port] = []
        
        if target_block_id not in self.connections[output_port]:
            self.connections[output_port].append(target_block_id)
            logger.info(f"Connected {self.id}:{output_port} -> {target_block_id}")
    
    def disconnect(self, output_port: str, target_block_id: str):
        """Remove a connection"""
        if output_port in self.connections:
            if target_block_id in self.connections[output_port]:
                self.connections[output_port].remove(target_block_id)
                logger.info(f"Disconnected {self.id}:{output_port} -> {target_block_id}")
    
    def reset(self):
        """Reset execution state"""
        self.executed = False
        self.output_data = {}
        self.error = None
    
    def to_dict(self) -> Dict:
        """Serialize block instance to dictionary"""
        return {
            "id": self.id,
            "type": self.definition.block_type,
            "x": self.x,
            "y": self.y,
            "parameters": self.parameter_values,
            "connections": self.connections
        }
    
    @classmethod
    def from_dict(cls, data: Dict, definition: BlockDefinition) -> 'BlockInstance':
        """Deserialize block instance from dictionary"""
        instance = cls(
            id=data.get("id", str(uuid.uuid4())),
            definition=definition,
            x=data.get("x", 0),
            y=data.get("y", 0),
            parameter_values=data.get("parameters", {}),
            connections=data.get("connections", {})
        )
        return instance


class BlockEngine:
    """
    Core engine responsible for executing blocks and managing workflow execution.
    Handles dependency resolution, data flow, and error management.
    """
    
    def __init__(self):
        self.blocks: Dict[str, BlockInstance] = {}
        self.execution_order: List[str] = []
        self.context: Dict[str, Any] = {}  # Shared execution context
        self.logger = logging.getLogger(__name__)
    
    def add_block(self, block: BlockInstance):
        """Add a block to the engine"""
        self.blocks[block.id] = block
        self.logger.info(f"Added block: {block.definition.name} ({block.id})")
    
    def remove_block(self, block_id: str):
        """Remove a block and its connections"""
        if block_id in self.blocks:
            # Remove all connections to this block
            for block in self.blocks.values():
                for output_port, targets in list(block.connections.items()):
                    if block_id in targets:
                        block.disconnect(output_port, block_id)
            
            del self.blocks[block_id]
            self.logger.info(f"Removed block: {block_id}")
    
    def calculate_execution_order(self) -> List[str]:
        """
        Calculate the order of block execution using topological sort.
        Ensures dependencies are executed before dependent blocks.
        """
        # Build dependency graph
        in_degree = {block_id: 0 for block_id in self.blocks}
        graph = {block_id: [] for block_id in self.blocks}
        
        for block_id, block in self.blocks.items():
            for targets in block.connections.values():
                for target_id in targets:
                    if target_id in self.blocks:
                        graph[block_id].append(target_id)
                        in_degree[target_id] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [block_id for block_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(self.blocks):
            raise RuntimeError("Circular dependency detected in workflow")
        
        self.execution_order = execution_order
        self.logger.info(f"Execution order: {execution_order}")
        return execution_order
    
    def execute_block(self, block: BlockInstance, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single block with given input data.
        Returns output data from the block.
        """
        try:
            self.logger.info(f"Executing block: {block.definition.name} ({block.id})")
            
            # Prepare execution context
            execution_context = {
                "block_id": block.id,
                "parameters": block.parameter_values,
                "inputs": input_data,
                "context": self.context
            }
            
            # Execute the block's function
            if block.definition.execute_func:
                output = block.definition.execute_func(execution_context)
                
                if not isinstance(output, dict):
                    output = {"result": output}
                
                block.output_data = output
                block.executed = True
                block.error = None
                
                self.logger.info(f"Block {block.id} executed successfully")
                return output
            else:
                raise RuntimeError(f"Block {block.definition.name} has no execute function")
        
        except Exception as e:
            self.logger.error(f"Error executing block {block.id}: {str(e)}")
            block.error = str(e)
            block.executed = False
            raise
    
    def execute_workflow(self, start_block_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the entire workflow or from a specific starting block.
        Returns execution results and statistics.
        """
        self.logger.info("="*50)
        self.logger.info("Starting workflow execution")
        self.logger.info("="*50)
        
        # Reset all blocks
        for block in self.blocks.values():
            block.reset()
        
        # Calculate execution order
        if not start_block_id:
            execution_order = self.calculate_execution_order()
        else:
            # Execute from specific block (for testing)
            execution_order = self._get_downstream_blocks(start_block_id)
        
        executed_blocks = []
        failed_blocks = []
        
        # Execute blocks in order
        for block_id in execution_order:
            block = self.blocks[block_id]
            
            try:
                # Gather input data from connected blocks
                input_data = self._gather_input_data(block)
                
                # Execute block
                self.execute_block(block, input_data)
                executed_blocks.append(block_id)
                
            except Exception as e:
                self.logger.error(f"Failed to execute block {block_id}: {e}")
                failed_blocks.append({"block_id": block_id, "error": str(e)})
                
                # Stop execution on error (can be made configurable)
                break
        
        # Execution summary
        results = {
            "success": len(failed_blocks) == 0,
            "executed_count": len(executed_blocks),
            "failed_count": len(failed_blocks),
            "executed_blocks": executed_blocks,
            "failed_blocks": failed_blocks,
            "output_data": {bid: self.blocks[bid].output_data for bid in executed_blocks}
        }
        
        self.logger.info(f"Workflow execution completed: {results['executed_count']} blocks executed, {results['failed_count']} failed")
        return results
    
    def _gather_input_data(self, block: BlockInstance) -> Dict[str, Any]:
        """Gather input data from connected predecessor blocks"""
        input_data = {}
        
        # Find blocks that connect to this block
        for other_id, other_block in self.blocks.items():
            for output_port, targets in other_block.connections.items():
                if block.id in targets and other_block.executed:
                    # Get the output data from the connected port
                    if output_port in other_block.output_data:
                        input_data[output_port] = other_block.output_data[output_port]
        
        return input_data
    
    def _get_downstream_blocks(self, start_block_id: str) -> List[str]:
        """Get all blocks downstream from a starting block"""
        visited = set()
        queue = [start_block_id]
        order = []
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            order.append(current)
            
            if current in self.blocks:
                block = self.blocks[current]
                for targets in block.connections.values():
                    queue.extend(targets)
        
        return order
    
    def validate_workflow(self) -> List[str]:
        """Validate workflow for common issues"""
        issues = []
        
        # Check for disconnected blocks
        for block_id, block in self.blocks.items():
            has_input = any(
                block_id in targets 
                for b in self.blocks.values() 
                for targets in b.connections.values()
            )
            has_output = any(block.connections.values())
            
            if not has_input and not has_output and len(self.blocks) > 1:
                issues.append(f"Block {block.definition.name} ({block_id}) is disconnected")
        
        # Check for missing required parameters
        for block in self.blocks.values():
            for param in block.definition.parameters:
                if param.required and param.name not in block.parameter_values:
                    issues.append(f"Block {block.definition.name} missing required parameter: {param.name}")
        
        return issues
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        return {
            "total_blocks": len(self.blocks),
            "executed_blocks": sum(1 for b in self.blocks.values() if b.executed),
            "failed_blocks": sum(1 for b in self.blocks.values() if b.error),
            "total_connections": sum(len(targets) for b in self.blocks.values() for targets in b.connections.values())
        }
