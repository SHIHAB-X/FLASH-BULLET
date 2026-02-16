"""
Block Registry - Central registry for all available block types
Manages block definitions and provides factory methods for creating block instances.
"""

from typing import Dict, List, Optional
from core.block_engine import BlockDefinition, BlockInstance, BlockType
import logging

logger = logging.getLogger(__name__)


class BlockRegistry:
    """
    Singleton registry that manages all available block definitions.
    Provides methods to register, retrieve, and instantiate blocks.
    """
    
    _instance = None
    _blocks: Dict[str, BlockDefinition] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BlockRegistry, cls).__new__(cls)
            cls._blocks = {}
        return cls._instance
    
    @classmethod
    def register(cls, block_def: BlockDefinition):
        """Register a new block definition"""
        try:
            block_def.validate()
            cls._blocks[block_def.block_type] = block_def
            logger.info(f"Registered block: {block_def.name} ({block_def.block_type})")
        except Exception as e:
            logger.error(f"Failed to register block {block_def.name}: {e}")
            raise
    
    @classmethod
    def unregister(cls, block_type: str):
        """Remove a block definition from registry"""
        if block_type in cls._blocks:
            del cls._blocks[block_type]
            logger.info(f"Unregistered block type: {block_type}")
    
    @classmethod
    def get_definition(cls, block_type: str) -> Optional[BlockDefinition]:
        """Get a block definition by type"""
        return cls._blocks.get(block_type)
    
    @classmethod
    def create_instance(cls, block_type: str, **kwargs) -> BlockInstance:
        """
        Factory method to create a block instance from its type.
        
        Args:
            block_type: The type identifier of the block
            **kwargs: Additional parameters for BlockInstance constructor
        
        Returns:
            A new BlockInstance with the specified definition
        """
        definition = cls.get_definition(block_type)
        
        if not definition:
            raise ValueError(f"Block type '{block_type}' not found in registry")
        
        instance = BlockInstance(definition=definition, **kwargs)
        
        # Set default parameter values
        for param in definition.parameters:
            if param.default_value is not None:
                instance.parameter_values[param.name] = param.default_value
        
        logger.debug(f"Created instance of {definition.name}")
        return instance
    
    @classmethod
    def get_all_blocks(cls) -> Dict[str, BlockDefinition]:
        """Get all registered block definitions"""
        return cls._blocks.copy()
    
    @classmethod
    def get_blocks_by_category(cls, category: BlockType) -> List[BlockDefinition]:
        """Get all blocks in a specific category"""
        return [
            block for block in cls._blocks.values() 
            if block.category == category
        ]
    
    @classmethod
    def search_blocks(cls, query: str) -> List[BlockDefinition]:
        """Search blocks by name or description"""
        query = query.lower()
        return [
            block for block in cls._blocks.values()
            if query in block.name.lower() or query in block.description.lower()
        ]
    
    @classmethod
    def get_categories(cls) -> List[BlockType]:
        """Get all unique categories from registered blocks"""
        return list(set(block.category for block in cls._blocks.values()))
    
    @classmethod
    def clear(cls):
        """Clear all registered blocks (useful for testing)"""
        cls._blocks.clear()
        logger.warning("Cleared all registered blocks")
    
    @classmethod
    def get_block_count(cls) -> int:
        """Get total number of registered blocks"""
        return len(cls._blocks)
    
    @classmethod
    def export_registry(cls) -> Dict:
        """Export registry metadata for documentation/debugging"""
        return {
            "total_blocks": len(cls._blocks),
            "categories": [cat.value for cat in cls.get_categories()],
            "blocks": [
                {
                    "type": block.block_type,
                    "name": block.name,
                    "category": block.category.value,
                    "description": block.description,
                    "version": block.version,
                    "inputs": [p.name for p in block.input_ports],
                    "outputs": [p.name for p in block.output_ports],
                    "parameters": [p.name for p in block.parameters]
                }
                for block in cls._blocks.values()
            ]
        }


# Convenience functions for common operations
def register_block(block_def: BlockDefinition):
    """Convenience function to register a block"""
    BlockRegistry.register(block_def)


def create_block(block_type: str, **kwargs) -> BlockInstance:
    """Convenience function to create a block instance"""
    return BlockRegistry.create_instance(block_type, **kwargs)


def get_block(block_type: str) -> Optional[BlockDefinition]:
    """Convenience function to get a block definition"""
    return BlockRegistry.get_definition(block_type)
