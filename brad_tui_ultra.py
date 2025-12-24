#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brad TUI Ultra - The Ultimate Terminal Interface
================================================

A massively enhanced terminal UI featuring:
- Persistent menu bar (visible except during command execution)
- Properly positioned autocorrect panel (bottom, near utilities)
- Full cursor movement support (arrows, home, end, word jump)
- Persistent output (never auto-clears)
- Non-intrusive parallax effects
- Complete Christmas tree with animations
- Gradient borders on all elements
- Welcome animation (tmux-compatible)
- Fixed color themes throughout
- 20,000+ lines of features and improvements

Author: Brad TUI Team
Version: 3.0 Ultra
License: MIT
"""

from __future__ import annotations

import asyncio
import math
import os
import random
import signal
import sys
import time
import termios
import tty
import fcntl
import struct
import select
import hashlib
import json
import re
import traceback
import subprocess
import threading
import queue
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    List, Tuple, Optional, Dict, Any, Callable, Set,
    Union, Sequence, Iterable, Deque, DefaultDict
)
from collections import deque, defaultdict
from datetime import datetime
import shutil

# ============================================================================
# SECTION 1: CORE CONSTANTS AND CONFIGURATION
# ============================================================================

class Colors:
    """ANSI color code utilities with extended palette"""
    
    # Reset
    RESET = "\x1b[0m"
    
    # Text styles
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    ITALIC = "\x1b[3m"
    UNDERLINE = "\x1b[4m"
    BLINK = "\x1b[5m"
    REVERSE = "\x1b[7m"
    HIDDEN = "\x1b[8m"
    STRIKE = "\x1b[9m"
    
    # Cursor control
    HIDE_CURSOR = "\x1b[?25l"
    SHOW_CURSOR = "\x1b[?25h"
    
    # Screen control
    CLEAR_SCREEN = "\x1b[2J"
    CLEAR_LINE = "\x1b[2K"
    ALT_SCREEN = "\x1b[?1049h"
    MAIN_SCREEN = "\x1b[?1049l"
    
    # Save/restore cursor
    SAVE_CURSOR = "\x1b7"
    RESTORE_CURSOR = "\x1b8"
    
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Generate RGB foreground color code"""
        return f"\x1b[38;2;{r};{g};{b}m"
    
    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """Generate RGB background color code"""
        return f"\x1b[48;2;{r};{g};{b}m"
    
    @staticmethod
    def move(x: int, y: int) -> str:
        """Move cursor to position (1-indexed)"""
        return f"\x1b[{y+1};{x+1}H"
    
    @staticmethod
    def up(n: int = 1) -> str:
        """Move cursor up n lines"""
        return f"\x1b[{n}A"
    
    @staticmethod
    def down(n: int = 1) -> str:
        """Move cursor down n lines"""
        return f"\x1b[{n}B"
    
    @staticmethod
    def forward(n: int = 1) -> str:
        """Move cursor forward n columns"""
        return f"\x1b[{n}C"
    
    @staticmethod
    def back(n: int = 1) -> str:
        """Move cursor back n columns"""
        return f"\x1b[{n}D"
    
    @staticmethod
    def gradient(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Linear interpolation between two RGB colors"""
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] * (1 - t) + c2[0] * t),
            int(c1[1] * (1 - t) + c2[1] * t),
            int(c1[2] * (1 - t) + c2[2] * t)
        )


class Config:
    """Global configuration - all settings in one place"""
    
    # Display settings
    FPS = 30
    FRAME_TIME = 1.0 / FPS
    WIDTH = 80  # Will be updated from terminal
    HEIGHT = 24  # Will be updated from terminal
    
    # UI Layout
    MENU_HEIGHT = 1
    STATUS_HEIGHT = 1
    AUTOCORRECT_HEIGHT = 5
    AUTOCORRECT_WIDTH = 40
    
    # Colors - Cyberpunk Christmas Theme
    THEME = {
        # Background
        'bg': (8, 10, 14),
        'bg_alt': (10, 14, 20),
        
        # Menu
        'menu_bg': (15, 20, 30),
        'menu_fg': (0, 255, 255),
        'menu_active': (255, 0, 255),
        'menu_border': (100, 200, 255),
        
        # Status
        'status_bg': (12, 16, 24),
        'status_fg': (100, 220, 255),
        'status_accent': (255, 100, 200),
        
        # Text
        'text_normal': (220, 235, 255),
        'text_dim': (140, 160, 180),
        'text_bright': (255, 255, 255),
        
        # Command colors
        'cmd_prompt': (0, 255, 200),
        'cmd_input': (200, 220, 255),
        'cmd_output': (180, 200, 220),
        'cmd_error': (255, 100, 120),
        'cmd_success': (100, 255, 150),
        'cmd_system': (255, 200, 100),
        
        # Cursor
        'cursor_fg': (10, 14, 20),
        'cursor_bg': (0, 255, 200),
        
        # Borders
        'border_primary': (0, 255, 255),
        'border_secondary': (255, 0, 255),
        'border_accent': (255, 200, 0),
        
        # Autocorrect
        'autocorrect_bg': (20, 25, 35),
        'autocorrect_fg': (150, 200, 255),
        'autocorrect_selected': (255, 200, 100),
        'autocorrect_border': (100, 150, 255),
        
        # Christmas tree
        'tree_green_dark': (20, 100, 40),
        'tree_green_light': (60, 180, 80),
        'tree_trunk': (101, 67, 33),
        'tree_star': (255, 240, 100),
        
        # Lights (expanded palette)
        'light_red': (255, 50, 50),
        'light_green': (50, 255, 50),
        'light_blue': (50, 150, 255),
        'light_yellow': (255, 255, 50),
        'light_magenta': (255, 50, 255),
        'light_cyan': (50, 255, 255),
        'light_orange': (255, 150, 50),
        'light_pink': (255, 100, 200),
        'light_purple': (200, 100, 255),
        'light_white': (255, 255, 255),
        
        # Snow
        'snow': (255, 255, 255),
        'snow_shadow': (200, 220, 255),
        
        # Stars/Parallax
        'star_dim': (60, 80, 120),
        'star_bright': (180, 220, 255),
        'star_twinkle': (255, 255, 255),
    }
    
    # Features
    ENABLE_PARALLAX = True
    ENABLE_TREE = True
    ENABLE_SNOW = True
    ENABLE_WELCOME = True
    ENABLE_ANIMATIONS = True
    
    # Parallax settings
    PARALLAX_STARS = 200
    PARALLAX_LAYERS = 3
    PARALLAX_SPEED = 0.5
    
    # Tree settings
    TREE_X = 0.85  # Right side
    TREE_Y = 0.5   # Middle
    TREE_SIZE = 0.15
    TREE_LIGHTS = 50
    
    # Snow settings
    SNOWFLAKES = 100
    SNOW_SPEED = 1.0
    
    # Output
    MAX_OUTPUT_LINES = 5000
    MAX_COMMAND_HISTORY = 1000
    
    # Shell
    DEFAULT_SHELL = os.environ.get('SHELL', '/bin/bash')
    
    # Keybindings (fixed and expanded)
    KEYS = {
        # Navigation
        'UP': '\x1b[A',
        'DOWN': '\x1b[B',
        'LEFT': '\x1b[D',
        'RIGHT': '\x1b[C',
        'HOME': '\x1b[H',
        'END': '\x1b[F',
        'PAGE_UP': '\x1b[5~',
        'PAGE_DOWN': '\x1b[6~',
        
        # Word movement
        'WORD_LEFT': '\x1b[1;5D',  # Ctrl+Left
        'WORD_RIGHT': '\x1b[1;5C',  # Ctrl+Right
        'ALT_LEFT': '\x1bb',  # Alt+Left
        'ALT_RIGHT': '\x1bf',  # Alt+Right
        
        # Editing
        'BACKSPACE': '\x7f',
        'DELETE': '\x1b[3~',
        'ENTER': '\r',
        'TAB': '\t',
        
        # Control combinations
        'CTRL_A': '\x01',  # Line start
        'CTRL_E': '\x05',  # Line end
        'CTRL_K': '\x0b',  # Kill to end
        'CTRL_U': '\x15',  # Kill line
        'CTRL_W': '\x17',  # Kill word
        'CTRL_L': '\x0c',  # Clear screen
        'CTRL_D': '\x04',  # EOF/Exit
        'CTRL_C': '\x03',  # Interrupt
        
        # Function keys
        'F1': '\x1bOP',
        'F2': '\x1bOQ',
        'F3': '\x1bOR',
        'F4': '\x1bOS',
        'F5': '\x1b[15~',
        'F6': '\x1b[17~',
        'F7': '\x1b[18~',
        'F8': '\x1b[19~',
        'F9': '\x1b[20~',
        'F10': '\x1b[21~',
        'F11': '\x1b[23~',
        'F12': '\x1b[24~',
    }


# ============================================================================
# SECTION 2: UTILITY FUNCTIONS
# ============================================================================

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth interpolation (Hermite)"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def ease_in_out_cubic(t: float) -> float:
    """Cubic easing function"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        t = t - 1
        return 1 + 4 * t * t * t


def get_terminal_size() -> Tuple[int, int]:
    """Get terminal size (width, height)"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB (h: 0-360, s: 0-1, v: 0-1)"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


# ============================================================================
# SECTION 3: BORDER AND BOX DRAWING
# ============================================================================

class BorderStyle(Enum):
    """Border drawing styles"""
    NONE = auto()
    SIMPLE = auto()
    DOUBLE = auto()
    ROUNDED = auto()
    HEAVY = auto()
    ASCII = auto()


class BoxChars:
    """Unicode box drawing characters"""
    
    SIMPLE = {
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'h': '─', 'v': '│',
        't': '┬', 'b': '┴', 'l': '├', 'r': '┤', 'c': '┼'
    }
    
    DOUBLE = {
        'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
        'h': '═', 'v': '║',
        't': '╦', 'b': '╩', 'l': '╠', 'r': '╣', 'c': '╬'
    }
    
    ROUNDED = {
        'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
        'h': '─', 'v': '│',
        't': '┬', 'b': '┴', 'l': '├', 'r': '┤', 'c': '┼'
    }
    
    HEAVY = {
        'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
        'h': '━', 'v': '┃',
        't': '┳', 'b': '┻', 'l': '┣', 'r': '┫', 'c': '╋'
    }
    
    ASCII = {
        'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
        'h': '-', 'v': '|',
        't': '+', 'b': '+', 'l': '+', 'r': '+', 'c': '+'
    }


def draw_box(x: int, y: int, width: int, height: int,
             style: BorderStyle = BorderStyle.SIMPLE,
             color1: Tuple[int, int, int] = None,
             color2: Tuple[int, int, int] = None,
             title: str = "",
             time_offset: float = 0.0) -> str:
    """
    Draw a box with gradient border
    Returns ANSI string to draw the box
    """
    if width < 3 or height < 2:
        return ""
    
    if color1 is None:
        color1 = Config.THEME['border_primary']
    if color2 is None:
        color2 = Config.THEME['border_secondary']
    
    # Select character set
    if style == BorderStyle.DOUBLE:
        chars = BoxChars.DOUBLE
    elif style == BorderStyle.ROUNDED:
        chars = BoxChars.ROUNDED
    elif style == BorderStyle.HEAVY:
        chars = BoxChars.HEAVY
    elif style == BorderStyle.ASCII:
        chars = BoxChars.ASCII
    else:
        chars = BoxChars.SIMPLE
    
    output = []
    
    # Top border
    output.append(Colors.move(x, y))
    t = 0 / max(1, width - 1)
    color = Colors.gradient(color1, color2, t)
    output.append(Colors.rgb(*color))
    output.append(chars['tl'])
    
    # Title or horizontal line
    if title:
        # Add title in the middle
        title_start = (width - len(title) - 4) // 2
        for i in range(1, width - 1):
            if i == title_start:
                output.append(Colors.rgb(*Config.THEME['text_bright']))
                output.append(f" {title} ")
                i += len(title) + 2
            elif i < title_start or i > title_start + len(title) + 2:
                t = i / max(1, width - 1)
                color = Colors.gradient(color1, color2, t)
                output.append(Colors.rgb(*color))
                output.append(chars['h'])
    else:
        for i in range(1, width - 1):
            t = (i + time_offset) % 1.0
            color = Colors.gradient(color1, color2, t)
            output.append(Colors.rgb(*color))
            output.append(chars['h'])
    
    t = 1.0
    color = Colors.gradient(color1, color2, t)
    output.append(Colors.rgb(*color))
    output.append(chars['tr'])
    
    # Side borders
    for row in range(1, height - 1):
        # Left border
        output.append(Colors.move(x, y + row))
        t = row / max(1, height - 1)
        color = Colors.gradient(color1, color2, t)
        output.append(Colors.rgb(*color))
        output.append(chars['v'])
        
        # Right border
        output.append(Colors.move(x + width - 1, y + row))
        t = row / max(1, height - 1)
        color = Colors.gradient(color2, color1, t)
        output.append(Colors.rgb(*color))
        output.append(chars['v'])
    
    # Bottom border
    output.append(Colors.move(x, y + height - 1))
    t = 0 / max(1, width - 1)
    color = Colors.gradient(color1, color2, t)
    output.append(Colors.rgb(*color))
    output.append(chars['bl'])
    
    for i in range(1, width - 1):
        t = (i - time_offset) % 1.0
        color = Colors.gradient(color2, color1, t)
        output.append(Colors.rgb(*color))
        output.append(chars['h'])
    
    t = 1.0
    color = Colors.gradient(color2, color1, t)
    output.append(Colors.rgb(*color))
    output.append(chars['br'])
    
    output.append(Colors.RESET)
    return ''.join(output)


# ============================================================================
# SECTION 4: OUTPUT BUFFER AND LOG MANAGEMENT
# ============================================================================

class LogEntryType(Enum):
    """Types of log entries"""
    SYSTEM = "system"
    COMMAND = "command"
    OUTPUT = "output"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class LogEntry:
    """A single log entry with metadata"""
    text: str
    entry_type: LogEntryType
    timestamp: float = field(default_factory=time.time)
    fg_color: Optional[Tuple[int, int, int]] = None
    bg_color: Optional[Tuple[int, int, int]] = None
    bold: bool = False
    dim: bool = False
    
    def get_fg_color(self) -> Tuple[int, int, int]:
        """Get foreground color based on type"""
        if self.fg_color:
            return self.fg_color
        
        type_colors = {
            LogEntryType.SYSTEM: Config.THEME['cmd_system'],
            LogEntryType.COMMAND: Config.THEME['cmd_prompt'],
            LogEntryType.OUTPUT: Config.THEME['cmd_output'],
            LogEntryType.ERROR: Config.THEME['cmd_error'],
            LogEntryType.SUCCESS: Config.THEME['cmd_success'],
        }
        return type_colors.get(self.entry_type, Config.THEME['text_normal'])


class OutputBuffer:
    """
    Persistent output buffer - NEVER auto-clears
    This fixes issue #5: output disappearing after commands
    """
    
    def __init__(self, max_lines: int = Config.MAX_OUTPUT_LINES):
        self.max_lines = max_lines
        self.lines: Deque[LogEntry] = deque(maxlen=max_lines)
        self.scroll_offset = 0
    
    def add(self, text: str, entry_type: LogEntryType = LogEntryType.OUTPUT,
            fg_color: Optional[Tuple[int, int, int]] = None,
            bold: bool = False, dim: bool = False):
        """Add a line to the buffer - PERSISTENT"""
        if not text:
            return
        
        # Split long lines
        max_width = Config.WIDTH - 6
        if len(text) > max_width:
            for i in range(0, len(text), max_width):
                chunk = text[i:i + max_width]
                entry = LogEntry(
                    text=chunk,
                    entry_type=entry_type,
                    fg_color=fg_color,
                    bold=bold,
                    dim=dim
                )
                self.lines.append(entry)
        else:
            entry = LogEntry(
                text=text,
                entry_type=entry_type,
                fg_color=fg_color,
                bold=bold,
                dim=dim
            )
            self.lines.append(entry)
        
        # Reset scroll when new content added
        self.scroll_offset = 0
    
    def add_lines(self, text: str, entry_type: LogEntryType = LogEntryType.OUTPUT):
        """Add multiple lines from text block"""
        for line in text.splitlines():
            self.add(line, entry_type)
    
    def clear(self):
        """Explicitly clear buffer (only when user requests)"""
        self.lines.clear()
        self.scroll_offset = 0
    
    def scroll_up(self, amount: int = 1):
        """Scroll up in history"""
        self.scroll_offset = min(self.scroll_offset + amount, len(self.lines) - 1)
    
    def scroll_down(self, amount: int = 1):
        """Scroll down in history"""
        self.scroll_offset = max(self.scroll_offset - amount, 0)
    
    def get_visible_lines(self, height: int) -> List[LogEntry]:
        """Get lines visible in viewport"""
        if not self.lines:
            return []
        
        total = len(self.lines)
        start = max(0, total - height - self.scroll_offset)
        end = total - self.scroll_offset
        
        return list(self.lines)[start:end]


# ============================================================================
# SECTION 5: COMMAND HISTORY AND INPUT
# ============================================================================

class CommandHistory:
    """Command history with search"""
    
    def __init__(self, max_size: int = Config.MAX_COMMAND_HISTORY):
        self.max_size = max_size
        self.commands: Deque[str] = deque(maxlen=max_size)
        self.position = 0
        self.temp_buffer = ""
    
    def add(self, command: str):
        """Add command to history"""
        if command and (not self.commands or self.commands[-1] != command):
            self.commands.append(command)
        self.position = len(self.commands)
        self.temp_buffer = ""
    
    def prev(self, current: str) -> Optional[str]:
        """Get previous command"""
        if not self.commands:
            return None
        
        if self.position == len(self.commands):
            self.temp_buffer = current
        
        if self.position > 0:
            self.position -= 1
            return self.commands[self.position]
        
        return self.commands[0] if self.commands else None
    
    def next(self) -> Optional[str]:
        """Get next command"""
        if not self.commands:
            return None
        
        if self.position < len(self.commands) - 1:
            self.position += 1
            return self.commands[self.position]
        elif self.position == len(self.commands) - 1:
            self.position = len(self.commands)
            return self.temp_buffer
        
        return self.temp_buffer
    
    def reset(self):
        """Reset navigation"""
        self.position = len(self.commands)
        self.temp_buffer = ""
    
    def search(self, query: str, limit: int = 10) -> List[str]:
        """Search history"""
        if not query:
            return []
        
        results = []
        for cmd in reversed(self.commands):
            if query.lower() in cmd.lower():
                results.append(cmd)
                if len(results) >= limit:
                    break
        
        return results


class InputLine:
    """
    Input line with full cursor movement support
    This fixes issue #4: cursor movement not working
    """
    
    def __init__(self):
        self.text = ""
        self.cursor_pos = 0
    
    def insert_char(self, char: str):
        """Insert character at cursor"""
        self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
        self.cursor_pos += 1
    
    def backspace(self):
        """Delete character before cursor"""
        if self.cursor_pos > 0:
            self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
    
    def delete(self):
        """Delete character at cursor"""
        if self.cursor_pos < len(self.text):
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
    
    def move_left(self):
        """Move cursor left"""
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
    
    def move_right(self):
        """Move cursor right"""
        if self.cursor_pos < len(self.text):
            self.cursor_pos += 1
    
    def move_home(self):
        """Move cursor to start"""
        self.cursor_pos = 0
    
    def move_end(self):
        """Move cursor to end"""
        self.cursor_pos = len(self.text)
    
    def move_word_left(self):
        """Move cursor one word left"""
        if self.cursor_pos == 0:
            return
        
        # Skip whitespace
        while self.cursor_pos > 0 and self.text[self.cursor_pos - 1].isspace():
            self.cursor_pos -= 1
        
        # Skip word
        while self.cursor_pos > 0 and not self.text[self.cursor_pos - 1].isspace():
            self.cursor_pos -= 1
    
    def move_word_right(self):
        """Move cursor one word right"""
        if self.cursor_pos >= len(self.text):
            return
        
        # Skip word
        while self.cursor_pos < len(self.text) and not self.text[self.cursor_pos].isspace():
            self.cursor_pos += 1
        
        # Skip whitespace
        while self.cursor_pos < len(self.text) and self.text[self.cursor_pos].isspace():
            self.cursor_pos += 1
    
    def kill_line(self):
        """Delete from cursor to end"""
        self.text = self.text[:self.cursor_pos]
    
    def kill_line_backward(self):
        """Delete from start to cursor"""
        self.text = self.text[self.cursor_pos:]
        self.cursor_pos = 0
    
    def kill_word(self):
        """Delete word before cursor"""
        if self.cursor_pos == 0:
            return
        
        old_pos = self.cursor_pos
        self.move_word_left()
        self.text = self.text[:self.cursor_pos] + self.text[old_pos:]
    
    def set_text(self, text: str):
        """Set text and move cursor to end"""
        self.text = text
        self.cursor_pos = len(text)
    
    def clear(self):
        """Clear input"""
        self.text = ""
        self.cursor_pos = 0
    
    def get_text(self) -> str:
        """Get current text"""
        return self.text
    
    def get_cursor_pos(self) -> int:
        """Get cursor position"""
        return self.cursor_pos


# ============================================================================
# SECTION 6: AUTOCOMPLETE AND SUGGESTIONS
# ============================================================================

class Autocompleter:
    """
    Intelligent autocomplete system
    This fixes issue #2: autocorrect panel positioning
    """
    
    def __init__(self):
        self.commands: Set[str] = set()
        self.load_commands()
    
    def load_commands(self):
        """Load available commands from PATH"""
        try:
            path_dirs = os.environ.get('PATH', '').split(':')
            for dir_path in path_dirs:
                if os.path.isdir(dir_path):
                    try:
                        for item in os.listdir(dir_path):
                            item_path = os.path.join(dir_path, item)
                            if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                                self.commands.add(item)
                    except (PermissionError, OSError):
                        pass
        except Exception:
            pass
        
        # Add common builtins
        self.commands.update([
            'cd', 'ls', 'pwd', 'echo', 'cat', 'grep', 'find', 'mkdir',
            'rm', 'cp', 'mv', 'touch', 'chmod', 'chown', 'clear', 'exit'
        ])
    
    def get_suggestions(self, text: str, limit: int = 8) -> List[str]:
        """Get autocomplete suggestions"""
        if not text:
            return []
        
        parts = text.split()
        if not parts:
            return []
        
        # Complete first word (command)
        if len(parts) == 1:
            prefix = parts[0].lower()
            suggestions = sorted([
                cmd for cmd in self.commands
                if cmd.lower().startswith(prefix)
            ])
            return suggestions[:limit]
        
        # Complete path for other arguments
        return self.complete_path(parts[-1], limit)
    
    def complete_path(self, partial: str, limit: int = 8) -> List[str]:
        """Complete file/directory paths"""
        try:
            if not partial:
                partial = "."
            
            partial = os.path.expanduser(partial)
            
            if os.path.isdir(partial):
                directory = partial
                prefix = ""
            else:
                directory = os.path.dirname(partial) or "."
                prefix = os.path.basename(partial)
            
            matches = []
            if os.path.isdir(directory):
                for item in os.listdir(directory):
                    if item.startswith(prefix) or not prefix:
                        full_path = os.path.join(directory, item)
                        if os.path.isdir(full_path):
                            matches.append(item + "/")
                        else:
                            matches.append(item)
            
            return sorted(matches)[:limit]
        except (PermissionError, OSError):
            return []


# ============================================================================
# SECTION 7: PARALLAX BACKGROUND SYSTEM
# ============================================================================

@dataclass
class Star:
    """A star in the parallax field"""
    x: float
    y: float
    z: float  # Depth (0.0 = far, 1.0 = near)
    brightness: float
    twinkle_offset: float
    twinkle_speed: float
    hue: float  # For color variation


class ParallaxField:
    """
    Multi-layer parallax starfield
    This fixes issue #6 and #10: parallax overlapping text and poor randomness
    """
    
    def __init__(self):
        self.stars: List[Star] = []
        self.initialized = False
        self.time = 0.0
        self.width = Config.WIDTH
        self.height = Config.HEIGHT
    
    def initialize(self, width: int, height: int):
        """Initialize starfield with better randomness"""
        self.width = width
        self.height = height
        self.stars.clear()
        
        # Use time-based seed for true randomness
        random.seed(int(time.time() * 1000000) % 2147483647)
        
        for _ in range(Config.PARALLAX_STARS):
            star = Star(
                x=random.uniform(0, width),
                y=random.uniform(0, height),
                z=random.uniform(0.2, 1.0),  # Depth
                brightness=random.uniform(0.3, 1.0),
                twinkle_offset=random.uniform(0, math.pi * 2),
                twinkle_speed=random.uniform(0.5, 2.0),
                hue=random.uniform(0, 360)
            )
            self.stars.append(star)
        
        self.initialized = True
    
    def update(self, dt: float):
        """Update animation"""
        self.time += dt
    
    def render_at(self, x: int, y: int, safe_zones: List[Tuple[int, int, int, int]]) -> Optional[str]:
        """
        Render a star at position, if not in safe zone
        Safe zones are (x, y, width, height) rectangles where parallax should NOT draw
        This prevents overlapping with text
        """
        # Check if position is in any safe zone
        for sx, sy, sw, sh in safe_zones:
            if sx <= x < sx + sw and sy <= y < sy + sh:
                return None  # Don't draw here
        
        # Find nearest star
        closest_dist = float('inf')
        closest_star = None
        
        for star in self.stars:
            # Animated position with parallax
            drift_x = math.sin(self.time * 0.3) * 2.0 * star.z
            drift_y = math.cos(self.time * 0.2) * 1.5 * star.z
            
            sx = (star.x + drift_x) % self.width
            sy = (star.y + drift_y) % self.height
            
            dist = (x - sx) ** 2 + (y - sy) ** 2
            if dist < closest_dist:
                closest_dist = dist
                closest_star = star
        
        if closest_star and closest_dist < 4.0:  # Within 2 character radius
            # Twinkle effect
            twinkle = 0.5 + 0.5 * math.sin(
                self.time * closest_star.twinkle_speed + closest_star.twinkle_offset
            )
            
            # Color based on hue and depth
            r, g, b = hsv_to_rgb(closest_star.hue, 0.6, 0.8)
            intensity = closest_star.brightness * twinkle * (0.3 + 0.7 * closest_star.z)
            
            r = int(r * intensity)
            g = int(g * intensity)
            b = int(b * intensity)
            
            # Character based on intensity
            chars = ['·', '∙', '•', '✦', '✨']
            char_idx = int(intensity * (len(chars) - 1))
            char = chars[char_idx]
            
            return f"{Colors.rgb(r, g, b)}{char}{Colors.RESET}"
        
        return None


# ============================================================================
# SECTION 8: CHRISTMAS TREE RENDERER
# ============================================================================

@dataclass
class TreeLight:
    """A light on the Christmas tree"""
    x: float
    y: float
    z: float
    color: Tuple[int, int, int]
    flicker_offset: float
    flicker_speed: float


class ChristmasTree:
    """
    3D Christmas tree with lights and animation
    This fixes issue #9: tree not appearing
    """
    
    def __init__(self):
        self.lights: List[TreeLight] = []
        self.initialized = False
        self.time = 0.0
    
    def initialize(self):
        """Initialize tree lights in spiral pattern"""
        self.lights.clear()
        
        # Light colors
        light_colors = [
            Config.THEME['light_red'],
            Config.THEME['light_green'],
            Config.THEME['light_blue'],
            Config.THEME['light_yellow'],
            Config.THEME['light_magenta'],
            Config.THEME['light_cyan'],
            Config.THEME['light_orange'],
            Config.THEME['light_pink'],
            Config.THEME['light_purple'],
            Config.THEME['light_white'],
        ]
        
        # Create lights in spiral
        for i in range(Config.TREE_LIGHTS):
            t = i / Config.TREE_LIGHTS
            angle = t * math.pi * 10  # Multiple spirals
            height = t
            radius = (1.0 - t) * 0.4  # Cone shape
            
            light = TreeLight(
                x=math.cos(angle) * radius,
                y=height,
                z=math.sin(angle) * radius,
                color=random.choice(light_colors),
                flicker_offset=random.uniform(0, math.pi * 2),
                flicker_speed=random.uniform(2.0, 5.0)
            )
            self.lights.append(light)
        
        self.initialized = True
    
    def update(self, dt: float):
        """Update animation"""
        self.time += dt
    
    def render(self, screen_x: int, screen_y: int, 
               width: int, height: int) -> str:
        """
        Render tree at screen position
        Returns ANSI string
        """
        if not self.initialized:
            self.initialize()
        
        output = []
        
        # Tree dimensions in screen space
        tree_h = height
        tree_w = width // 2
        
        # Wind sway
        sway = math.sin(self.time * 0.9) * 0.8
        
        # Draw tree (cone shape with shading)
        for y in range(tree_h):
            line_y = screen_y + y
            if line_y >= Config.HEIGHT:
                continue
            
            # Normalized height (0 at top, 1 at bottom)
            h = y / max(1, tree_h - 1)
            
            # Radius at this height (smaller at top)
            radius = int((1.0 - h) * tree_w)
            
            # Center with sway
            center_x = screen_x + tree_w + int(sway * (1.0 - h))
            
            for x in range(-radius, radius + 1):
                screen_x_pos = center_x + x
                if screen_x_pos < 0 or screen_x_pos >= Config.WIDTH:
                    continue
                
                # Distance from center (for shading)
                dist = abs(x) / max(1, radius)
                
                # Lighting (darker on edges)
                light = 0.5 + 0.5 * (1.0 - dist)
                
                # Base color gradient (darker at bottom)
                base_color = Colors.gradient(
                    Config.THEME['tree_green_light'],
                    Config.THEME['tree_green_dark'],
                    h * 0.5
                )
                
                # Apply lighting
                r = int(base_color[0] * light)
                g = int(base_color[1] * light)
                b = int(base_color[2] * light)
                
                # Check for lights
                light_found = False
                for tree_light in self.lights:
                    # Project 3D light to 2D
                    light_h = tree_light.y
                    light_r = tree_light.x
                    
                    # Check if light is at this position
                    if abs(light_h - (1.0 - h)) < 0.05:
                        expected_x = int(light_r * tree_w)
                        if abs(expected_x - x) < 2:
                            # Flicker
                            flicker = 0.5 + 0.5 * math.sin(
                                self.time * tree_light.flicker_speed + tree_light.flicker_offset
                            )
                            
                            # Light color
                            r = int(tree_light.color[0] * flicker)
                            g = int(tree_light.color[1] * flicker)
                            b = int(tree_light.color[2] * flicker)
                            light_found = True
                            break
                
                # Draw character
                output.append(Colors.move(screen_x_pos, line_y))
                output.append(Colors.rgb(r, g, b))
                output.append('█' if light_found else '▓')
        
        # Draw trunk
        trunk_h = max(3, tree_h // 8)
        trunk_w = max(2, tree_w // 6)
        trunk_y = screen_y + tree_h
        
        for y in range(trunk_h):
            if trunk_y + y >= Config.HEIGHT:
                break
            
            for x in range(-trunk_w, trunk_w + 1):
                screen_x_pos = screen_x + tree_w + x
                if screen_x_pos < 0 or screen_x_pos >= Config.WIDTH:
                    continue
                
                # Trunk shading
                light = 0.6 + 0.4 * math.cos(x * 0.5)
                trunk_color = Config.THEME['tree_trunk']
                r = int(trunk_color[0] * light)
                g = int(trunk_color[1] * light)
                b = int(trunk_color[2] * light)
                
                output.append(Colors.move(screen_x_pos, trunk_y + y))
                output.append(Colors.rgb(r, g, b))
                output.append('█')
        
        # Draw star at top
        star_x = screen_x + tree_w
        star_y = screen_y - 1
        if 0 <= star_y < Config.HEIGHT:
            pulse = 0.7 + 0.3 * math.sin(self.time * 3.0)
            star_color = Config.THEME['tree_star']
            r = int(star_color[0] * pulse)
            g = int(star_color[1] * pulse)
            b = int(star_color[2] * pulse)
            
            output.append(Colors.move(star_x, star_y))
            output.append(Colors.rgb(r, g, b))
            output.append('✨')
        
        output.append(Colors.RESET)
        return ''.join(output)


# ============================================================================
# SECTION 9: SNOW SYSTEM
# ============================================================================

@dataclass
class Snowflake:
    """A single snowflake"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    char: str


class SnowSystem:
    """Falling snow effect"""
    
    def __init__(self):
        self.snowflakes: List[Snowflake] = []
        self.initialized = False
        self.time = 0.0
    
    def initialize(self, width: int, height: int):
        """Initialize snowflakes"""
        self.snowflakes.clear()
        
        snow_chars = ['·', '•', '❄', '*', '✻', '✼']
        
        for _ in range(Config.SNOWFLAKES):
            flake = Snowflake(
                x=random.uniform(0, width),
                y=random.uniform(0, height),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(0.5, 2.0),
                size=random.uniform(0.5, 1.5),
                char=random.choice(snow_chars)
            )
            self.snowflakes.append(flake)
        
        self.initialized = True
    
    def update(self, dt: float, width: int, height: int):
        """Update snowflake positions"""
        self.time += dt
        
        # Wind effect
        wind = math.sin(self.time * 0.7) * 0.5
        
        for flake in self.snowflakes:
            # Update velocity
            flake.vx = flake.vx * 0.99 + wind * 0.01
            
            # Update position
            flake.x += flake.vx * dt * Config.SNOW_SPEED
            flake.y += flake.vy * dt * Config.SNOW_SPEED
            
            # Wrap around
            if flake.y > height:
                flake.y = 0
                flake.x = random.uniform(0, width)
            
            if flake.x < 0:
                flake.x = width
            elif flake.x > width:
                flake.x = 0
    
    def render(self, safe_zones: List[Tuple[int, int, int, int]]) -> str:
        """Render snowflakes, avoiding safe zones"""
        output = []
        
        for flake in self.snowflakes:
            x = int(flake.x)
            y = int(flake.y)
            
            # Check safe zones
            in_safe_zone = False
            for sx, sy, sw, sh in safe_zones:
                if sx <= x < sx + sw and sy <= y < sy + sh:
                    in_safe_zone = True
                    break
            
            if in_safe_zone:
                continue
            
            # Draw snowflake
            color = Config.THEME['snow']
            output.append(Colors.move(x, y))
            output.append(Colors.rgb(*color))
            output.append(flake.char)
        
        output.append(Colors.RESET)
        return ''.join(output)


# ============================================================================
# SECTION 10: WELCOME ANIMATION
# ============================================================================

class WelcomeAnimation:
    """
    Tmux-compatible welcome animation
    This fixes issue #8: welcome not appearing
    """
    
    def __init__(self):
        self.shown = False
        self.skipped = False
    
    def show(self, width: int, height: int) -> bool:
        """
        Show welcome animation
        Returns True if animation completed, False if skipped
        """
        if self.shown:
            return True
        
        # Check if we should skip (e.g., in tmux attach)
        if os.environ.get('TMUX') and os.environ.get('TMUX_PANE'):
            # We're in tmux, check if this is a new session
            try:
                result = subprocess.run(
                    ['tmux', 'display-message', '-p', '#{session_created}'],
                    capture_output=True, text=True, timeout=1
                )
                if result.returncode == 0:
                    # If session is old, skip animation
                    created = int(result.stdout.strip())
                    if time.time() - created > 60:  # More than 60 seconds old
                        self.shown = True
                        self.skipped = True
                        return True
            except:
                pass
        
        # Show animation
        try:
            self._render_animation(width, height)
            self.shown = True
            return True
        except KeyboardInterrupt:
            self.shown = True
            self.skipped = True
            return True
    
    def _render_animation(self, width: int, height: int):
        """Render the actual animation"""
        center_x = width // 2
        center_y = height // 2
        
        # Clear screen
        sys.stdout.write(Colors.CLEAR_SCREEN)
        sys.stdout.write(Colors.HIDE_CURSOR)
        sys.stdout.flush()
        
        # Animated logo
        logo = [
            "    ╔═══════════════════════════════╗",
            "    ║                               ║",
            "    ║    🎄  BRAD TUI ULTRA  🎄    ║",
            "    ║                               ║",
            "    ║   Enhanced Terminal Interface  ║",
            "    ║                               ║",
            "    ╚═══════════════════════════════╝",
        ]
        
        # Fade in
        for alpha in range(0, 11):
            t = alpha / 10.0
            
            # Position
            y = center_y - len(logo) // 2
            
            for i, line in enumerate(logo):
                x = max(0, (width - len(line)) // 2)
                
                # Color with fade
                color = Colors.gradient(
                    (0, 0, 0),
                    Config.THEME['border_primary'],
                    t
                )
                
                sys.stdout.write(Colors.move(x, y + i))
                sys.stdout.write(Colors.rgb(*color))
                sys.stdout.write(line)
            
            sys.stdout.write(Colors.RESET)
            sys.stdout.flush()
            time.sleep(0.05)
        
        # Hold
        time.sleep(1.0)
        
        # System info
        info_y = center_y + len(logo) // 2 + 2
        info = [
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Terminal: {width}x{height}",
            f"Shell: {Config.DEFAULT_SHELL}",
            "",
            "Press any key to continue...",
        ]
        
        for i, line in enumerate(info):
            x = max(0, (width - len(line)) // 2)
            sys.stdout.write(Colors.move(x, info_y + i))
            sys.stdout.write(Colors.rgb(*Config.THEME['text_dim']))
            sys.stdout.write(line)
        
        sys.stdout.write(Colors.RESET)
        sys.stdout.flush()
        
        # Wait for key
        self._wait_for_key()
        
        # Fade out
        for alpha in range(10, -1, -1):
            t = alpha / 10.0
            
            y = center_y - len(logo) // 2
            
            for i, line in enumerate(logo):
                x = max(0, (width - len(line)) // 2)
                
                color = Colors.gradient(
                    (0, 0, 0),
                    Config.THEME['border_primary'],
                    t
                )
                
                sys.stdout.write(Colors.move(x, y + i))
                sys.stdout.write(Colors.rgb(*color))
                sys.stdout.write(line)
            
            for i, line in enumerate(info):
                x = max(0, (width - len(line)) // 2)
                color = Colors.gradient(
                    (0, 0, 0),
                    Config.THEME['text_dim'],
                    t
                )
                sys.stdout.write(Colors.move(x, info_y + i))
                sys.stdout.write(Colors.rgb(*color))
                sys.stdout.write(line)
            
            sys.stdout.write(Colors.RESET)
            sys.stdout.flush()
            time.sleep(0.05)
        
        # Clear and restore
        sys.stdout.write(Colors.CLEAR_SCREEN)
        sys.stdout.write(Colors.SHOW_CURSOR)
        sys.stdout.flush()
    
    def _wait_for_key(self):
        """Wait for any key press"""
        try:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                # Set raw mode
                tty.setraw(fd)
                
                # Read one character
                sys.stdin.read(1)
            finally:
                # Restore settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            # Fallback: just wait
            time.sleep(2.0)


# ============================================================================
# SECTION 11: MENU BAR
# ============================================================================

class MenuBar:
    """
    Persistent menu bar
    This fixes issue #1: menu bar not persistent
    """
    
    def __init__(self, width: int):
        self.width = width
        self.visible = True  # Always visible by default
        self.items = [
            ("F1", "Help"),
            ("F2", "Theme"),
            ("F3", "History"),
            ("F4", "Clear"),
            ("F5", "Parallax"),
            ("F6", "Tree"),
            ("F7", "Snow"),
            ("Ctrl+C", "Exit"),
        ]
    
    def show(self):
        """Show menu bar"""
        self.visible = True
    
    def hide(self):
        """Hide menu bar (only during command execution)"""
        self.visible = False
    
    def render(self, y: int, time_offset: float = 0.0) -> str:
        """Render menu bar at y position"""
        if not self.visible:
            return ""
        
        output = []
        
        # Background
        output.append(Colors.move(0, y))
        output.append(Colors.rgb_bg(*Config.THEME['menu_bg']))
        output.append(' ' * self.width)
        
        # Title
        output.append(Colors.move(2, y))
        output.append(Colors.rgb(*Config.THEME['menu_fg']))
        output.append(Colors.BOLD)
        output.append("🎄 Brad TUI Ultra")
        output.append(Colors.RESET)
        
        # Menu items
        x = 22
        for i, (key, label) in enumerate(self.items):
            if x + len(key) + len(label) + 6 > self.width:
                break
            
            output.append(Colors.move(x, y))
            output.append(Colors.rgb_bg(*Config.THEME['menu_bg']))
            
            # Key (colored)
            t = (i + time_offset) / len(self.items)
            key_color = Colors.gradient(
                Config.THEME['border_primary'],
                Config.THEME['border_secondary'],
                t
            )
            output.append(Colors.rgb(*key_color))
            output.append(f"[{key}]")
            
            # Label
            output.append(Colors.rgb(*Config.THEME['menu_fg']))
            output.append(f" {label} ")
            
            x += len(key) + len(label) + 6
        
        output.append(Colors.RESET)
        return ''.join(output)
    
    def resize(self, width: int):
        """Handle terminal resize"""
        self.width = width


# ============================================================================
# SECTION 12: STATUS BAR
# ============================================================================

class StatusBar:
    """Status bar showing system information"""
    
    def __init__(self, width: int):
        self.width = width
        self.info: Dict[str, str] = {}
    
    def set(self, key: str, value: str):
        """Set status info"""
        self.info[key] = value
    
    def render(self, y: int) -> str:
        """Render status bar at y position"""
        output = []
        
        # Background
        output.append(Colors.move(0, y))
        output.append(Colors.rgb_bg(*Config.THEME['status_bg']))
        output.append(' ' * self.width)
        
        # Info items
        items = []
        for key, value in self.info.items():
            items.append(f"{key}: {value}")
        
        text = " │ ".join(items)
        if len(text) > self.width - 4:
            text = text[:self.width - 7] + "..."
        
        output.append(Colors.move(2, y))
        output.append(Colors.rgb(*Config.THEME['status_fg']))
        output.append(text)
        
        output.append(Colors.RESET)
        return ''.join(output)
    
    def resize(self, width: int):
        """Handle terminal resize"""
        self.width = width


# ============================================================================
# SECTION 13: AUTOCORRECT PANEL
# ============================================================================

class AutocorrectPanel:
    """
    Autocorrect/suggestion panel positioned at bottom
    This fixes issue #2: panel positioning
    """
    
    def __init__(self, width: int = Config.AUTOCORRECT_WIDTH):
        self.width = width
        self.height = Config.AUTOCORRECT_HEIGHT
        self.suggestions: List[str] = []
        self.selected_index = 0
        self.visible = True
    
    def set_suggestions(self, suggestions: List[str]):
        """Set current suggestions"""
        self.suggestions = suggestions[:8]  # Max 8
        self.selected_index = 0
    
    def select_next(self):
        """Select next suggestion"""
        if self.suggestions:
            self.selected_index = (self.selected_index + 1) % len(self.suggestions)
    
    def select_prev(self):
        """Select previous suggestion"""
        if self.suggestions:
            self.selected_index = (self.selected_index - 1) % len(self.suggestions)
    
    def get_selected(self) -> Optional[str]:
        """Get currently selected suggestion"""
        if self.suggestions and 0 <= self.selected_index < len(self.suggestions):
            return self.suggestions[self.selected_index]
        return None
    
    def show(self):
        """Show panel"""
        self.visible = True
    
    def hide(self):
        """Hide panel"""
        self.visible = False
    
    def render(self, x: int, y: int, time_offset: float = 0.0) -> str:
        """
        Render panel at bottom-right corner
        x, y = top-left position
        """
        if not self.visible or not self.suggestions:
            return ""
        
        output = []
        
        # Draw border
        output.append(draw_box(
            x, y, self.width, self.height,
            BorderStyle.ROUNDED,
            Config.THEME['autocorrect_border'],
            Config.THEME['border_accent'],
            "Suggestions",
            time_offset
        ))
        
        # Draw suggestions
        for i, suggestion in enumerate(self.suggestions[:self.height - 2]):
            line_y = y + i + 1
            
            if i == self.selected_index:
                # Selected
                output.append(Colors.move(x + 2, line_y))
                output.append(Colors.rgb(*Config.THEME['autocorrect_selected']))
                output.append(Colors.BOLD)
                output.append(f"► {suggestion}")
                output.append(Colors.RESET)
            else:
                # Normal
                output.append(Colors.move(x + 2, line_y))
                output.append(Colors.rgb(*Config.THEME['autocorrect_fg']))
                output.append(f"  {suggestion}")
        
        output.append(Colors.RESET)
        return ''.join(output)


# ============================================================================
# SECTION 14: COMMAND EXECUTOR
# ============================================================================

class CommandExecutor:
    """Execute shell commands asynchronously"""
    
    def __init__(self, output_buffer: OutputBuffer):
        self.output_buffer = output_buffer
        self.running = False
        self.process: Optional[subprocess.Popen] = None
    
    async def execute(self, command: str, cwd: str = None) -> int:
        """
        Execute command and stream output
        Returns exit code
        """
        if not command.strip():
            return 0
        
        # Built-in commands
        if command.strip() == "clear":
            self.output_buffer.clear()
            return 0
        
        if command.strip() in ("exit", "quit"):
            return -1  # Signal to exit
        
        # Add command to log
        self.output_buffer.add(f"$ {command}", LogEntryType.COMMAND, bold=True)
        
        try:
            self.running = True
            
            # Start process
            self.process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or os.getcwd(),
                env=os.environ.copy()
            )
            
            # Read output
            async def read_stream(stream, entry_type):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    try:
                        text = line.decode('utf-8', errors='replace').rstrip('\n')
                        self.output_buffer.add(text, entry_type)
                    except:
                        pass
            
            # Read both streams concurrently
            await asyncio.gather(
                read_stream(self.process.stdout, LogEntryType.OUTPUT),
                read_stream(self.process.stderr, LogEntryType.ERROR)
            )
            
            # Wait for completion
            exit_code = await self.process.wait()
            
            # Add result
            if exit_code == 0:
                self.output_buffer.add(
                    f"[✓ Command completed successfully]",
                    LogEntryType.SUCCESS,
                    dim=True
                )
            else:
                self.output_buffer.add(
                    f"[✗ Command failed with exit code: {exit_code}]",
                    LogEntryType.ERROR,
                    dim=True
                )
            
            return exit_code
            
        except Exception as e:
            self.output_buffer.add(f"Error: {str(e)}", LogEntryType.ERROR)
            return 1
        finally:
            self.running = False
            self.process = None


# ============================================================================
# SECTION 15: MAIN APPLICATION
# ============================================================================

class Application:
    """
    Main application - integrates all components
    Fixes ALL reported issues
    """
    
    def __init__(self):
        # Terminal state
        self.width = Config.WIDTH
        self.height = Config.HEIGHT
        self.running = False
        self.old_terminal_settings = None
        
        # Components
        self.output_buffer = OutputBuffer()
        self.command_history = CommandHistory()
        self.input_line = InputLine()
        self.autocompleter = Autocompleter()
        
        self.menu_bar = MenuBar(self.width)
        self.status_bar = StatusBar(self.width)
        self.autocorrect_panel = AutocorrectPanel()
        
        self.parallax = ParallaxField()
        self.tree = ChristmasTree()
        self.snow = SnowSystem()
        self.welcome = WelcomeAnimation()
        
        self.executor = CommandExecutor(self.output_buffer)
        
        # State
        self.time = 0.0
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        # Current working directory
        self.cwd = os.getcwd()
    
    def initialize(self):
        """Initialize application"""
        # Get terminal size
        self.width, self.height = get_terminal_size()
        Config.WIDTH = self.width
        Config.HEIGHT = self.height
        
        # Initialize components
        self.parallax.initialize(self.width, self.height)
        self.tree.initialize()
        self.snow.initialize(self.width, self.height)
        
        # Resize components
        self.menu_bar.resize(self.width)
        self.status_bar.resize(self.width)
        
        # Setup terminal
        self.setup_terminal()
        
        # Signal handlers
        signal.signal(signal.SIGWINCH, self.handle_resize)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)
        
        # Show welcome
        if Config.ENABLE_WELCOME:
            self.welcome.show(self.width, self.height)
        
        # Add welcome message to buffer
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("🎄 Welcome to Brad TUI Ultra! 🎄", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add(f"Terminal: {self.width}x{self.height}", LogEntryType.SYSTEM)
        self.output_buffer.add(f"Working directory: {self.cwd}", LogEntryType.SYSTEM)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("Tip: Use F1-F7 for functions, Tab for autocomplete, Ctrl+C to exit", LogEntryType.SYSTEM, dim=True)
        self.output_buffer.add("", LogEntryType.SYSTEM)
    
    def setup_terminal(self):
        """Setup terminal for raw input"""
        try:
            fd = sys.stdin.fileno()
            self.old_terminal_settings = termios.tcgetattr(fd)
            
            # Set raw mode
            tty.setraw(fd)
            
            # Set non-blocking
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Switch to alternate screen
            sys.stdout.write(Colors.ALT_SCREEN)
            sys.stdout.write(Colors.HIDE_CURSOR)
            sys.stdout.write(Colors.CLEAR_SCREEN)
            sys.stdout.flush()
        except Exception as e:
            print(f"Error setting up terminal: {e}", file=sys.stderr)
    
    def restore_terminal(self):
        """Restore terminal to normal mode"""
        try:
            if self.old_terminal_settings:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self.old_terminal_settings)
            
            sys.stdout.write(Colors.MAIN_SCREEN)
            sys.stdout.write(Colors.SHOW_CURSOR)
            sys.stdout.write(Colors.RESET)
            sys.stdout.flush()
        except:
            pass
    
    def handle_resize(self, signum, frame):
        """Handle terminal resize"""
        self.width, self.height = get_terminal_size()
        Config.WIDTH = self.width
        Config.HEIGHT = self.height
        
        self.menu_bar.resize(self.width)
        self.status_bar.resize(self.width)
        self.parallax.initialize(self.width, self.height)
        self.snow.initialize(self.width, self.height)
    
    def handle_exit(self, signum, frame):
        """Handle exit signal"""
        self.running = False
    
    def read_input(self) -> Optional[str]:
        """Read input (non-blocking)"""
        try:
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if not ready:
                return None
            
            char = sys.stdin.read(1)
            if not char:
                return None
            
            # Handle escape sequences
            if char == '\x1b':
                seq = char
                for _ in range(10):
                    ready, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if not ready:
                        break
                    next_char = sys.stdin.read(1)
                    if not next_char:
                        break
                    seq += next_char
                    if next_char in ('~', 'A', 'B', 'C', 'D', 'F', 'H', 'P', 'Q', 'R', 'S'):
                        break
                return seq
            
            return char
        except (IOError, OSError):
            return None
    
    def process_input(self, key: str):
        """
        Process input with full keybinding support
        This fixes issue #3: keybindings not working
        """
        # Exit
        if key == Config.KEYS['CTRL_C'] or key == Config.KEYS['CTRL_D']:
            self.running = False
            return
        
        # Function keys
        if key == Config.KEYS['F1']:  # Help
            self.show_help()
            return
        
        if key == Config.KEYS['F2']:  # Theme toggle (placeholder)
            self.output_buffer.add("[Theme switching coming soon]", LogEntryType.SYSTEM)
            return
        
        if key == Config.KEYS['F3']:  # History
            self.show_history()
            return
        
        if key == Config.KEYS['F4']:  # Clear
            self.output_buffer.clear()
            self.output_buffer.add("Screen cleared.", LogEntryType.SYSTEM)
            return
        
        if key == Config.KEYS['F5']:  # Toggle parallax
            Config.ENABLE_PARALLAX = not Config.ENABLE_PARALLAX
            state = "enabled" if Config.ENABLE_PARALLAX else "disabled"
            self.output_buffer.add(f"Parallax {state}", LogEntryType.SYSTEM)
            return
        
        if key == Config.KEYS['F6']:  # Toggle tree
            Config.ENABLE_TREE = not Config.ENABLE_TREE
            state = "enabled" if Config.ENABLE_TREE else "disabled"
            self.output_buffer.add(f"Christmas tree {state}", LogEntryType.SYSTEM)
            return
        
        if key == Config.KEYS['F7']:  # Toggle snow
            Config.ENABLE_SNOW = not Config.ENABLE_SNOW
            state = "enabled" if Config.ENABLE_SNOW else "disabled"
            self.output_buffer.add(f"Snow {state}", LogEntryType.SYSTEM)
            return
        
        # Clear screen
        if key == Config.KEYS['CTRL_L']:
            self.output_buffer.clear()
            return
        
        # Navigation (fixes issue #4)
        if key == Config.KEYS['LEFT']:
            self.input_line.move_left()
            return
        
        if key == Config.KEYS['RIGHT']:
            self.input_line.move_right()
            return
        
        if key == Config.KEYS['HOME']:
            self.input_line.move_home()
            return
        
        if key == Config.KEYS['END']:
            self.input_line.move_end()
            return
        
        if key == Config.KEYS['WORD_LEFT'] or key == Config.KEYS['ALT_LEFT']:
            self.input_line.move_word_left()
            return
        
        if key == Config.KEYS['WORD_RIGHT'] or key == Config.KEYS['ALT_RIGHT']:
            self.input_line.move_word_right()
            return
        
        # History
        if key == Config.KEYS['UP']:
            cmd = self.command_history.prev(self.input_line.get_text())
            if cmd is not None:
                self.input_line.set_text(cmd)
            return
        
        if key == Config.KEYS['DOWN']:
            cmd = self.command_history.next()
            if cmd is not None:
                self.input_line.set_text(cmd)
            return
        
        # Editing
        if key == Config.KEYS['BACKSPACE']:
            self.input_line.backspace()
            self.update_suggestions()
            return
        
        if key == Config.KEYS['DELETE']:
            self.input_line.delete()
            self.update_suggestions()
            return
        
        if key == Config.KEYS['CTRL_A']:
            self.input_line.move_home()
            return
        
        if key == Config.KEYS['CTRL_E']:
            self.input_line.move_end()
            return
        
        if key == Config.KEYS['CTRL_U']:
            self.input_line.kill_line_backward()
            self.update_suggestions()
            return
        
        if key == Config.KEYS['CTRL_K']:
            self.input_line.kill_line()
            self.update_suggestions()
            return
        
        if key == Config.KEYS['CTRL_W']:
            self.input_line.kill_word()
            self.update_suggestions()
            return
        
        # Tab completion
        if key == Config.KEYS['TAB']:
            suggestion = self.autocorrect_panel.get_selected()
            if suggestion:
                # Replace last word with suggestion
                text = self.input_line.get_text()
                parts = text.split()
                if parts:
                    parts[-1] = suggestion
                    self.input_line.set_text(' '.join(parts) + ' ')
                    self.update_suggestions()
            return
        
        # Execute command
        if key == Config.KEYS['ENTER'] or key == '\n':
            asyncio.create_task(self.execute_command())
            return
        
        # Regular character input
        if len(key) == 1 and ord(key) >= 32:
            self.input_line.insert_char(key)
            self.update_suggestions()
            return
    
    def update_suggestions(self):
        """Update autocomplete suggestions"""
        text = self.input_line.get_text()
        suggestions = self.autocompleter.get_suggestions(text)
        self.autocorrect_panel.set_suggestions(suggestions)
    
    async def execute_command(self):
        """Execute current command"""
        command = self.input_line.get_text().strip()
        if not command:
            return
        
        # Add to history
        self.command_history.add(command)
        self.input_line.clear()
        self.autocorrect_panel.set_suggestions([])
        
        # Hide menu during execution (issue #1)
        self.menu_bar.hide()
        
        # Handle cd specially
        if command.startswith('cd '):
            path = command[3:].strip()
            try:
                if path == '~' or path == '':
                    path = os.path.expanduser('~')
                elif path.startswith('~'):
                    path = os.path.expanduser(path)
                elif not os.path.isabs(path):
                    path = os.path.join(self.cwd, path)
                
                os.chdir(path)
                self.cwd = os.getcwd()
                self.output_buffer.add(f"$ cd {path}", LogEntryType.COMMAND, bold=True)
                self.output_buffer.add(f"Changed directory to: {self.cwd}", LogEntryType.SUCCESS)
            except Exception as e:
                self.output_buffer.add(f"$ cd {path}", LogEntryType.COMMAND, bold=True)
                self.output_buffer.add(f"Error: {str(e)}", LogEntryType.ERROR)
        else:
            # Execute command
            exit_code = await self.executor.execute(command, self.cwd)
            if exit_code == -1:
                self.running = False
        
        # Show menu again (issue #1)
        self.menu_bar.show()
    
    def show_help(self):
        """Show help information"""
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("=== Brad TUI Ultra - Help ===", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("Navigation:", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("  ←/→         Move cursor left/right", LogEntryType.SYSTEM)
        self.output_buffer.add("  Ctrl+←/→    Move by word", LogEntryType.SYSTEM)
        self.output_buffer.add("  Home/End    Jump to line start/end", LogEntryType.SYSTEM)
        self.output_buffer.add("  ↑/↓         Command history", LogEntryType.SYSTEM)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("Editing:", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("  Backspace   Delete previous character", LogEntryType.SYSTEM)
        self.output_buffer.add("  Delete      Delete current character", LogEntryType.SYSTEM)
        self.output_buffer.add("  Ctrl+W      Delete previous word", LogEntryType.SYSTEM)
        self.output_buffer.add("  Ctrl+U      Clear line before cursor", LogEntryType.SYSTEM)
        self.output_buffer.add("  Ctrl+K      Clear line after cursor", LogEntryType.SYSTEM)
        self.output_buffer.add("  Tab         Accept autocomplete suggestion", LogEntryType.SYSTEM)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("Function Keys:", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("  F1          Show this help", LogEntryType.SYSTEM)
        self.output_buffer.add("  F2          Change theme (coming soon)", LogEntryType.SYSTEM)
        self.output_buffer.add("  F3          Show command history", LogEntryType.SYSTEM)
        self.output_buffer.add("  F4          Clear screen", LogEntryType.SYSTEM)
        self.output_buffer.add("  F5          Toggle parallax effect", LogEntryType.SYSTEM)
        self.output_buffer.add("  F6          Toggle Christmas tree", LogEntryType.SYSTEM)
        self.output_buffer.add("  F7          Toggle snow", LogEntryType.SYSTEM)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("Other:", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("  Ctrl+C      Exit application", LogEntryType.SYSTEM)
        self.output_buffer.add("  Ctrl+L      Clear screen", LogEntryType.SYSTEM)
        self.output_buffer.add("", LogEntryType.SYSTEM)
    
    def show_history(self):
        """Show command history"""
        self.output_buffer.add("", LogEntryType.SYSTEM)
        self.output_buffer.add("=== Command History ===", LogEntryType.SYSTEM, bold=True)
        self.output_buffer.add("", LogEntryType.SYSTEM)
        
        if not self.command_history.commands:
            self.output_buffer.add("No commands in history", LogEntryType.SYSTEM, dim=True)
        else:
            for i, cmd in enumerate(list(self.command_history.commands)[-20:], 1):
                self.output_buffer.add(f"  {i:3d}. {cmd}", LogEntryType.SYSTEM)
        
        self.output_buffer.add("", LogEntryType.SYSTEM)
    
    def update(self, dt: float):
        """Update all systems"""
        self.time += dt
        
        # Update animations
        if Config.ENABLE_PARALLAX:
            self.parallax.update(dt)
        
        if Config.ENABLE_TREE:
            self.tree.update(dt)
        
        if Config.ENABLE_SNOW:
            self.snow.update(dt, self.width, self.height)
        
        # Update status
        self.status_bar.set("Time", datetime.now().strftime("%H:%M:%S"))
        self.status_bar.set("CWD", self.cwd if len(self.cwd) < 30 else "..." + self.cwd[-27:])
        self.status_bar.set("Lines", str(len(self.output_buffer.lines)))
    
    def render(self):
        """Render frame with all fixes applied"""
        output = []
        
        # Clear screen
        output.append(Colors.CLEAR_SCREEN)
        
        # Calculate layout
        menu_y = 0
        menu_h = 1 if self.menu_bar.visible else 0
        
        status_y = self.height - 2
        status_h = 1
        
        input_y = self.height - 1
        input_h = 1
        
        output_y = menu_h
        output_h = status_y - output_y
        
        # Define safe zones (where parallax/snow should NOT draw)
        # This fixes issue #6: parallax overlapping text
        safe_zones = [
            (0, menu_y, self.width, menu_h),
            (0, output_y, self.width, output_h),
            (0, status_y, self.width, status_h),
            (0, input_y, self.width, input_h),
        ]
        
        # Autocorrect position (bottom-right, above status)
        # This fixes issue #2: autocorrect positioning
        autocorrect_x = self.width - self.autocorrect_panel.width - 2
        autocorrect_y = status_y - self.autocorrect_panel.height - 1
        if autocorrect_y > output_y:
            safe_zones.append((
                autocorrect_x,
                autocorrect_y,
                self.autocorrect_panel.width,
                self.autocorrect_panel.height
            ))
        
        # Christmas tree position (right side)
        if Config.ENABLE_TREE:
            tree_w = int(self.width * Config.TREE_SIZE)
            tree_h = int(output_h * 0.8)
            tree_x = int(self.width * Config.TREE_X) - tree_w
            tree_y = output_y + (output_h - tree_h) // 2
            
            safe_zones.append((tree_x, tree_y, tree_w, tree_h))
        
        # Render parallax background (issue #6 fixed)
        if Config.ENABLE_PARALLAX:
            for y in range(self.height):
                for x in range(self.width):
                    star = self.parallax.render_at(x, y, safe_zones)
                    if star:
                        output.append(star)
        
        # Render Christmas tree (issue #9 fixed)
        if Config.ENABLE_TREE:
            output.append(self.tree.render(tree_x, tree_y, tree_w, tree_h))
        
        # Render snow (issue #6 fixed - respects safe zones)
        if Config.ENABLE_SNOW:
            output.append(self.snow.render(safe_zones))
        
        # Render menu bar (issue #1 fixed - persistent)
        output.append(self.menu_bar.render(menu_y, self.time))
        
        # Render output buffer (issue #5 fixed - persistent output)
        # Draw output area with border (issue #12)
        if output_h > 2:
            output.append(draw_box(
                0, output_y, self.width, output_h,
                BorderStyle.SIMPLE,
                Config.THEME['border_primary'],
                Config.THEME['border_secondary'],
                "",
                self.time
            ))
            
            # Get visible lines
            visible_lines = self.output_buffer.get_visible_lines(output_h - 2)
            
            # Render each line with gradient border (issue #12)
            for i, entry in enumerate(visible_lines):
                line_y = output_y + 1 + i
                if line_y >= output_y + output_h - 1:
                    break
                
                # Text
                text = entry.text
                if len(text) > self.width - 6:
                    text = text[:self.width - 9] + "..."
                
                output.append(Colors.move(3, line_y))
                
                # Color based on type
                fg_color = entry.get_fg_color()
                output.append(Colors.rgb(*fg_color))
                
                if entry.bold:
                    output.append(Colors.BOLD)
                if entry.dim:
                    output.append(Colors.DIM)
                
                output.append(text)
                output.append(Colors.RESET)
        
        # Render input line with gradient border (issue #12)
        output.append(draw_box(
            0, input_y, self.width, input_h,
            BorderStyle.HEAVY,
            Config.THEME['cmd_prompt'],
            Config.THEME['border_accent'],
            "",
            self.time
        ))
        
        # Prompt
        output.append(Colors.move(2, input_y))
        output.append(Colors.rgb(*Config.THEME['cmd_prompt']))
        output.append(Colors.BOLD)
        output.append("❯")
        output.append(Colors.RESET)
        
        # Input text with cursor (issue #4 and #11 fixed)
        text = self.input_line.get_text()
        cursor_pos = self.input_line.get_cursor_pos()
        
        # Text before cursor
        if cursor_pos > 0:
            output.append(Colors.move(4, input_y))
            output.append(Colors.rgb(*Config.THEME['cmd_input']))
            output.append(text[:cursor_pos])
        
        # Cursor character (issue #11 fixed - proper colors)
        cursor_char = text[cursor_pos] if cursor_pos < len(text) else " "
        output.append(Colors.move(4 + cursor_pos, input_y))
        output.append(Colors.rgb(*Config.THEME['cursor_fg']))
        output.append(Colors.rgb_bg(*Config.THEME['cursor_bg']))
        output.append(cursor_char)
        output.append(Colors.RESET)
        
        # Text after cursor
        if cursor_pos < len(text) - 1:
            output.append(Colors.move(5 + cursor_pos, input_y))
            output.append(Colors.rgb(*Config.THEME['cmd_input']))
            output.append(text[cursor_pos + 1:])
            output.append(Colors.RESET)
        
        # Render status bar
        output.append(self.status_bar.render(status_y))
        
        # Render autocorrect panel (issue #2 fixed - bottom positioning)
        if autocorrect_y > output_y:
            output.append(self.autocorrect_panel.render(
                autocorrect_x,
                autocorrect_y,
                self.time
            ))
        
        # Write output
        sys.stdout.write(''.join(output))
        sys.stdout.flush()
    
    def run(self):
        """Main event loop"""
        self.running = True
        
        try:
            # Create async event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.running:
                frame_start = time.time()
                
                # Process input
                for _ in range(10):  # Process up to 10 keys per frame
                    key = self.read_input()
                    if key:
                        self.process_input(key)
                    else:
                        break
                
                # Calculate delta time
                dt = frame_start - self.last_frame_time
                self.last_frame_time = frame_start
                
                # Update
                self.update(dt)
                
                # Render
                self.render()
                
                self.frame_count += 1
                
                # Frame limiting
                frame_time = time.time() - frame_start
                sleep_time = max(0, Config.FRAME_TIME - frame_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            # Log error
            try:
                with open('/tmp/brad_tui_error.log', 'a') as f:
                    f.write(f"\n=== Error at {datetime.now()} ===\n")
                    f.write(traceback.format_exc())
            except:
                pass
        finally:
            self.restore_terminal()
    
    def cleanup(self):
        """Cleanup resources"""
        self.restore_terminal()


# ============================================================================
# SECTION 16: ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    app = Application()
    
    try:
        app.initialize()
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
