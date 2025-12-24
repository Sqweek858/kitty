#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CYBERPUNK TERMINAL - MAIN APPLICATION                     ║
║              Complete Terminal UI with Advanced Graphics                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Main application integrating all components:
    - Persistent menu bar
    - Properly positioned autocomplete panel
    - Functional keybindings
    - Full cursor movement in text
    - Persistent command output
    - Advanced parallax effects
    - 3D Christmas tree with animations
    - Gradient borders for all elements
    - Clean, organized code structure

This is the main entry point for the Cyberpunk Terminal application.
"""

import sys
import time
import os
from typing import Optional, List

# Import all our modules
from terminal_core import (
    TerminalEngine, TerminalConfig, RenderQuality,
    ScreenBuffer, get_terminal_size
)
from shader_system import Color
from ui_components import (
    BorderedContainer, BorderedContainerStyle, BorderStyle,
    MenuBar, MenuItem,
    AutocompletePanel, AutocompleteEntry,
    StatusBar, StatusSegment,
    TextInput
)
from input_manager import InputContext, AutocompleteEngine
from terminal_session import TerminalSession, OutputType, OutputLine
from graphics_engine import GraphicsCompositor


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION STATE
# ═══════════════════════════════════════════════════════════════════════════════

class ApplicationMode:
    """Application modes"""
    NORMAL = "normal"
    COMMAND_INPUT = "command_input"
    MENU = "menu"
    HELP = "help"


class CyberpunkTerminalApp:
    """Main application class"""
    
    def __init__(self):
        # Configuration
        self.config = TerminalConfig(
            target_fps=60,
            render_quality=RenderQuality.ULTRA,
            show_fps=False,
            alternate_screen=True
        )
        
        # Core engine
        self.engine = TerminalEngine(self.config)
        
        # Get terminal size
        self.width, self.height = get_terminal_size()
        
        # Terminal session
        self.session = TerminalSession()
        self.session.on_output = self._handle_command_output
        self.session.on_command_complete = self._handle_command_complete
        
        # Input management
        self.input_context = InputContext()
        self.input_context.on_submit = self._handle_command_submit
        self.input_context.on_change = self._handle_input_change
        self.input_context.on_autocomplete_request = self._handle_autocomplete_request
        
        # Setup autocomplete suggestions
        self._setup_autocomplete()
        
        # UI Components
        self._setup_ui_components()
        
        # Graphics
        self.graphics = GraphicsCompositor(self.width, self.height)
        
        # State
        self.mode = ApplicationMode.COMMAND_INPUT
        self.show_graphics = True
        self.autocomplete_visible = False
        self.current_suggestions: List[AutocompleteEntry] = []
        
        # Performance
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0.0
    
    def _setup_autocomplete(self):
        """Setup autocomplete with common commands"""
        common_commands = [
            "ls", "cd", "pwd", "cat", "grep", "find", "echo", "clear",
            "mkdir", "rmdir", "rm", "cp", "mv", "touch", "chmod", "chown",
            "ps", "kill", "top", "htop", "df", "du", "free", "uname",
            "git", "python", "pip", "npm", "node", "docker", "ssh",
            "help", "man", "history", "export", "alias", "exit"
        ]
        
        self.input_context.autocomplete.set_suggestions(common_commands)
    
    def _setup_ui_components(self):
        """Setup all UI components"""
        # Menu bar (top of screen, always visible)
        menu_items = [
            MenuItem(label="File", action=lambda: self._menu_file()),
            MenuItem(label="Edit", action=lambda: self._menu_edit()),
            MenuItem(label="View", action=lambda: self._menu_view()),
            MenuItem(label="Tools", action=lambda: self._menu_tools()),
            MenuItem(label="Help", action=lambda: self._menu_help(), shortcut="F1"),
        ]
        self.menu_bar = MenuBar(0, 0, self.width, menu_items)
        
        # Output container (gradient bordered)
        output_height = self.height - 6  # Leave space for menu, input, status
        style = BorderedContainerStyle(
            border_style=BorderStyle.ROUNDED,
            gradient_type="cyberpunk",
            gradient_speed=0.5,
            padding=1,
            title="Terminal Output",
            title_align="center"
        )
        self.output_container = BorderedContainer(
            0, 1, self.width, output_height, style
        )
        
        # Input field container (gradient bordered)
        input_y = self.height - 4
        input_style = BorderedContainerStyle(
            border_style=BorderStyle.ROUNDED,
            gradient_type="christmas",
            gradient_speed=0.8,
            padding=0,
            title="Command Input",
            title_align="left"
        )
        self.input_container = BorderedContainer(
            0, input_y, self.width, 3, input_style
        )
        
        # Autocomplete panel (positioned above input)
        autocomplete_y = input_y - 12  # 12 lines above input
        self.autocomplete_panel = AutocompletePanel(
            2, autocomplete_y, self.width - 4, 10
        )
        self.autocomplete_panel.visible = False
        
        # Status bar (bottom of screen)
        self.status_bar = StatusBar(0, self.height - 1, self.width)
        self._update_status_bar()
    
    def _update_status_bar(self):
        """Update status bar segments"""
        segments = [
            StatusSegment(
                text=f"Mode: {self.mode.upper()}",
                align="left",
                color=(100, 200, 255)
            ),
            StatusSegment(
                text=f"CWD: {self.session.env.get_cwd()}",
                align="center",
                color=(200, 200, 200)
            ),
            StatusSegment(
                text=f"FPS: {self.current_fps:.1f}",
                align="right",
                color=(100, 255, 100)
            ),
        ]
        self.status_bar.set_segments(segments)
    
    # ═══════════════════════════════════════════════════════════════════════
    # INPUT HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_input(self, key: str):
        """Handle keyboard input"""
        current_time = time.time()
        
        # Global keybindings
        if key == '\x03':  # Ctrl+C
            self.engine.stop()
            return
        
        # Mode-specific handling
        if self.mode == ApplicationMode.COMMAND_INPUT:
            self._handle_command_input(key, current_time)
        elif self.mode == ApplicationMode.MENU:
            self._handle_menu_input(key)
        
    def _handle_command_input(self, key: str, current_time: float):
        """Handle input in command mode"""
        # Check if autocomplete is visible
        if self.autocomplete_visible and self.autocomplete_panel.visible:
            # Let autocomplete handle navigation keys
            if key in ['KEY_UP', 'KEY_DOWN', '\t', '\n']:
                if self.autocomplete_panel.handle_input(key):
                    if key == '\t' or key == '\n':
                        # Accept selected suggestion
                        selected = self.autocomplete_panel.get_selected()
                        if selected:
                            self.input_context.set_text(selected.text)
                        self.autocomplete_visible = False
                        self.autocomplete_panel.visible = False
                    return
        
        # Pass to input context
        self.input_context.handle_key(key, current_time)
    
    def _handle_menu_input(self, key: str):
        """Handle input in menu mode"""
        if self.menu_bar.handle_input(key):
            return
        
        if key == '\x1b':  # Escape
            self.mode = ApplicationMode.COMMAND_INPUT
    
    def _handle_command_submit(self, command: str):
        """Handle command submission"""
        if command.strip():
            # Execute command
            self.session.execute_command(command)
            
            # Hide autocomplete
            self.autocomplete_visible = False
            self.autocomplete_panel.visible = False
    
    def _handle_input_change(self, text: str):
        """Handle input text change"""
        # Update autocomplete
        if text.strip():
            self._update_autocomplete(text)
        else:
            self.autocomplete_visible = False
            self.autocomplete_panel.visible = False
    
    def _handle_autocomplete_request(self):
        """Handle autocomplete request (Tab key)"""
        text = self.input_context.get_text()
        if text.strip():
            self._update_autocomplete(text)
            if self.current_suggestions:
                self.autocomplete_visible = True
                self.autocomplete_panel.visible = True
    
    def _update_autocomplete(self, prefix: str):
        """Update autocomplete suggestions"""
        # Get completions
        completions = self.input_context.autocomplete.get_completions(prefix)
        
        # Convert to AutocompleteEntry
        entries = [
            AutocompleteEntry(text=cmd, score=score)
            for cmd, score in completions
        ]
        
        self.current_suggestions = entries
        self.autocomplete_panel.set_suggestions(entries)
        
        if entries:
            self.autocomplete_visible = True
            self.autocomplete_panel.visible = True
        else:
            self.autocomplete_visible = False
            self.autocomplete_panel.visible = False
    
    def _handle_command_output(self, line: str, output_type: OutputType):
        """Handle real-time command output"""
        # Output is already added to session buffer
        pass
    
    def _handle_command_complete(self, result):
        """Handle command completion"""
        # Update status or show notification if needed
        pass
    
    # ═══════════════════════════════════════════════════════════════════════
    # MENU ACTIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _menu_file(self):
        """File menu actions"""
        # Could open a submenu or perform action
        pass
    
    def _menu_edit(self):
        """Edit menu actions"""
        pass
    
    def _menu_view(self):
        """View menu actions"""
        self.show_graphics = not self.show_graphics
    
    def _menu_tools(self):
        """Tools menu actions"""
        pass
    
    def _menu_help(self):
        """Help menu actions"""
        help_text = [
            "╔════════════════════════════════════════════════════════╗",
            "║          CYBERPUNK TERMINAL - HELP                     ║",
            "╚════════════════════════════════════════════════════════╝",
            "",
            "Keybindings:",
            "  Ctrl+C         - Exit",
            "  Tab            - Autocomplete",
            "  Up/Down        - Command history",
            "  Ctrl+L         - Clear line",
            "  Ctrl+U         - Delete to start of line",
            "  Ctrl+K         - Delete to end of line",
            "  Ctrl+W         - Delete word",
            "  Ctrl+Left/Right - Move by word",
            "  Home/End       - Move to start/end of line",
            "",
            "Press any key to continue..."
        ]
        
        # Add to output
        for line in help_text:
            self.session.output.add_line(line, OutputType.INFO)
    
    # ═══════════════════════════════════════════════════════════════════════
    # UPDATE AND RENDER
    # ═══════════════════════════════════════════════════════════════════════
    
    def update(self, delta_time: float):
        """Update application state"""
        # Update graphics
        if self.show_graphics:
            self.graphics.update(delta_time)
        
        # Update UI components
        self.menu_bar.update(delta_time)
        self.output_container.update(delta_time)
        self.input_container.update(delta_time)
        self.status_bar.update(delta_time)
        
        if self.autocomplete_visible:
            self.autocomplete_panel.update(delta_time)
        
        # Update FPS counter
        self.frame_count += 1
        if time.time() - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count / (time.time() - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = time.time()
            self._update_status_bar()
    
    def render(self, screen: ScreenBuffer):
        """Render application to screen buffer"""
        current_time = time.time()
        
        # Layer 0: Graphics background (parallax, tree, snow)
        if self.show_graphics:
            self.graphics.render(screen, current_time)
        
        # Layer 1: Output container with command output
        self._render_output(screen, current_time)
        
        # Layer 2: Input container with command input
        self._render_input(screen, current_time)
        
        # Layer 3: Autocomplete panel (if visible)
        if self.autocomplete_visible and self.autocomplete_panel.visible:
            self.autocomplete_panel.render(screen, current_time)
        
        # Layer 4: Menu bar (always on top, persistent)
        self.menu_bar.render(screen, current_time)
        
        # Layer 5: Status bar (always on top)
        self.status_bar.render(screen, current_time)
    
    def _render_output(self, screen: ScreenBuffer, time: float):
        """Render output container with terminal output"""
        # Render container border
        self.output_container.render(screen, time)
        
        # Get visible output lines
        container_height = self.output_container.rect.height - 4  # Account for border + padding
        output_lines = self.session.get_output_lines(container_height)
        
        # Format output lines for display
        display_lines = []
        for line in output_lines:
            # Color code based on output type
            if line.output_type == OutputType.COMMAND:
                prefix = "$ "
                text = line.text
            elif line.output_type == OutputType.ERROR or line.output_type == OutputType.STDERR:
                prefix = "[ERROR] "
                text = line.text
            elif line.output_type == OutputType.SUCCESS:
                prefix = "[OK] "
                text = line.text
            elif line.output_type == OutputType.SYSTEM:
                prefix = "[SYS] "
                text = line.text
            else:
                prefix = ""
                text = line.text
            
            display_lines.append(prefix + text)
        
        # Set content
        self.output_container.set_content(display_lines)
    
    def _render_input(self, screen: ScreenBuffer, time: float):
        """Render input container with command input"""
        # Render container border
        self.input_container.render(screen, time)
        
        # Get input text and cursor position
        text = self.input_context.get_text()
        cursor_pos = self.input_context.get_cursor_pos()
        prompt = self.session.get_prompt()
        
        # Calculate display position
        input_x = self.input_container.rect.x + 2
        input_y = self.input_container.rect.y + 1
        input_width = self.input_container.rect.width - 4
        
        # Render prompt
        for i, char in enumerate(prompt):
            if i < input_width:
                screen.set_char(input_x + i, input_y, char, (100, 200, 255))
        
        # Calculate scroll for long input
        prompt_len = len(prompt)
        visible_start = 0
        
        if cursor_pos + prompt_len >= input_width:
            visible_start = cursor_pos - (input_width - prompt_len - 5)
        
        # Render input text
        visible_text = text[visible_start:visible_start + input_width - prompt_len]
        
        for i, char in enumerate(visible_text):
            screen_x = input_x + prompt_len + i
            if screen_x < input_x + input_width:
                screen.set_char(screen_x, input_y, char, (255, 255, 255))
        
        # Render cursor
        cursor_screen_x = input_x + prompt_len + (cursor_pos - visible_start)
        if input_x <= cursor_screen_x < input_x + input_width:
            # Blinking cursor
            if int(time * 2) % 2 == 0:
                screen.set_char(cursor_screen_x, input_y, '█', (255, 255, 100))
    
    # ═══════════════════════════════════════════════════════════════════════
    # RESIZE HANDLER
    # ═══════════════════════════════════════════════════════════════════════
    
    def handle_resize(self, new_width: int, new_height: int):
        """Handle terminal resize"""
        self.width = new_width
        self.height = new_height
        
        # Resize graphics
        self.graphics = GraphicsCompositor(new_width, new_height)
        
        # Recreate UI components
        self._setup_ui_components()
    
    # ═══════════════════════════════════════════════════════════════════════
    # RUN
    # ═══════════════════════════════════════════════════════════════════════
    
    def run(self):
        """Run the application"""
        # Set callbacks
        self.engine.set_update_callback(self.update)
        self.engine.set_render_callback(self.render)
        self.engine.set_input_callback(self._handle_input)
        self.engine.set_resize_callback(self.handle_resize)
        
        # Run engine
        self.engine.run()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    try:
        app = CyberpunkTerminalApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()