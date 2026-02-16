"""
Main Window - Primary application window with toolbar, canvas, and block palette
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging
from typing import Optional
from core import WorkflowExecutor, BlockRegistry
from gui.canvas import WorkflowCanvas
from utils.project_io import ProjectIO

logger = logging.getLogger(__name__)

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """
    Main application window providing the complete IDE-like interface
    for visual automation workflows.
    """
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Visual Automation Tool - Lite RPA Engine")
        self.geometry("1400x900")
        
        # State
        self.current_file: Optional[str] = None
        self.modified: bool = False
        self.executor = WorkflowExecutor()
        self.project_io = ProjectIO()
        
        # Setup GUI
        self._setup_menu()
        self._setup_toolbar()
        self._setup_main_area()
        self._setup_status_bar()
        
        # Setup callbacks
        self._setup_callbacks()
        
        logger.info("Main window initialized")
    
    def _setup_menu(self):
        """Setup menu bar (CustomTkinter doesn't have native menu, using buttons)"""
        menu_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        menu_frame.pack(side="top", fill="x", padx=0, pady=0)
        menu_frame.pack_propagate(False)
        
        # File menu
        file_btn = ctk.CTkButton(
            menu_frame, text="📁 File", width=80, height=35,
            command=self._show_file_menu
        )
        file_btn.pack(side="left", padx=5, pady=2)
        
        # Edit menu
        edit_btn = ctk.CTkButton(
            menu_frame, text="✏️ Edit", width=80, height=35,
            command=self._show_edit_menu
        )
        edit_btn.pack(side="left", padx=5, pady=2)
        
        # View menu
        view_btn = ctk.CTkButton(
            menu_frame, text="👁️ View", width=80, height=35,
            command=self._show_view_menu
        )
        view_btn.pack(side="left", padx=5, pady=2)
        
        # Help menu
        help_btn = ctk.CTkButton(
            menu_frame, text="❓ Help", width=80, height=35,
            command=self._show_help_menu
        )
        help_btn.pack(side="left", padx=5, pady=2)
        
    def _setup_toolbar(self):
        """Setup toolbar with action buttons"""
        toolbar = ctk.CTkFrame(self, height=60, corner_radius=0)
        toolbar.pack(side="top", fill="x", padx=5, pady=5)
        toolbar.pack_propagate(False)
        
        # New project
        self.new_btn = ctk.CTkButton(
            toolbar, text="🆕 New", width=100, height=50,
            command=self.new_project
        )
        self.new_btn.pack(side="left", padx=5)
        
        # Open project
        self.open_btn = ctk.CTkButton(
            toolbar, text="📂 Open", width=100, height=50,
            command=self.open_project
        )
        self.open_btn.pack(side="left", padx=5)
        
        # Save project
        self.save_btn = ctk.CTkButton(
            toolbar, text="💾 Save", width=100, height=50,
            command=self.save_project
        )
        self.save_btn.pack(side="left", padx=5)
        
        # Separator
        ctk.CTkLabel(toolbar, text="|", font=("Arial", 20)).pack(side="left", padx=10)
        
        # Run workflow
        self.run_btn = ctk.CTkButton(
            toolbar, text="▶️ Run", width=120, height=50,
            command=self.run_workflow,
            fg_color="green", hover_color="darkgreen"
        )
        self.run_btn.pack(side="left", padx=5)
        
        # Stop workflow
        self.stop_btn = ctk.CTkButton(
            toolbar, text="⏹️ Stop", width=100, height=50,
            command=self.stop_workflow,
            fg_color="red", hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # Separator
        ctk.CTkLabel(toolbar, text="|", font=("Arial", 20)).pack(side="left", padx=10)
        
        # Validate
        self.validate_btn = ctk.CTkButton(
            toolbar, text="✓ Validate", width=100, height=50,
            command=self.validate_workflow
        )
        self.validate_btn.pack(side="left", padx=5)
        
        # Settings
        self.settings_btn = ctk.CTkButton(
            toolbar, text="⚙️ Settings", width=100, height=50,
            command=self.show_settings
        )
        self.settings_btn.pack(side="right", padx=5)
    
    def _setup_main_area(self):
        """Setup main working area with block palette and canvas"""
        main_container = ctk.CTkFrame(self)
        main_container.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Block palette
        left_panel = ctk.CTkFrame(main_container, width=250)
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Palette title
        palette_title = ctk.CTkLabel(
            left_panel, text="📦 Block Palette",
            font=("Arial", 16, "bold")
        )
        palette_title.pack(pady=10)
        
        # Search box
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            left_panel, placeholder_text="🔍 Search blocks...",
            textvariable=self.search_var
        )
        search_entry.pack(fill="x", padx=10, pady=5)
        self.search_var.trace("w", self._on_search_changed)
        
        # Block list (scrollable)
        self.block_list_frame = ctk.CTkScrollableFrame(left_panel)
        self.block_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self._populate_block_palette()
        
        # Right panel - Canvas area
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Canvas title
        canvas_title_frame = ctk.CTkFrame(right_panel, height=40)
        canvas_title_frame.pack(fill="x", pady=(0, 5))
        canvas_title_frame.pack_propagate(False)
        
        canvas_title = ctk.CTkLabel(
            canvas_title_frame, text="🎨 Workflow Canvas",
            font=("Arial", 16, "bold")
        )
        canvas_title.pack(side="left", padx=10)
        
        # Zoom controls
        zoom_frame = ctk.CTkFrame(canvas_title_frame)
        zoom_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(zoom_frame, text="➖", width=40, command=self.zoom_out).pack(side="left", padx=2)
        self.zoom_label = ctk.CTkLabel(zoom_frame, text="100%", width=50)
        self.zoom_label.pack(side="left", padx=5)
        ctk.CTkButton(zoom_frame, text="➕", width=40, command=self.zoom_in).pack(side="left", padx=2)
        
        # Workflow canvas
        self.canvas = WorkflowCanvas(right_panel, self.executor)
        self.canvas.pack(fill="both", expand=True)
    
    def _setup_status_bar(self):
        """Setup status bar at bottom"""
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Ready", anchor="w"
        )
        self.status_label.pack(side="left", padx=10)
        
        self.block_count_label = ctk.CTkLabel(
            self.status_bar, text="Blocks: 0", anchor="e"
        )
        self.block_count_label.pack(side="right", padx=10)
    
    def _setup_callbacks(self):
        """Setup event callbacks"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _populate_block_palette(self):
        """Populate the block palette with available blocks"""
        # Clear existing
        for widget in self.block_list_frame.winfo_children():
            widget.destroy()
        
        # Get all blocks grouped by category
        categories = BlockRegistry.get_categories()
        
        for category in categories:
            blocks = BlockRegistry.get_blocks_by_category(category)
            
            if not blocks:
                continue
            
            # Category header
            category_label = ctk.CTkLabel(
                self.block_list_frame,
                text=f"▼ {category.value.replace('_', ' ').title()}",
                font=("Arial", 12, "bold"),
                anchor="w"
            )
            category_label.pack(fill="x", pady=(10, 5))
            
            # Block buttons
            for block_def in blocks:
                block_btn = ctk.CTkButton(
                    self.block_list_frame,
                    text=f"{block_def.icon} {block_def.name}",
                    anchor="w",
                    command=lambda bt=block_def.block_type: self.add_block_to_canvas(bt)
                )
                block_btn.pack(fill="x", pady=2)
    
    def _on_search_changed(self, *args):
        """Handle search box text change"""
        query = self.search_var.get()
        
        # Clear palette
        for widget in self.block_list_frame.winfo_children():
            widget.destroy()
        
        if not query:
            self._populate_block_palette()
            return
        
        # Search and display results
        results = BlockRegistry.search_blocks(query)
        
        if not results:
            ctk.CTkLabel(
                self.block_list_frame,
                text="No blocks found",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for block_def in results:
            block_btn = ctk.CTkButton(
                self.block_list_frame,
                text=f"{block_def.icon} {block_def.name}",
                anchor="w",
                command=lambda bt=block_def.block_type: self.add_block_to_canvas(bt)
            )
            block_btn.pack(fill="x", pady=2)
    
    # Menu actions
    def _show_file_menu(self):
        """Show file menu options"""
        menu = ctk.CTkToplevel(self)
        menu.title("File")
        menu.geometry("200x300")
        
        ctk.CTkButton(menu, text="New", command=lambda: [self.new_project(), menu.destroy()]).pack(pady=5)
        ctk.CTkButton(menu, text="Open", command=lambda: [self.open_project(), menu.destroy()]).pack(pady=5)
        ctk.CTkButton(menu, text="Save", command=lambda: [self.save_project(), menu.destroy()]).pack(pady=5)
        ctk.CTkButton(menu, text="Save As", command=lambda: [self.save_project_as(), menu.destroy()]).pack(pady=5)
        ctk.CTkButton(menu, text="Exit", command=self.on_closing).pack(pady=5)
    
    def _show_edit_menu(self):
        """Show edit menu options"""
        messagebox.showinfo("Edit", "Edit menu - Coming soon!")
    
    def _show_view_menu(self):
        """Show view menu options"""
        messagebox.showinfo("View", "View menu - Coming soon!")
    
    def _show_help_menu(self):
        """Show help menu options"""
        help_text = """
Visual Automation Tool v1.0

A drag-and-drop RPA tool for creating automation workflows.

Quick Start:
1. Drag blocks from palette to canvas
2. Connect blocks by clicking output → input
3. Configure blocks (double-click)
4. Run workflow (▶️ button)

For more help, visit documentation.
        """
        messagebox.showinfo("Help", help_text)
    
    # Toolbar actions
    def new_project(self):
        """Create new project"""
        if self.modified:
            if not messagebox.askyesno("Unsaved Changes", "Discard unsaved changes?"):
                return
        
        self.canvas.clear()
        self.current_file = None
        self.modified = False
        self.update_status("New project created")
    
    def open_project(self):
        """Open existing project"""
        filename = filedialog.askopenfilename(
            title="Open Workflow",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                workflow_data = self.project_io.load(filename)
                self.canvas.load_workflow(workflow_data)
                self.current_file = filename
                self.modified = False
                self.update_status(f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def save_project(self):
        """Save current project"""
        if self.current_file:
            try:
                workflow_data = self.canvas.serialize()
                self.project_io.save(workflow_data, self.current_file)
                self.modified = False
                self.update_status(f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Save project with new name"""
        filename = filedialog.asksaveasfilename(
            title="Save Workflow",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                workflow_data = self.canvas.serialize()
                self.project_io.save(workflow_data, filename)
                self.current_file = filename
                self.modified = False
                self.update_status(f"Saved as: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def run_workflow(self):
        """Execute the workflow"""
        self.update_status("Running workflow...")
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        try:
            # Load workflow into executor
            workflow_data = self.canvas.serialize()
            self.executor.load_workflow(workflow_data)
            
            # Execute
            results = self.executor.execute()
            
            # Show results
            if results["success"]:
                messagebox.showinfo(
                    "Success",
                    f"Workflow completed successfully!\n\n"
                    f"Executed: {results['executed_count']} blocks\n"
                    f"Time: {results['execution_time']:.2f}s"
                )
                self.update_status("Workflow completed successfully")
            else:
                messagebox.showerror(
                    "Error",
                    f"Workflow failed!\n\n"
                    f"Failed blocks: {results['failed_count']}"
                )
                self.update_status("Workflow failed")
        
        except Exception as e:
            messagebox.showerror("Execution Error", str(e))
            self.update_status(f"Error: {e}")
        
        finally:
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
    
    def stop_workflow(self):
        """Stop workflow execution"""
        # TODO: Implement workflow interruption
        self.update_status("Workflow stopped")
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
    
    def validate_workflow(self):
        """Validate current workflow"""
        workflow_data = self.canvas.serialize()
        self.executor.load_workflow(workflow_data)
        issues = self.executor.validate()
        
        if not issues:
            messagebox.showinfo("Validation", "Workflow is valid! ✓")
        else:
            issue_text = "\n".join(f"• {issue}" for issue in issues)
            messagebox.showwarning("Validation Issues", f"Found {len(issues)} issue(s):\n\n{issue_text}")
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog - Coming soon!")
    
    def add_block_to_canvas(self, block_type: str):
        """Add a block to the canvas"""
        self.canvas.add_block(block_type)
        self.modified = True
        self.update_block_count()
    
    def zoom_in(self):
        """Zoom in canvas"""
        self.canvas.zoom_in()
        self.update_zoom_label()
    
    def zoom_out(self):
        """Zoom out canvas"""
        self.canvas.zoom_out()
        self.update_zoom_label()
    
    def update_zoom_label(self):
        """Update zoom level display"""
        zoom = int(self.canvas.zoom_level * 100)
        self.zoom_label.configure(text=f"{zoom}%")
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)
        logger.info(message)
    
    def update_block_count(self):
        """Update block count in status bar"""
        count = len(self.executor.engine.blocks)
        self.block_count_label.configure(text=f"Blocks: {count}")
    
    def on_closing(self):
        """Handle window close event"""
        if self.modified:
            if messagebox.askyesno("Unsaved Changes", "Save before closing?"):
                self.save_project()
        
        self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
