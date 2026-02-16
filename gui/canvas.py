"""
Workflow Canvas - Interactive drag-and-drop canvas for visual block programming
"""

import tkinter as tk
from tkinter import Canvas
from typing import Dict, List, Optional, Tuple
from core import BlockInstance, BlockRegistry, WorkflowExecutor
import logging

logger = logging.getLogger(__name__)


class VisualBlock:
    """Visual representation of a block on the canvas"""
    
    def __init__(self, canvas: Canvas, instance: BlockInstance, x: float, y: float):
        self.canvas = canvas
        self.instance = instance
        self.x = x
        self.y = y
        
        # Visual properties
        self.width = 180
        self.height = 80
        self.selected = False
        
        # Canvas item IDs
        self.rect_id = None
        self.text_id = None
        self.icon_id = None
        self.input_ports: Dict[str, int] = {}
        self.output_ports: Dict[str, int] = {}
        
        self.draw()
    
    def draw(self):
        """Draw the block on canvas"""
        # Main rectangle
        color = self.instance.definition.color
        outline_color = "#4C566A" if not self.selected else "#88C0D0"
        outline_width = 2 if not self.selected else 4
        
        self.rect_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill=color, outline=outline_color, width=outline_width,
            tags=("block", self.instance.id)
        )
        
        # Icon
        icon = self.instance.definition.icon
        self.icon_id = self.canvas.create_text(
            self.x + 20, self.y + 15,
            text=icon, font=("Arial", 16), fill="white",
            tags=("block", self.instance.id)
        )
        
        # Block name
        name = self.instance.definition.name
        if len(name) > 18:
            name = name[:15] + "..."
        
        self.text_id = self.canvas.create_text(
            self.x + self.width / 2, self.y + self.height / 2,
            text=name, font=("Arial", 11, "bold"), fill="white",
            tags=("block", self.instance.id)
        )
        
        # Status indicator
        if self.instance.executed:
            status_color = "#A3BE8C" if not self.instance.error else "#BF616A"
            self.canvas.create_oval(
                self.x + self.width - 15, self.y + 5,
                self.x + self.width - 5, self.y + 15,
                fill=status_color, outline="",
                tags=("block", self.instance.id)
            )
        
        # Draw ports
        self._draw_ports()
    
    def _draw_ports(self):
        """Draw input and output ports"""
        # Input ports (left side)
        port_spacing = self.height / (len(self.instance.definition.input_ports) + 1)
        for i, port in enumerate(self.instance.definition.input_ports):
            port_y = self.y + port_spacing * (i + 1)
            port_id = self.canvas.create_oval(
                self.x - 6, port_y - 6,
                self.x + 6, port_y + 6,
                fill="#5E81AC", outline="#4C566A", width=2,
                tags=("port", "input_port", self.instance.id, port.name)
            )
            self.input_ports[port.name] = port_id
        
        # Output ports (right side)
        port_spacing = self.height / (len(self.instance.definition.output_ports) + 1)
        for i, port in enumerate(self.instance.definition.output_ports):
            port_y = self.y + port_spacing * (i + 1)
            port_id = self.canvas.create_oval(
                self.x + self.width - 6, port_y - 6,
                self.x + self.width + 6, port_y + 6,
                fill="#88C0D0", outline="#4C566A", width=2,
                tags=("port", "output_port", self.instance.id, port.name)
            )
            self.output_ports[port.name] = port_id
    
    def move(self, dx: float, dy: float):
        """Move block by delta"""
        self.x += dx
        self.y += dy
        self.instance.x = self.x
        self.instance.y = self.y
        self.canvas.move(self.instance.id, dx, dy)
    
    def delete(self):
        """Remove block from canvas"""
        self.canvas.delete(self.instance.id)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected
        outline_color = "#88C0D0" if selected else "#4C566A"
        outline_width = 4 if selected else 2
        self.canvas.itemconfig(self.rect_id, outline=outline_color, width=outline_width)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside block"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def get_port_position(self, port_name: str, is_output: bool) -> Tuple[float, float]:
        """Get the absolute position of a port"""
        ports = self.output_ports if is_output else self.input_ports
        if port_name in ports:
            coords = self.canvas.coords(ports[port_name])
            if coords:
                return ((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2)
        return (0, 0)


class Connection:
    """Visual representation of a connection between blocks"""
    
    def __init__(self, canvas: Canvas, from_block: VisualBlock, from_port: str,
                 to_block: VisualBlock, to_port: str):
        self.canvas = canvas
        self.from_block = from_block
        self.from_port = from_port
        self.to_block = to_block
        self.to_port = to_port
        self.line_id = None
        
        self.draw()
    
    def draw(self):
        """Draw connection line"""
        x1, y1 = self.from_block.get_port_position(self.from_port, True)
        x2, y2 = self.to_block.get_port_position(self.to_port, False)
        
        # Bezier curve control points for smooth connection
        cx1 = x1 + (x2 - x1) / 3
        cy1 = y1
        cx2 = x2 - (x2 - x1) / 3
        cy2 = y2
        
        self.line_id = self.canvas.create_line(
            x1, y1, cx1, cy1, cx2, cy2, x2, y2,
            smooth=True, width=3, fill="#81A1C1",
            arrow=tk.LAST, tags=("connection",)
        )
        
        # Send to back
        self.canvas.tag_lower(self.line_id)
    
    def update(self):
        """Update connection position when blocks move"""
        if self.line_id:
            self.canvas.delete(self.line_id)
        self.draw()
    
    def delete(self):
        """Remove connection"""
        if self.line_id:
            self.canvas.delete(self.line_id)


class WorkflowCanvas(Canvas):
    """
    Main canvas for drag-and-drop workflow creation.
    Handles block placement, connections, and user interactions.
    """
    
    def __init__(self, parent, executor: WorkflowExecutor):
        super().__init__(
            parent,
            bg="#2E3440",
            highlightthickness=0
        )
        
        self.executor = executor
        self.blocks: Dict[str, VisualBlock] = {}
        self.connections: List[Connection] = []
        
        # Interaction state
        self.selected_block: Optional[VisualBlock] = None
        self.drag_start: Optional[Tuple[float, float]] = None
        self.connecting_from: Optional[Tuple[VisualBlock, str]] = None
        self.temp_line = None
        
        # View state
        self.zoom_level = 1.0
        self.pan_offset = [0, 0]
        
        # Setup interactions
        self._setup_bindings()
        
        # Draw grid
        self._draw_grid()
        
        logger.info("Canvas initialized")
    
    def _setup_bindings(self):
        """Setup mouse and keyboard bindings"""
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Double-Button-1>", self.on_double_click)
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<Delete>", self.on_delete)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-c>", self.copy_selected)
        self.bind("<Control-v>", self.paste)
    
    def _draw_grid(self):
        """Draw background grid"""
        grid_size = 30
        width = self.winfo_width() or 1000
        height = self.winfo_height() or 800
        
        # Vertical lines
        for x in range(0, width, grid_size):
            self.create_line(x, 0, x, height, fill="#3B4252", tags="grid")
        
        # Horizontal lines
        for y in range(0, height, grid_size):
            self.create_line(0, y, width, y, fill="#3B4252", tags="grid")
        
        self.tag_lower("grid")
    
    def add_block(self, block_type: str, x: Optional[float] = None, y: Optional[float] = None):
        """Add a new block to the canvas"""
        try:
            # Create block instance
            instance = BlockRegistry.create_instance(block_type)
            
            # Position
            if x is None or y is None:
                x = 100 + len(self.blocks) * 50
                y = 100 + len(self.blocks) * 30
            
            instance.x = x
            instance.y = y
            
            # Add to executor
            self.executor.engine.add_block(instance)
            
            # Create visual block
            visual_block = VisualBlock(self, instance, x, y)
            self.blocks[instance.id] = visual_block
            
            logger.info(f"Added block {block_type} at ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Failed to add block: {e}")
    
    def remove_block(self, block_id: str):
        """Remove a block from canvas"""
        if block_id in self.blocks:
            visual_block = self.blocks[block_id]
            
            # Remove connections
            self._remove_block_connections(block_id)
            
            # Remove from executor
            self.executor.engine.remove_block(block_id)
            
            # Remove visual
            visual_block.delete()
            del self.blocks[block_id]
            
            logger.info(f"Removed block {block_id}")
    
    def _remove_block_connections(self, block_id: str):
        """Remove all connections involving a block"""
        self.connections = [
            conn for conn in self.connections
            if conn.from_block.instance.id != block_id and 
               conn.to_block.instance.id != block_id
        ]
    
    def create_connection(self, from_block: VisualBlock, from_port: str,
                         to_block: VisualBlock, to_port: str):
        """Create a connection between two blocks"""
        try:
            # Create logical connection
            from_block.instance.connect_to(from_port, to_block.instance.id)
            
            # Create visual connection
            connection = Connection(self, from_block, from_port, to_block, to_port)
            self.connections.append(connection)
            
            logger.info(f"Connected {from_block.instance.id}:{from_port} -> {to_block.instance.id}:{to_port}")
            
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
    
    def on_left_click(self, event):
        """Handle left mouse click"""
        x, y = event.x, event.y
        
        # Check if clicked on a port
        clicked_item = self.find_closest(x, y)[0]
        tags = self.gettags(clicked_item)
        
        if "output_port" in tags:
            # Start connection from output port
            block_id = tags[2]
            port_name = tags[3]
            if block_id in self.blocks:
                self.connecting_from = (self.blocks[block_id], port_name)
                return
        
        elif "input_port" in tags:
            # Complete connection to input port
            if self.connecting_from:
                from_block, from_port = self.connecting_from
                block_id = tags[2]
                port_name = tags[3]
                if block_id in self.blocks:
                    to_block = self.blocks[block_id]
                    self.create_connection(from_block, from_port, to_block, port_name)
                self.connecting_from = None
                if self.temp_line:
                    self.delete(self.temp_line)
                    self.temp_line = None
                return
        
        # Check if clicked on a block
        for visual_block in self.blocks.values():
            if visual_block.contains_point(x, y):
                self.select_block(visual_block)
                self.drag_start = (x, y)
                return
        
        # Clicked on empty space
        self.deselect_all()
    
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.connecting_from:
            # Draw temporary connection line
            from_block, from_port = self.connecting_from
            x1, y1 = from_block.get_port_position(from_port, True)
            
            if self.temp_line:
                self.delete(self.temp_line)
            
            self.temp_line = self.create_line(
                x1, y1, event.x, event.y,
                fill="#88C0D0", width=2, dash=(5, 5)
            )
        
        elif self.selected_block and self.drag_start:
            # Drag block
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            
            self.selected_block.move(dx, dy)
            self.drag_start = (event.x, event.y)
            
            # Update connections
            self._update_connections(self.selected_block)
    
    def on_release(self, event):
        """Handle mouse release"""
        if self.temp_line:
            self.delete(self.temp_line)
            self.temp_line = None
        
        self.drag_start = None
    
    def on_double_click(self, event):
        """Handle double click - open block configuration"""
        for visual_block in self.blocks.values():
            if visual_block.contains_point(event.x, event.y):
                self._configure_block(visual_block)
                return
    
    def on_right_click(self, event):
        """Handle right click - show context menu"""
        # TODO: Implement context menu
        pass
    
    def on_delete(self, event):
        """Handle delete key - remove selected block"""
        if self.selected_block:
            self.remove_block(self.selected_block.instance.id)
            self.selected_block = None
    
    def select_block(self, visual_block: VisualBlock):
        """Select a block"""
        self.deselect_all()
        self.selected_block = visual_block
        visual_block.set_selected(True)
    
    def deselect_all(self):
        """Deselect all blocks"""
        if self.selected_block:
            self.selected_block.set_selected(False)
        self.selected_block = None
    
    def select_all(self, event):
        """Select all blocks"""
        # TODO: Implement multi-selection
        pass
    
    def copy_selected(self, event):
        """Copy selected block"""
        # TODO: Implement copy
        pass
    
    def paste(self, event):
        """Paste copied block"""
        # TODO: Implement paste
        pass
    
    def _configure_block(self, visual_block: VisualBlock):
        """Open configuration dialog for block"""
        # TODO: Implement configuration dialog
        logger.info(f"Configure block: {visual_block.instance.definition.name}")
    
    def _update_connections(self, visual_block: VisualBlock):
        """Update all connections involving a block"""
        for connection in self.connections:
            if (connection.from_block == visual_block or 
                connection.to_block == visual_block):
                connection.update()
    
    def zoom_in(self):
        """Zoom in canvas"""
        self.zoom_level = min(2.0, self.zoom_level + 0.1)
        self.scale("all", 0, 0, 1.1, 1.1)
    
    def zoom_out(self):
        """Zoom out canvas"""
        self.zoom_level = max(0.5, self.zoom_level - 0.1)
        self.scale("all", 0, 0, 0.9, 0.9)
    
    def clear(self):
        """Clear all blocks and connections"""
        for block_id in list(self.blocks.keys()):
            self.remove_block(block_id)
        self.connections.clear()
        logger.info("Canvas cleared")
    
    def serialize(self) -> Dict:
        """Serialize canvas state to dictionary"""
        return {
            "blocks": [
                block.instance.to_dict()
                for block in self.blocks.values()
            ],
            "metadata": {
                "block_count": len(self.blocks),
                "connection_count": len(self.connections)
            }
        }
    
    def load_workflow(self, workflow_data: Dict):
        """Load workflow from serialized data"""
        self.clear()
        
        # Load blocks
        for block_data in workflow_data.get("blocks", []):
            block_type = block_data.get("type")
            x = block_data.get("x", 100)
            y = block_data.get("y", 100)
            
            self.add_block(block_type, x, y)
            
            # Set parameters
            block_id = block_data.get("id")
            if block_id in self.blocks:
                visual_block = self.blocks[block_id]
                for param, value in block_data.get("parameters", {}).items():
                    visual_block.instance.set_parameter(param, value)
        
        # Recreate connections
        for block_data in workflow_data.get("blocks", []):
            block_id = block_data.get("id")
            if block_id not in self.blocks:
                continue
            
            from_block = self.blocks[block_id]
            for output_port, target_ids in block_data.get("connections", {}).items():
                for target_id in target_ids:
                    if target_id in self.blocks:
                        to_block = self.blocks[target_id]
                        # Find matching input port (simplified)
                        if to_block.instance.definition.input_ports:
                            input_port = to_block.instance.definition.input_ports[0].name
                            self.create_connection(from_block, output_port, to_block, input_port)
        
        logger.info(f"Loaded workflow with {len(self.blocks)} blocks")
