#!/usr/bin/env python3
"""
Brad TUI Ultra - UI Components Module
=====================================

Reusable UI components for Brad TUI Ultra.
Includes widgets, dialogs, menus, and interactive elements.

Features:
- Buttons and interactive controls
- Progress bars and spinners
- Dialog boxes (alert, confirm, prompt)
- Menus and selections
- Tables and lists
- Forms and input fields
- Notifications and toasts
- Modal windows
"""

import time
from typing import List, Optional, Callable, Any, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# BASE COMPONENT
# =============================================================================

class Component:
    """Base class for UI components"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 10, height: int = 1):
        """Initialize component"""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        self.focused = False
    
    def render(self) -> List[str]:
        """Render component to list of strings"""
        return []
    
    def handle_key(self, key: str) -> bool:
        """Handle key press. Return True if handled."""
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """Handle mouse event. Return True if handled."""
        return False
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside component"""
        return (
            self.x <= x < self.x + self.width and
            self.y <= y < self.y + self.height
        )


# =============================================================================
# BUTTON
# =============================================================================

class ButtonStyle(Enum):
    """Button styles"""
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class Button(Component):
    """Interactive button component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        width: Optional[int] = None,
        style: ButtonStyle = ButtonStyle.DEFAULT,
        on_click: Optional[Callable[[], None]] = None
    ):
        """Initialize button"""
        if width is None:
            width = len(text) + 4
        
        super().__init__(x, y, width, 3)
        self.text = text
        self.style = style
        self.on_click = on_click
    
    def render(self) -> List[str]:
        """Render button"""
        if not self.visible:
            return []
        
        # Colors based on style
        colors = {
            ButtonStyle.DEFAULT: (180, 180, 180),
            ButtonStyle.PRIMARY: (0, 150, 255),
            ButtonStyle.SUCCESS: (0, 200, 100),
            ButtonStyle.WARNING: (255, 180, 0),
            ButtonStyle.DANGER: (255, 50, 50),
        }
        
        color = colors[self.style]
        
        # Different appearance when focused
        if self.focused:
            color = tuple(min(255, c + 50) for c in color)
        
        if not self.enabled:
            color = (100, 100, 100)
        
        # Build button
        lines = []
        
        # Top border
        lines.append(f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m╭{'─' * (self.width - 2)}╮\x1b[0m")
        
        # Text line
        text = self.text.center(self.width - 2)
        lines.append(f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m│{text}│\x1b[0m")
        
        # Bottom border
        lines.append(f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m╰{'─' * (self.width - 2)}╯\x1b[0m")
        
        return lines
    
    def handle_key(self, key: str) -> bool:
        """Handle key press"""
        if not self.enabled:
            return False
        
        if key in ['enter', '\r', '\n'] and self.focused:
            if self.on_click:
                self.on_click()
            return True
        
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """Handle mouse click"""
        if not self.enabled:
            return False
        
        if self.contains_point(x, y) and button == 1:  # Left click
            if self.on_click:
                self.on_click()
            return True
        
        return False


# =============================================================================
# PROGRESS BAR
# =============================================================================

class ProgressBar(Component):
    """Progress bar component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        progress: float = 0.0,
        show_percent: bool = True
    ):
        """Initialize progress bar"""
        super().__init__(x, y, width, 1)
        self.progress = max(0.0, min(1.0, progress))
        self.show_percent = show_percent
    
    def set_progress(self, progress: float) -> None:
        """Set progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
    
    def render(self) -> List[str]:
        """Render progress bar"""
        if not self.visible:
            return []
        
        filled_width = int(self.width * self.progress)
        empty_width = self.width - filled_width
        
        # Build progress bar
        bar = '█' * filled_width + '░' * empty_width
        
        if self.show_percent:
            percent = f" {int(self.progress * 100)}%"
            bar = bar[:self.width - len(percent)] + percent
        
        # Color gradient
        color = self._get_color_for_progress(self.progress)
        
        return [f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m{bar}\x1b[0m"]
    
    def _get_color_for_progress(self, progress: float) -> Tuple[int, int, int]:
        """Get color based on progress"""
        if progress < 0.33:
            # Red to yellow
            return (255, int(255 * progress * 3), 0)
        elif progress < 0.66:
            # Yellow to green
            t = (progress - 0.33) * 3
            return (int(255 * (1 - t)), 255, 0)
        else:
            # Green
            return (0, 255, 0)


# =============================================================================
# SPINNER
# =============================================================================

class Spinner(Component):
    """Loading spinner component"""
    
    SPINNERS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['-', '\\', '|', '/'],
        'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'box': ['◰', '◳', '◲', '◱'],
        'circle': ['◐', '◓', '◑', '◒'],
        'bounce': ['⠁', '⠂', '⠄', '⠂'],
    }
    
    def __init__(
        self,
        x: int,
        y: int,
        style: str = 'dots',
        text: str = "Loading..."
    ):
        """Initialize spinner"""
        super().__init__(x, y, len(text) + 2, 1)
        self.style = style
        self.text = text
        self.frame = 0
        self.last_update = time.time()
        self.fps = 10
    
    def update(self) -> None:
        """Update spinner animation"""
        now = time.time()
        if now - self.last_update >= 1.0 / self.fps:
            self.frame = (self.frame + 1) % len(self.SPINNERS[self.style])
            self.last_update = now
    
    def render(self) -> List[str]:
        """Render spinner"""
        if not self.visible:
            return []
        
        spinner_char = self.SPINNERS[self.style][self.frame]
        return [f"\x1b[36m{spinner_char}\x1b[0m {self.text}"]


# =============================================================================
# DIALOG
# =============================================================================

class DialogType(Enum):
    """Dialog types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


class Dialog(Component):
    """Modal dialog box"""
    
    def __init__(
        self,
        title: str,
        message: str,
        dialog_type: DialogType = DialogType.INFO,
        buttons: Optional[List[str]] = None,
        width: int = 50,
        height: int = 10
    ):
        """Initialize dialog"""
        # Center on screen (will be adjusted in render)
        super().__init__(0, 0, width, height)
        
        self.title = title
        self.message = message
        self.dialog_type = dialog_type
        self.buttons = buttons or ["OK"]
        self.selected_button = 0
        self.result: Optional[str] = None
    
    def render(self) -> List[str]:
        """Render dialog"""
        if not self.visible:
            return []
        
        lines = []
        
        # Icon based on type
        icons = {
            DialogType.INFO: 'ℹ',
            DialogType.SUCCESS: '✓',
            DialogType.WARNING: '⚠',
            DialogType.ERROR: '✗',
            DialogType.QUESTION: '?',
        }
        
        icon = icons[self.dialog_type]
        
        # Border color based on type
        colors = {
            DialogType.INFO: (100, 150, 255),
            DialogType.SUCCESS: (0, 255, 100),
            DialogType.WARNING: (255, 200, 0),
            DialogType.ERROR: (255, 50, 50),
            DialogType.QUESTION: (255, 150, 0),
        }
        
        color = colors[self.dialog_type]
        color_code = f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m"
        reset = "\x1b[0m"
        
        # Top border with title
        title_text = f" {icon} {self.title} "
        title_padded = title_text.center(self.width - 2)
        lines.append(f"{color_code}╭{title_padded}╮{reset}")
        
        # Empty line
        lines.append(f"{color_code}│{' ' * (self.width - 2)}│{reset}")
        
        # Message lines (wrapped)
        message_lines = self._wrap_text(self.message, self.width - 4)
        for line in message_lines:
            padded_line = line.center(self.width - 2)
            lines.append(f"{color_code}│{padded_line}│{reset}")
        
        # Empty lines to fill height
        message_height = len(message_lines) + 2
        button_height = 3
        remaining = self.height - message_height - button_height - 1
        
        for _ in range(remaining):
            lines.append(f"{color_code}│{' ' * (self.width - 2)}│{reset}")
        
        # Buttons
        button_line = self._render_buttons()
        lines.append(f"{color_code}│{button_line}│{reset}")
        
        # Bottom border
        lines.append(f"{color_code}╰{'─' * (self.width - 2)}╯{reset}")
        
        return lines
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_len = len(word)
            if current_length + word_len + len(current_line) <= width:
                current_line.append(word)
                current_length += word_len
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_len
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _render_buttons(self) -> str:
        """Render buttons"""
        button_strs = []
        
        for i, button_text in enumerate(self.buttons):
            if i == self.selected_button:
                button_str = f"[ {button_text} ]"
            else:
                button_str = f"  {button_text}  "
            button_strs.append(button_str)
        
        buttons_line = '  '.join(button_strs)
        return buttons_line.center(self.width - 2)
    
    def handle_key(self, key: str) -> bool:
        """Handle key press"""
        if key in ['left', 'h']:
            self.selected_button = max(0, self.selected_button - 1)
            return True
        elif key in ['right', 'l']:
            self.selected_button = min(len(self.buttons) - 1, self.selected_button + 1)
            return True
        elif key in ['enter', '\r', '\n']:
            self.result = self.buttons[self.selected_button]
            return True
        elif key == 'esc':
            self.result = "Cancel"
            return True
        
        return False


# =============================================================================
# MENU
# =============================================================================

class MenuItem:
    """Menu item"""
    
    def __init__(
        self,
        text: str,
        action: Optional[Callable[[], None]] = None,
        shortcut: Optional[str] = None,
        enabled: bool = True
    ):
        """Initialize menu item"""
        self.text = text
        self.action = action
        self.shortcut = shortcut
        self.enabled = enabled


class Menu(Component):
    """Dropdown menu component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        items: List[MenuItem],
        width: int = 30
    ):
        """Initialize menu"""
        super().__init__(x, y, width, len(items) + 2)
        self.items = items
        self.selected_index = 0
    
    def render(self) -> List[str]:
        """Render menu"""
        if not self.visible:
            return []
        
        lines = []
        
        # Top border
        lines.append(f"╭{'─' * (self.width - 2)}╮")
        
        # Menu items
        for i, item in enumerate(self.items):
            # Selection indicator
            if i == self.selected_index:
                indicator = '▶'
                color = '\x1b[36m'
            else:
                indicator = ' '
                color = ''
            
            # Disabled styling
            if not item.enabled:
                color = '\x1b[90m'
            
            # Build line
            text = item.text
            if item.shortcut:
                shortcut_text = f"  [{item.shortcut}]"
                text = text.ljust(self.width - len(shortcut_text) - 4) + shortcut_text
            else:
                text = text.ljust(self.width - 4)
            
            line = f"│ {indicator} {text}│"
            lines.append(f"{color}{line}\x1b[0m")
        
        # Bottom border
        lines.append(f"╰{'─' * (self.width - 2)}╯")
        
        return lines
    
    def handle_key(self, key: str) -> bool:
        """Handle key press"""
        if key in ['up', 'k']:
            # Move up, skip disabled items
            new_index = self.selected_index - 1
            while new_index >= 0 and not self.items[new_index].enabled:
                new_index -= 1
            
            if new_index >= 0:
                self.selected_index = new_index
            return True
        
        elif key in ['down', 'j']:
            # Move down, skip disabled items
            new_index = self.selected_index + 1
            while new_index < len(self.items) and not self.items[new_index].enabled:
                new_index += 1
            
            if new_index < len(self.items):
                self.selected_index = new_index
            return True
        
        elif key in ['enter', '\r', '\n']:
            # Execute selected item
            item = self.items[self.selected_index]
            if item.enabled and item.action:
                item.action()
            return True
        
        return False


# =============================================================================
# TABLE
# =============================================================================

class Table(Component):
    """Table component for displaying data"""
    
    def __init__(
        self,
        x: int,
        y: int,
        headers: List[str],
        rows: List[List[str]],
        width: int = 80
    ):
        """Initialize table"""
        height = len(rows) + 3  # Header + borders
        super().__init__(x, y, width, height)
        
        self.headers = headers
        self.rows = rows
        self.selected_row = 0
        
        # Calculate column widths
        self.column_widths = self._calculate_column_widths()
    
    def _calculate_column_widths(self) -> List[int]:
        """Calculate optimal column widths"""
        num_cols = len(self.headers)
        
        if num_cols == 0:
            return []
        
        # Start with header widths
        widths = [len(h) for h in self.headers]
        
        # Check row data
        for row in self.rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Adjust to fit total width
        total = sum(widths) + (num_cols - 1) * 3 + 4  # separators and borders
        
        if total > self.width:
            # Scale down proportionally
            scale = (self.width - (num_cols - 1) * 3 - 4) / sum(widths)
            widths = [max(5, int(w * scale)) for w in widths]
        
        return widths
    
    def render(self) -> List[str]:
        """Render table"""
        if not self.visible:
            return []
        
        lines = []
        
        # Top border
        border_parts = ['╭']
        for i, width in enumerate(self.column_widths):
            border_parts.append('─' * (width + 2))
            if i < len(self.column_widths) - 1:
                border_parts.append('┬')
        border_parts.append('╮')
        lines.append(''.join(border_parts))
        
        # Header
        header_parts = ['│']
        for i, (header, width) in enumerate(zip(self.headers, self.column_widths)):
            header_parts.append(f" {header.ljust(width)} ")
            if i < len(self.headers) - 1:
                header_parts.append('│')
        header_parts.append('│')
        lines.append('\x1b[1m' + ''.join(header_parts) + '\x1b[0m')
        
        # Header separator
        sep_parts = ['├']
        for i, width in enumerate(self.column_widths):
            sep_parts.append('─' * (width + 2))
            if i < len(self.column_widths) - 1:
                sep_parts.append('┼')
        sep_parts.append('┤')
        lines.append(''.join(sep_parts))
        
        # Rows
        for row_idx, row in enumerate(self.rows):
            row_parts = ['│']
            
            # Highlight selected row
            if row_idx == self.selected_row:
                color = '\x1b[44m'  # Blue background
            else:
                color = ''
            
            for i, (cell, width) in enumerate(zip(row, self.column_widths)):
                cell_str = str(cell).ljust(width)
                row_parts.append(f" {cell_str} ")
                if i < len(row) - 1:
                    row_parts.append('│')
            
            row_parts.append('│')
            lines.append(color + ''.join(row_parts) + '\x1b[0m')
        
        # Bottom border
        border_parts = ['╰']
        for i, width in enumerate(self.column_widths):
            border_parts.append('─' * (width + 2))
            if i < len(self.column_widths) - 1:
                border_parts.append('┴')
        border_parts.append('╯')
        lines.append(''.join(border_parts))
        
        return lines
    
    def handle_key(self, key: str) -> bool:
        """Handle key press"""
        if key in ['up', 'k']:
            self.selected_row = max(0, self.selected_row - 1)
            return True
        elif key in ['down', 'j']:
            self.selected_row = min(len(self.rows) - 1, self.selected_row + 1)
            return True
        
        return False


# =============================================================================
# NOTIFICATION
# =============================================================================

class Notification(Component):
    """Toast notification component"""
    
    def __init__(
        self,
        message: str,
        duration: float = 3.0,
        notification_type: DialogType = DialogType.INFO
    ):
        """Initialize notification"""
        width = min(50, len(message) + 4)
        super().__init__(0, 0, width, 3)
        
        self.message = message
        self.duration = duration
        self.notification_type = notification_type
        self.start_time = time.time()
    
    def is_expired(self) -> bool:
        """Check if notification has expired"""
        return time.time() - self.start_time >= self.duration
    
    def render(self) -> List[str]:
        """Render notification"""
        if not self.visible or self.is_expired():
            return []
        
        # Colors based on type
        colors = {
            DialogType.INFO: (100, 150, 255),
            DialogType.SUCCESS: (0, 255, 100),
            DialogType.WARNING: (255, 200, 0),
            DialogType.ERROR: (255, 50, 50),
        }
        
        color = colors[self.notification_type]
        color_code = f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m"
        reset = "\x1b[0m"
        
        lines = []
        
        # Top border
        lines.append(f"{color_code}╭{'─' * (self.width - 2)}╮{reset}")
        
        # Message
        message_padded = self.message.center(self.width - 2)
        lines.append(f"{color_code}│{message_padded}│{reset}")
        
        # Bottom border
        lines.append(f"{color_code}╰{'─' * (self.width - 2)}╯{reset}")
        
        return lines


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - UI Components Module")
    print("=" * 50)
    
    # Test button
    print("\nButton:")
    button = Button(0, 0, "Click Me", style=ButtonStyle.PRIMARY)
    for line in button.render():
        print(line)
    
    # Test progress bar
    print("\nProgress Bar:")
    progress = ProgressBar(0, 0, 40, progress=0.65)
    for line in progress.render():
        print(line)
    
    # Test spinner
    print("\nSpinner:")
    spinner = Spinner(0, 0, style='dots', text="Loading...")
    for line in spinner.render():
        print(line)
    
    # Test menu
    print("\nMenu:")
    menu_items = [
        MenuItem("New File", shortcut="Ctrl+N"),
        MenuItem("Open File", shortcut="Ctrl+O"),
        MenuItem("Save", shortcut="Ctrl+S"),
        MenuItem("Exit", shortcut="Ctrl+Q"),
    ]
    menu = Menu(0, 0, menu_items)
    for line in menu.render():
        print(line)
    
    # Test table
    print("\nTable:")
    table = Table(
        0, 0,
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "25", "San Francisco"],
            ["Charlie", "35", "Chicago"],
        ],
        width=50
    )
    for line in table.render():
        print(line)
    
    print("\n✅ UI components module test complete")
