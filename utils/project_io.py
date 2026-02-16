"""
Project I/O - Save and load workflow projects
Handles JSON serialization/deserialization of workflows
"""

import json
import os
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProjectIO:
    """
    Handles saving and loading of workflow projects.
    Projects are saved as JSON files with metadata.
    """
    
    def __init__(self):
        self.version = "1.0.0"
    
    def save(self, workflow_data: Dict, filepath: str):
        """
        Save workflow to JSON file.
        
        Args:
            workflow_data: Workflow data dictionary
            filepath: Target file path
        """
        try:
            # Add metadata
            project = {
                "version": self.version,
                "created_at": datetime.now().isoformat(),
                "workflow": workflow_data
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save with pretty formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved project to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            raise
    
    def load(self, filepath: str) -> Dict:
        """
        Load workflow from JSON file.
        
        Args:
            filepath: Source file path
        
        Returns:
            Workflow data dictionary
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                project = json.load(f)
            
            # Validate version (basic check)
            if "version" not in project:
                logger.warning("Loading project without version info")
            
            # Extract workflow data
            workflow_data = project.get("workflow", project)
            
            logger.info(f"Loaded project from: {filepath}")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            raise
    
    def export_template(self, workflow_data: Dict, filepath: str, name: str = "Template", 
                       description: str = ""):
        """
        Export workflow as a reusable template.
        
        Args:
            workflow_data: Workflow data
            filepath: Target file path
            name: Template name
            description: Template description
        """
        try:
            template = {
                "template_name": name,
                "description": description,
                "version": self.version,
                "created_at": datetime.now().isoformat(),
                "workflow": workflow_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported template to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            raise
    
    def validate_project_file(self, filepath: str) -> bool:
        """
        Validate if a file is a valid project file.
        
        Args:
            filepath: File path to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Basic validation
            if isinstance(data, dict):
                # Check for workflow data
                workflow = data.get("workflow", data)
                if "blocks" in workflow:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
    
    def backup_project(self, filepath: str):
        """
        Create a backup of an existing project file.
        
        Args:
            filepath: Original file path
        """
        try:
            if not os.path.exists(filepath):
                return
            
            # Create backup filename
            backup_name = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Copy file
            with open(filepath, 'r') as source:
                content = source.read()
            
            with open(backup_name, 'w') as backup:
                backup.write(content)
            
            logger.info(f"Created backup: {backup_name}")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")


class WorkflowValidator:
    """Validates workflow structure and integrity"""
    
    @staticmethod
    def validate(workflow_data: Dict) -> tuple[bool, list[str]]:
        """
        Validate workflow data structure.
        
        Args:
            workflow_data: Workflow data to validate
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check structure
        if not isinstance(workflow_data, dict):
            issues.append("Workflow data must be a dictionary")
            return False, issues
        
        # Check for blocks
        if "blocks" not in workflow_data:
            issues.append("Workflow missing 'blocks' key")
            return False, issues
        
        blocks = workflow_data["blocks"]
        if not isinstance(blocks, list):
            issues.append("Blocks must be a list")
            return False, issues
        
        # Validate each block
        block_ids = set()
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                issues.append(f"Block {i} is not a dictionary")
                continue
            
            # Check required fields
            if "id" not in block:
                issues.append(f"Block {i} missing 'id'")
            else:
                block_id = block["id"]
                if block_id in block_ids:
                    issues.append(f"Duplicate block ID: {block_id}")
                block_ids.add(block_id)
            
            if "type" not in block:
                issues.append(f"Block {i} missing 'type'")
        
        # Validate connections
        for block in blocks:
            connections = block.get("connections", {})
            for port, targets in connections.items():
                if not isinstance(targets, list):
                    issues.append(f"Block {block.get('id', '?')} connections must be lists")
                    continue
                
                for target_id in targets:
                    if target_id not in block_ids:
                        issues.append(f"Connection to non-existent block: {target_id}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
