"""
Executor - High-level workflow execution manager
Handles workflow loading, execution, error handling, and result reporting.
"""

from typing import Dict, List, Optional, Callable
from core.block_engine import BlockEngine, BlockInstance
from core.block_registry import BlockRegistry
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class ExecutionContext:
    """Shared context for workflow execution"""
    
    def __init__(self):
        self.variables: Dict[str, any] = {}
        self.browser_instances: Dict[str, any] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.execution_log: List[Dict] = []
    
    def set_variable(self, name: str, value: any):
        """Set a global variable"""
        self.variables[name] = value
        logger.debug(f"Set variable: {name} = {value}")
    
    def get_variable(self, name: str, default=None) -> any:
        """Get a global variable"""
        return self.variables.get(name, default)
    
    def log_event(self, event_type: str, message: str, block_id: Optional[str] = None):
        """Log an execution event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "block_id": block_id
        }
        self.execution_log.append(event)
    
    def cleanup(self):
        """Cleanup resources (close browsers, etc.)"""
        # Close all browser instances
        for browser_id, browser in self.browser_instances.items():
            try:
                if hasattr(browser, 'quit'):
                    browser.quit()
                    logger.info(f"Closed browser instance: {browser_id}")
            except Exception as e:
                logger.error(f"Error closing browser {browser_id}: {e}")
        
        self.browser_instances.clear()


class WorkflowExecutor:
    """
    High-level executor for managing workflow execution.
    Provides hooks for monitoring, error handling, and result collection.
    """
    
    def __init__(self):
        self.engine = BlockEngine()
        self.context = ExecutionContext()
        self.callbacks: Dict[str, List[Callable]] = {
            "on_start": [],
            "on_block_start": [],
            "on_block_end": [],
            "on_block_error": [],
            "on_complete": [],
            "on_error": []
        }
    
    def add_callback(self, event: str, callback: Callable):
        """Register a callback for an execution event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown callback event: {event}")
    
    def _trigger_callbacks(self, event: str, *args, **kwargs):
        """Trigger all callbacks for an event"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    def load_workflow(self, workflow_data: Dict):
        """
        Load a workflow from serialized data.
        
        Args:
            workflow_data: Dictionary containing blocks and connections
        """
        try:
            # Clear existing workflow
            self.engine.blocks.clear()
            
            # Create block instances
            for block_data in workflow_data.get("blocks", []):
                block_type = block_data.get("type")
                definition = BlockRegistry.get_definition(block_type)
                
                if not definition:
                    logger.warning(f"Block type {block_type} not found, skipping")
                    continue
                
                instance = BlockInstance.from_dict(block_data, definition)
                self.engine.add_block(instance)
            
            logger.info(f"Loaded workflow with {len(self.engine.blocks)} blocks")
            
        except Exception as e:
            logger.error(f"Error loading workflow: {e}")
            raise
    
    def execute(self, start_block_id: Optional[str] = None) -> Dict:
        """
        Execute the loaded workflow.
        
        Args:
            start_block_id: Optional specific block to start from
        
        Returns:
            Dictionary containing execution results and statistics
        """
        self.context.start_time = datetime.now()
        self.context.log_event("workflow_start", "Workflow execution started")
        
        try:
            # Validate workflow before execution
            issues = self.engine.validate_workflow()
            if issues:
                logger.warning("Workflow validation issues:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
            
            # Trigger start callbacks
            self._trigger_callbacks("on_start", self.engine)
            
            # Share context with engine
            self.engine.context = self.context.__dict__
            
            # Execute workflow
            results = self.engine.execute_workflow(start_block_id)
            
            # Add execution metadata
            self.context.end_time = datetime.now()
            execution_time = (self.context.end_time - self.context.start_time).total_seconds()
            
            results.update({
                "execution_time": execution_time,
                "start_time": self.context.start_time.isoformat(),
                "end_time": self.context.end_time.isoformat(),
                "execution_log": self.context.execution_log
            })
            
            self.context.log_event("workflow_complete", f"Workflow completed in {execution_time:.2f}s")
            
            # Trigger completion callbacks
            self._trigger_callbacks("on_complete", results)
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            self.context.log_event("workflow_error", str(e))
            self._trigger_callbacks("on_error", e)
            
            return {
                "success": False,
                "error": str(e),
                "execution_log": self.context.execution_log
            }
        
        finally:
            # Cleanup resources
            self.context.cleanup()
    
    def execute_single_block(self, block_id: str, input_data: Dict = None) -> Dict:
        """
        Execute a single block for testing purposes.
        
        Args:
            block_id: ID of the block to execute
            input_data: Input data for the block
        
        Returns:
            Block output data
        """
        if block_id not in self.engine.blocks:
            raise ValueError(f"Block {block_id} not found")
        
        block = self.engine.blocks[block_id]
        input_data = input_data or {}
        
        try:
            self._trigger_callbacks("on_block_start", block)
            output = self.engine.execute_block(block, input_data)
            self._trigger_callbacks("on_block_end", block, output)
            return output
        
        except Exception as e:
            self._trigger_callbacks("on_block_error", block, e)
            raise
    
    def get_execution_report(self) -> Dict:
        """Generate a detailed execution report"""
        stats = self.engine.get_statistics()
        
        return {
            "workflow_info": {
                "total_blocks": stats["total_blocks"],
                "executed_blocks": stats["executed_blocks"],
                "failed_blocks": stats["failed_blocks"],
                "total_connections": stats["total_connections"]
            },
            "timing": {
                "start_time": self.context.start_time.isoformat() if self.context.start_time else None,
                "end_time": self.context.end_time.isoformat() if self.context.end_time else None,
                "duration": (self.context.end_time - self.context.start_time).total_seconds() 
                           if self.context.start_time and self.context.end_time else None
            },
            "blocks": [
                {
                    "id": block.id,
                    "name": block.definition.name,
                    "type": block.definition.block_type,
                    "executed": block.executed,
                    "has_error": block.error is not None,
                    "error": block.error
                }
                for block in self.engine.blocks.values()
            ],
            "execution_log": self.context.execution_log,
            "variables": self.context.variables
        }
    
    def reset(self):
        """Reset executor state"""
        self.engine.blocks.clear()
        self.context = ExecutionContext()
        logger.info("Executor reset complete")
    
    def validate(self) -> List[str]:
        """Validate current workflow"""
        return self.engine.validate_workflow()


class AsyncWorkflowExecutor(WorkflowExecutor):
    """
    Asynchronous version of WorkflowExecutor (placeholder for future implementation).
    Can be extended to support async/await execution for long-running workflows.
    """
    
    async def execute_async(self, start_block_id: Optional[str] = None) -> Dict:
        """
        Asynchronous workflow execution.
        TODO: Implement async execution support
        """
        raise NotImplementedError("Async execution not yet implemented")
