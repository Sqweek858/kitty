#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ADVANCED UI COMPONENTS SYSTEM                          ║
║           Rich Terminal User Interface with Gradient Borders                ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides sophisticated UI components for terminal interfaces:
    - Menu bars with persistent display
    - Autocomplete panels with fuzzy matching
    - Gradient bordered containers
    - Status bars and indicators
    - Modal dialogs and notifications
    - Progress bars and spinners
    - Tables and lists with scrolling
    - Input fields with validation
"""

import math
import time
from typing import List, Optional, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque

from shader_system import Color, Vec2


# ═══════════════════════════════════════════════════════════════════════════════
# BORDER STYLES AND CHARACTERS
# ═══════════════════════════════════════════════════════════════════════════════

class BorderStyle(Enum):
    """Border drawing styles"""
    NONE = auto()
    SINGLE = auto()
    DOUBLE = auto()
    ROUNDED = auto()
    THICK = auto()
    DASHED = auto()
    DOTTED = auto()
    GRADIENT = auto()


@dataclass
class BorderChars:
    """Border character set"""
    top_left: str
    top_right: str
    bottom_left: str
    bottom_right: str
    horizontal: str
    vertical: str
    top_join: str
    bottom_join: str
    left_join: str
    right_join: str
    cross: str


# Border character sets
BORDER_CHARS = {
    BorderStyle.SINGLE: BorderChars('┌', '┐', '└', '┘', '─', '│', '┬', '┴', '├', '┤', '┼'),
    BorderStyle.DOUBLE: BorderChars('╔', '╗', '╚', '╝', '═', '║', '╦', '╩', '╠', '╣', '╬'),
    BorderStyle.ROUNDED: BorderChars('╭', '╮', '╰', '╯', '─', '│', '┬', '┴', '├', '┤', '┼'),
    BorderStyle.THICK: BorderChars('┏', '┓', '┗', '┛', '━', '┃', '┳', '┻', '┣', '┫', '╋'),
    BorderStyle.DASHED: BorderChars('┌', '┐', '└', '┘', '╌', '╎', '┬', '┴', '├', '┤', '┼'),
    BorderStyle.DOTTED: BorderChars('┌', '┐', '└', '┘', '┄', '┆', '┬', '┴', '├', '┤', '┼'),
}


# ═══════════════════════════════════════════════════════════════════════════════
# GRADIENT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

class GradientType(Enum):
    """Gradient direction types"""
    HORIZONTAL = auto()
    VERTICAL = auto()
    DIAGONAL_TL_BR = auto()  # Top-left to bottom-right
    DIAGONAL_TR_BL = auto()  # Top-right to bottom-left
    RADIAL = auto()
    CONIC = auto()


class GradientGenerator:
    """Generate color gradients for borders and backgrounds"""
    
    @staticmethod
    def linear(start: Color, end: Color, t: float) -> Color:
        """Linear gradient interpolation"""
        return start.blend(end, t)
    
    @staticmethod
    def multi_stop(colors: List[Tuple[float, Color]], t: float) -> Color:
        """Multi-stop gradient"""
        if not colors:
            return Color(1, 1, 1)
        
        if t <= colors[0][0]:
            return colors[0][1]
        if t >= colors[-1][0]:
            return colors[-1][1]
        
        # Find the two colors to interpolate between
        for i in range(len(colors) - 1):
            if colors[i][0] <= t <= colors[i + 1][0]:
                local_t = (t - colors[i][0]) / (colors[i + 1][0] - colors[i][0])
                return GradientGenerator.linear(colors[i][1], colors[i + 1][1], local_t)
        
        return colors[-1][1]
    
    @staticmethod
    def rainbow(t: float, saturation: float = 1.0, value: float = 1.0) -> Color:
        """Rainbow gradient"""
        hue = t * 360.0
        return Color.from_hsv(hue, saturation, value)
    
    @staticmethod
    def cyberpunk(t: float) -> Color:
        """Cyberpunk-themed gradient (cyan -> magenta -> yellow)"""
        stops = [
            (0.0, Color(0.0, 1.0, 1.0)),    # Cyan
            (0.33, Color(0.5, 0.0, 1.0)),   # Purple
            (0.66, Color(1.0, 0.0, 0.5)),   # Magenta
            (1.0, Color(1.0, 1.0, 0.0))     # Yellow
        ]
        return GradientGenerator.multi_stop(stops, t)
    
    @staticmethod
    def fire(t: float) -> Color:
        """Fire gradient (black -> red -> orange -> yellow -> white)"""
        stops = [
            (0.0, Color(0.0, 0.0, 0.0)),    # Black
            (0.25, Color(0.5, 0.0, 0.0)),   # Dark red
            (0.5, Color(1.0, 0.2, 0.0)),    # Red-orange
            (0.75, Color(1.0, 0.7, 0.0)),   # Orange-yellow
            (1.0, Color(1.0, 1.0, 0.8))     # Pale yellow
        ]
        return GradientGenerator.multi_stop(stops, t)
    
    @staticmethod
    def ice(t: float) -> Color:
        """Ice gradient (dark blue -> cyan -> white)"""
        stops = [
            (0.0, Color(0.0, 0.1, 0.3)),    # Dark blue
            (0.5, Color(0.0, 0.8, 1.0)),    # Cyan
            (1.0, Color(0.9, 1.0, 1.0))     # Pale cyan-white
        ]
        return GradientGenerator.multi_stop(stops, t)
    
    @staticmethod
    def matrix(t: float) -> Color:
        """Matrix-style green gradient"""
        stops = [
            (0.0, Color(0.0, 0.2, 0.0)),    # Dark green
            (0.5, Color(0.0, 1.0, 0.0)),    # Bright green
            (1.0, Color(0.8, 1.0, 0.8))     # Pale green
        ]
        return GradientGenerator.multi_stop(stops, t)
    
    @staticmethod
    def christmas(t: float) -> Color:
        """Christmas gradient (red -> green -> gold)"""
        stops = [
            (0.0, Color(0.8, 0.0, 0.0)),    # Red
            (0.5, Color(0.0, 0.6, 0.2)),    # Green
            (1.0, Color(1.0, 0.84, 0.0))    # Gold
        ]
        return GradientGenerator.multi_stop(stops, t)


# ═══════════════════════════════════════════════════════════════════════════════
# BASE UI COMPONENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Rect:
    """Rectangle definition"""
    x: int
    y: int
    width: int
    height: int
    
    def contains(self, px: int, py: int) -> bool:
        """Check if point is inside rectangle"""
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height
    
    def intersects(self, other: 'Rect') -> bool:
        """Check if rectangles intersect"""
        return not (self.x + self.width <= other.x or
                   other.x + other.width <= self.x or
                   self.y + self.height <= other.y or
                   other.y + other.height <= self.y)


class UIComponent:
    """Base class for all UI components"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.focused = False
        self.dirty = True  # Needs redraw
        
    def render(self, screen, time: float):
        """Render component to screen buffer"""
        pass
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input. Return True if handled."""
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """Handle mouse input. Return True if handled."""
        return False
    
    def update(self, delta_time: float):
        """Update component state"""
        pass
    
    def set_position(self, x: int, y: int):
        """Set component position"""
        self.rect.x = x
        self.rect.y = y
        self.dirty = True
    
    def set_size(self, width: int, height: int):
        """Set component size"""
        self.rect.width = width
        self.rect.height = height
        self.dirty = True


# ═══════════════════════════════════════════════════════════════════════════════
# BORDERED CONTAINER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BorderedContainerStyle:
    """Style configuration for bordered containers"""
    border_style: BorderStyle = BorderStyle.ROUNDED
    gradient_type: Optional[str] = "cyberpunk"  # None, "rainbow", "cyberpunk", "fire", etc.
    gradient_speed: float = 1.0
    padding: int = 1
    title: Optional[str] = None
    title_align: str = "center"  # "left", "center", "right"


class BorderedContainer(UIComponent):
    """Container with animated gradient border"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 style: Optional[BorderedContainerStyle] = None):
        super().__init__(x, y, width, height)
        self.style = style or BorderedContainerStyle()
        self.content: List[str] = []
        self.gradient_offset = 0.0
        
    def set_content(self, lines: List[str]):
        """Set container content"""
        self.content = lines
        self.dirty = True
    
    def update(self, delta_time: float):
        """Update gradient animation"""
        if self.style.gradient_type:
            self.gradient_offset += delta_time * self.style.gradient_speed
            if self.gradient_offset > 1.0:
                self.gradient_offset -= 1.0
            self.dirty = True
    
    def _get_gradient_color(self, position: float, time_offset: float = 0.0) -> Color:
        """Get gradient color at position"""
        t = (position + self.gradient_offset + time_offset) % 1.0
        
        if self.style.gradient_type == "rainbow":
            return GradientGenerator.rainbow(t)
        elif self.style.gradient_type == "cyberpunk":
            return GradientGenerator.cyberpunk(t)
        elif self.style.gradient_type == "fire":
            return GradientGenerator.fire(t)
        elif self.style.gradient_type == "ice":
            return GradientGenerator.ice(t)
        elif self.style.gradient_type == "matrix":
            return GradientGenerator.matrix(t)
        elif self.style.gradient_type == "christmas":
            return GradientGenerator.christmas(t)
        else:
            return Color(0.5, 0.5, 0.5)
    
    def render(self, screen, time: float):
        """Render bordered container with gradient"""
        if not self.visible:
            return
        
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height
        
        border = BORDER_CHARS.get(self.style.border_style)
        if not border:
            return
        
        # Calculate gradient for borders
        perimeter = 2 * (w + h - 2)
        
        def get_border_color(edge_pos: int) -> Tuple[int, int, int]:
            """Get color for border character at edge position"""
            t = edge_pos / perimeter
            color = self._get_gradient_color(t)
            return color.to_rgb255()
        
        # Top border
        edge_pos = 0
        for col in range(w):
            char = border.top_left if col == 0 else \
                   border.top_right if col == w - 1 else \
                   border.horizontal
            
            color = get_border_color(edge_pos)
            screen.set_char(x + col, y, char, color)
            edge_pos += 1
        
        # Right border
        for row in range(1, h - 1):
            color = get_border_color(edge_pos)
            screen.set_char(x + w - 1, y + row, border.vertical, color)
            edge_pos += 1
        
        # Bottom border
        for col in range(w - 1, -1, -1):
            char = border.bottom_right if col == w - 1 else \
                   border.bottom_left if col == 0 else \
                   border.horizontal
            
            color = get_border_color(edge_pos)
            screen.set_char(x + col, y + h - 1, char, color)
            edge_pos += 1
        
        # Left border
        for row in range(h - 2, 0, -1):
            color = get_border_color(edge_pos)
            screen.set_char(x, y + row, border.vertical, color)
            edge_pos += 1
        
        # Title
        if self.style.title:
            title = f" {self.style.title} "
            title_len = len(title)
            
            if self.style.title_align == "center":
                title_x = x + (w - title_len) // 2
            elif self.style.title_align == "right":
                title_x = x + w - title_len - 1
            else:  # left
                title_x = x + 1
            
            title_color = self._get_gradient_color(0.5).to_rgb255()
            for i, char in enumerate(title):
                screen.set_char(title_x + i, y, char, title_color)
        
        # Render content inside border
        content_x = x + 1 + self.style.padding
        content_y = y + 1 + self.style.padding
        content_w = w - 2 - 2 * self.style.padding
        content_h = h - 2 - 2 * self.style.padding
        
        for i, line in enumerate(self.content):
            if i >= content_h:
                break
            
            # Truncate or pad line
            display_line = line[:content_w].ljust(content_w)
            
            for j, char in enumerate(display_line):
                screen.set_char(content_x + j, content_y + i, char, None)


# ═══════════════════════════════════════════════════════════════════════════════
# MENU BAR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MenuItem:
    """Menu item definition"""
    label: str
    action: Optional[Callable[[], None]] = None
    shortcut: Optional[str] = None
    submenu: Optional[List['MenuItem']] = None
    separator: bool = False


class MenuBar(UIComponent):
    """Persistent menu bar at top of screen"""
    
    def __init__(self, x: int, y: int, width: int, items: List[MenuItem]):
        super().__init__(x, y, width, 1)
        self.items = items
        self.selected_index = -1
        self.submenu_open = False
        self.gradient_offset = 0.0
        
    def update(self, delta_time: float):
        """Update animations"""
        self.gradient_offset += delta_time * 0.5
        if self.gradient_offset > 1.0:
            self.gradient_offset -= 1.0
        self.dirty = True
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input"""
        if key == 'KEY_LEFT':
            self.selected_index = max(-1, self.selected_index - 1)
            self.dirty = True
            return True
        elif key == 'KEY_RIGHT':
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            self.dirty = True
            return True
        elif key == '\n' or key == ' ':
            if 0 <= self.selected_index < len(self.items):
                item = self.items[self.selected_index]
                if item.action:
                    item.action()
                return True
        elif key == '\x1b':  # Escape
            self.selected_index = -1
            self.dirty = True
            return True
        
        return False
    
    def render(self, screen, time: float):
        """Render menu bar"""
        if not self.visible:
            return
        
        x, y = self.rect.x, self.rect.y
        
        # Background with gradient
        for col in range(self.rect.width):
            t = (col / self.rect.width + self.gradient_offset) % 1.0
            bg_color = GradientGenerator.cyberpunk(t)
            bg_color = bg_color * 0.3  # Dim background
            screen.set_char(x + col, y, ' ', bg_color.to_rgb255())
        
        # Render menu items
        current_x = x + 2
        for i, item in enumerate(self.items):
            if item.separator:
                screen.set_char(current_x, y, '│', (100, 100, 100))
                current_x += 2
                continue
            
            # Highlight selected item
            if i == self.selected_index:
                fg_color = (255, 255, 100)  # Yellow
                label = f"[ {item.label} ]"
            else:
                fg_color = (200, 200, 200)
                label = f" {item.label} "
            
            # Add shortcut hint
            if item.shortcut:
                label += f" ({item.shortcut})"
            
            for char in label:
                screen.set_char(current_x, y, char, fg_color)
                current_x += 1
            
            current_x += 1  # Spacing


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOCOMPLETE PANEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AutocompleteEntry:
    """Autocomplete suggestion entry"""
    text: str
    description: Optional[str] = None
    score: float = 1.0  # Relevance score


class AutocompletePanel(UIComponent):
    """Autocomplete suggestions panel"""
    
    def __init__(self, x: int, y: int, width: int, max_height: int = 10):
        super().__init__(x, y, width, max_height)
        self.entries: List[AutocompleteEntry] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = max_height - 2  # Account for border
        
    def set_suggestions(self, entries: List[AutocompleteEntry]):
        """Set autocomplete suggestions"""
        self.entries = sorted(entries, key=lambda e: e.score, reverse=True)
        self.selected_index = 0
        self.scroll_offset = 0
        self.dirty = True
    
    def clear(self):
        """Clear suggestions"""
        self.entries = []
        self.dirty = True
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input"""
        if not self.entries:
            return False
        
        if key == 'KEY_UP':
            self.selected_index = max(0, self.selected_index - 1)
            
            # Adjust scroll
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            
            self.dirty = True
            return True
        
        elif key == 'KEY_DOWN':
            self.selected_index = min(len(self.entries) - 1, self.selected_index + 1)
            
            # Adjust scroll
            if self.selected_index >= self.scroll_offset + self.max_visible:
                self.scroll_offset = self.selected_index - self.max_visible + 1
            
            self.dirty = True
            return True
        
        elif key == '\t' or key == '\n':
            # Accept selected suggestion
            return True
        
        return False
    
    def get_selected(self) -> Optional[AutocompleteEntry]:
        """Get currently selected entry"""
        if 0 <= self.selected_index < len(self.entries):
            return self.entries[self.selected_index]
        return None
    
    def render(self, screen, time: float):
        """Render autocomplete panel"""
        if not self.visible or not self.entries:
            return
        
        x, y = self.rect.x, self.rect.y
        w = self.rect.width
        
        # Calculate actual height based on entries
        actual_height = min(len(self.entries) + 2, self.rect.height)
        
        # Draw border
        border = BORDER_CHARS[BorderStyle.ROUNDED]
        
        # Top border
        screen.set_char(x, y, border.top_left, (100, 200, 255))
        for col in range(1, w - 1):
            screen.set_char(x + col, y, border.horizontal, (100, 200, 255))
        screen.set_char(x + w - 1, y, border.top_right, (100, 200, 255))
        
        # Content
        visible_entries = self.entries[self.scroll_offset:self.scroll_offset + self.max_visible]
        
        for i, entry in enumerate(visible_entries):
            row = y + 1 + i
            
            # Left border
            screen.set_char(x, row, border.vertical, (100, 200, 255))
            
            # Entry content
            is_selected = (self.scroll_offset + i) == self.selected_index
            
            if is_selected:
                bg_color = (50, 100, 150)
                fg_color = (255, 255, 255)
                prefix = "▶ "
            else:
                bg_color = (20, 30, 40)
                fg_color = (200, 200, 200)
                prefix = "  "
            
            # Background
            for col in range(1, w - 1):
                screen.set_char(x + col, row, ' ', bg_color)
            
            # Text
            display_text = prefix + entry.text
            if entry.description:
                display_text += f" - {entry.description}"
            
            display_text = display_text[:w - 3]
            
            for col, char in enumerate(display_text):
                screen.set_char(x + 1 + col, row, char, fg_color)
            
            # Right border
            screen.set_char(x + w - 1, row, border.vertical, (100, 200, 255))
        
        # Bottom border
        bottom_y = y + 1 + len(visible_entries)
        screen.set_char(x, bottom_y, border.bottom_left, (100, 200, 255))
        for col in range(1, w - 1):
            screen.set_char(x + col, bottom_y, border.horizontal, (100, 200, 255))
        screen.set_char(x + w - 1, bottom_y, border.bottom_right, (100, 200, 255))
        
        # Scroll indicator
        if len(self.entries) > self.max_visible:
            if self.scroll_offset > 0:
                screen.set_char(x + w - 2, y + 1, '▲', (255, 255, 255))
            if self.scroll_offset + self.max_visible < len(self.entries):
                screen.set_char(x + w - 2, bottom_y - 1, '▼', (255, 255, 255))


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS BAR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StatusSegment:
    """Status bar segment"""
    text: str
    align: str = "left"  # "left", "center", "right"
    color: Optional[Tuple[int, int, int]] = None
    width: Optional[int] = None  # Fixed width, None for auto


class StatusBar(UIComponent):
    """Bottom status bar with multiple segments"""
    
    def __init__(self, x: int, y: int, width: int):
        super().__init__(x, y, width, 1)
        self.segments: List[StatusSegment] = []
        self.gradient_offset = 0.0
    
    def set_segments(self, segments: List[StatusSegment]):
        """Set status bar segments"""
        self.segments = segments
        self.dirty = True
    
    def update(self, delta_time: float):
        """Update animations"""
        self.gradient_offset += delta_time * 0.3
        if self.gradient_offset > 1.0:
            self.gradient_offset -= 1.0
        self.dirty = True
    
    def render(self, screen, time: float):
        """Render status bar"""
        if not self.visible:
            return
        
        x, y = self.rect.x, self.rect.y
        w = self.rect.width
        
        # Gradient background
        for col in range(w):
            t = (col / w + self.gradient_offset) % 1.0
            bg_color = GradientGenerator.cyberpunk(t)
            bg_color = bg_color * 0.2
            screen.set_char(x + col, y, ' ', bg_color.to_rgb255())
        
        # Render segments
        left_segments = [s for s in self.segments if s.align == "left"]
        center_segments = [s for s in self.segments if s.align == "center"]
        right_segments = [s for s in self.segments if s.align == "right"]
        
        # Left aligned
        current_x = x + 1
        for segment in left_segments:
            text = f" {segment.text} "
            color = segment.color or (200, 200, 200)
            
            for char in text:
                if current_x >= x + w:
                    break
                screen.set_char(current_x, y, char, color)
                current_x += 1
            
            current_x += 1  # Separator
        
        # Right aligned (render from right to left)
        current_x = x + w - 1
        for segment in reversed(right_segments):
            text = f" {segment.text} "
            color = segment.color or (200, 200, 200)
            
            for char in reversed(text):
                if current_x < x:
                    break
                screen.set_char(current_x, y, char, color)
                current_x -= 1
            
            current_x -= 1  # Separator
        
        # Center aligned
        if center_segments:
            center_text = " │ ".join([s.text for s in center_segments])
            center_x = x + (w - len(center_text)) // 2
            
            for i, char in enumerate(center_text):
                if x <= center_x + i < x + w:
                    screen.set_char(center_x + i, y, char, (200, 200, 200))


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT INPUT FIELD
# ═══════════════════════════════════════════════════════════════════════════════

class TextInput(UIComponent):
    """Single-line text input field with cursor"""
    
    def __init__(self, x: int, y: int, width: int, 
                 placeholder: str = "", max_length: Optional[int] = None):
        super().__init__(x, y, width, 1)
        self.text = ""
        self.cursor_pos = 0
        self.scroll_offset = 0
        self.placeholder = placeholder
        self.max_length = max_length
        self.cursor_visible = True
        self.cursor_blink_time = 0.0
        self.on_change: Optional[Callable[[str], None]] = None
        self.on_submit: Optional[Callable[[str], None]] = None
    
    def update(self, delta_time: float):
        """Update cursor blink"""
        self.cursor_blink_time += delta_time
        if self.cursor_blink_time >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = 0.0
            self.dirty = True
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input"""
        if not self.enabled:
            return False
        
        changed = False
        
        if key == 'KEY_LEFT':
            self.cursor_pos = max(0, self.cursor_pos - 1)
            self._adjust_scroll()
            self.dirty = True
            return True
        
        elif key == 'KEY_RIGHT':
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            self._adjust_scroll()
            self.dirty = True
            return True
        
        elif key == 'KEY_HOME':
            self.cursor_pos = 0
            self._adjust_scroll()
            self.dirty = True
            return True
        
        elif key == 'KEY_END':
            self.cursor_pos = len(self.text)
            self._adjust_scroll()
            self.dirty = True
            return True
        
        elif key == 'KEY_DELETE':
            if self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                changed = True
            self.dirty = True
            return True
        
        elif key == '\x7f' or key == '\x08':  # Backspace
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
                self._adjust_scroll()
                changed = True
            self.dirty = True
            return True
        
        elif key == '\n':  # Enter
            if self.on_submit:
                self.on_submit(self.text)
            return True
        
        elif len(key) == 1 and key.isprintable():
            # Regular character input
            if self.max_length is None or len(self.text) < self.max_length:
                self.text = self.text[:self.cursor_pos] + key + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self._adjust_scroll()
                changed = True
            self.dirty = True
            return True
        
        if changed and self.on_change:
            self.on_change(self.text)
        
        return False
    
    def _adjust_scroll(self):
        """Adjust scroll offset to keep cursor visible"""
        visible_width = self.rect.width
        
        if self.cursor_pos < self.scroll_offset:
            self.scroll_offset = self.cursor_pos
        elif self.cursor_pos >= self.scroll_offset + visible_width:
            self.scroll_offset = self.cursor_pos - visible_width + 1
    
    def render(self, screen, time: float):
        """Render text input"""
        if not self.visible:
            return
        
        x, y = self.rect.x, self.rect.y
        w = self.rect.width
        
        # Display text or placeholder
        if self.text:
            visible_text = self.text[self.scroll_offset:self.scroll_offset + w]
            text_color = (255, 255, 255) if self.focused else (200, 200, 200)
        else:
            visible_text = self.placeholder[:w]
            text_color = (100, 100, 100)
        
        # Render text
        for i in range(w):
            if i < len(visible_text):
                char = visible_text[i]
            else:
                char = ' '
            
            screen.set_char(x + i, y, char, text_color)
        
        # Render cursor
        if self.focused and self.cursor_visible:
            cursor_x = x + (self.cursor_pos - self.scroll_offset)
            if 0 <= cursor_x - x < w:
                # Use block cursor
                screen.set_char(cursor_x, y, '█', (100, 200, 255))


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'BorderStyle', 'BorderChars', 'BORDER_CHARS',
    'GradientType', 'GradientGenerator',
    'Rect', 'UIComponent',
    'BorderedContainer', 'BorderedContainerStyle',
    'MenuBar', 'MenuItem',
    'AutocompletePanel', 'AutocompleteEntry',
    'StatusBar', 'StatusSegment',
    'TextInput',
]
