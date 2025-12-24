#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UTILITY FUNCTIONS                                   ║
║                    Helper Functions and Utilities                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Common utility functions used across the application.
"""

import math
import time
from typing import List, Tuple, Optional
from functools import wraps


# ═══════════════════════════════════════════════════════════════════════════════
# MATH UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b"""
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth interpolation between edge0 and edge1"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def remap(value: float, in_min: float, in_max: float, 
         out_min: float, out_max: float) -> float:
    """Remap value from one range to another"""
    return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min)


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate 2D distance"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def angle_between(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle between two points in radians"""
    return math.atan2(y2 - y1, x2 - x1)


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex string"""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex string to RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hsv(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convert RGB (0-1) to HSV"""
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c
    
    # Hue
    if delta == 0:
        h = 0
    elif max_c == r:
        h = 60 * (((g - b) / delta) % 6)
    elif max_c == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)
    
    # Saturation
    s = 0 if max_c == 0 else delta / max_c
    
    # Value
    v = max_c
    
    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
    """Convert HSV to RGB (0-1)"""
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
    
    return r + m, g + m, b + m


def interpolate_color(color1: Tuple[int, int, int], 
                     color2: Tuple[int, int, int], 
                     t: float) -> Tuple[int, int, int]:
    """Interpolate between two RGB colors"""
    r = int(lerp(color1[0], color2[0], t))
    g = int(lerp(color1[1], color2[1], t))
    b = int(lerp(color1[2], color2[2], t))
    return (r, g, b)


# ═══════════════════════════════════════════════════════════════════════════════
# STRING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def truncate_string(s: str, max_length: int, ellipsis: str = "...") -> str:
    """Truncate string to max length with ellipsis"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(ellipsis)] + ellipsis


def pad_string(s: str, width: int, align: str = "left", char: str = " ") -> str:
    """Pad string to width"""
    if len(s) >= width:
        return s
    
    padding = char * (width - len(s))
    
    if align == "left":
        return s + padding
    elif align == "right":
        return padding + s
    else:  # center
        left_pad = len(padding) // 2
        right_pad = len(padding) - left_pad
        return char * left_pad + s + char * right_pad


def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to specified width"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        
        if current_length + word_length + len(current_line) <= width:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text"""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


# ═══════════════════════════════════════════════════════════════════════════════
# TIME UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def format_time(seconds: float) -> str:
    """Format seconds to human-readable string"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def format_timestamp(timestamp: float, format_str: str = "%H:%M:%S") -> str:
    """Format Unix timestamp to string"""
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)


# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {format_time(duration)}")
        return result
    return wrapper


class Timer:
    """Simple timer context manager"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.duration = time.time() - self.start_time
        print(f"{self.name} completed in {format_time(self.duration)}")


class FPSCounter:
    """FPS counter with smoothing"""
    
    def __init__(self, sample_size: int = 60):
        self.sample_size = sample_size
        self.frame_times = []
        self.last_time = time.time()
    
    def tick(self) -> float:
        """Update FPS counter and return current FPS"""
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(delta)
        if len(self.frame_times) > self.sample_size:
            self.frame_times.pop(0)
        
        avg_delta = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_delta if avg_delta > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# FILE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except:
        return False


def get_file_size(path: str) -> Optional[int]:
    """Get file size in bytes"""
    try:
        return os.path.getsize(path)
    except:
        return None


def format_file_size(size_bytes: int) -> str:
    """Format file size to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def is_valid_rgb(r: int, g: int, b: int) -> bool:
    """Check if RGB values are valid"""
    return all(0 <= val <= 255 for val in [r, g, b])


def is_valid_hex_color(hex_color: str) -> bool:
    """Check if hex color string is valid"""
    if not hex_color.startswith('#'):
        hex_color = '#' + hex_color
    
    if len(hex_color) != 7:
        return False
    
    try:
        int(hex_color[1:], 16)
        return True
    except:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Math
    'clamp', 'lerp', 'smoothstep', 'remap',
    'distance_2d', 'angle_between',
    
    # Color
    'rgb_to_hex', 'hex_to_rgb',
    'rgb_to_hsv', 'hsv_to_rgb',
    'interpolate_color',
    
    # String
    'truncate_string', 'pad_string', 'wrap_text', 'strip_ansi',
    
    # Time
    'format_time', 'format_timestamp',
    
    # Performance
    'timing_decorator', 'Timer', 'FPSCounter',
    
    # File
    'ensure_directory', 'get_file_size', 'format_file_size',
    
    # Validation
    'is_valid_rgb', 'is_valid_hex_color',
]
