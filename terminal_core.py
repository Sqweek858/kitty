#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CYBERPUNK TERMINAL - CORE ENGINE                          ║
║                         Advanced Terminal System                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Core terminal engine providing foundational functionality for the terminal UI.
This module handles the main event loop, rendering pipeline, and system integration.

Architecture:
    - Event loop management with precise timing
    - Screen buffer management and double buffering
    - Terminal state persistence and restoration
    - Signal handling and graceful shutdown
    - Performance monitoring and profiling
"""

import os
import sys
import time
import signal
import termios
import tty
import select
import fcntl
import struct
import atexit
import threading
from typing import Optional, Callable, List, Tuple, Dict, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL CONSTANTS AND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalMode(Enum):
    """Terminal operating modes"""
    NORMAL = auto()      # Regular input/output
    RAW = auto()         # Raw mode for direct key capture
    CBREAK = auto()      # Character-at-a-time mode
    ALTERNATE = auto()   # Alternate screen buffer


class RenderQuality(Enum):
    """Rendering quality levels"""
    LOW = 1              # Minimal effects, maximum performance
    MEDIUM = 2           # Balanced quality and performance
    HIGH = 3             # High quality effects
    ULTRA = 4            # Maximum quality, all effects enabled
    INSANE = 5           # Extreme quality with experimental features


@dataclass
class TerminalConfig:
    """Terminal configuration settings"""
    # Display settings
    target_fps: int = 60
    vsync: bool = True
    double_buffer: bool = True
    render_quality: RenderQuality = RenderQuality.ULTRA
    
    # Performance settings
    max_frame_time: float = 0.1  # Maximum time per frame in seconds
    adaptive_quality: bool = True  # Adjust quality based on performance
    profiling_enabled: bool = False
    
    # Terminal settings
    alternate_screen: bool = True
    mouse_support: bool = True
    bracketed_paste: bool = True
    utf8_encoding: bool = True
    
    # Buffer settings
    max_history_lines: int = 10000
    scroll_buffer_size: int = 50000
    
    # Visual settings
    cursor_blink_rate: float = 0.5  # Seconds
    animation_speed: float = 1.0
    particle_count: int = 200
    
    # Debug settings
    show_fps: bool = False
    show_debug_info: bool = False
    log_performance: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# ANSI ESCAPE CODE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

class ANSIEscape:
    """ANSI escape sequence constants and utilities"""
    
    # Cursor control
    HIDE_CURSOR = "\x1b[?25l"
    SHOW_CURSOR = "\x1b[?25h"
    SAVE_CURSOR = "\x1b[s"
    RESTORE_CURSOR = "\x1b[u"
    
    # Screen control
    CLEAR_SCREEN = "\x1b[2J"
    CLEAR_LINE = "\x1b[2K"
    CLEAR_TO_EOL = "\x1b[K"
    CLEAR_TO_BOL = "\x1b[1K"
    HOME = "\x1b[H"
    
    # Alternate screen
    ENTER_ALT_SCREEN = "\x1b[?1049h"
    EXIT_ALT_SCREEN = "\x1b[?1049l"
    
    # Mouse support
    ENABLE_MOUSE = "\x1b[?1000h\x1b[?1002h\x1b[?1015h\x1b[?1006h"
    DISABLE_MOUSE = "\x1b[?1006l\x1b[?1015l\x1b[?1002l\x1b[?1000l"
    
    # Bracketed paste
    ENABLE_BRACKETED_PASTE = "\x1b[?2004h"
    DISABLE_BRACKETED_PASTE = "\x1b[?2004l"
    
    # Text formatting
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    ITALIC = "\x1b[3m"
    UNDERLINE = "\x1b[4m"
    BLINK = "\x1b[5m"
    REVERSE = "\x1b[7m"
    HIDDEN = "\x1b[8m"
    STRIKETHROUGH = "\x1b[9m"
    
    @staticmethod
    def cursor_to(row: int, col: int) -> str:
        """Move cursor to specific position (1-indexed)"""
        return f"\x1b[{row};{col}H"
    
    @staticmethod
    def cursor_up(n: int = 1) -> str:
        """Move cursor up n lines"""
        return f"\x1b[{n}A"
    
    @staticmethod
    def cursor_down(n: int = 1) -> str:
        """Move cursor down n lines"""
        return f"\x1b[{n}B"
    
    @staticmethod
    def cursor_forward(n: int = 1) -> str:
        """Move cursor forward n columns"""
        return f"\x1b[{n}C"
    
    @staticmethod
    def cursor_backward(n: int = 1) -> str:
        """Move cursor backward n columns"""
        return f"\x1b[{n}D"
    
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """RGB foreground color"""
        return f"\x1b[38;2;{r};{g};{b}m"
    
    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """RGB background color"""
        return f"\x1b[48;2;{r};{g};{b}m"
    
    @staticmethod
    def color_256(n: int) -> str:
        """256-color foreground"""
        return f"\x1b[38;5;{n}m"
    
    @staticmethod
    def color_256_bg(n: int) -> str:
        """256-color background"""
        return f"\x1b[48;5;{n}m"


# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    frame_count: int = 0
    total_time: float = 0.0
    render_times: deque = field(default_factory=lambda: deque(maxlen=100))
    update_times: deque = field(default_factory=lambda: deque(maxlen=100))
    fps_history: deque = field(default_factory=lambda: deque(maxlen=60))
    
    def add_frame(self, render_time: float, update_time: float):
        """Record frame timing"""
        self.frame_count += 1
        self.render_times.append(render_time)
        self.update_times.append(update_time)
        total_frame_time = render_time + update_time
        if total_frame_time > 0:
            self.fps_history.append(1.0 / total_frame_time)
    
    @property
    def current_fps(self) -> float:
        """Get current FPS"""
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)
    
    @property
    def avg_render_time(self) -> float:
        """Average render time in ms"""
        if not self.render_times:
            return 0.0
        return (sum(self.render_times) / len(self.render_times)) * 1000
    
    @property
    def avg_update_time(self) -> float:
        """Average update time in ms"""
        if not self.update_times:
            return 0.0
        return (sum(self.update_times) / len(self.update_times)) * 1000


# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN BUFFER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class ScreenBuffer:
    """Double-buffered screen management with dirty region tracking"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.front_buffer: List[List[str]] = [[' ' for _ in range(width)] for _ in range(height)]
        self.back_buffer: List[List[str]] = [[' ' for _ in range(width)] for _ in range(height)]
        self.dirty_regions: List[Tuple[int, int, int, int]] = []  # (x1, y1, x2, y2)
        self.full_redraw = True
        
        # Color buffers (RGB tuples)
        self.front_colors: List[List[Optional[Tuple[int, int, int]]]] = \
            [[None for _ in range(width)] for _ in range(height)]
        self.back_colors: List[List[Optional[Tuple[int, int, int]]]] = \
            [[None for _ in range(width)] for _ in range(height)]
    
    def resize(self, width: int, height: int):
        """Resize buffers"""
        self.width = width
        self.height = height
        self.front_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.back_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.front_colors = [[None for _ in range(width)] for _ in range(height)]
        self.back_colors = [[None for _ in range(width)] for _ in range(height)]
        self.full_redraw = True
    
    def set_char(self, x: int, y: int, char: str, color: Optional[Tuple[int, int, int]] = None):
        """Set character in back buffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.back_buffer[y][x] = char
            self.back_colors[y][x] = color
    
    def clear(self, char: str = ' ', color: Optional[Tuple[int, int, int]] = None):
        """Clear back buffer"""
        for y in range(self.height):
            for x in range(self.width):
                self.back_buffer[y][x] = char
                self.back_colors[y][x] = color
    
    def swap_buffers(self):
        """Swap front and back buffers"""
        self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
        self.front_colors, self.back_colors = self.back_colors, self.front_colors
    
    def get_render_commands(self) -> List[str]:
        """Generate minimal render commands for changed regions"""
        commands = []
        
        if self.full_redraw:
            commands.append(ANSIEscape.HOME)
            for y in range(self.height):
                commands.append(ANSIEscape.cursor_to(y + 1, 1))
                line_parts = []
                current_color = None
                
                for x in range(self.width):
                    char = self.front_buffer[y][x]
                    color = self.front_colors[y][x]
                    
                    if color != current_color:
                        if color is not None:
                            line_parts.append(ANSIEscape.rgb(*color))
                        else:
                            line_parts.append(ANSIEscape.RESET)
                        current_color = color
                    
                    line_parts.append(char)
                
                if current_color is not None:
                    line_parts.append(ANSIEscape.RESET)
                
                commands.append(''.join(line_parts))
            
            self.full_redraw = False
        else:
            # Differential rendering - only update changed cells
            for y in range(self.height):
                line_changed = False
                changes = []
                
                for x in range(self.width):
                    if (self.front_buffer[y][x] != self.back_buffer[y][x] or 
                        self.front_colors[y][x] != self.back_colors[y][x]):
                        if not line_changed:
                            line_changed = True
                            changes.append((x, self.front_buffer[y][x], self.front_colors[y][x]))
                        else:
                            changes.append((x, self.front_buffer[y][x], self.front_colors[y][x]))
                
                if line_changed and changes:
                    # Optimize: group consecutive changes
                    start_x = changes[0][0]
                    commands.append(ANSIEscape.cursor_to(y + 1, start_x + 1))
                    
                    current_color = None
                    for x, char, color in changes:
                        if color != current_color:
                            if color is not None:
                                commands.append(ANSIEscape.rgb(*color))
                            else:
                                commands.append(ANSIEscape.RESET)
                            current_color = color
                        commands.append(char)
                    
                    if current_color is not None:
                        commands.append(ANSIEscape.RESET)
        
        return commands


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalState:
    """Manages terminal state and restoration"""
    
    def __init__(self):
        self.original_settings = None
        self.in_alternate_screen = False
        self.cursor_hidden = False
        self.mouse_enabled = False
        self.bracketed_paste_enabled = False
        
    def save_state(self):
        """Save original terminal state"""
        if sys.stdin.isatty():
            self.original_settings = termios.tcgetattr(sys.stdin.fileno())
    
    def restore_state(self):
        """Restore original terminal state"""
        if self.original_settings and sys.stdin.isatty():
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.original_settings)
        
        # Restore terminal features
        if self.in_alternate_screen:
            sys.stdout.write(ANSIEscape.EXIT_ALT_SCREEN)
        if self.cursor_hidden:
            sys.stdout.write(ANSIEscape.SHOW_CURSOR)
        if self.mouse_enabled:
            sys.stdout.write(ANSIEscape.DISABLE_MOUSE)
        if self.bracketed_paste_enabled:
            sys.stdout.write(ANSIEscape.DISABLE_BRACKETED_PASTE)
        
        sys.stdout.write(ANSIEscape.RESET)
        sys.stdout.flush()
    
    def enter_raw_mode(self):
        """Enter raw terminal mode"""
        if sys.stdin.isatty():
            tty.setraw(sys.stdin.fileno())
    
    def enter_cbreak_mode(self):
        """Enter cbreak mode"""
        if sys.stdin.isatty():
            tty.setcbreak(sys.stdin.fileno())
    
    def enable_alternate_screen(self):
        """Enable alternate screen buffer"""
        sys.stdout.write(ANSIEscape.ENTER_ALT_SCREEN)
        sys.stdout.flush()
        self.in_alternate_screen = True
    
    def hide_cursor(self):
        """Hide cursor"""
        sys.stdout.write(ANSIEscape.HIDE_CURSOR)
        sys.stdout.flush()
        self.cursor_hidden = True
    
    def enable_mouse(self):
        """Enable mouse support"""
        sys.stdout.write(ANSIEscape.ENABLE_MOUSE)
        sys.stdout.flush()
        self.mouse_enabled = True
    
    def enable_bracketed_paste(self):
        """Enable bracketed paste mode"""
        sys.stdout.write(ANSIEscape.ENABLE_BRACKETED_PASTE)
        sys.stdout.flush()
        self.bracketed_paste_enabled = True


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL SIZE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_terminal_size() -> Tuple[int, int]:
    """Get current terminal size (width, height)"""
    try:
        # Try ioctl first
        size_data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b'\x00' * 8)
        rows, cols = struct.unpack('4H', size_data)[:2]
        return cols, rows
    except:
        # Fallback to environment variables
        try:
            cols = int(os.environ.get('COLUMNS', 80))
            rows = int(os.environ.get('LINES', 24))
            return cols, rows
        except:
            return 80, 24


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class InputHandler:
    """Non-blocking input handler with key sequence parsing"""
    
    def __init__(self):
        self.input_buffer = []
        self.escape_sequences = {
            '\x1b[A': 'KEY_UP',
            '\x1b[B': 'KEY_DOWN',
            '\x1b[C': 'KEY_RIGHT',
            '\x1b[D': 'KEY_LEFT',
            '\x1b[H': 'KEY_HOME',
            '\x1b[F': 'KEY_END',
            '\x1b[5~': 'KEY_PAGEUP',
            '\x1b[6~': 'KEY_PAGEDOWN',
            '\x1b[3~': 'KEY_DELETE',
            '\x1b[2~': 'KEY_INSERT',
            '\x1bOP': 'KEY_F1',
            '\x1bOQ': 'KEY_F2',
            '\x1bOR': 'KEY_F3',
            '\x1bOS': 'KEY_F4',
            '\x1b[15~': 'KEY_F5',
            '\x1b[17~': 'KEY_F6',
            '\x1b[18~': 'KEY_F7',
            '\x1b[19~': 'KEY_F8',
            '\x1b[20~': 'KEY_F9',
            '\x1b[21~': 'KEY_F10',
            '\x1b[23~': 'KEY_F11',
            '\x1b[24~': 'KEY_F12',
        }
    
    def has_input(self, timeout: float = 0.0) -> bool:
        """Check if input is available"""
        if not sys.stdin.isatty():
            return False
        
        readable, _, _ = select.select([sys.stdin], [], [], timeout)
        return bool(readable)
    
    def read_key(self) -> Optional[str]:
        """Read a single key or escape sequence"""
        if not self.has_input(0.0):
            return None
        
        try:
            char = sys.stdin.read(1)
            
            if char == '\x1b':  # Escape sequence
                sequence = char
                # Read the next character(s)
                if self.has_input(0.05):  # Short timeout for escape sequences
                    char2 = sys.stdin.read(1)
                    sequence += char2
                    
                    if char2 == '[' or char2 == 'O':
                        # Could be longer sequence
                        while self.has_input(0.05):
                            next_char = sys.stdin.read(1)
                            sequence += next_char
                            if next_char.isalpha() or next_char == '~':
                                break
                
                # Check if it's a known escape sequence
                return self.escape_sequences.get(sequence, sequence)
            
            return char
        except:
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# CORE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalEngine:
    """Core terminal engine managing the main loop and subsystems"""
    
    def __init__(self, config: Optional[TerminalConfig] = None):
        self.config = config or TerminalConfig()
        self.running = False
        self.paused = False
        
        # State management
        self.state = TerminalState()
        self.state.save_state()
        
        # Get terminal size
        self.width, self.height = get_terminal_size()
        
        # Screen buffer
        self.screen = ScreenBuffer(self.width, self.height)
        
        # Input handling
        self.input_handler = InputHandler()
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        
        # Callbacks
        self.update_callback: Optional[Callable[[float], None]] = None
        self.render_callback: Optional[Callable[[ScreenBuffer], None]] = None
        self.input_callback: Optional[Callable[[str], None]] = None
        self.resize_callback: Optional[Callable[[int, int], None]] = None
        
        # Timing
        self.last_frame_time = time.time()
        self.accumulated_time = 0.0
        self.target_frame_time = 1.0 / self.config.target_fps
        
        # Signal handlers
        self._setup_signal_handlers()
        
        # Ensure cleanup on exit
        atexit.register(self.cleanup)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def handle_signal(signum, frame):
            self.stop()
        
        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGWINCH, self._handle_resize)
    
    def _handle_resize(self, signum, frame):
        """Handle terminal resize"""
        old_width, old_height = self.width, self.height
        self.width, self.height = get_terminal_size()
        
        if self.width != old_width or self.height != old_height:
            self.screen.resize(self.width, self.height)
            if self.resize_callback:
                self.resize_callback(self.width, self.height)
    
    def initialize(self):
        """Initialize terminal for rendering"""
        # Enter raw mode
        self.state.enter_raw_mode()
        
        # Setup terminal features
        if self.config.alternate_screen:
            self.state.enable_alternate_screen()
        
        self.state.hide_cursor()
        
        if self.config.mouse_support:
            self.state.enable_mouse()
        
        if self.config.bracketed_paste:
            self.state.enable_bracketed_paste()
        
        # Clear screen
        sys.stdout.write(ANSIEscape.CLEAR_SCREEN + ANSIEscape.HOME)
        sys.stdout.flush()
    
    def cleanup(self):
        """Cleanup and restore terminal state"""
        self.state.restore_state()
    
    def set_update_callback(self, callback: Callable[[float], None]):
        """Set update callback (called every frame with delta time)"""
        self.update_callback = callback
    
    def set_render_callback(self, callback: Callable[[ScreenBuffer], None]):
        """Set render callback (called to render to screen buffer)"""
        self.render_callback = callback
    
    def set_input_callback(self, callback: Callable[[str], None]):
        """Set input callback (called for each key press)"""
        self.input_callback = callback
    
    def set_resize_callback(self, callback: Callable[[int, int], None]):
        """Set resize callback"""
        self.resize_callback = callback
    
    def run(self):
        """Main engine loop"""
        self.running = True
        self.initialize()
        
        try:
            while self.running:
                frame_start = time.time()
                
                # Calculate delta time
                delta_time = frame_start - self.last_frame_time
                self.last_frame_time = frame_start
                
                # Cap delta time to prevent spiral of death
                if delta_time > self.config.max_frame_time:
                    delta_time = self.config.max_frame_time
                
                # Handle input
                update_start = time.time()
                while self.input_handler.has_input(0.0):
                    key = self.input_handler.read_key()
                    if key and self.input_callback:
                        self.input_callback(key)
                
                # Update logic
                if not self.paused and self.update_callback:
                    self.update_callback(delta_time)
                
                update_time = time.time() - update_start
                
                # Render
                render_start = time.time()
                if self.render_callback:
                    self.screen.clear()
                    self.render_callback(self.screen)
                    self.screen.swap_buffers()
                    
                    # Output to terminal
                    commands = self.screen.get_render_commands()
                    sys.stdout.write(''.join(commands))
                    sys.stdout.flush()
                
                render_time = time.time() - render_start
                
                # Update metrics
                self.metrics.add_frame(render_time, update_time)
                
                # Frame timing
                frame_time = time.time() - frame_start
                if self.config.vsync:
                    sleep_time = max(0, self.target_frame_time - frame_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
        
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the engine"""
        self.running = False
    
    def pause(self):
        """Pause updates"""
        self.paused = True
    
    def resume(self):
        """Resume updates"""
        self.paused = False


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'TerminalEngine',
    'TerminalConfig',
    'TerminalMode',
    'RenderQuality',
    'ScreenBuffer',
    'ANSIEscape',
    'PerformanceMetrics',
    'get_terminal_size',
]
