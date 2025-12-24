#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Terminal UI with 3D Christmas Tree, Parallax Effects, and Full Terminal Emulation

This is a comprehensive TUI application featuring:
- Full terminal emulation with command execution
- Persistent menu bar
- Autocorrect panel
- Advanced keybindings
- GLSL/HLSL shader integration for visual effects
- 3D Christmas tree with realistic lighting and snow
- Multi-layer parallax effects
- Gradient borders on all UI elements
"""

import os
import sys
import time
import math
import random
import signal
import shutil
import subprocess
import threading
import queue
import select
import termios
import tty
import fcntl
import struct
import re
import json
import hashlib
from datetime import datetime
from collections import deque, defaultdict
from typing import List, Tuple, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import traceback

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

class Config:
    """Global configuration for the TUI application"""
    
    # Terminal settings
    DEFAULT_SHELL = os.environ.get('SHELL', '/bin/bash')
    HISTORY_SIZE = 1000
    MAX_OUTPUT_LINES = 10000
    
    # Visual settings
    FPS = 60
    FRAME_TIME = 1.0 / FPS
    
    # Menu bar settings
    MENU_HEIGHT = 3
    MENU_ALWAYS_VISIBLE = True
    
    # Status bar settings
    STATUS_BAR_HEIGHT = 2
    
    # Autocorrect panel settings
    AUTOCORRECT_HEIGHT = 4
    AUTOCORRECT_MAX_SUGGESTIONS = 8
    
    # Shader settings
    ENABLE_SHADERS = True
    SHADER_QUALITY = 'high'  # low, medium, high, ultra
    
    # Christmas tree settings
    TREE_ENABLE_3D = True
    TREE_ENABLE_SHADOWS = True
    TREE_ENABLE_SNOW = True
    TREE_ENABLE_LIGHTS_FLICKER = True
    TREE_POSITION = (0.85, 0.5)  # Right side of screen
    TREE_SIZE = 0.15  # Percentage of screen
    
    # Parallax settings
    PARALLAX_LAYERS = 5
    PARALLAX_STARS_PER_LAYER = 100
    PARALLAX_SPEED_MULTIPLIER = 1.0
    PARALLAX_ENABLE_GLOW = True
    
    # Color schemes
    THEME = {
        'menu_bg': (20, 25, 35),
        'menu_fg': (200, 220, 255),
        'menu_active': (100, 180, 255),
        'status_bg': (15, 20, 30),
        'status_fg': (180, 200, 220),
        'border_primary': (80, 120, 200),
        'border_secondary': (120, 80, 200),
        'text_normal': (220, 220, 230),
        'text_command': (100, 255, 150),
        'text_output': (200, 210, 220),
        'text_error': (255, 100, 100),
        'cursor': (0, 255, 200),
        'selection': (60, 80, 120),
        'autocorrect_bg': (25, 30, 40),
        'autocorrect_fg': (180, 200, 220),
        'autocorrect_selected': (255, 200, 100),
    }
    
    # Keybindings
    KEYBINDINGS = {
        'menu_toggle': '\x1b[19~',  # F8
        'autocorrect_toggle': '\x1b[20~',  # F9
        'clear_screen': '\x1b[21~',  # F10
        'history_prev': '\x1b[A',  # Up arrow
        'history_next': '\x1b[B',  # Down arrow
        'cursor_left': '\x1b[D',  # Left arrow
        'cursor_right': '\x1b[C',  # Right arrow
        'cursor_home': '\x1b[H',  # Home
        'cursor_end': '\x1b[F',  # End
        'delete_char': '\x7f',  # Backspace
        'delete_forward': '\x1b[3~',  # Delete
        'word_left': '\x1b[1;5D',  # Ctrl+Left
        'word_right': '\x1b[1;5C',  # Ctrl+Right
        'line_start': '\x01',  # Ctrl+A
        'line_end': '\x05',  # Ctrl+E
        'delete_line': '\x15',  # Ctrl+U
        'delete_word': '\x17',  # Ctrl+W
        'accept_suggestion': '\t',  # Tab
        'exit': '\x03',  # Ctrl+C
    }

# ============================================================================
# UTILITY CLASSES AND FUNCTIONS
# ============================================================================

class Color:
    """ANSI color utilities"""
    
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Convert RGB to ANSI escape sequence"""
        return f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m"
    
    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Convert RGB to ANSI background escape sequence"""
        return f"\x1b[48;2;{int(r)};{int(g)};{int(b)}m"
    
    @staticmethod
    def gradient(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Linear interpolation between two colors"""
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] * (1 - t) + c2[0] * t),
            int(c1[1] * (1 - t) + c2[1] * t),
            int(c1[2] * (1 - t) + c2[2] * t)
        )
    
    @staticmethod
    def reset() -> str:
        """Reset all attributes"""
        return "\x1b[0m"
    
    @staticmethod
    def bold() -> str:
        """Bold text"""
        return "\x1b[1m"
    
    @staticmethod
    def dim() -> str:
        """Dim text"""
        return "\x1b[2m"
    
    @staticmethod
    def italic() -> str:
        """Italic text"""
        return "\x1b[3m"
    
    @staticmethod
    def underline() -> str:
        """Underline text"""
        return "\x1b[4m"
    
    @staticmethod
    def blink() -> str:
        """Blinking text"""
        return "\x1b[5m"
    
    @staticmethod
    def reverse() -> str:
        """Reverse video"""
        return "\x1b[7m"

class Cursor:
    """Terminal cursor utilities"""
    
    @staticmethod
    def hide() -> str:
        """Hide cursor"""
        return "\x1b[?25l"
    
    @staticmethod
    def show() -> str:
        """Show cursor"""
        return "\x1b[?25h"
    
    @staticmethod
    def move(x: int, y: int) -> str:
        """Move cursor to position"""
        return f"\x1b[{y+1};{x+1}H"
    
    @staticmethod
    def up(n: int = 1) -> str:
        """Move cursor up"""
        return f"\x1b[{n}A"
    
    @staticmethod
    def down(n: int = 1) -> str:
        """Move cursor down"""
        return f"\x1b[{n}B"
    
    @staticmethod
    def forward(n: int = 1) -> str:
        """Move cursor forward"""
        return f"\x1b[{n}C"
    
    @staticmethod
    def back(n: int = 1) -> str:
        """Move cursor back"""
        return f"\x1b[{n}D"
    
    @staticmethod
    def save() -> str:
        """Save cursor position"""
        return "\x1b[s"
    
    @staticmethod
    def restore() -> str:
        """Restore cursor position"""
        return "\x1b[u"

class Screen:
    """Terminal screen utilities"""
    
    @staticmethod
    def clear() -> str:
        """Clear entire screen"""
        return "\x1b[2J"
    
    @staticmethod
    def clear_line() -> str:
        """Clear current line"""
        return "\x1b[2K"
    
    @staticmethod
    def clear_to_end() -> str:
        """Clear from cursor to end of screen"""
        return "\x1b[J"
    
    @staticmethod
    def clear_to_start() -> str:
        """Clear from cursor to start of screen"""
        return "\x1b[1J"
    
    @staticmethod
    def alternate_screen() -> str:
        """Switch to alternate screen buffer"""
        return "\x1b[?1049h"
    
    @staticmethod
    def main_screen() -> str:
        """Switch to main screen buffer"""
        return "\x1b[?1049l"
    
    @staticmethod
    def get_size() -> Tuple[int, int]:
        """Get terminal size (columns, rows)"""
        return shutil.get_terminal_size((80, 24))

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t

def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth interpolation"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

# ============================================================================
# SHADER SYSTEM
# ============================================================================

class ShaderType(Enum):
    """Types of shaders available"""
    PARALLAX = auto()
    CHRISTMAS_TREE = auto()
    SNOW = auto()
    GLOW = auto()
    BORDER = auto()

@dataclass
class ShaderInput:
    """Input data for shader execution"""
    time: float
    resolution: Tuple[int, int]
    position: Tuple[float, float]
    mouse: Tuple[float, float] = (0.0, 0.0)
    custom: Dict[str, Any] = field(default_factory=dict)

class Shader:
    """Base class for shader implementations"""
    
    def __init__(self, shader_type: ShaderType):
        self.shader_type = shader_type
        self.enabled = True
        self.uniforms: Dict[str, Any] = {}
    
    def execute(self, input_data: ShaderInput) -> Tuple[int, int, int, float]:
        """
        Execute shader and return RGBA color
        Returns: (r, g, b, a) where each component is 0-255
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def set_uniform(self, name: str, value: Any):
        """Set a uniform variable"""
        self.uniforms[name] = value
    
    def get_uniform(self, name: str, default: Any = None) -> Any:
        """Get a uniform variable"""
        return self.uniforms.get(name, default)

class ParallaxShader(Shader):
    """Advanced parallax shader with multiple layers and effects"""
    
    def __init__(self):
        super().__init__(ShaderType.PARALLAX)
        self.stars: List[Dict[str, float]] = []
        self.initialize_stars()
    
    def initialize_stars(self):
        """Initialize star field"""
        random.seed(12345)  # Deterministic seed for consistency
        
        for layer in range(Config.PARALLAX_LAYERS):
            layer_stars = []
            num_stars = Config.PARALLAX_STARS_PER_LAYER
            depth = (layer + 1) / Config.PARALLAX_LAYERS
            
            for _ in range(num_stars):
                star = {
                    'x': random.random(),
                    'y': random.random(),
                    'size': random.uniform(0.5, 2.0) * depth,
                    'brightness': random.uniform(0.3, 1.0),
                    'speed': depth * Config.PARALLAX_SPEED_MULTIPLIER,
                    'flicker_offset': random.uniform(0, math.pi * 2),
                    'flicker_speed': random.uniform(0.5, 2.0),
                    'color_hue': random.uniform(0, 360),
                    'layer': layer,
                }
                layer_stars.append(star)
            
            self.stars.extend(layer_stars)
    
    def execute(self, input_data: ShaderInput) -> Tuple[int, int, int, float]:
        """Execute parallax shader"""
        if not self.enabled:
            return (0, 0, 0, 0)
        
        time_val = input_data.time
        res_x, res_y = input_data.resolution
        pos_x, pos_y = input_data.position
        
        # Normalize position
        uv_x = pos_x / max(res_x, 1)
        uv_y = pos_y / max(res_y, 1)
        
        # Accumulate color from all stars
        final_r, final_g, final_b, final_a = 0.0, 0.0, 0.0, 0.0
        
        for star in self.stars:
            # Animated star position
            star_x = (star['x'] + time_val * star['speed'] * 0.01) % 1.0
            star_y = star['y']
            
            # Distance from current pixel to star
            dx = (uv_x - star_x) * res_x / 50.0
            dy = (uv_y - star_y) * res_y / 50.0
            dist = math.sqrt(dx * dx + dy * dy)
            
            # Flicker effect
            flicker = 0.7 + 0.3 * math.sin(time_val * star['flicker_speed'] + star['flicker_offset'])
            
            # Star intensity based on distance
            size = star['size'] * flicker
            intensity = 0.0
            
            if dist < size:
                intensity = 1.0 - (dist / size)
                intensity = smoothstep(0.0, 1.0, intensity)
                
                if Config.PARALLAX_ENABLE_GLOW:
                    # Add glow
                    glow_radius = size * 2.0
                    if dist < glow_radius:
                        glow = 0.3 * (1.0 - dist / glow_radius) ** 2
                        intensity += glow
            
            if intensity > 0:
                # Color based on hue
                hue = star['color_hue']
                color = self._hue_to_rgb(hue)
                brightness = star['brightness'] * intensity
                
                final_r += color[0] * brightness
                final_g += color[1] * brightness
                final_b += color[2] * brightness
                final_a = max(final_a, intensity * 0.8)
        
        # Clamp values
        final_r = min(255, int(final_r * 255))
        final_g = min(255, int(final_g * 255))
        final_b = min(255, int(final_b * 255))
        final_a = min(255, int(final_a * 255))
        
        return (final_r, final_g, final_b, final_a)
    
    def _hue_to_rgb(self, hue: float) -> Tuple[float, float, float]:
        """Convert HSV to RGB (S=1, V=1)"""
        hue = hue % 360
        h = hue / 60.0
        i = int(h)
        f = h - i
        
        if i == 0:
            return (1.0, f, 0.0)
        elif i == 1:
            return (1.0 - f, 1.0, 0.0)
        elif i == 2:
            return (0.0, 1.0, f)
        elif i == 3:
            return (0.0, 1.0 - f, 1.0)
        elif i == 4:
            return (f, 0.0, 1.0)
        else:
            return (1.0, 0.0, 1.0 - f)

class ChristmasTreeShader(Shader):
    """Advanced 3D Christmas tree shader with realistic lighting"""
    
    def __init__(self):
        super().__init__(ShaderType.CHRISTMAS_TREE)
        self.lights: List[Dict[str, Any]] = []
        self.initialize_lights()
    
    def initialize_lights(self):
        """Initialize Christmas lights on the tree"""
        random.seed(54321)
        
        # Create lights in spiral pattern
        num_lights = 40
        for i in range(num_lights):
            t = i / num_lights
            angle = t * math.pi * 8  # Multiple spirals
            height = t
            radius = (1.0 - t) * 0.4  # Cone shape
            
            light = {
                'x': math.cos(angle) * radius,
                'y': height,
                'z': math.sin(angle) * radius,
                'color': random.choice([
                    (255, 50, 50),    # Red
                    (50, 255, 50),    # Green
                    (50, 50, 255),    # Blue
                    (255, 255, 50),   # Yellow
                    (255, 50, 255),   # Magenta
                    (50, 255, 255),   # Cyan
                ]),
                'flicker_offset': random.uniform(0, math.pi * 2),
                'flicker_speed': random.uniform(2.0, 5.0),
            }
            self.lights.append(light)
    
    def execute(self, input_data: ShaderInput) -> Tuple[int, int, int, float]:
        """Execute Christmas tree shader"""
        if not self.enabled:
            return (0, 0, 0, 0)
        
        time_val = input_data.time
        res_x, res_y = input_data.resolution
        pos_x, pos_y = input_data.position
        
        # Normalize position
        uv_x = pos_x / max(res_x, 1)
        uv_y = pos_y / max(res_y, 1)
        
        # Tree center position
        tree_x = Config.TREE_POSITION[0]
        tree_y = Config.TREE_POSITION[1]
        tree_size = Config.TREE_SIZE
        
        # Transform to tree space
        local_x = (uv_x - tree_x) / tree_size
        local_y = (uv_y - tree_y) / tree_size
        
        # Check if we're within tree bounds
        if abs(local_x) > 1.0 or abs(local_y) > 1.0:
            return (0, 0, 0, 0)
        
        # Map to 3D cone
        height = (1.0 - local_y) * 0.5 + 0.5  # 0 at bottom, 1 at top
        radius_at_height = (1.0 - height) * 0.5
        dist_from_center = abs(local_x)
        
        # Check if inside cone
        if dist_from_center > radius_at_height and height < 0.85:
            # Check trunk
            if height < 0.15 and abs(local_x) < 0.1:
                # Trunk color
                return self._calculate_trunk_color(local_x, local_y, time_val)
            return (0, 0, 0, 0)
        
        # Calculate tree color with lighting
        if height < 0.85:
            return self._calculate_tree_color(local_x, local_y, height, time_val)
        else:
            # Star at top
            return self._calculate_star_color(local_x, local_y, time_val)
    
    def _calculate_tree_color(self, x: float, y: float, height: float, time: float) -> Tuple[int, int, int, float]:
        """Calculate tree color with 3D lighting"""
        # Base tree color (gradient from dark green to light green)
        base_color = Color.gradient((20, 100, 40), (60, 180, 80), height)
        
        # Calculate normal (approximate cone normal)
        nx = x
        ny = 0.6
        nz = math.sqrt(max(0, 1 - nx*nx - ny*ny))
        
        # Rotating light direction
        light_angle = time * 0.5
        light_x = math.cos(light_angle)
        light_y = -0.3
        light_z = math.sin(light_angle)
        
        # Lambertian lighting
        dot = max(0, nx * light_x + ny * light_y + nz * light_z)
        ambient = 0.3
        lighting = ambient + (1.0 - ambient) * dot
        
        # Apply lighting
        lit_r = int(base_color[0] * lighting)
        lit_g = int(base_color[1] * lighting)
        lit_b = int(base_color[2] * lighting)
        
        # Add Christmas lights
        if Config.TREE_ENABLE_LIGHTS_FLICKER:
            for light in self.lights:
                # Check if light is close to this pixel
                dx = x - light['x']
                dy = (height - 0.5) * 2 - light['y']
                dist_2d = math.sqrt(dx * dx + dy * dy)
                
                if dist_2d < 0.05:
                    # Flicker
                    flicker = 0.5 + 0.5 * math.sin(time * light['flicker_speed'] + light['flicker_offset'])
                    
                    # Blend light color
                    blend = smoothstep(0.05, 0.0, dist_2d) * flicker
                    lit_r = int(lit_r * (1 - blend) + light['color'][0] * blend)
                    lit_g = int(lit_g * (1 - blend) + light['color'][1] * blend)
                    lit_b = int(lit_b * (1 - blend) + light['color'][2] * blend)
                elif dist_2d < 0.15:
                    # Glow
                    glow = 0.3 * smoothstep(0.15, 0.05, dist_2d)
                    flicker = 0.5 + 0.5 * math.sin(time * light['flicker_speed'] + light['flicker_offset'])
                    glow *= flicker
                    lit_r = min(255, int(lit_r + light['color'][0] * glow))
                    lit_g = min(255, int(lit_g + light['color'][1] * glow))
                    lit_b = min(255, int(lit_b + light['color'][2] * glow))
        
        # Add shadow if enabled
        if Config.TREE_ENABLE_SHADOWS:
            shadow = 1.0 - 0.2 * smoothstep(0, 0.3, height)
            lit_r = int(lit_r * shadow)
            lit_g = int(lit_g * shadow)
            lit_b = int(lit_b * shadow)
        
        return (lit_r, lit_g, lit_b, 255)
    
    def _calculate_trunk_color(self, x: float, y: float, time: float) -> Tuple[int, int, int, float]:
        """Calculate trunk color"""
        # Brown color with some variation
        base_brown = (101, 67, 33)
        
        # Simple lighting
        lighting = 0.7 + 0.3 * math.cos(x * 5)
        
        r = int(base_brown[0] * lighting)
        g = int(base_brown[1] * lighting)
        b = int(base_brown[2] * lighting)
        
        return (r, g, b, 255)
    
    def _calculate_star_color(self, x: float, y: float, time: float) -> Tuple[int, int, int, float]:
        """Calculate star color at top of tree"""
        # Distance from star center
        star_y = 0.95
        dist = math.sqrt(x * x + (y - star_y) ** 2) / 0.1
        
        if dist > 1.0:
            return (0, 0, 0, 0)
        
        # Pulsing effect
        pulse = 0.7 + 0.3 * math.sin(time * 3.0)
        intensity = (1.0 - dist) * pulse
        
        # Yellow-white star
        r = int(255 * intensity)
        g = int(240 * intensity)
        b = int(100 * intensity)
        
        return (r, g, b, int(255 * intensity))

class SnowShader(Shader):
    """Snow particle shader"""
    
    def __init__(self):
        super().__init__(ShaderType.SNOW)
        self.snowflakes: List[Dict[str, float]] = []
        self.initialize_snowflakes()
    
    def initialize_snowflakes(self):
        """Initialize snowflakes"""
        random.seed(99999)
        
        num_flakes = 150
        for _ in range(num_flakes):
            flake = {
                'x': random.random(),
                'y': random.random(),
                'size': random.uniform(0.3, 1.5),
                'speed': random.uniform(0.02, 0.08),
                'sway': random.uniform(-0.02, 0.02),
                'sway_speed': random.uniform(1.0, 3.0),
                'sway_offset': random.uniform(0, math.pi * 2),
            }
            self.snowflakes.append(flake)
    
    def execute(self, input_data: ShaderInput) -> Tuple[int, int, int, float]:
        """Execute snow shader"""
        if not self.enabled or not Config.TREE_ENABLE_SNOW:
            return (0, 0, 0, 0)
        
        time_val = input_data.time
        res_x, res_y = input_data.resolution
        pos_x, pos_y = input_data.position
        
        # Normalize position
        uv_x = pos_x / max(res_x, 1)
        uv_y = pos_y / max(res_y, 1)
        
        # Check all snowflakes
        for flake in self.snowflakes:
            # Animated position
            flake_x = flake['x'] + math.sin(time_val * flake['sway_speed'] + flake['sway_offset']) * flake['sway']
            flake_y = (flake['y'] + time_val * flake['speed']) % 1.0
            
            # Distance to snowflake
            dx = (uv_x - flake_x) * res_x / 20.0
            dy = (uv_y - flake_y) * res_y / 20.0
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < flake['size']:
                intensity = 1.0 - (dist / flake['size'])
                alpha = int(255 * intensity * 0.8)
                return (255, 255, 255, alpha)
        
        return (0, 0, 0, 0)

class ShaderManager:
    """Manages all shaders in the application"""
    
    def __init__(self):
        self.shaders: Dict[ShaderType, Shader] = {}
        self.initialize_shaders()
    
    def initialize_shaders(self):
        """Initialize all shaders"""
        if Config.ENABLE_SHADERS:
            self.shaders[ShaderType.PARALLAX] = ParallaxShader()
            self.shaders[ShaderType.CHRISTMAS_TREE] = ChristmasTreeShader()
            self.shaders[ShaderType.SNOW] = SnowShader()
    
    def get_shader(self, shader_type: ShaderType) -> Optional[Shader]:
        """Get a shader by type"""
        return self.shaders.get(shader_type)
    
    def execute_shader(self, shader_type: ShaderType, input_data: ShaderInput) -> Tuple[int, int, int, float]:
        """Execute a shader and return color"""
        shader = self.get_shader(shader_type)
        if shader and shader.enabled:
            return shader.execute(input_data)
        return (0, 0, 0, 0)
    
    def render_layer(self, shader_type: ShaderType, width: int, height: int, time: float) -> List[List[Tuple[int, int, int, float]]]:
        """Render entire layer from shader"""
        layer = []
        for y in range(height):
            row = []
            for x in range(width):
                input_data = ShaderInput(
                    time=time,
                    resolution=(width, height),
                    position=(x, y)
                )
                color = self.execute_shader(shader_type, input_data)
                row.append(color)
            layer.append(row)
        return layer

# ============================================================================
# BORDER AND DECORATION SYSTEM
# ============================================================================

class BorderStyle(Enum):
    """Border styles"""
    NONE = auto()
    SIMPLE = auto()
    DOUBLE = auto()
    ROUNDED = auto()
    GRADIENT = auto()
    ANIMATED = auto()

class Border:
    """Border drawing utilities"""
    
    # Box drawing characters
    CHARS_SIMPLE = {
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'h': '─', 'v': '│', 't': '┬', 'b': '┴', 'l': '├', 'r': '┤', 'c': '┼'
    }
    
    CHARS_DOUBLE = {
        'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
        'h': '═', 'v': '║', 't': '╦', 'b': '╩', 'l': '╠', 'r': '╣', 'c': '╬'
    }
    
    CHARS_ROUNDED = {
        'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
        'h': '─', 'v': '│', 't': '┬', 'b': '┴', 'l': '├', 'r': '┤', 'c': '┼'
    }
    
    @staticmethod
    def draw_box(x: int, y: int, width: int, height: int, style: BorderStyle, 
                 color1: Tuple[int, int, int], color2: Optional[Tuple[int, int, int]] = None,
                 time: float = 0.0) -> List[str]:
        """
        Draw a box with gradient border
        Returns list of strings to be drawn at specified positions
        """
        if width < 2 or height < 2:
            return []
        
        if style == BorderStyle.NONE:
            return []
        
        # Select character set
        if style == BorderStyle.DOUBLE:
            chars = Border.CHARS_DOUBLE
        elif style == BorderStyle.ROUNDED:
            chars = Border.CHARS_ROUNDED
        else:
            chars = Border.CHARS_SIMPLE
        
        lines = []
        
        # If no second color, use same as first
        if color2 is None:
            color2 = color1
        
        # Top border
        top_line = ""
        top_line += Border._get_colored_char(chars['tl'], color1, color2, 0, width, time)
        for i in range(1, width - 1):
            t = i / (width - 1)
            color = Color.gradient(color1, color2, t)
            if style == BorderStyle.ANIMATED:
                # Add animation offset
                anim_t = (t + time * 0.5) % 1.0
                color = Color.gradient(color1, color2, anim_t)
            top_line += Color.rgb(*color) + chars['h']
        top_line += Border._get_colored_char(chars['tr'], color1, color2, width-1, width, time)
        top_line += Color.reset()
        lines.append((x, y, top_line))
        
        # Side borders
        for i in range(1, height - 1):
            t = i / (height - 1)
            left_color = Color.gradient(color1, color2, t)
            right_color = Color.gradient(color2, color1, t)
            
            if style == BorderStyle.ANIMATED:
                anim_t = (t + time * 0.5) % 1.0
                left_color = Color.gradient(color1, color2, anim_t)
                right_color = Color.gradient(color2, color1, anim_t)
            
            left_str = Color.rgb(*left_color) + chars['v'] + Color.reset()
            right_str = Color.rgb(*right_color) + chars['v'] + Color.reset()
            lines.append((x, y + i, left_str))
            lines.append((x + width - 1, y + i, right_str))
        
        # Bottom border
        bottom_line = ""
        bottom_line += Border._get_colored_char(chars['bl'], color1, color2, 0, width, time)
        for i in range(1, width - 1):
            t = i / (width - 1)
            color = Color.gradient(color2, color1, t)
            if style == BorderStyle.ANIMATED:
                anim_t = (t + time * 0.5) % 1.0
                color = Color.gradient(color2, color1, anim_t)
            bottom_line += Color.rgb(*color) + chars['h']
        bottom_line += Border._get_colored_char(chars['br'], color1, color2, width-1, width, time)
        bottom_line += Color.reset()
        lines.append((x, y + height - 1, bottom_line))
        
        return lines
    
    @staticmethod
    def _get_colored_char(char: str, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                         pos: int, total: int, time: float) -> str:
        """Get a colored character for border"""
        t = pos / max(total - 1, 1)
        color = Color.gradient(color1, color2, t)
        return Color.rgb(*color) + char

# ============================================================================
# TEXT BUFFER AND RENDERING
# ============================================================================

@dataclass
class TextSegment:
    """A segment of text with styling"""
    text: str
    fg_color: Optional[Tuple[int, int, int]] = None
    bg_color: Optional[Tuple[int, int, int]] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False

class TextBuffer:
    """Buffer for storing and rendering text with styling"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.lines: List[List[TextSegment]] = [[] for _ in range(height)]
        self.clear()
    
    def clear(self):
        """Clear the buffer"""
        self.lines = [[] for _ in range(self.height)]
    
    def resize(self, width: int, height: int):
        """Resize the buffer"""
        old_lines = self.lines
        self.width = width
        self.height = height
        self.lines = [[] for _ in range(height)]
        
        # Copy old content
        for i, line in enumerate(old_lines):
            if i < height:
                self.lines[i] = line
    
    def write(self, x: int, y: int, segments: List[TextSegment]):
        """Write text segments at position"""
        if 0 <= y < self.height:
            self.lines[y] = segments
    
    def write_string(self, x: int, y: int, text: str, 
                    fg_color: Optional[Tuple[int, int, int]] = None,
                    bg_color: Optional[Tuple[int, int, int]] = None):
        """Write a simple string at position"""
        if 0 <= y < self.height:
            segment = TextSegment(text=text, fg_color=fg_color, bg_color=bg_color)
            self.lines[y] = [segment]
    
    def render(self) -> str:
        """Render the buffer to a string"""
        output = []
        
        for y, line in enumerate(self.lines):
            # Move to line start
            output.append(Cursor.move(0, y))
            
            # Render segments
            for segment in line:
                # Apply styling
                if segment.fg_color:
                    output.append(Color.rgb(*segment.fg_color))
                if segment.bg_color:
                    output.append(Color.bg_rgb(*segment.bg_color))
                if segment.bold:
                    output.append(Color.bold())
                if segment.italic:
                    output.append(Color.italic())
                if segment.underline:
                    output.append(Color.underline())
                
                # Write text
                output.append(segment.text)
                
                # Reset after segment
                output.append(Color.reset())
        
        return ''.join(output)

# ============================================================================
# MENU BAR
# ============================================================================

@dataclass
class MenuItem:
    """A menu item"""
    label: str
    callback: Optional[Callable] = None
    shortcut: Optional[str] = None
    enabled: bool = True

class MenuBar:
    """Persistent menu bar at top of screen"""
    
    def __init__(self, width: int):
        self.width = width
        self.height = Config.MENU_HEIGHT
        self.visible = Config.MENU_ALWAYS_VISIBLE
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.buffer = TextBuffer(width, self.height)
        self.initialize_menu()
    
    def initialize_menu(self):
        """Initialize menu items"""
        self.items = [
            MenuItem("File", shortcut="F1"),
            MenuItem("Edit", shortcut="F2"),
            MenuItem("View", shortcut="F3"),
            MenuItem("Tools", shortcut="F4"),
            MenuItem("Help", shortcut="F5"),
        ]
    
    def show(self):
        """Show menu bar"""
        self.visible = True
    
    def hide(self):
        """Hide menu bar"""
        self.visible = False
    
    def toggle(self):
        """Toggle menu visibility"""
        self.visible = not self.visible
    
    def resize(self, width: int):
        """Resize menu bar"""
        self.width = width
        self.buffer.resize(width, self.height)
    
    def render(self, time: float) -> List[str]:
        """Render menu bar"""
        if not self.visible:
            return []
        
        output = []
        
        # Draw border
        border_lines = Border.draw_box(
            0, 0, self.width, self.height,
            BorderStyle.GRADIENT,
            Config.THEME['border_primary'],
            Config.THEME['border_secondary'],
            time
        )
        
        for bx, by, btext in border_lines:
            output.append(Cursor.move(bx, by) + btext)
        
        # Draw menu items
        x_offset = 2
        menu_text = ""
        
        for i, item in enumerate(self.items):
            if i == self.selected_index:
                menu_text += Color.rgb(*Config.THEME['menu_active'])
                menu_text += Color.bold()
            else:
                menu_text += Color.rgb(*Config.THEME['menu_fg'])
            
            menu_text += f" {item.label} "
            
            if item.shortcut:
                menu_text += Color.dim() + f"({item.shortcut})" + Color.reset()
            
            menu_text += "  "
            x_offset += len(item.label) + 6
        
        output.append(Cursor.move(2, 1) + menu_text + Color.reset())
        
        return output

# ============================================================================
# STATUS BAR
# ============================================================================

class StatusBar:
    """Status bar at bottom of terminal area"""
    
    def __init__(self, width: int):
        self.width = width
        self.height = Config.STATUS_BAR_HEIGHT
        self.buffer = TextBuffer(width, self.height)
        self.info: Dict[str, str] = {}
    
    def set_info(self, key: str, value: str):
        """Set status information"""
        self.info[key] = value
    
    def resize(self, width: int):
        """Resize status bar"""
        self.width = width
        self.buffer.resize(width, self.height)
    
    def render(self, y_position: int, time: float) -> List[str]:
        """Render status bar"""
        output = []
        
        # Draw border
        border_lines = Border.draw_box(
            0, y_position, self.width, self.height,
            BorderStyle.GRADIENT,
            Config.THEME['border_primary'],
            Config.THEME['border_secondary'],
            time
        )
        
        for bx, by, btext in border_lines:
            output.append(Cursor.move(bx, by) + btext)
        
        # Draw status information
        status_text = ""
        for key, value in self.info.items():
            status_text += Color.rgb(*Config.THEME['status_fg'])
            status_text += f" {key}: "
            status_text += Color.bold()
            status_text += value
            status_text += Color.reset()
            status_text += " │ "
        
        if status_text:
            status_text = status_text[:-3]  # Remove last separator
        
        output.append(Cursor.move(2, y_position + 1) + status_text)
        
        return output

# ============================================================================
# AUTOCORRECT PANEL
# ============================================================================

class AutocorrectPanel:
    """Autocorrect/suggestion panel"""
    
    def __init__(self, width: int):
        self.width = width
        self.height = Config.AUTOCORRECT_HEIGHT
        self.visible = True
        self.suggestions: List[str] = []
        self.selected_index = 0
        self.buffer = TextBuffer(width, self.height)
    
    def show(self):
        """Show autocorrect panel"""
        self.visible = True
    
    def hide(self):
        """Hide autocorrect panel"""
        self.visible = False
    
    def toggle(self):
        """Toggle panel visibility"""
        self.visible = not self.visible
    
    def set_suggestions(self, suggestions: List[str]):
        """Set suggestions"""
        self.suggestions = suggestions[:Config.AUTOCORRECT_MAX_SUGGESTIONS]
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
    
    def resize(self, width: int):
        """Resize panel"""
        self.width = width
        self.buffer.resize(width, self.height)
    
    def render(self, y_position: int, time: float) -> List[str]:
        """Render autocorrect panel"""
        if not self.visible or not self.suggestions:
            return []
        
        output = []
        
        # Draw border
        border_lines = Border.draw_box(
            0, y_position, self.width, self.height,
            BorderStyle.GRADIENT,
            Config.THEME['border_primary'],
            Config.THEME['border_secondary'],
            time
        )
        
        for bx, by, btext in border_lines:
            output.append(Cursor.move(bx, by) + btext)
        
        # Draw title
        title = " Suggestions "
        output.append(
            Cursor.move(2, y_position) +
            Color.rgb(*Config.THEME['autocorrect_fg']) +
            Color.bold() +
            title +
            Color.reset()
        )
        
        # Draw suggestions
        x_offset = 2
        for i, suggestion in enumerate(self.suggestions[:self.width // 15]):
            if i == self.selected_index:
                color = Config.THEME['autocorrect_selected']
                text = Color.rgb(*color) + Color.bold() + f"[{suggestion}]" + Color.reset()
            else:
                color = Config.THEME['autocorrect_fg']
                text = Color.rgb(*color) + suggestion + Color.reset()
            
            output.append(Cursor.move(x_offset, y_position + 1) + text)
            x_offset += len(suggestion) + 4
            
            if x_offset >= self.width - 10:
                break
        
        return output

# ============================================================================
# COMMAND HISTORY
# ============================================================================

class CommandHistory:
    """Command history management"""
    
    def __init__(self, max_size: int = Config.HISTORY_SIZE):
        self.max_size = max_size
        self.commands: deque = deque(maxlen=max_size)
        self.current_index = -1
        self.temp_command = ""
    
    def add(self, command: str):
        """Add command to history"""
        if command and (not self.commands or self.commands[-1] != command):
            self.commands.append(command)
        self.current_index = len(self.commands)
        self.temp_command = ""
    
    def get_prev(self, current: str) -> Optional[str]:
        """Get previous command"""
        if not self.commands:
            return None
        
        if self.current_index == len(self.commands):
            self.temp_command = current
        
        if self.current_index > 0:
            self.current_index -= 1
            return self.commands[self.current_index]
        
        return self.commands[0] if self.commands else None
    
    def get_next(self) -> Optional[str]:
        """Get next command"""
        if not self.commands:
            return None
        
        if self.current_index < len(self.commands):
            self.current_index += 1
            
            if self.current_index >= len(self.commands):
                return self.temp_command
            else:
                return self.commands[self.current_index]
        
        return self.temp_command
    
    def reset(self):
        """Reset history navigation"""
        self.current_index = len(self.commands)
        self.temp_command = ""
    
    def search(self, query: str) -> List[str]:
        """Search history for commands matching query"""
        if not query:
            return []
        
        results = []
        for cmd in reversed(self.commands):
            if query.lower() in cmd.lower():
                results.append(cmd)
                if len(results) >= 10:
                    break
        
        return results

# ============================================================================
# COMMAND AUTOCOMPLETE
# ============================================================================

class Autocompleter:
    """Command and path autocompletion"""
    
    def __init__(self):
        self.commands: List[str] = []
        self.load_commands()
    
    def load_commands(self):
        """Load available commands from PATH"""
        try:
            path_dirs = os.environ.get('PATH', '').split(':')
            commands = set()
            
            for dir_path in path_dirs:
                if os.path.isdir(dir_path):
                    try:
                        for item in os.listdir(dir_path):
                            item_path = os.path.join(dir_path, item)
                            if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                                commands.add(item)
                    except (PermissionError, OSError):
                        pass
            
            self.commands = sorted(commands)
        except Exception:
            self.commands = []
    
    def complete(self, text: str) -> List[str]:
        """Get completions for text"""
        if not text:
            return []
        
        completions = []
        
        # Split into parts
        parts = text.split()
        if not parts:
            return []
        
        # First word - command completion
        if len(parts) == 1:
            prefix = parts[0]
            completions = [cmd for cmd in self.commands if cmd.startswith(prefix)]
        else:
            # Path completion
            last_part = parts[-1]
            completions = self._complete_path(last_part)
        
        return completions[:Config.AUTOCORRECT_MAX_SUGGESTIONS]
    
    def _complete_path(self, partial_path: str) -> List[str]:
        """Complete file/directory paths"""
        try:
            if not partial_path:
                partial_path = "."
            
            # Expand home directory
            partial_path = os.path.expanduser(partial_path)
            
            # Get directory and prefix
            if os.path.isdir(partial_path):
                directory = partial_path
                prefix = ""
            else:
                directory = os.path.dirname(partial_path) or "."
                prefix = os.path.basename(partial_path)
            
            # List matching files
            matches = []
            if os.path.isdir(directory):
                for item in os.listdir(directory):
                    if item.startswith(prefix):
                        full_path = os.path.join(directory, item)
                        if os.path.isdir(full_path):
                            matches.append(item + "/")
                        else:
                            matches.append(item)
            
            return sorted(matches)
        except (PermissionError, OSError):
            return []

# ============================================================================
# TERMINAL OUTPUT BUFFER
# ============================================================================

@dataclass
class OutputLine:
    """A line of terminal output"""
    text: str
    timestamp: float
    type: str = "normal"  # normal, command, error, system
    fg_color: Optional[Tuple[int, int, int]] = None
    bg_color: Optional[Tuple[int, int, int]] = None

class TerminalOutputBuffer:
    """Buffer for terminal output with persistent storage"""
    
    def __init__(self, max_lines: int = Config.MAX_OUTPUT_LINES):
        self.max_lines = max_lines
        self.lines: deque = deque(maxlen=max_lines)
        self.scroll_offset = 0
    
    def add_line(self, text: str, line_type: str = "normal",
                 fg_color: Optional[Tuple[int, int, int]] = None):
        """Add a line to the buffer"""
        line = OutputLine(
            text=text,
            timestamp=time.time(),
            type=line_type,
            fg_color=fg_color
        )
        self.lines.append(line)
        self.scroll_offset = 0  # Reset scroll when new content arrives
    
    def add_command(self, command: str):
        """Add a command line"""
        self.add_line(command, "command", Config.THEME['text_command'])
    
    def add_output(self, text: str):
        """Add command output"""
        for line in text.splitlines():
            self.add_line(line, "normal", Config.THEME['text_output'])
    
    def add_error(self, text: str):
        """Add error message"""
        for line in text.splitlines():
            self.add_line(line, "error", Config.THEME['text_error'])
    
    def scroll_up(self, amount: int = 1):
        """Scroll up in history"""
        self.scroll_offset = min(self.scroll_offset + amount, len(self.lines) - 1)
    
    def scroll_down(self, amount: int = 1):
        """Scroll down in history"""
        self.scroll_offset = max(self.scroll_offset - amount, 0)
    
    def get_visible_lines(self, num_lines: int) -> List[OutputLine]:
        """Get visible lines for display"""
        if not self.lines:
            return []
        
        start_idx = max(0, len(self.lines) - num_lines - self.scroll_offset)
        end_idx = len(self.lines) - self.scroll_offset
        
        return list(self.lines)[start_idx:end_idx]
    
    def clear(self):
        """Clear output buffer"""
        self.lines.clear()
        self.scroll_offset = 0

# ============================================================================
# TERMINAL EMULATOR
# ============================================================================

class TerminalEmulator:
    """Terminal emulator with command execution"""
    
    def __init__(self):
        self.output_buffer = TerminalOutputBuffer()
        self.command_history = CommandHistory()
        self.autocompleter = Autocompleter()
        self.current_command = ""
        self.cursor_position = 0
        self.running_process: Optional[subprocess.Popen] = None
        self.process_lock = threading.Lock()
    
    def set_command(self, command: str):
        """Set current command"""
        self.current_command = command
        self.cursor_position = len(command)
    
    def insert_char(self, char: str):
        """Insert character at cursor position"""
        self.current_command = (
            self.current_command[:self.cursor_position] +
            char +
            self.current_command[self.cursor_position:]
        )
        self.cursor_position += len(char)
    
    def delete_char(self):
        """Delete character before cursor"""
        if self.cursor_position > 0:
            self.current_command = (
                self.current_command[:self.cursor_position-1] +
                self.current_command[self.cursor_position:]
            )
            self.cursor_position -= 1
    
    def delete_forward(self):
        """Delete character at cursor"""
        if self.cursor_position < len(self.current_command):
            self.current_command = (
                self.current_command[:self.cursor_position] +
                self.current_command[self.cursor_position+1:]
            )
    
    def move_cursor_left(self):
        """Move cursor left"""
        if self.cursor_position > 0:
            self.cursor_position -= 1
    
    def move_cursor_right(self):
        """Move cursor right"""
        if self.cursor_position < len(self.current_command):
            self.cursor_position += 1
    
    def move_cursor_home(self):
        """Move cursor to start"""
        self.cursor_position = 0
    
    def move_cursor_end(self):
        """Move cursor to end"""
        self.cursor_position = len(self.current_command)
    
    def move_word_left(self):
        """Move cursor one word left"""
        if self.cursor_position == 0:
            return
        
        # Skip whitespace
        while self.cursor_position > 0 and self.current_command[self.cursor_position-1].isspace():
            self.cursor_position -= 1
        
        # Skip non-whitespace
        while self.cursor_position > 0 and not self.current_command[self.cursor_position-1].isspace():
            self.cursor_position -= 1
    
    def move_word_right(self):
        """Move cursor one word right"""
        if self.cursor_position >= len(self.current_command):
            return
        
        # Skip non-whitespace
        while self.cursor_position < len(self.current_command) and not self.current_command[self.cursor_position].isspace():
            self.cursor_position += 1
        
        # Skip whitespace
        while self.cursor_position < len(self.current_command) and self.current_command[self.cursor_position].isspace():
            self.cursor_position += 1
    
    def delete_line(self):
        """Delete entire line"""
        self.current_command = ""
        self.cursor_position = 0
    
    def delete_word(self):
        """Delete word before cursor"""
        if self.cursor_position == 0:
            return
        
        old_pos = self.cursor_position
        self.move_word_left()
        self.current_command = (
            self.current_command[:self.cursor_position] +
            self.current_command[old_pos:]
        )
    
    def execute_command(self):
        """Execute the current command"""
        if not self.current_command.strip():
            return
        
        # Add to history
        self.command_history.add(self.current_command)
        
        # Add to output buffer
        self.output_buffer.add_command(f"$ {self.current_command}")
        
        # Execute command
        try:
            # Check for built-in commands
            if self.current_command.strip() == "clear":
                self.output_buffer.clear()
            elif self.current_command.strip() == "exit":
                sys.exit(0)
            else:
                # Execute in shell
                result = subprocess.run(
                    self.current_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Add output
                if result.stdout:
                    self.output_buffer.add_output(result.stdout)
                if result.stderr:
                    self.output_buffer.add_error(result.stderr)
                
                # Add return code if non-zero
                if result.returncode != 0:
                    self.output_buffer.add_error(f"[Exit code: {result.returncode}]")
        
        except subprocess.TimeoutExpired:
            self.output_buffer.add_error("Command timed out")
        except Exception as e:
            self.output_buffer.add_error(f"Error: {str(e)}")
        
        # Clear current command
        self.current_command = ""
        self.cursor_position = 0
    
    def get_completions(self) -> List[str]:
        """Get completions for current command"""
        return self.autocompleter.complete(self.current_command)
    
    def history_prev(self):
        """Navigate to previous command in history"""
        cmd = self.command_history.get_prev(self.current_command)
        if cmd is not None:
            self.set_command(cmd)
    
    def history_next(self):
        """Navigate to next command in history"""
        cmd = self.command_history.get_next()
        if cmd is not None:
            self.set_command(cmd)

# ============================================================================
# WELCOME SCREEN
# ============================================================================

class WelcomeScreen:
    """Welcome intro screen"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.shown = False
    
    def render(self, time: float) -> List[str]:
        """Render welcome screen"""
        if self.shown:
            return []
        
        output = []
        
        # Center position
        center_y = self.height // 2
        
        # Title
        title_lines = [
            "╔═══════════════════════════════════════════════════════╗",
            "║                                                       ║",
            "║          ✨ ADVANCED TERMINAL UI ✨                  ║",
            "║                                                       ║",
            "║              With Christmas Magic 🎄                  ║",
            "║                                                       ║",
            "╚═══════════════════════════════════════════════════════╝",
        ]
        
        start_y = center_y - len(title_lines) // 2
        
        for i, line in enumerate(title_lines):
            y = start_y + i
            if 0 <= y < self.height:
                # Gradient color
                t = i / len(title_lines)
                color = Color.gradient(
                    Config.THEME['border_primary'],
                    Config.THEME['border_secondary'],
                    t
                )
                
                # Pulsing effect
                pulse = 0.7 + 0.3 * math.sin(time * 2 + i * 0.5)
                color = tuple(int(c * pulse) for c in color)
                
                # Center the line
                x = (self.width - len(line)) // 2
                output.append(
                    Cursor.move(x, y) +
                    Color.rgb(*color) +
                    Color.bold() +
                    line +
                    Color.reset()
                )
        
        # Instructions
        instructions = [
            "",
            "Press any key to start...",
        ]
        
        for i, line in enumerate(instructions):
            y = start_y + len(title_lines) + 2 + i
            if 0 <= y < self.height:
                x = (self.width - len(line)) // 2
                output.append(
                    Cursor.move(x, y) +
                    Color.rgb(*Config.THEME['text_normal']) +
                    line +
                    Color.reset()
                )
        
        return output
    
    def dismiss(self):
        """Dismiss welcome screen"""
        self.shown = True

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class Application:
    """Main TUI application"""
    
    def __init__(self):
        self.running = False
        self.width = 0
        self.height = 0
        
        # Components
        self.menu_bar: Optional[MenuBar] = None
        self.status_bar: Optional[StatusBar] = None
        self.autocorrect_panel: Optional[AutocorrectPanel] = None
        self.terminal: Optional[TerminalEmulator] = None
        self.welcome_screen: Optional[WelcomeScreen] = None
        self.shader_manager: Optional[ShaderManager] = None
        
        # Advanced systems
        self.render_engine: Optional[RenderEngine] = None
        self.particle_system: Optional[ParticleSystem] = None
        self.theme_manager: Optional[ThemeManager] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.animation_controller: Optional[AnimationController] = None
        self.notification_manager: Optional[NotificationManager] = None
        self.command_executor: Optional[CommandExecutor] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        self.session_manager: Optional[SessionManager] = None
        self.config_manager: Optional[ConfigManager] = None
        self.macro_manager: Optional[MacroManager] = None
        self.search_engine: Optional[SearchEngine] = None
        self.script_engine: Optional[ScriptEngine] = None
        self.tab_manager: Optional[TabManager] = None
        self.clipboard_manager: Optional[ClipboardManager] = None
        
        # State
        self.start_time = 0.0
        self.frame_count = 0
        self.show_welcome = True
        self.input_queue: queue.Queue = queue.Queue()
        self.last_update_time = 0.0
        
        # Terminal state
        self.old_terminal_settings = None
    
    def initialize(self):
        """Initialize the application"""
        # Get terminal size
        self.width, self.height = Screen.get_size()
        
        # Initialize core systems
        self.config_manager = ConfigManager()
        self.config_manager.apply_to_config_class()
        self.theme_manager = ThemeManager()
        self.plugin_manager = PluginManager()
        self.performance_monitor = PerformanceMonitor()
        self.animation_controller = AnimationController()
        self.session_manager = SessionManager()
        self.macro_manager = MacroManager()
        self.search_engine = SearchEngine()
        self.script_engine = ScriptEngine()
        self.tab_manager = TabManager()
        self.clipboard_manager = ClipboardManager()
        
        # Initialize components
        self.menu_bar = MenuBar(self.width)
        self.status_bar = StatusBar(self.width)
        self.autocorrect_panel = AutocorrectPanel(self.width)
        self.terminal = TerminalEmulator()
        self.welcome_screen = WelcomeScreen(self.width, self.height)
        self.shader_manager = ShaderManager()
        self.render_engine = RenderEngine(self.width, self.height)
        self.particle_system = ParticleSystem()
        self.notification_manager = NotificationManager(self.width, self.height)
        self.command_executor = ExtendedCommandExecutor(self)
        
        # Create initial session and tab
        session_id = self.session_manager.create_session("main")
        tab_id = self.tab_manager.create_tab("Terminal", session_id)
        
        # Load built-in plugins
        self.plugin_manager.load_plugin(ClockPlugin())
        self.plugin_manager.load_plugin(WeatherPlugin())
        
        # Load theme from config
        theme_name = self.config_manager.get('theme', 'default')
        self.theme_manager.set_theme(theme_name)
        
        # Create particle emitters for snow effect
        if Config.TREE_ENABLE_SNOW:
            tree_x = int(self.width * Config.TREE_POSITION[0])
            tree_y = int(self.height * Config.TREE_POSITION[1])
            snow_emitter = ParticleEmitter(tree_x, tree_y - 10)
            snow_emitter.particle_life = 5.0
            snow_emitter.particle_color = (255, 255, 255)
            snow_emitter.particle_speed = 2.0
            snow_emitter.gravity = (0.1, 1.0)
            snow_emitter.emission_rate = 5.0
            snow_emitter.spread_angle = 180
            self.particle_system.add_emitter(snow_emitter)
        
        # Setup terminal
        self.setup_terminal()
        
        # Setup signal handlers
        signal.signal(signal.SIGWINCH, self.handle_resize)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)
        
        # Start time
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        # Show welcome notification
        self.notification_manager.add_notification("Welcome to Advanced Terminal UI! 🎄", "success", 5.0)
    
    def setup_terminal(self):
        """Setup terminal for raw input"""
        # Save old settings
        self.old_terminal_settings = termios.tcgetattr(sys.stdin)
        
        # Set raw mode
        tty.setraw(sys.stdin)
        
        # Set non-blocking
        flags = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Switch to alternate screen
        sys.stdout.write(Screen.alternate_screen())
        sys.stdout.write(Cursor.hide())
        sys.stdout.write(Screen.clear())
        sys.stdout.flush()
    
    def restore_terminal(self):
        """Restore terminal to normal mode"""
        if self.old_terminal_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_terminal_settings)
        
        # Restore screen
        sys.stdout.write(Screen.main_screen())
        sys.stdout.write(Cursor.show())
        sys.stdout.write(Color.reset())
        sys.stdout.flush()
    
    def handle_resize(self, signum, frame):
        """Handle terminal resize"""
        self.width, self.height = Screen.get_size()
        
        if self.menu_bar:
            self.menu_bar.resize(self.width)
        if self.status_bar:
            self.status_bar.resize(self.width)
        if self.autocorrect_panel:
            self.autocorrect_panel.resize(self.width)
        if self.welcome_screen:
            self.welcome_screen = WelcomeScreen(self.width, self.height)
        if self.render_engine:
            self.render_engine.resize(self.width, self.height)
        if self.notification_manager:
            self.notification_manager.width = self.width
            self.notification_manager.height = self.height
    
    def handle_exit(self, signum, frame):
        """Handle exit signal"""
        self.running = False
    
    def read_input(self) -> Optional[str]:
        """Read input from terminal (non-blocking)"""
        try:
            # Check if data is available
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if not ready:
                return None
            
            # Read one byte
            char = sys.stdin.read(1)
            if not char:
                return None
            
            # Check for escape sequences
            if char == '\x1b':
                # Read next characters for escape sequence
                seq = char
                for _ in range(10):  # Max escape sequence length
                    ready, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if not ready:
                        break
                    next_char = sys.stdin.read(1)
                    if not next_char:
                        break
                    seq += next_char
                    # Check if we have a complete sequence
                    if next_char in ('~', 'A', 'B', 'C', 'D', 'F', 'H'):
                        break
                return seq
            
            return char
        
        except (IOError, OSError):
            return None
    
    def process_input(self, input_char: str):
        """Process input character"""
        if not input_char:
            return
        
        # Dismiss welcome screen on any key
        if self.show_welcome:
            self.welcome_screen.dismiss()
            self.show_welcome = False
            return
        
        # Check keybindings
        if input_char == Config.KEYBINDINGS['exit']:
            self.running = False
            return
        
        elif input_char == Config.KEYBINDINGS['menu_toggle']:
            if self.menu_bar:
                self.menu_bar.toggle()
            return
        
        elif input_char == Config.KEYBINDINGS['autocorrect_toggle']:
            if self.autocorrect_panel:
                self.autocorrect_panel.toggle()
            return
        
        elif input_char == Config.KEYBINDINGS['clear_screen']:
            if self.terminal:
                self.terminal.output_buffer.clear()
            return
        
        elif input_char == Config.KEYBINDINGS['history_prev']:
            if self.terminal:
                self.terminal.history_prev()
            return
        
        elif input_char == Config.KEYBINDINGS['history_next']:
            if self.terminal:
                self.terminal.history_next()
            return
        
        elif input_char == Config.KEYBINDINGS['cursor_left']:
            if self.terminal:
                self.terminal.move_cursor_left()
            return
        
        elif input_char == Config.KEYBINDINGS['cursor_right']:
            if self.terminal:
                self.terminal.move_cursor_right()
            return
        
        elif input_char == Config.KEYBINDINGS['cursor_home']:
            if self.terminal:
                self.terminal.move_cursor_home()
            return
        
        elif input_char == Config.KEYBINDINGS['cursor_end']:
            if self.terminal:
                self.terminal.move_cursor_end()
            return
        
        elif input_char == Config.KEYBINDINGS['delete_char']:
            if self.terminal:
                self.terminal.delete_char()
            return
        
        elif input_char == Config.KEYBINDINGS['delete_forward']:
            if self.terminal:
                self.terminal.delete_forward()
            return
        
        elif input_char == Config.KEYBINDINGS['word_left']:
            if self.terminal:
                self.terminal.move_word_left()
            return
        
        elif input_char == Config.KEYBINDINGS['word_right']:
            if self.terminal:
                self.terminal.move_word_right()
            return
        
        elif input_char == Config.KEYBINDINGS['line_start']:
            if self.terminal:
                self.terminal.move_cursor_home()
            return
        
        elif input_char == Config.KEYBINDINGS['line_end']:
            if self.terminal:
                self.terminal.move_cursor_end()
            return
        
        elif input_char == Config.KEYBINDINGS['delete_line']:
            if self.terminal:
                self.terminal.delete_line()
            return
        
        elif input_char == Config.KEYBINDINGS['delete_word']:
            if self.terminal:
                self.terminal.delete_word()
            return
        
        elif input_char == '\r' or input_char == '\n':
            # Execute command
            if self.terminal:
                # Parse and check for built-in commands
                command_text = self.terminal.current_command.strip()
                
                if command_text:
                    # Try built-in commands first
                    command = CommandParser.parse(command_text)
                    result = self.command_executor.execute(command)
                    
                    if result is not None:
                        # Built-in command
                        self.terminal.command_history.add(command_text)
                        self.terminal.output_buffer.add_command(f"$ {command_text}")
                        if result:
                            self.terminal.output_buffer.add_output(result)
                        self.terminal.current_command = ""
                        self.terminal.cursor_position = 0
                    else:
                        # Try plugins
                        plugin_result = self.plugin_manager.on_command(command_text)
                        
                        if plugin_result:
                            self.terminal.command_history.add(command_text)
                            self.terminal.output_buffer.add_command(f"$ {command_text}")
                            self.terminal.output_buffer.add_output(plugin_result)
                            self.terminal.current_command = ""
                            self.terminal.cursor_position = 0
                        else:
                            # Hide menu temporarily during command execution
                            if self.menu_bar:
                                self.menu_bar.hide()
                            
                            self.terminal.execute_command()
                            
                            # Show menu after command completes
                            if self.menu_bar and Config.MENU_ALWAYS_VISIBLE:
                                self.menu_bar.show()
            return
        
        elif input_char == Config.KEYBINDINGS['accept_suggestion']:
            # Accept autocomplete suggestion
            if self.autocorrect_panel and self.terminal:
                suggestion = self.autocorrect_panel.get_selected()
                if suggestion:
                    # Replace last word with suggestion
                    parts = self.terminal.current_command.split()
                    if parts:
                        parts[-1] = suggestion
                        self.terminal.set_command(' '.join(parts))
            return
        
        # Regular character input
        if len(input_char) == 1 and ord(input_char) >= 32:
            if self.terminal:
                self.terminal.insert_char(input_char)
                
                # Update autocomplete suggestions
                if self.autocorrect_panel:
                    suggestions = self.terminal.get_completions()
                    self.autocorrect_panel.set_suggestions(suggestions)
    
    def update(self, dt: float):
        """Update application state"""
        # Update animations
        if self.animation_controller:
            self.animation_controller.update(dt)
        
        # Update particles
        if self.particle_system:
            self.particle_system.update(dt)
        
        # Update notifications
        if self.notification_manager:
            self.notification_manager.update()
    
    def render_frame(self):
        """Render a single frame"""
        render_start = time.time()
        current_time = time.time() - self.start_time
        
        # Calculate delta time
        dt = current_time - (self.last_update_time - self.start_time)
        self.last_update_time = time.time()
        
        # Update systems
        update_start = time.time()
        self.update(dt)
        update_time = time.time() - update_start
        if self.performance_monitor:
            self.performance_monitor.record_update_time(update_time)
        
        # Build output buffer
        output = []
        
        # Clear screen
        output.append(Screen.clear())
        output.append(Cursor.move(0, 0))
        
        # Show welcome screen if needed
        if self.show_welcome:
            output.extend(self.welcome_screen.render(current_time))
            
            # Write output
            sys.stdout.write(''.join(output))
            sys.stdout.flush()
            return
        
        # Calculate layout
        menu_height = self.menu_bar.height if self.menu_bar and self.menu_bar.visible else 0
        status_height = self.status_bar.height
        autocorrect_height = self.autocorrect_panel.height if self.autocorrect_panel and self.autocorrect_panel.visible else 0
        
        terminal_start_y = menu_height
        terminal_height = self.height - menu_height - status_height - autocorrect_height
        
        status_y = self.height - status_height - autocorrect_height
        autocorrect_y = self.height - autocorrect_height
        
        # Render parallax background (layer 0)
        if self.shader_manager and Config.ENABLE_SHADERS:
            parallax_shader = self.shader_manager.get_shader(ShaderType.PARALLAX)
            if parallax_shader:
                # Render parallax at low resolution for performance
                sample_step = 2
                for y in range(0, self.height, sample_step):
                    for x in range(0, self.width, sample_step):
                        shader_input = ShaderInput(
                            time=current_time,
                            resolution=(self.width, self.height),
                            position=(x, y)
                        )
                        r, g, b, a = parallax_shader.execute(shader_input)
                        
                        if a > 10:  # Only draw if visible
                            output.append(Cursor.move(x, y))
                            output.append(Color.rgb(r, g, b))
                            output.append('·')
        
        # Render Christmas tree
        if self.shader_manager and Config.ENABLE_SHADERS and Config.TREE_ENABLE_3D:
            tree_shader = self.shader_manager.get_shader(ShaderType.CHRISTMAS_TREE)
            snow_shader = self.shader_manager.get_shader(ShaderType.SNOW)
            
            # Render tree in its area
            tree_center_x = int(self.width * Config.TREE_POSITION[0])
            tree_center_y = int(self.height * Config.TREE_POSITION[1])
            tree_radius = int(min(self.width, self.height) * Config.TREE_SIZE)
            
            for y in range(max(0, tree_center_y - tree_radius), min(self.height, tree_center_y + tree_radius)):
                for x in range(max(0, tree_center_x - tree_radius), min(self.width, tree_center_x + tree_radius)):
                    # Don't draw over menu or status bars
                    if y < menu_height or y >= self.height - status_height - autocorrect_height:
                        continue
                    
                    shader_input = ShaderInput(
                        time=current_time,
                        resolution=(self.width, self.height),
                        position=(x, y)
                    )
                    
                    # Tree
                    r, g, b, a = tree_shader.execute(shader_input)
                    if a > 128:
                        output.append(Cursor.move(x, y))
                        output.append(Color.rgb(r, g, b))
                        output.append('█')
                        continue
                    
                    # Snow
                    if snow_shader:
                        r, g, b, a = snow_shader.execute(shader_input)
                        if a > 128:
                            output.append(Cursor.move(x, y))
                            output.append(Color.rgb(r, g, b))
                            output.append('*')
        
        # Render menu bar
        if self.menu_bar and self.menu_bar.visible:
            output.extend(self.menu_bar.render(current_time))
        
        # Render terminal output with borders
        if self.terminal and terminal_height > 4:
            # Draw border around terminal area
            border_lines = Border.draw_box(
                0, terminal_start_y, self.width, terminal_height,
                BorderStyle.GRADIENT,
                Config.THEME['border_primary'],
                Config.THEME['border_secondary'],
                current_time
            )
            output.extend([Cursor.move(bx, by) + btext for bx, by, btext in border_lines])
            
            # Get visible output lines
            visible_lines = self.terminal.output_buffer.get_visible_lines(terminal_height - 4)
            
            # Render output lines with individual borders
            for i, line in enumerate(visible_lines):
                y = terminal_start_y + 2 + i
                if y >= terminal_start_y + terminal_height - 2:
                    break
                
                # Draw line with border
                line_text = line.text[:self.width - 6]  # Leave space for borders
                
                output.append(Cursor.move(2, y))
                if line.fg_color:
                    output.append(Color.rgb(*line.fg_color))
                output.append(line_text)
                output.append(Color.reset())
            
            # Render command prompt
            prompt_y = terminal_start_y + terminal_height - 2
            output.append(Cursor.move(2, prompt_y))
            output.append(Color.rgb(*Config.THEME['text_command']))
            output.append(Color.bold())
            output.append("$ ")
            output.append(Color.reset())
            
            # Render command with cursor
            if self.terminal.current_command:
                before_cursor = self.terminal.current_command[:self.terminal.cursor_position]
                at_cursor = self.terminal.current_command[self.terminal.cursor_position:self.terminal.cursor_position+1] or " "
                after_cursor = self.terminal.current_command[self.terminal.cursor_position+1:]
                
                output.append(Color.rgb(*Config.THEME['text_normal']))
                output.append(before_cursor)
                output.append(Color.rgb(*Config.THEME['cursor']))
                output.append(Color.reverse())
                output.append(at_cursor)
                output.append(Color.reset())
                output.append(Color.rgb(*Config.THEME['text_normal']))
                output.append(after_cursor)
            else:
                # Show cursor
                output.append(Color.rgb(*Config.THEME['cursor']))
                output.append(Color.reverse())
                output.append(" ")
            
            output.append(Color.reset())
        
        # Render particles
        if self.particle_system:
            output.extend(self.particle_system.render(self.width, self.height))
        
        # Render plugin content
        if self.plugin_manager:
            plugin_context = {
                'width': self.width,
                'height': self.height,
                'time': current_time,
            }
            output.extend(self.plugin_manager.on_render(plugin_context))
        
        # Render status bar
        if self.status_bar:
            # Update status info
            fps = self.performance_monitor.get_fps() if self.performance_monitor else 0
            self.status_bar.set_info("Time", datetime.now().strftime("%H:%M:%S"))
            self.status_bar.set_info("Lines", str(len(self.terminal.output_buffer.lines)))
            self.status_bar.set_info("FPS", f"{fps:.1f}")
            self.status_bar.set_info("Theme", self.theme_manager.current_theme_name if self.theme_manager else "default")
            
            output.extend(self.status_bar.render(status_y, current_time))
        
        # Render autocorrect panel
        if self.autocorrect_panel and self.autocorrect_panel.visible:
            output.extend(self.autocorrect_panel.render(autocorrect_y, current_time))
        
        # Render notifications
        if self.notification_manager:
            output.extend(self.notification_manager.render(current_time))
        
        # Write output
        sys.stdout.write(''.join(output))
        sys.stdout.flush()
        
        # Record frame time
        render_time = time.time() - render_start
        if self.performance_monitor:
            self.performance_monitor.record_render_time(render_time)
        
        self.frame_count += 1
    
    def run(self):
        """Main application loop"""
        self.running = True
        
        try:
            while self.running:
                if self.performance_monitor:
                    self.performance_monitor.start_frame()
                
                frame_start = time.time()
                
                # Process input (multiple keys per frame for responsiveness)
                for _ in range(10):  # Process up to 10 keys per frame
                    input_char = self.read_input()
                    if input_char:
                        # Check if plugin handles it
                        if self.plugin_manager and self.plugin_manager.on_input(input_char):
                            continue
                        self.process_input(input_char)
                    else:
                        break
                
                # Render frame
                self.render_frame()
                
                if self.performance_monitor:
                    self.performance_monitor.end_frame()
                
                # Frame timing
                frame_time = time.time() - frame_start
                sleep_time = max(0, Config.FRAME_TIME - frame_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            pass
        except Exception as e:
            # Log error
            error_log = '/tmp/tui_error.log'
            try:
                with open(error_log, 'a') as f:
                    f.write(f"\n\n=== Error at {datetime.now()} ===\n")
                    f.write(traceback.format_exc())
                    f.write(f"\n")
            except:
                pass
        finally:
            self.restore_terminal()
    
    def cleanup(self):
        """Cleanup resources"""
        self.restore_terminal()

# ============================================================================
# ADVANCED RENDERING ENGINE
# ============================================================================

class RenderLayer:
    """Represents a rendering layer"""
    
    def __init__(self, z_index: int, name: str):
        self.z_index = z_index
        self.name = name
        self.visible = True
        self.opacity = 1.0
        self.blend_mode = 'normal'  # normal, add, multiply, screen
        self.elements: List[Callable] = []
    
    def add_element(self, render_func: Callable):
        """Add a renderable element to this layer"""
        self.elements.append(render_func)
    
    def render(self, context: Dict[str, Any]) -> List[str]:
        """Render all elements in this layer"""
        if not self.visible:
            return []
        
        output = []
        for element in self.elements:
            try:
                result = element(context)
                if result:
                    output.extend(result)
            except Exception as e:
                # Log but don't crash
                pass
        
        return output

class RenderEngine:
    """Advanced multi-layer rendering engine"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers: Dict[int, RenderLayer] = {}
        self.framebuffer: List[List[Tuple[int, int, int]]] = []
        self.initialize_framebuffer()
    
    def initialize_framebuffer(self):
        """Initialize framebuffer"""
        self.framebuffer = [
            [(0, 0, 0) for _ in range(self.width)]
            for _ in range(self.height)
        ]
    
    def add_layer(self, layer: RenderLayer):
        """Add a rendering layer"""
        self.layers[layer.z_index] = layer
    
    def get_layer(self, z_index: int) -> Optional[RenderLayer]:
        """Get layer by z-index"""
        return self.layers.get(z_index)
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render all layers"""
        output = []
        
        # Sort layers by z-index
        sorted_layers = sorted(self.layers.values(), key=lambda l: l.z_index)
        
        # Render each layer
        for layer in sorted_layers:
            layer_output = layer.render(context)
            output.extend(layer_output)
        
        return ''.join(output)
    
    def resize(self, width: int, height: int):
        """Resize rendering surface"""
        self.width = width
        self.height = height
        self.initialize_framebuffer()
    
    def clear(self):
        """Clear framebuffer"""
        self.initialize_framebuffer()
    
    def blend_color(self, base: Tuple[int, int, int], overlay: Tuple[int, int, int], 
                   alpha: float, mode: str = 'normal') -> Tuple[int, int, int]:
        """Blend two colors with various blend modes"""
        alpha = clamp(alpha, 0.0, 1.0)
        
        if mode == 'normal':
            return (
                int(base[0] * (1 - alpha) + overlay[0] * alpha),
                int(base[1] * (1 - alpha) + overlay[1] * alpha),
                int(base[2] * (1 - alpha) + overlay[2] * alpha)
            )
        elif mode == 'add':
            return (
                min(255, int(base[0] + overlay[0] * alpha)),
                min(255, int(base[1] + overlay[1] * alpha)),
                min(255, int(base[2] + overlay[2] * alpha))
            )
        elif mode == 'multiply':
            return (
                int(base[0] * overlay[0] / 255 * alpha + base[0] * (1 - alpha)),
                int(base[1] * overlay[1] / 255 * alpha + base[1] * (1 - alpha)),
                int(base[2] * overlay[2] / 255 * alpha + base[2] * (1 - alpha))
            )
        elif mode == 'screen':
            return (
                int(255 - (255 - base[0]) * (255 - overlay[0]) / 255 * alpha),
                int(255 - (255 - base[1]) * (255 - overlay[1]) / 255 * alpha),
                int(255 - (255 - base[2]) * (255 - overlay[2]) / 255 * alpha)
            )
        else:
            return base

# ============================================================================
# PARTICLE SYSTEM
# ============================================================================

@dataclass
class Particle:
    """A single particle"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    char: str = '•'

class ParticleEmitter:
    """Particle emitter"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.particles: List[Particle] = []
        self.emission_rate = 10.0  # particles per second
        self.emission_timer = 0.0
        self.active = True
        
        # Particle properties
        self.particle_life = 2.0
        self.particle_life_variation = 0.5
        self.particle_speed = 5.0
        self.particle_speed_variation = 2.0
        self.particle_color = (255, 255, 255)
        self.particle_size = 1.0
        self.gravity = (0.0, 0.5)
        self.spread_angle = 360.0
    
    def update(self, dt: float):
        """Update particles"""
        if not self.active:
            return
        
        # Emit new particles
        self.emission_timer += dt
        particles_to_emit = int(self.emission_timer * self.emission_rate)
        self.emission_timer -= particles_to_emit / self.emission_rate
        
        for _ in range(particles_to_emit):
            self.emit_particle()
        
        # Update existing particles
        particles_to_remove = []
        for particle in self.particles:
            particle.life -= dt
            
            if particle.life <= 0:
                particles_to_remove.append(particle)
                continue
            
            # Update position
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            
            # Apply gravity
            particle.vx += self.gravity[0] * dt
            particle.vy += self.gravity[1] * dt
        
        # Remove dead particles
        for particle in particles_to_remove:
            self.particles.remove(particle)
    
    def emit_particle(self):
        """Emit a single particle"""
        # Random angle
        angle = random.uniform(0, self.spread_angle) * math.pi / 180.0
        
        # Random speed
        speed = self.particle_speed + random.uniform(-self.particle_speed_variation, self.particle_speed_variation)
        
        # Velocity
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Life
        life = self.particle_life + random.uniform(-self.particle_life_variation, self.particle_life_variation)
        
        particle = Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=life,
            max_life=life,
            color=self.particle_color,
            size=self.particle_size
        )
        
        self.particles.append(particle)
    
    def render(self, width: int, height: int) -> List[Tuple[int, int, str, Tuple[int, int, int]]]:
        """Render particles"""
        rendered = []
        
        for particle in self.particles:
            x = int(particle.x)
            y = int(particle.y)
            
            if 0 <= x < width and 0 <= y < height:
                # Fade based on life
                alpha = particle.life / particle.max_life
                color = tuple(int(c * alpha) for c in particle.color)
                rendered.append((x, y, particle.char, color))
        
        return rendered

class ParticleSystem:
    """Manages multiple particle emitters"""
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
    
    def add_emitter(self, emitter: ParticleEmitter):
        """Add a particle emitter"""
        self.emitters.append(emitter)
    
    def remove_emitter(self, emitter: ParticleEmitter):
        """Remove a particle emitter"""
        if emitter in self.emitters:
            self.emitters.remove(emitter)
    
    def update(self, dt: float):
        """Update all emitters"""
        for emitter in self.emitters:
            emitter.update(dt)
    
    def render(self, width: int, height: int) -> List[str]:
        """Render all particles"""
        output = []
        
        # Collect all particles
        all_particles = []
        for emitter in self.emitters:
            all_particles.extend(emitter.render(width, height))
        
        # Render particles
        for x, y, char, color in all_particles:
            output.append(Cursor.move(x, y))
            output.append(Color.rgb(*color))
            output.append(char)
        
        return output

# ============================================================================
# THEME SYSTEM
# ============================================================================

class Theme:
    """Color theme"""
    
    def __init__(self, name: str):
        self.name = name
        self.colors: Dict[str, Tuple[int, int, int]] = {}
    
    def set_color(self, name: str, color: Tuple[int, int, int]):
        """Set a color"""
        self.colors[name] = color
    
    def get_color(self, name: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get a color"""
        return self.colors.get(name, default)

class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme_name = "default"
        self.initialize_themes()
    
    def initialize_themes(self):
        """Initialize built-in themes"""
        # Default theme
        default = Theme("default")
        default.colors = Config.THEME.copy()
        self.themes["default"] = default
        
        # Dark theme
        dark = Theme("dark")
        dark.colors = {
            'menu_bg': (10, 10, 15),
            'menu_fg': (180, 180, 200),
            'menu_active': (80, 150, 255),
            'status_bg': (8, 8, 12),
            'status_fg': (160, 160, 180),
            'border_primary': (60, 80, 150),
            'border_secondary': (80, 60, 150),
            'text_normal': (200, 200, 210),
            'text_command': (80, 255, 150),
            'text_output': (180, 190, 200),
            'text_error': (255, 80, 80),
            'cursor': (0, 230, 180),
            'selection': (40, 60, 90),
            'autocorrect_bg': (15, 15, 25),
            'autocorrect_fg': (160, 180, 200),
            'autocorrect_selected': (255, 180, 80),
        }
        self.themes["dark"] = dark
        
        # Light theme
        light = Theme("light")
        light.colors = {
            'menu_bg': (240, 240, 245),
            'menu_fg': (40, 40, 60),
            'menu_active': (20, 100, 200),
            'status_bg': (235, 235, 240),
            'status_fg': (50, 50, 70),
            'border_primary': (100, 120, 200),
            'border_secondary': (150, 100, 200),
            'text_normal': (30, 30, 40),
            'text_command': (20, 150, 80),
            'text_output': (40, 40, 50),
            'text_error': (200, 40, 40),
            'cursor': (0, 180, 140),
            'selection': (180, 200, 230),
            'autocorrect_bg': (230, 235, 245),
            'autocorrect_fg': (50, 60, 80),
            'autocorrect_selected': (200, 140, 20),
        }
        self.themes["light"] = light
        
        # Christmas theme
        christmas = Theme("christmas")
        christmas.colors = {
            'menu_bg': (180, 20, 20),
            'menu_fg': (255, 240, 220),
            'menu_active': (255, 215, 0),
            'status_bg': (20, 120, 40),
            'status_fg': (240, 240, 250),
            'border_primary': (200, 40, 40),
            'border_secondary': (40, 180, 60),
            'text_normal': (240, 240, 250),
            'text_command': (100, 255, 150),
            'text_output': (230, 230, 240),
            'text_error': (255, 100, 100),
            'cursor': (255, 215, 0),
            'selection': (120, 40, 40),
            'autocorrect_bg': (150, 30, 30),
            'autocorrect_fg': (240, 230, 220),
            'autocorrect_selected': (255, 215, 0),
        }
        self.themes["christmas"] = christmas
        
        # Cyberpunk theme
        cyberpunk = Theme("cyberpunk")
        cyberpunk.colors = {
            'menu_bg': (10, 0, 25),
            'menu_fg': (0, 255, 255),
            'menu_active': (255, 0, 255),
            'status_bg': (5, 0, 20),
            'status_fg': (255, 0, 255),
            'border_primary': (0, 255, 255),
            'border_secondary': (255, 0, 255),
            'text_normal': (0, 255, 200),
            'text_command': (255, 0, 255),
            'text_output': (0, 255, 255),
            'text_error': (255, 0, 100),
            'cursor': (255, 255, 0),
            'selection': (100, 0, 100),
            'autocorrect_bg': (20, 0, 40),
            'autocorrect_fg': (0, 255, 200),
            'autocorrect_selected': (255, 255, 0),
        }
        self.themes["cyberpunk"] = cyberpunk
    
    def add_theme(self, theme: Theme):
        """Add a custom theme"""
        self.themes[theme.name] = theme
    
    def set_theme(self, name: str) -> bool:
        """Set the current theme"""
        if name in self.themes:
            self.current_theme_name = name
            # Update Config.THEME
            Config.THEME = self.themes[name].colors.copy()
            return True
        return False
    
    def get_current_theme(self) -> Theme:
        """Get current theme"""
        return self.themes[self.current_theme_name]
    
    def list_themes(self) -> List[str]:
        """List available themes"""
        return list(self.themes.keys())

# ============================================================================
# PLUGIN SYSTEM
# ============================================================================

class Plugin:
    """Base plugin class"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.enabled = True
    
    def on_load(self):
        """Called when plugin is loaded"""
        pass
    
    def on_unload(self):
        """Called when plugin is unloaded"""
        pass
    
    def on_command(self, command: str) -> Optional[str]:
        """Called when a command is executed"""
        return None
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Called during rendering"""
        return []
    
    def on_input(self, key: str) -> bool:
        """Called on input. Return True to consume input."""
        return False

class PluginManager:
    """Manages plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    def load_plugin(self, plugin: Plugin):
        """Load a plugin"""
        self.plugins[plugin.name] = plugin
        plugin.on_load()
    
    def unload_plugin(self, name: str):
        """Unload a plugin"""
        if name in self.plugins:
            self.plugins[name].on_unload()
            del self.plugins[name]
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List loaded plugins"""
        return list(self.plugins.keys())
    
    def on_command(self, command: str) -> Optional[str]:
        """Notify plugins of command"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                result = plugin.on_command(command)
                if result:
                    return result
        return None
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Collect render output from plugins"""
        output = []
        for plugin in self.plugins.values():
            if plugin.enabled:
                output.extend(plugin.on_render(context))
        return output
    
    def on_input(self, key: str) -> bool:
        """Notify plugins of input"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                if plugin.on_input(key):
                    return True
        return False

# ============================================================================
# BUILT-IN PLUGINS
# ============================================================================

class ClockPlugin(Plugin):
    """Digital clock plugin"""
    
    def __init__(self):
        super().__init__("clock", "1.0")
        self.position = (0.95, 0.05)
        self.format = "%H:%M:%S"
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Render clock"""
        time_str = datetime.now().strftime(self.format)
        width = context.get('width', 80)
        height = context.get('height', 24)
        
        x = int(width * self.position[0]) - len(time_str)
        y = int(height * self.position[1])
        
        output = []
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(100, 200, 255))
        output.append(Color.bold())
        output.append(time_str)
        output.append(Color.reset())
        
        return output

class WeatherPlugin(Plugin):
    """Weather display plugin (mock)"""
    
    def __init__(self):
        super().__init__("weather", "1.0")
        self.position = (0.05, 0.05)
        self.weather = "❄️  -5°C"
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Render weather"""
        width = context.get('width', 80)
        height = context.get('height', 24)
        
        x = int(width * self.position[0])
        y = int(height * self.position[1])
        
        output = []
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(150, 220, 255))
        output.append(self.weather)
        output.append(Color.reset())
        
        return output

class SystemInfoPlugin(Plugin):
    """System information plugin"""
    
    def __init__(self):
        super().__init__("sysinfo", "1.0")
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle sysinfo command"""
        if command.strip() == "sysinfo":
            import platform
            import psutil
            
            info = []
            info.append(f"System: {platform.system()} {platform.release()}")
            info.append(f"Python: {platform.python_version()}")
            info.append(f"CPU: {psutil.cpu_percent()}%")
            info.append(f"Memory: {psutil.virtual_memory().percent}%")
            
            return "\n".join(info)
        
        return None

class CalculatorPlugin(Plugin):
    """Simple calculator plugin"""
    
    def __init__(self):
        super().__init__("calculator", "1.0")
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle calc command"""
        if command.strip().startswith("calc "):
            expression = command.strip()[5:]
            try:
                # Safe eval with limited scope
                result = eval(expression, {"__builtins__": {}}, {
                    "abs": abs,
                    "max": max,
                    "min": min,
                    "pow": pow,
                    "round": round,
                    "sum": sum,
                })
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return None

# ============================================================================
# ADVANCED TEXT RENDERING
# ============================================================================

class TextRenderer:
    """Advanced text rendering with effects"""
    
    @staticmethod
    def render_text_with_shadow(text: str, x: int, y: int, 
                               color: Tuple[int, int, int],
                               shadow_color: Tuple[int, int, int] = (0, 0, 0),
                               shadow_offset: Tuple[int, int] = (1, 1)) -> List[str]:
        """Render text with shadow"""
        output = []
        
        # Shadow
        output.append(Cursor.move(x + shadow_offset[0], y + shadow_offset[1]))
        output.append(Color.rgb(*shadow_color))
        output.append(text)
        
        # Main text
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(*color))
        output.append(text)
        output.append(Color.reset())
        
        return output
    
    @staticmethod
    def render_gradient_text(text: str, x: int, y: int,
                           color1: Tuple[int, int, int],
                           color2: Tuple[int, int, int]) -> List[str]:
        """Render text with gradient"""
        output = []
        output.append(Cursor.move(x, y))
        
        for i, char in enumerate(text):
            t = i / max(len(text) - 1, 1)
            color = Color.gradient(color1, color2, t)
            output.append(Color.rgb(*color))
            output.append(char)
        
        output.append(Color.reset())
        return output
    
    @staticmethod
    def render_rainbow_text(text: str, x: int, y: int, time_offset: float = 0) -> List[str]:
        """Render rainbow text"""
        output = []
        output.append(Cursor.move(x, y))
        
        for i, char in enumerate(text):
            hue = (i * 30 + time_offset * 100) % 360
            r, g, b = TextRenderer._hsv_to_rgb(hue, 1.0, 1.0)
            output.append(Color.rgb(int(r * 255), int(g * 255), int(b * 255)))
            output.append(char)
        
        output.append(Color.reset())
        return output
    
    @staticmethod
    def render_glitch_text(text: str, x: int, y: int, intensity: float = 0.5) -> List[str]:
        """Render glitched text"""
        output = []
        
        # Main text
        output.append(Cursor.move(x, y))
        
        for char in text:
            if random.random() < intensity * 0.1:
                # Glitch character
                glitch_char = random.choice(['█', '▓', '▒', '░', '▄', '▀'])
                r = random.randint(100, 255)
                g = random.randint(0, 100)
                b = random.randint(100, 255)
                output.append(Color.rgb(r, g, b))
                output.append(glitch_char)
            else:
                output.append(char)
        
        output.append(Color.reset())
        
        # Glitch artifacts
        if random.random() < intensity * 0.2:
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-1, 1)
            output.append(Cursor.move(x + offset_x, y + offset_y))
            output.append(Color.rgb(255, 0, 0))
            output.append(text[:len(text)//2])
        
        return output
    
    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
        """Convert HSV to RGB"""
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
        
        return (r + m, g + m, b + m)

# ============================================================================
# ANIMATION SYSTEM
# ============================================================================

class Animation:
    """Base animation class"""
    
    def __init__(self, duration: float, loop: bool = False):
        self.duration = duration
        self.loop = loop
        self.elapsed = 0.0
        self.finished = False
    
    def update(self, dt: float) -> float:
        """Update animation and return progress (0-1)"""
        self.elapsed += dt
        
        if self.elapsed >= self.duration:
            if self.loop:
                self.elapsed = self.elapsed % self.duration
            else:
                self.elapsed = self.duration
                self.finished = True
        
        return self.elapsed / self.duration
    
    def reset(self):
        """Reset animation"""
        self.elapsed = 0.0
        self.finished = False

class EasingFunction:
    """Easing functions for animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        else:
            return -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        t -= 1
        return t * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        if t < 0.5:
            return 4 * t * t * t
        else:
            t -= 1
            return 1 + 4 * t * t * t
    
    @staticmethod
    def bounce(t: float) -> float:
        if t < 0.5:
            return 8 * (1 - t) * (1 - t) * t
        else:
            return 8 * t * t * (1 - t)
    
    @staticmethod
    def elastic(t: float) -> float:
        if t == 0 or t == 1:
            return t
        return pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1

class AnimationController:
    """Controls multiple animations"""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
    
    def add_animation(self, name: str, animation: Animation):
        """Add an animation"""
        self.animations[name] = animation
    
    def remove_animation(self, name: str):
        """Remove an animation"""
        if name in self.animations:
            del self.animations[name]
    
    def update(self, dt: float):
        """Update all animations"""
        finished = []
        
        for name, animation in self.animations.items():
            animation.update(dt)
            if animation.finished:
                finished.append(name)
        
        # Remove finished non-looping animations
        for name in finished:
            if not self.animations[name].loop:
                del self.animations[name]
    
    def get_progress(self, name: str) -> float:
        """Get animation progress"""
        if name in self.animations:
            return self.animations[name].elapsed / self.animations[name].duration
        return 0.0

# ============================================================================
# NOTIFICATION SYSTEM
# ============================================================================

@dataclass
class Notification:
    """A notification message"""
    message: str
    type: str  # info, warning, error, success
    duration: float
    created_at: float
    x: int = 0
    y: int = 0

class NotificationManager:
    """Manages notification messages"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.notifications: deque = deque(maxlen=5)
        self.position = (0.7, 0.1)  # Right side, near top
    
    def add_notification(self, message: str, notification_type: str = "info", duration: float = 3.0):
        """Add a notification"""
        notification = Notification(
            message=message,
            type=notification_type,
            duration=duration,
            created_at=time.time()
        )
        self.notifications.append(notification)
    
    def update(self):
        """Update notifications (remove expired)"""
        current_time = time.time()
        expired = []
        
        for notification in self.notifications:
            if current_time - notification.created_at > notification.duration:
                expired.append(notification)
        
        for notification in expired:
            self.notifications.remove(notification)
    
    def render(self, current_time: float) -> List[str]:
        """Render notifications"""
        output = []
        
        start_x = int(self.width * self.position[0])
        start_y = int(self.height * self.position[1])
        
        for i, notification in enumerate(self.notifications):
            y = start_y + i * 3
            
            # Fade out effect
            age = current_time - notification.created_at
            alpha = 1.0 if age < notification.duration - 0.5 else (notification.duration - age) / 0.5
            
            # Color based on type
            if notification.type == "error":
                color = (255, 100, 100)
            elif notification.type == "warning":
                color = (255, 200, 100)
            elif notification.type == "success":
                color = (100, 255, 150)
            else:
                color = (150, 200, 255)
            
            # Apply alpha
            color = tuple(int(c * alpha) for c in color)
            
            # Draw border
            border_width = len(notification.message) + 4
            border_lines = Border.draw_box(
                start_x, y, border_width, 3,
                BorderStyle.SIMPLE,
                color, color,
                current_time
            )
            output.extend([Cursor.move(bx, by) + btext for bx, by, btext in border_lines])
            
            # Draw message
            output.append(Cursor.move(start_x + 2, y + 1))
            output.append(Color.rgb(*color))
            output.append(notification.message)
            output.append(Color.reset())
        
        return output

# ============================================================================
# COMMAND PARSER AND EXECUTOR
# ============================================================================

class Command:
    """Represents a parsed command"""
    
    def __init__(self, name: str, args: List[str], kwargs: Dict[str, str]):
        self.name = name
        self.args = args
        self.kwargs = kwargs

class CommandParser:
    """Parses command strings"""
    
    @staticmethod
    def parse(command_string: str) -> Command:
        """Parse a command string"""
        parts = command_string.strip().split()
        
        if not parts:
            return Command("", [], {})
        
        name = parts[0]
        args = []
        kwargs = {}
        
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                kwargs[key] = value
            else:
                args.append(part)
        
        return Command(name, args, kwargs)

class CommandExecutor:
    """Executes built-in commands"""
    
    def __init__(self, app: 'Application'):
        self.app = app
        self.commands: Dict[str, Callable] = {}
        self.register_builtin_commands()
    
    def register_builtin_commands(self):
        """Register built-in commands"""
        self.commands['help'] = self.cmd_help
        self.commands['clear'] = self.cmd_clear
        self.commands['exit'] = self.cmd_exit
        self.commands['theme'] = self.cmd_theme
        self.commands['plugin'] = self.cmd_plugin
        self.commands['keybinds'] = self.cmd_keybinds
        self.commands['about'] = self.cmd_about
        self.commands['time'] = self.cmd_time
        self.commands['history'] = self.cmd_history
        self.commands['echo'] = self.cmd_echo
    
    def execute(self, command: Command) -> Optional[str]:
        """Execute a command"""
        if command.name in self.commands:
            try:
                return self.commands[command.name](command)
            except Exception as e:
                return f"Error executing command: {str(e)}"
        
        return None
    
    def cmd_help(self, command: Command) -> str:
        """Show help"""
        help_text = [
            "Available commands:",
            "",
            "  help              - Show this help",
            "  clear             - Clear the screen",
            "  exit              - Exit the application",
            "  theme [name]      - Change theme (default, dark, light, christmas, cyberpunk)",
            "  plugin list       - List loaded plugins",
            "  plugin load NAME  - Load a plugin",
            "  keybinds          - Show keybindings",
            "  about             - About this application",
            "  time              - Show current time",
            "  history           - Show command history",
            "  echo [text]       - Echo text",
            "",
            "Any other command will be executed in the shell.",
        ]
        return "\n".join(help_text)
    
    def cmd_clear(self, command: Command) -> str:
        """Clear screen"""
        if self.app.terminal:
            self.app.terminal.output_buffer.clear()
        return ""
    
    def cmd_exit(self, command: Command) -> str:
        """Exit application"""
        self.app.running = False
        return "Goodbye!"
    
    def cmd_theme(self, command: Command) -> str:
        """Change theme"""
        if not command.args:
            themes = self.app.theme_manager.list_themes()
            return f"Available themes: {', '.join(themes)}\nCurrent: {self.app.theme_manager.current_theme_name}"
        
        theme_name = command.args[0]
        if self.app.theme_manager.set_theme(theme_name):
            return f"Theme changed to: {theme_name}"
        else:
            return f"Unknown theme: {theme_name}"
    
    def cmd_plugin(self, command: Command) -> str:
        """Plugin management"""
        if not command.args:
            return "Usage: plugin [list|load|unload] [name]"
        
        action = command.args[0]
        
        if action == "list":
            plugins = self.app.plugin_manager.list_plugins()
            if plugins:
                return "Loaded plugins:\n" + "\n".join(f"  - {p}" for p in plugins)
            else:
                return "No plugins loaded"
        
        elif action == "load":
            if len(command.args) < 2:
                return "Usage: plugin load NAME"
            # Plugin loading would be implemented here
            return f"Plugin loading not implemented in this demo"
        
        elif action == "unload":
            if len(command.args) < 2:
                return "Usage: plugin unload NAME"
            plugin_name = command.args[1]
            self.app.plugin_manager.unload_plugin(plugin_name)
            return f"Plugin unloaded: {plugin_name}"
        
        return f"Unknown action: {action}"
    
    def cmd_keybinds(self, command: Command) -> str:
        """Show keybindings"""
        bindings = [
            "Keybindings:",
            "",
            "  F8                - Toggle menu bar",
            "  F9                - Toggle autocorrect panel",
            "  F10               - Clear screen",
            "  Up/Down           - Command history",
            "  Left/Right        - Move cursor",
            "  Home/End          - Jump to line start/end",
            "  Ctrl+Left/Right   - Jump by word",
            "  Ctrl+A / Ctrl+E   - Jump to line start/end",
            "  Ctrl+U            - Clear line",
            "  Ctrl+W            - Delete word",
            "  Tab               - Accept suggestion",
            "  Ctrl+C            - Exit",
        ]
        return "\n".join(bindings)
    
    def cmd_about(self, command: Command) -> str:
        """About this application"""
        about = [
            "╔═══════════════════════════════════════════════╗",
            "║  Advanced Terminal UI with Christmas Magic  ║",
            "╚═══════════════════════════════════════════════╝",
            "",
            "A feature-rich terminal UI featuring:",
            "  • Full terminal emulation",
            "  • Persistent menu and status bars",
            "  • Intelligent autocomplete",
            "  • GLSL-inspired shader effects",
            "  • 3D Christmas tree with lights",
            "  • Multi-layer parallax background",
            "  • Plugin system",
            "  • Theme support",
            "  • And much more!",
            "",
            f"Version: 2.0",
            f"Built with Python {sys.version.split()[0]}",
        ]
        return "\n".join(about)
    
    def cmd_time(self, command: Command) -> str:
        """Show current time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cmd_history(self, command: Command) -> str:
        """Show command history"""
        if self.app.terminal:
            commands = list(self.app.terminal.command_history.commands)
            if commands:
                return "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(commands[-20:]))
            else:
                return "No command history"
        return ""
    
    def cmd_echo(self, command: Command) -> str:
        """Echo text"""
        return " ".join(command.args)

class ExtendedCommandExecutor(CommandExecutor):
    """Extended command executor with more commands"""
    
    def register_builtin_commands(self):
        """Register all built-in commands"""
        super().register_builtin_commands()
        
        # Add extended commands
        self.commands['session'] = self.cmd_session
        self.commands['tab'] = self.cmd_tab
        self.commands['search'] = self.cmd_search
        self.commands['macro'] = self.cmd_macro
        self.commands['script'] = self.cmd_script
        self.commands['copy'] = self.cmd_copy
        self.commands['paste'] = self.cmd_paste
        self.commands['config'] = self.cmd_config
        self.commands['notify'] = self.cmd_notify
        self.commands['fps'] = self.cmd_fps
        self.commands['record'] = self.cmd_record
        self.commands['play'] = self.cmd_play
    
    def cmd_session(self, command: Command) -> str:
        """Session management"""
        if not command.args:
            sessions = self.app.session_manager.list_sessions()
            if sessions:
                lines = ["Sessions:"]
                for sid, name, active in sessions:
                    marker = "→" if active else " "
                    lines.append(f"  {marker} [{sid}] {name}")
                return "\n".join(lines)
            return "No sessions"
        
        action = command.args[0]
        
        if action == "new":
            name = command.args[1] if len(command.args) > 1 else "session"
            session_id = self.app.session_manager.create_session(name)
            return f"Created session: {session_id}"
        
        elif action == "switch":
            if len(command.args) < 2:
                return "Usage: session switch SESSION_ID"
            session_id = command.args[1]
            if self.app.session_manager.switch_session(session_id):
                return f"Switched to session: {session_id}"
            return f"Session not found: {session_id}"
        
        elif action == "close":
            if len(command.args) < 2:
                return "Usage: session close SESSION_ID"
            session_id = command.args[1]
            if self.app.session_manager.close_session(session_id):
                return f"Closed session: {session_id}"
            return f"Session not found: {session_id}"
        
        return f"Unknown action: {action}"
    
    def cmd_tab(self, command: Command) -> str:
        """Tab management"""
        if not command.args:
            tabs = self.app.tab_manager.list_tabs()
            if tabs:
                lines = ["Tabs:"]
                for tid, name, active in tabs:
                    marker = "→" if active else " "
                    lines.append(f"  {marker} [{tid}] {name}")
                return "\n".join(lines)
            return "No tabs"
        
        action = command.args[0]
        
        if action == "new":
            name = command.args[1] if len(command.args) > 1 else "Tab"
            session = self.app.session_manager.get_active_session()
            if session:
                tab_id = self.app.tab_manager.create_tab(name, session.id)
                return f"Created tab: {tab_id}"
            return "No active session"
        
        elif action == "next":
            self.app.tab_manager.next_tab()
            return "Switched to next tab"
        
        elif action == "prev":
            self.app.tab_manager.prev_tab()
            return "Switched to previous tab"
        
        elif action == "close":
            active_tab = self.app.tab_manager.get_active_tab()
            if active_tab:
                self.app.tab_manager.close_tab(active_tab.id)
                return f"Closed tab: {active_tab.name}"
            return "No active tab"
        
        return f"Unknown action: {action}"
    
    def cmd_search(self, command: Command) -> str:
        """Search through output"""
        if not command.args:
            return "Usage: search QUERY"
        
        query = " ".join(command.args)
        results = self.app.search_engine.search(self.app.terminal.output_buffer, query)
        
        if results:
            return f"Found {len(results)} matches for '{query}'"
        return f"No matches found for '{query}'"
    
    def cmd_macro(self, command: Command) -> str:
        """Macro management"""
        if not command.args:
            macros = self.app.macro_manager.list_macros()
            if macros:
                return "Macros:\n" + "\n".join(f"  - {m}" for m in macros)
            return "No macros defined"
        
        action = command.args[0]
        
        if action == "record":
            if len(command.args) < 2:
                return "Usage: macro record NAME"
            name = command.args[1]
            self.app.macro_manager.start_recording(name)
            return f"Recording macro: {name}"
        
        elif action == "stop":
            if len(command.args) < 2:
                return "Usage: macro stop TRIGGER"
            trigger = command.args[1]
            self.app.macro_manager.stop_recording(trigger)
            return f"Macro saved with trigger: {trigger}"
        
        return f"Unknown action: {action}"
    
    def cmd_script(self, command: Command) -> str:
        """Script management"""
        if not command.args:
            scripts = list(self.app.script_engine.scripts.keys())
            if scripts:
                return "Scripts:\n" + "\n".join(f"  - {s}" for s in scripts)
            return "No scripts loaded"
        
        action = command.args[0]
        
        if action == "load":
            if len(command.args) < 2:
                return "Usage: script load FILEPATH"
            filepath = command.args[1]
            if self.app.script_engine.load_script_from_file(filepath):
                return f"Loaded script: {filepath}"
            return f"Failed to load script: {filepath}"
        
        elif action == "run":
            if len(command.args) < 2:
                return "Usage: script run NAME"
            name = command.args[1]
            if self.app.script_engine.start_script(name):
                return f"Running script: {name}"
            return f"Script not found: {name}"
        
        elif action == "stop":
            self.app.script_engine.stop_script()
            return "Stopped script"
        
        return f"Unknown action: {action}"
    
    def cmd_copy(self, command: Command) -> str:
        """Copy text to clipboard"""
        if not command.args:
            return "Usage: copy TEXT"
        
        text = " ".join(command.args)
        self.app.clipboard_manager.copy(text)
        return f"Copied to clipboard: {text}"
    
    def cmd_paste(self, command: Command) -> str:
        """Paste text from clipboard"""
        text = self.app.clipboard_manager.paste()
        if text:
            return text
        return "Clipboard is empty"
    
    def cmd_config(self, command: Command) -> str:
        """Configuration management"""
        if not command.args:
            config = self.app.config_manager.config
            lines = ["Configuration:"]
            for key, value in config.items():
                lines.append(f"  {key} = {value}")
            return "\n".join(lines)
        
        action = command.args[0]
        
        if action == "get":
            if len(command.args) < 2:
                return "Usage: config get KEY"
            key = command.args[1]
            value = self.app.config_manager.get(key)
            return f"{key} = {value}"
        
        elif action == "set":
            if len(command.args) < 3:
                return "Usage: config set KEY VALUE"
            key = command.args[1]
            value = " ".join(command.args[2:])
            
            # Try to parse value
            try:
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
            except:
                pass
            
            self.app.config_manager.set(key, value)
            return f"Set {key} = {value}"
        
        elif action == "save":
            self.app.config_manager.save_config()
            return "Configuration saved"
        
        return f"Unknown action: {action}"
    
    def cmd_notify(self, command: Command) -> str:
        """Show a notification"""
        if not command.args:
            return "Usage: notify MESSAGE [type]"
        
        message = " ".join(command.args[:-1]) if len(command.args) > 1 else " ".join(command.args)
        notif_type = command.args[-1] if len(command.args) > 1 and command.args[-1] in ['info', 'warning', 'error', 'success'] else 'info'
        
        if notif_type in ['info', 'warning', 'error', 'success']:
            message = " ".join(command.args[:-1])
        else:
            notif_type = 'info'
        
        self.app.notification_manager.add_notification(message, notif_type)
        return ""
    
    def cmd_fps(self, command: Command) -> str:
        """Show/set FPS"""
        if not command.args:
            fps = self.app.performance_monitor.get_fps()
            return f"Current FPS: {fps:.2f}"
        
        try:
            new_fps = int(command.args[0])
            if 1 <= new_fps <= 120:
                Config.FPS = new_fps
                Config.FRAME_TIME = 1.0 / new_fps
                return f"FPS set to: {new_fps}"
            return "FPS must be between 1 and 120"
        except ValueError:
            return "Invalid FPS value"
    
    def cmd_record(self, command: Command) -> str:
        """Start recording macro"""
        if not command.args:
            return "Usage: record MACRO_NAME"
        
        name = command.args[0]
        self.app.macro_manager.start_recording(name)
        return f"Recording macro: {name}. Type 'record stop TRIGGER' to finish."
    
    def cmd_play(self, command: Command) -> str:
        """Play a macro"""
        if not command.args:
            return "Usage: play MACRO_NAME"
        
        name = command.args[0]
        macro = self.app.macro_manager.get_macro(name)
        
        if macro:
            # Execute macro commands
            for action in macro.actions:
                # This would need to be integrated into the input system
                pass
            return f"Played macro: {name}"
        
        return f"Macro not found: {name}"

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@dataclass
class Session:
    """Represents a terminal session"""
    id: str
    name: str
    created_at: float
    output_buffer: TerminalOutputBuffer
    command_history: CommandHistory
    working_directory: str
    environment: Dict[str, str]

class SessionManager:
    """Manages multiple terminal sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None
    
    def create_session(self, name: str) -> str:
        """Create a new session"""
        session_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
        
        session = Session(
            id=session_id,
            name=name,
            created_at=time.time(),
            output_buffer=TerminalOutputBuffer(),
            command_history=CommandHistory(),
            working_directory=os.getcwd(),
            environment=os.environ.copy()
        )
        
        self.sessions[session_id] = session
        
        if self.active_session_id is None:
            self.active_session_id = session_id
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def get_active_session(self) -> Optional[Session]:
        """Get the active session"""
        if self.active_session_id:
            return self.sessions.get(self.active_session_id)
        return None
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        if session_id in self.sessions:
            self.active_session_id = session_id
            return True
        return False
    
    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            if self.active_session_id == session_id:
                if self.sessions:
                    self.active_session_id = list(self.sessions.keys())[0]
                else:
                    self.active_session_id = None
            
            return True
        return False
    
    def list_sessions(self) -> List[Tuple[str, str, bool]]:
        """List all sessions (id, name, is_active)"""
        result = []
        for session_id, session in self.sessions.items():
            is_active = (session_id == self.active_session_id)
            result.append((session_id, session.name, is_active))
        return result

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "~/.tui_config.json"):
        self.config_file = os.path.expanduser(config_file)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            self.config = self.get_default_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            pass
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'theme': 'default',
            'fps': 60,
            'enable_shaders': True,
            'enable_particles': True,
            'enable_animations': True,
            'show_welcome': True,
            'keybindings': Config.KEYBINDINGS.copy(),
            'plugins': [],
            'font_size': 12,
            'shell': Config.DEFAULT_SHELL,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
        self.save_config()
    
    def apply_to_config_class(self):
        """Apply loaded config to Config class"""
        Config.FPS = self.get('fps', 60)
        Config.FRAME_TIME = 1.0 / Config.FPS
        Config.ENABLE_SHADERS = self.get('enable_shaders', True)
        Config.TREE_ENABLE_SNOW = self.get('enable_particles', True)

# ============================================================================
# MACRO SYSTEM
# ============================================================================

@dataclass
class Macro:
    """Represents a keyboard macro"""
    name: str
    trigger: str
    actions: List[str]
    enabled: bool = True

class MacroManager:
    """Manages keyboard macros"""
    
    def __init__(self):
        self.macros: Dict[str, Macro] = {}
        self.recording = False
        self.recording_macro_name: Optional[str] = None
        self.recorded_actions: List[str] = []
    
    def add_macro(self, macro: Macro):
        """Add a macro"""
        self.macros[macro.name] = macro
    
    def remove_macro(self, name: str):
        """Remove a macro"""
        if name in self.macros:
            del self.macros[name]
    
    def get_macro(self, name: str) -> Optional[Macro]:
        """Get a macro by name"""
        return self.macros.get(name)
    
    def find_macro_by_trigger(self, trigger: str) -> Optional[Macro]:
        """Find a macro by its trigger"""
        for macro in self.macros.values():
            if macro.enabled and macro.trigger == trigger:
                return macro
        return None
    
    def start_recording(self, name: str):
        """Start recording a macro"""
        self.recording = True
        self.recording_macro_name = name
        self.recorded_actions = []
    
    def stop_recording(self, trigger: str):
        """Stop recording and save macro"""
        if self.recording and self.recording_macro_name:
            macro = Macro(
                name=self.recording_macro_name,
                trigger=trigger,
                actions=self.recorded_actions.copy()
            )
            self.add_macro(macro)
        
        self.recording = False
        self.recording_macro_name = None
        self.recorded_actions = []
    
    def record_action(self, action: str):
        """Record an action during macro recording"""
        if self.recording:
            self.recorded_actions.append(action)
    
    def list_macros(self) -> List[str]:
        """List all macro names"""
        return list(self.macros.keys())

# ============================================================================
# SEARCH FUNCTIONALITY
# ============================================================================

class SearchEngine:
    """Search through terminal output"""
    
    def __init__(self):
        self.last_query = ""
        self.last_results: List[Tuple[int, str]] = []
        self.current_result_index = 0
    
    def search(self, output_buffer: TerminalOutputBuffer, query: str, 
              case_sensitive: bool = False, regex: bool = False) -> List[Tuple[int, str]]:
        """Search through output buffer"""
        if not query:
            return []
        
        self.last_query = query
        self.last_results = []
        self.current_result_index = 0
        
        lines = list(output_buffer.lines)
        
        if regex:
            try:
                pattern = re.compile(query if case_sensitive else query, 
                                   0 if case_sensitive else re.IGNORECASE)
            except re.error:
                return []
            
            for i, line in enumerate(lines):
                if pattern.search(line.text):
                    self.last_results.append((i, line.text))
        else:
            search_query = query if case_sensitive else query.lower()
            
            for i, line in enumerate(lines):
                search_text = line.text if case_sensitive else line.text.lower()
                if search_query in search_text:
                    self.last_results.append((i, line.text))
        
        return self.last_results
    
    def next_result(self) -> Optional[Tuple[int, str]]:
        """Get next search result"""
        if not self.last_results:
            return None
        
        self.current_result_index = (self.current_result_index + 1) % len(self.last_results)
        return self.last_results[self.current_result_index]
    
    def prev_result(self) -> Optional[Tuple[int, str]]:
        """Get previous search result"""
        if not self.last_results:
            return None
        
        self.current_result_index = (self.current_result_index - 1) % len(self.last_results)
        return self.last_results[self.current_result_index]
    
    def get_current_result(self) -> Optional[Tuple[int, str]]:
        """Get current search result"""
        if self.last_results and 0 <= self.current_result_index < len(self.last_results):
            return self.last_results[self.current_result_index]
        return None
    
    def highlight_matches(self, text: str, query: str, 
                         color: Tuple[int, int, int] = (255, 255, 0)) -> str:
        """Highlight search matches in text"""
        if not query:
            return text
        
        # Simple case-insensitive highlight
        highlighted = text
        start = 0
        result = []
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                result.append(text[start:])
                break
            
            result.append(text[start:pos])
            result.append(Color.rgb(*color))
            result.append(Color.reverse())
            result.append(text[pos:pos+len(query)])
            result.append(Color.reset())
            
            start = pos + len(query)
        
        return ''.join(result)

# ============================================================================
# SCRIPTING ENGINE
# ============================================================================

class Script:
    """Represents a script"""
    
    def __init__(self, name: str, commands: List[str]):
        self.name = name
        self.commands = commands
        self.current_line = 0
        self.running = False
    
    def reset(self):
        """Reset script to beginning"""
        self.current_line = 0
        self.running = False
    
    def get_next_command(self) -> Optional[str]:
        """Get next command in script"""
        if self.current_line < len(self.commands):
            cmd = self.commands[self.current_line]
            self.current_line += 1
            return cmd
        return None
    
    def has_more_commands(self) -> bool:
        """Check if script has more commands"""
        return self.current_line < len(self.commands)

class ScriptEngine:
    """Executes scripts"""
    
    def __init__(self):
        self.scripts: Dict[str, Script] = {}
        self.running_script: Optional[Script] = None
        self.script_delay = 0.5  # Delay between commands in seconds
        self.last_command_time = 0.0
    
    def add_script(self, script: Script):
        """Add a script"""
        self.scripts[script.name] = script
    
    def remove_script(self, name: str):
        """Remove a script"""
        if name in self.scripts:
            del self.scripts[name]
    
    def get_script(self, name: str) -> Optional[Script]:
        """Get a script by name"""
        return self.scripts.get(name)
    
    def start_script(self, name: str) -> bool:
        """Start executing a script"""
        script = self.get_script(name)
        if script:
            script.reset()
            script.running = True
            self.running_script = script
            self.last_command_time = time.time()
            return True
        return False
    
    def stop_script(self):
        """Stop current script"""
        if self.running_script:
            self.running_script.running = False
            self.running_script = None
    
    def update(self, current_time: float) -> Optional[str]:
        """Update script execution, returns next command if ready"""
        if not self.running_script or not self.running_script.running:
            return None
        
        # Check if enough time has passed
        if current_time - self.last_command_time < self.script_delay:
            return None
        
        # Get next command
        command = self.running_script.get_next_command()
        
        if command:
            self.last_command_time = current_time
            return command
        else:
            # Script finished
            self.stop_script()
            return None
    
    def is_running(self) -> bool:
        """Check if a script is currently running"""
        return self.running_script is not None and self.running_script.running
    
    def load_script_from_file(self, filepath: str) -> bool:
        """Load a script from a file"""
        try:
            with open(filepath, 'r') as f:
                commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            script_name = os.path.basename(filepath)
            script = Script(script_name, commands)
            self.add_script(script)
            return True
        except Exception:
            return False

# ============================================================================
# TAB MANAGEMENT
# ============================================================================

@dataclass
class Tab:
    """Represents a tab in the terminal"""
    id: str
    name: str
    session_id: str
    created_at: float

class TabManager:
    """Manages terminal tabs"""
    
    def __init__(self):
        self.tabs: Dict[str, Tab] = {}
        self.active_tab_id: Optional[str] = None
        self.tab_order: List[str] = []
    
    def create_tab(self, name: str, session_id: str) -> str:
        """Create a new tab"""
        tab_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
        
        tab = Tab(
            id=tab_id,
            name=name,
            session_id=session_id,
            created_at=time.time()
        )
        
        self.tabs[tab_id] = tab
        self.tab_order.append(tab_id)
        
        if self.active_tab_id is None:
            self.active_tab_id = tab_id
        
        return tab_id
    
    def get_tab(self, tab_id: str) -> Optional[Tab]:
        """Get a tab by ID"""
        return self.tabs.get(tab_id)
    
    def get_active_tab(self) -> Optional[Tab]:
        """Get the active tab"""
        if self.active_tab_id:
            return self.tabs.get(self.active_tab_id)
        return None
    
    def switch_tab(self, tab_id: str) -> bool:
        """Switch to a different tab"""
        if tab_id in self.tabs:
            self.active_tab_id = tab_id
            return True
        return False
    
    def next_tab(self):
        """Switch to next tab"""
        if not self.tab_order or not self.active_tab_id:
            return
        
        current_index = self.tab_order.index(self.active_tab_id)
        next_index = (current_index + 1) % len(self.tab_order)
        self.active_tab_id = self.tab_order[next_index]
    
    def prev_tab(self):
        """Switch to previous tab"""
        if not self.tab_order or not self.active_tab_id:
            return
        
        current_index = self.tab_order.index(self.active_tab_id)
        prev_index = (current_index - 1) % len(self.tab_order)
        self.active_tab_id = self.tab_order[prev_index]
    
    def close_tab(self, tab_id: str) -> bool:
        """Close a tab"""
        if tab_id in self.tabs:
            del self.tabs[tab_id]
            self.tab_order.remove(tab_id)
            
            if self.active_tab_id == tab_id:
                if self.tab_order:
                    self.active_tab_id = self.tab_order[-1]
                else:
                    self.active_tab_id = None
            
            return True
        return False
    
    def list_tabs(self) -> List[Tuple[str, str, bool]]:
        """List all tabs (id, name, is_active)"""
        result = []
        for tab_id in self.tab_order:
            tab = self.tabs[tab_id]
            is_active = (tab_id == self.active_tab_id)
            result.append((tab_id, tab.name, is_active))
        return result
    
    def render_tab_bar(self, width: int, y: int, time_val: float) -> List[str]:
        """Render tab bar"""
        output = []
        
        # Draw background
        output.append(Cursor.move(0, y))
        output.append(Color.bg_rgb(30, 35, 45))
        output.append(' ' * width)
        
        # Draw tabs
        x_offset = 2
        for i, tab_id in enumerate(self.tab_order):
            tab = self.tabs[tab_id]
            is_active = (tab_id == self.active_tab_id)
            
            # Tab text
            tab_text = f" {tab.name} "
            if len(tab_text) > 20:
                tab_text = tab_text[:17] + "... "
            
            # Colors
            if is_active:
                bg_color = (60, 80, 120)
                fg_color = (255, 255, 255)
            else:
                bg_color = (40, 45, 55)
                fg_color = (180, 180, 200)
            
            # Draw tab
            output.append(Cursor.move(x_offset, y))
            output.append(Color.bg_rgb(*bg_color))
            output.append(Color.rgb(*fg_color))
            output.append(tab_text)
            output.append(Color.reset())
            
            x_offset += len(tab_text) + 1
            
            if x_offset >= width - 10:
                break
        
        return output

# ============================================================================
# CLIPBOARD MANAGER
# ============================================================================

class ClipboardManager:
    """Manages clipboard operations"""
    
    def __init__(self):
        self.clipboard_content = ""
        self.history: deque = deque(maxlen=50)
    
    def copy(self, text: str):
        """Copy text to clipboard"""
        self.clipboard_content = text
        if text and text not in self.history:
            self.history.append(text)
        
        # Try to use system clipboard
        try:
            # Try xclip
            subprocess.run(['xclip', '-selection', 'clipboard'], 
                         input=text.encode(), check=False, timeout=1)
        except:
            try:
                # Try xsel
                subprocess.run(['xsel', '--clipboard'], 
                             input=text.encode(), check=False, timeout=1)
            except:
                pass
    
    def paste(self) -> str:
        """Paste text from clipboard"""
        # Try to get from system clipboard first
        try:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except:
            try:
                result = subprocess.run(['xsel', '--clipboard'], 
                                      capture_output=True, text=True, timeout=1)
                if result.returncode == 0 and result.stdout:
                    return result.stdout
            except:
                pass
        
        return self.clipboard_content
    
    def get_history(self) -> List[str]:
        """Get clipboard history"""
        return list(self.history)

# ============================================================================
# PERFORMANCE MONITOR
# ============================================================================

class PerformanceMonitor:
    """Monitors application performance"""
    
    def __init__(self):
        self.frame_times: deque = deque(maxlen=60)
        self.render_times: deque = deque(maxlen=60)
        self.update_times: deque = deque(maxlen=60)
        self.last_frame_time = 0.0
    
    def start_frame(self):
        """Mark start of frame"""
        self.last_frame_time = time.time()
    
    def end_frame(self):
        """Mark end of frame"""
        frame_time = time.time() - self.last_frame_time
        self.frame_times.append(frame_time)
    
    def record_render_time(self, render_time: float):
        """Record render time"""
        self.render_times.append(render_time)
    
    def record_update_time(self, update_time: float):
        """Record update time"""
        self.update_times.append(update_time)
    
    def get_fps(self) -> float:
        """Get average FPS"""
        if not self.frame_times:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def get_avg_render_time(self) -> float:
        """Get average render time"""
        if not self.render_times:
            return 0.0
        return sum(self.render_times) / len(self.render_times)
    
    def get_avg_update_time(self) -> float:
        """Get average update time"""
        if not self.update_times:
            return 0.0
        return sum(self.update_times) / len(self.update_times)
    
    def get_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        return {
            'fps': self.get_fps(),
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0.0,
            'avg_render_time': self.get_avg_render_time(),
            'avg_update_time': self.get_avg_update_time(),
        }

# ============================================================================
# BRAILLE GRAPHICS SYSTEM
# ============================================================================

class BrailleCanvas:
    """Canvas for drawing with Braille characters"""
    
    # Braille dot patterns (2x4 grid per character)
    DOTS = [
        (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (0, 3, 0x40),
        (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (1, 3, 0x80)
    ]
    
    def __init__(self, width: int, height: int):
        """Initialize canvas (width and height in characters)"""
        self.char_width = width
        self.char_height = height
        self.pixel_width = width * 2
        self.pixel_height = height * 4
        
        # Buffer: [y][x] = (pattern_bits, r, g, b)
        self.buffer = [
            [(0, 0, 0, 0) for _ in range(self.char_width)]
            for _ in range(self.char_height)
        ]
        
        # Pixel buffer for sub-pixel access
        self.pixels = [
            [(0, 0, 0) for _ in range(self.pixel_width)]
            for _ in range(self.pixel_height)
        ]
    
    def clear(self):
        """Clear the canvas"""
        self.buffer = [
            [(0, 0, 0, 0) for _ in range(self.char_width)]
            for _ in range(self.char_height)
        ]
        self.pixels = [
            [(0, 0, 0) for _ in range(self.pixel_width)]
            for _ in range(self.pixel_height)
        ]
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """Set a pixel (sub-character resolution)"""
        if not (0 <= x < self.pixel_width and 0 <= y < self.pixel_height):
            return
        
        self.pixels[y][x] = color
        
        # Update braille character
        char_x = x // 2
        char_y = y // 4
        sub_x = x % 2
        sub_y = y % 4
        
        if char_y < self.char_height and char_x < self.char_width:
            # Get current pattern and color
            pattern, r, g, b = self.buffer[char_y][char_x]
            
            # Set bit for this pixel
            for dx, dy, mask in self.DOTS:
                if dx == sub_x and dy == sub_y:
                    pattern |= mask
                    break
            
            # Update color (average)
            count = bin(pattern).count('1')
            if count > 0:
                self.buffer[char_y][char_x] = (
                    pattern,
                    (r * (count - 1) + color[0]) // count,
                    (g * (count - 1) + color[1]) // count,
                    (b * (count - 1) + color[2]) // count
                )
            else:
                self.buffer[char_y][char_x] = (pattern, *color)
    
    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]):
        """Draw a line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            self.set_pixel(x, y, color)
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def draw_circle(self, cx: int, cy: int, radius: int, color: Tuple[int, int, int]):
        """Draw a circle using midpoint circle algorithm"""
        x = radius
        y = 0
        err = 0
        
        while x >= y:
            self.set_pixel(cx + x, cy + y, color)
            self.set_pixel(cx + y, cy + x, color)
            self.set_pixel(cx - y, cy + x, color)
            self.set_pixel(cx - x, cy + y, color)
            self.set_pixel(cx - x, cy - y, color)
            self.set_pixel(cx - y, cy - x, color)
            self.set_pixel(cx + y, cy - x, color)
            self.set_pixel(cx + x, cy - y, color)
            
            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x
    
    def fill_circle(self, cx: int, cy: int, radius: int, color: Tuple[int, int, int]):
        """Draw a filled circle"""
        for y in range(-radius, radius + 1):
            for x in range(-radius, radius + 1):
                if x * x + y * y <= radius * radius:
                    self.set_pixel(cx + x, cy + y, color)
    
    def draw_rect(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]):
        """Draw a rectangle outline"""
        # Top and bottom
        for i in range(width):
            self.set_pixel(x + i, y, color)
            self.set_pixel(x + i, y + height - 1, color)
        
        # Left and right
        for i in range(height):
            self.set_pixel(x, y + i, color)
            self.set_pixel(x + width - 1, y + i, color)
    
    def fill_rect(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]):
        """Draw a filled rectangle"""
        for j in range(height):
            for i in range(width):
                self.set_pixel(x + i, y + j, color)
    
    def render(self, offset_x: int = 0, offset_y: int = 0) -> List[str]:
        """Render canvas to output"""
        output = []
        
        for y in range(self.char_height):
            line_output = []
            line_output.append(Cursor.move(offset_x, offset_y + y))
            
            prev_color = None
            
            for x in range(self.char_width):
                pattern, r, g, b = self.buffer[y][x]
                
                if pattern == 0:
                    if prev_color is not None:
                        line_output.append(Color.reset())
                        prev_color = None
                    line_output.append(' ')
                else:
                    # Braille character
                    char = chr(0x2800 + pattern)
                    
                    # Color
                    color_code = Color.rgb(r, g, b)
                    if color_code != prev_color:
                        line_output.append(color_code)
                        prev_color = color_code
                    
                    line_output.append(char)
            
            if prev_color is not None:
                line_output.append(Color.reset())
            
            output.append(''.join(line_output))
        
        return output

# ============================================================================
# ASCII ART RENDERER
# ============================================================================

class ASCIIArtRenderer:
    """Renders ASCII art with color support"""
    
    # Grayscale ramp (darkest to lightest)
    GRAYSCALE = " .:-=+*#%@"
    
    def __init__(self):
        self.art_cache: Dict[str, List[str]] = {}
    
    def load_art(self, name: str, art: str):
        """Load ASCII art"""
        lines = art.strip().split('\n')
        self.art_cache[name] = lines
    
    def render_art(self, name: str, x: int, y: int, 
                   color: Optional[Tuple[int, int, int]] = None,
                   gradient: bool = False,
                   color2: Optional[Tuple[int, int, int]] = None) -> List[str]:
        """Render ASCII art"""
        if name not in self.art_cache:
            return []
        
        output = []
        lines = self.art_cache[name]
        
        for i, line in enumerate(lines):
            output.append(Cursor.move(x, y + i))
            
            if color:
                if gradient and color2:
                    # Gradient from top to bottom
                    t = i / max(len(lines) - 1, 1)
                    line_color = Color.gradient(color, color2, t)
                    output.append(Color.rgb(*line_color))
                else:
                    output.append(Color.rgb(*color))
            
            output.append(line)
            
            if color:
                output.append(Color.reset())
        
        return output
    
    def create_box_art(self, width: int, height: int, style: str = "simple") -> str:
        """Create a box ASCII art"""
        if style == "simple":
            chars = {'tl': '+', 'tr': '+', 'bl': '+', 'br': '+', 'h': '-', 'v': '|'}
        elif style == "double":
            chars = {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 'h': '═', 'v': '║'}
        else:
            chars = {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'h': '─', 'v': '│'}
        
        lines = []
        
        # Top
        lines.append(chars['tl'] + chars['h'] * (width - 2) + chars['tr'])
        
        # Middle
        for _ in range(height - 2):
            lines.append(chars['v'] + ' ' * (width - 2) + chars['v'])
        
        # Bottom
        lines.append(chars['bl'] + chars['h'] * (width - 2) + chars['br'])
        
        return '\n'.join(lines)

# ============================================================================
# ADVANCED INPUT HANDLER
# ============================================================================

class InputHandler:
    """Advanced input handling with event system"""
    
    def __init__(self):
        self.key_bindings: Dict[str, List[Callable]] = defaultdict(list)
        self.input_buffer = ""
        self.escape_sequence_timeout = 0.1
        self.last_input_time = 0.0
    
    def bind_key(self, key_sequence: str, callback: Callable):
        """Bind a key sequence to a callback"""
        self.key_bindings[key_sequence].append(callback)
    
    def unbind_key(self, key_sequence: str, callback: Optional[Callable] = None):
        """Unbind a key sequence"""
        if callback is None:
            if key_sequence in self.key_bindings:
                del self.key_bindings[key_sequence]
        else:
            if key_sequence in self.key_bindings:
                self.key_bindings[key_sequence].remove(callback)
    
    def process_input(self, char: str) -> bool:
        """Process input character. Returns True if handled."""
        current_time = time.time()
        
        # Check if we're in the middle of an escape sequence
        if self.input_buffer:
            # Check timeout
            if current_time - self.last_input_time > self.escape_sequence_timeout:
                # Timeout, process what we have
                handled = self._try_execute(self.input_buffer)
                self.input_buffer = char
                self.last_input_time = current_time
                return handled
        
        self.input_buffer += char
        self.last_input_time = current_time
        
        # Try to match current buffer
        if self.input_buffer in self.key_bindings:
            # Exact match
            handled = self._try_execute(self.input_buffer)
            self.input_buffer = ""
            return handled
        
        # Check if buffer could be a prefix of any binding
        is_prefix = any(
            binding.startswith(self.input_buffer)
            for binding in self.key_bindings.keys()
        )
        
        if not is_prefix:
            # No possible match, process as single char
            handled = self._try_execute(self.input_buffer)
            self.input_buffer = ""
            return handled
        
        # Could be a prefix, wait for more input
        return False
    
    def _try_execute(self, key_sequence: str) -> bool:
        """Try to execute callbacks for a key sequence"""
        if key_sequence in self.key_bindings:
            for callback in self.key_bindings[key_sequence]:
                try:
                    callback()
                except Exception as e:
                    pass
            return True
        return False

# ============================================================================
# FILE BROWSER COMPONENT
# ============================================================================

class FileBrowser:
    """File browser component"""
    
    def __init__(self, width: int, height: int, x: int, y: int):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.current_path = os.getcwd()
        self.files: List[Tuple[str, bool]] = []  # (name, is_dir)
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible = False
        self.refresh()
    
    def refresh(self):
        """Refresh file list"""
        try:
            entries = os.listdir(self.current_path)
            self.files = []
            
            # Add parent directory
            if self.current_path != '/':
                self.files.append(('..', True))
            
            # Add directories first, then files
            dirs = []
            files = []
            
            for entry in sorted(entries):
                full_path = os.path.join(self.current_path, entry)
                if os.path.isdir(full_path):
                    dirs.append((entry, True))
                else:
                    files.append((entry, False))
            
            self.files.extend(dirs)
            self.files.extend(files)
            
        except PermissionError:
            self.files = [('..', True)]
    
    def navigate_up(self):
        """Navigate to parent directory"""
        self.current_path = os.path.dirname(self.current_path)
        if not self.current_path:
            self.current_path = '/'
        self.selected_index = 0
        self.scroll_offset = 0
        self.refresh()
    
    def navigate_down(self):
        """Navigate into selected directory"""
        if self.files and 0 <= self.selected_index < len(self.files):
            name, is_dir = self.files[self.selected_index]
            
            if is_dir:
                if name == '..':
                    self.navigate_up()
                else:
                    self.current_path = os.path.join(self.current_path, name)
                    self.selected_index = 0
                    self.scroll_offset = 0
                    self.refresh()
    
    def select_next(self):
        """Select next file"""
        if self.files:
            self.selected_index = (self.selected_index + 1) % len(self.files)
            
            # Adjust scroll
            visible_count = self.height - 4
            if self.selected_index >= self.scroll_offset + visible_count:
                self.scroll_offset = self.selected_index - visible_count + 1
            elif self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
    
    def select_prev(self):
        """Select previous file"""
        if self.files:
            self.selected_index = (self.selected_index - 1) % len(self.files)
            
            # Adjust scroll
            visible_count = self.height - 4
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            elif self.selected_index >= self.scroll_offset + visible_count:
                self.scroll_offset = self.selected_index - visible_count + 1
    
    def get_selected_path(self) -> Optional[str]:
        """Get path of selected file"""
        if self.files and 0 <= self.selected_index < len(self.files):
            name, _ = self.files[self.selected_index]
            if name == '..':
                return os.path.dirname(self.current_path)
            return os.path.join(self.current_path, name)
        return None
    
    def render(self, time_val: float) -> List[str]:
        """Render file browser"""
        if not self.visible:
            return []
        
        output = []
        
        # Draw border
        border_lines = Border.draw_box(
            self.x, self.y, self.width, self.height,
            BorderStyle.DOUBLE,
            (100, 180, 255),
            (180, 100, 255),
            time_val
        )
        output.extend([Cursor.move(bx, by) + btext for bx, by, btext in border_lines])
        
        # Draw title
        title = f" {self.current_path} "
        if len(title) > self.width - 4:
            title = "..." + title[-(self.width-7):]
        title_x = self.x + 2
        output.append(Cursor.move(title_x, self.y))
        output.append(Color.rgb(255, 255, 255))
        output.append(Color.bold())
        output.append(title)
        output.append(Color.reset())
        
        # Draw files
        visible_count = self.height - 4
        start_idx = self.scroll_offset
        end_idx = min(start_idx + visible_count, len(self.files))
        
        for i in range(start_idx, end_idx):
            name, is_dir = self.files[i]
            display_name = name
            
            # Truncate if needed
            max_name_len = self.width - 6
            if len(display_name) > max_name_len:
                display_name = display_name[:max_name_len-3] + "..."
            
            # Add indicator
            if is_dir:
                display_name = "📁 " + display_name
            else:
                display_name = "📄 " + display_name
            
            y_pos = self.y + 2 + (i - start_idx)
            is_selected = (i == self.selected_index)
            
            if is_selected:
                output.append(Cursor.move(self.x + 1, y_pos))
                output.append(Color.bg_rgb(80, 120, 180))
                output.append(Color.rgb(255, 255, 255))
                output.append(f" {display_name:<{self.width-2}} ")
                output.append(Color.reset())
            else:
                output.append(Cursor.move(self.x + 2, y_pos))
                if is_dir:
                    output.append(Color.rgb(100, 180, 255))
                else:
                    output.append(Color.rgb(200, 210, 230))
                output.append(display_name)
        
        # Draw scrollbar if needed
        if len(self.files) > visible_count:
            scrollbar_height = self.height - 4
            thumb_size = max(1, int(scrollbar_height * visible_count / len(self.files)))
            thumb_pos = int(scrollbar_height * self.scroll_offset / len(self.files))
            
            for i in range(scrollbar_height):
                y_pos = self.y + 2 + i
                output.append(Cursor.move(self.x + self.width - 2, y_pos))
                
                if thumb_pos <= i < thumb_pos + thumb_size:
                    output.append(Color.rgb(100, 150, 200))
                    output.append('█')
                else:
                    output.append(Color.rgb(60, 70, 90))
                    output.append('░')
        
        output.append(Color.reset())
        return output

# ============================================================================
# TEXT EDITOR COMPONENT
# ============================================================================

class TextEditor:
    """Simple text editor component"""
    
    def __init__(self, width: int, height: int, x: int, y: int):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.lines: List[str] = [""]
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_x = 0
        self.scroll_y = 0
        self.visible = False
        self.modified = False
        self.filename: Optional[str] = None
    
    def load_file(self, filename: str):
        """Load a file"""
        try:
            with open(filename, 'r') as f:
                self.lines = f.readlines()
                # Remove newlines
                self.lines = [line.rstrip('\n') for line in self.lines]
                if not self.lines:
                    self.lines = [""]
            self.filename = filename
            self.modified = False
            self.cursor_x = 0
            self.cursor_y = 0
            self.scroll_x = 0
            self.scroll_y = 0
        except Exception:
            self.lines = [""]
    
    def save_file(self, filename: Optional[str] = None):
        """Save file"""
        if filename:
            self.filename = filename
        
        if not self.filename:
            return False
        
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))
            self.modified = False
            return True
        except Exception:
            return False
    
    def insert_char(self, char: str):
        """Insert character at cursor"""
        if not self.lines:
            self.lines = [""]
        
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x:]
        self.cursor_x += 1
        self.modified = True
    
    def delete_char(self):
        """Delete character before cursor"""
        if self.cursor_x > 0:
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[:self.cursor_x-1] + line[self.cursor_x:]
            self.cursor_x -= 1
            self.modified = True
        elif self.cursor_y > 0:
            # Join with previous line
            current_line = self.lines[self.cursor_y]
            previous_line = self.lines[self.cursor_y - 1]
            self.cursor_x = len(previous_line)
            self.lines[self.cursor_y - 1] = previous_line + current_line
            self.lines.pop(self.cursor_y)
            self.cursor_y -= 1
            self.modified = True
    
    def insert_newline(self):
        """Insert newline at cursor"""
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = line[:self.cursor_x]
        self.lines.insert(self.cursor_y + 1, line[self.cursor_x:])
        self.cursor_y += 1
        self.cursor_x = 0
        self.modified = True
    
    def move_cursor(self, dx: int, dy: int):
        """Move cursor"""
        self.cursor_y = clamp(self.cursor_y + dy, 0, len(self.lines) - 1)
        self.cursor_x = clamp(self.cursor_x + dx, 0, len(self.lines[self.cursor_y]))
        
        # Adjust scroll
        visible_lines = self.height - 4
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        elif self.cursor_y >= self.scroll_y + visible_lines:
            self.scroll_y = self.cursor_y - visible_lines + 1
    
    def render(self, time_val: float) -> List[str]:
        """Render text editor"""
        if not self.visible:
            return []
        
        output = []
        
        # Draw border
        border_lines = Border.draw_box(
            self.x, self.y, self.width, self.height,
            BorderStyle.DOUBLE,
            (100, 200, 150),
            (150, 200, 100),
            time_val
        )
        output.extend([Cursor.move(bx, by) + btext for bx, by, btext in border_lines])
        
        # Draw title bar
        title = f" {self.filename or 'Untitled'} "
        if self.modified:
            title += "[+] "
        title_x = self.x + 2
        output.append(Cursor.move(title_x, self.y))
        output.append(Color.rgb(255, 255, 255))
        output.append(Color.bold())
        output.append(title)
        output.append(Color.reset())
        
        # Draw lines
        visible_lines = self.height - 4
        start_line = self.scroll_y
        end_line = min(start_line + visible_lines, len(self.lines))
        
        for i in range(start_line, end_line):
            line = self.lines[i]
            display_line = line[self.scroll_x:self.scroll_x + self.width - 10]
            
            y_pos = self.y + 2 + (i - start_line)
            
            # Line number
            output.append(Cursor.move(self.x + 2, y_pos))
            output.append(Color.rgb(100, 120, 150))
            output.append(f"{i+1:4d} ")
            
            # Line content
            output.append(Color.rgb(220, 220, 230))
            output.append(display_line)
        
        # Draw cursor
        if start_line <= self.cursor_y < end_line:
            cursor_screen_y = self.y + 2 + (self.cursor_y - start_line)
            cursor_screen_x = self.x + 7 + (self.cursor_x - self.scroll_x)
            
            if self.x + 7 <= cursor_screen_x < self.x + self.width - 2:
                output.append(Cursor.move(cursor_screen_x, cursor_screen_y))
                output.append(Color.rgb(*Config.THEME['cursor']))
                output.append(Color.reverse())
                
                # Get character at cursor
                line = self.lines[self.cursor_y]
                char = line[self.cursor_x] if self.cursor_x < len(line) else ' '
                output.append(char)
                output.append(Color.reset())
        
        # Status bar
        status_y = self.y + self.height - 1
        status = f" Line {self.cursor_y + 1}/{len(self.lines)} Col {self.cursor_x + 1} "
        output.append(Cursor.move(self.x + self.width - len(status) - 1, status_y))
        output.append(Color.rgb(180, 190, 200))
        output.append(status)
        
        output.append(Color.reset())
        return output

# ============================================================================
# CHART RENDERING
# ============================================================================

class ChartRenderer:
    """Renders various types of charts"""
    
    @staticmethod
    def render_bar_chart(data: List[Tuple[str, float]], width: int, height: int,
                        x: int, y: int, title: str = "") -> List[str]:
        """Render a bar chart"""
        output = []
        
        if not data:
            return output
        
        # Find max value
        max_value = max(value for _, value in data)
        if max_value == 0:
            max_value = 1
        
        # Draw title
        if title:
            output.append(Cursor.move(x, y))
            output.append(Color.rgb(200, 220, 255))
            output.append(Color.bold())
            output.append(title)
            output.append(Color.reset())
            y += 2
        
        # Calculate bar parameters
        bar_height = (height - (2 if title else 0) - len(data)) // len(data)
        bar_height = max(1, bar_height)
        
        current_y = y
        
        for label, value in data:
            # Label
            output.append(Cursor.move(x, current_y))
            output.append(Color.rgb(200, 200, 220))
            output.append(f"{label[:15]:<15} ")
            
            # Bar
            bar_width = int((width - 20) * value / max_value)
            bar_width = max(0, min(bar_width, width - 20))
            
            # Color based on value
            t = value / max_value
            color = Color.gradient((100, 100, 255), (255, 100, 100), t)
            
            output.append(Color.rgb(*color))
            output.append('█' * bar_width)
            
            # Value
            output.append(Color.reset())
            output.append(Color.rgb(255, 255, 255))
            output.append(f" {value:.1f}")
            
            current_y += bar_height
        
        output.append(Color.reset())
        return output
    
    @staticmethod
    def render_line_graph(data: List[float], width: int, height: int,
                         x: int, y: int, title: str = "") -> List[str]:
        """Render a line graph"""
        output = []
        
        if not data or len(data) < 2:
            return output
        
        # Draw title
        if title:
            output.append(Cursor.move(x, y))
            output.append(Color.rgb(200, 220, 255))
            output.append(Color.bold())
            output.append(title)
            output.append(Color.reset())
            y += 2
            height -= 2
        
        # Normalize data
        min_val = min(data)
        max_val = max(data)
        value_range = max_val - min_val
        if value_range == 0:
            value_range = 1
        
        # Calculate point positions
        points = []
        for i, value in enumerate(data):
            px = x + int((width - 1) * i / (len(data) - 1))
            py = y + height - 1 - int((height - 1) * (value - min_val) / value_range)
            points.append((px, py))
        
        # Draw axes
        for i in range(height):
            output.append(Cursor.move(x, y + i))
            output.append(Color.rgb(100, 100, 120))
            output.append('│')
        
        output.append(Cursor.move(x, y + height))
        output.append(Color.rgb(100, 100, 120))
        output.append('└' + '─' * (width - 1))
        
        # Draw lines
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # Simple line drawing
            steps = max(abs(x2 - x1), abs(y2 - y1))
            if steps == 0:
                steps = 1
            
            for step in range(steps + 1):
                t = step / steps
                px = int(x1 + (x2 - x1) * t)
                py = int(y1 + (y2 - y1) * t)
                
                output.append(Cursor.move(px, py))
                
                # Color gradient
                color = Color.gradient((100, 200, 255), (255, 100, 200), i / len(points))
                output.append(Color.rgb(*color))
                output.append('●')
        
        # Draw points
        for px, py in points:
            output.append(Cursor.move(px, py))
            output.append(Color.rgb(255, 255, 100))
            output.append('●')
        
        output.append(Color.reset())
        return output

# ============================================================================
# SYNTAX HIGHLIGHTER
# ============================================================================

class SyntaxHighlighter:
    """Syntax highlighting for various languages"""
    
    def __init__(self):
        self.keywords = {
            'python': ['def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for', 'while', 
                      'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'lambda',
                      'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'],
            'javascript': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                          'return', 'class', 'extends', 'import', 'export', 'default',
                          'true', 'false', 'null', 'undefined', 'this', 'new'],
            'shell': ['if', 'then', 'else', 'fi', 'for', 'do', 'done', 'while', 'case',
                     'esac', 'function', 'return', 'exit', 'echo', 'cd', 'ls', 'grep']
        }
        
        self.colors = {
            'keyword': (255, 100, 150),
            'string': (100, 255, 150),
            'comment': (100, 120, 140),
            'number': (255, 200, 100),
            'function': (100, 200, 255),
            'operator': (255, 150, 100),
        }
    
    def highlight_line(self, line: str, language: str = 'python') -> str:
        """Highlight a single line of code"""
        if language not in self.keywords:
            return line
        
        # This is a simplified highlighter
        output = []
        words = line.split()
        
        for word in words:
            if word in self.keywords[language]:
                output.append(Color.rgb(*self.colors['keyword']))
                output.append(word)
                output.append(Color.reset())
            elif word.startswith('"') or word.startswith("'"):
                output.append(Color.rgb(*self.colors['string']))
                output.append(word)
                output.append(Color.reset())
            elif word.startswith('#'):
                output.append(Color.rgb(*self.colors['comment']))
                output.append(word)
                output.append(Color.reset())
            elif word.isdigit():
                output.append(Color.rgb(*self.colors['number']))
                output.append(word)
                output.append(Color.reset())
            else:
                output.append(word)
            
            output.append(' ')
        
        return ''.join(output)

# ============================================================================
# MARKDOWN RENDERER
# ============================================================================

class MarkdownRenderer:
    """Render markdown-like text with formatting"""
    
    def __init__(self):
        self.in_code_block = False
        self.code_block_lines: List[str] = []
    
    def render_text(self, text: str, x: int, y: int, width: int) -> List[str]:
        """Render markdown text"""
        output = []
        lines = text.split('\n')
        current_y = y
        
        for line in lines:
            rendered = self._render_line(line, x, current_y, width)
            output.extend(rendered)
            current_y += 1
        
        return output
    
    def _render_line(self, line: str, x: int, y: int, width: int) -> List[str]:
        """Render a single markdown line"""
        output = []
        output.append(Cursor.move(x, y))
        
        # Headers
        if line.startswith('# '):
            output.append(Color.rgb(255, 200, 100))
            output.append(Color.bold())
            output.append(line[2:])
            output.append(Color.reset())
            return output
        elif line.startswith('## '):
            output.append(Color.rgb(200, 180, 255))
            output.append(Color.bold())
            output.append(line[3:])
            output.append(Color.reset())
            return output
        elif line.startswith('### '):
            output.append(Color.rgb(180, 200, 255))
            output.append(Color.bold())
            output.append(line[4:])
            output.append(Color.reset())
            return output
        
        # Code blocks
        if line.strip() == '```':
            self.in_code_block = not self.in_code_block
            return output
        
        if self.in_code_block:
            output.append(Color.bg_rgb(30, 35, 40))
            output.append(Color.rgb(200, 255, 200))
            output.append(f"  {line}")
            output.append(Color.reset())
            return output
        
        # Lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            indent = len(line) - len(line.lstrip())
            output.append(' ' * indent)
            output.append(Color.rgb(255, 200, 100))
            output.append('• ')
            output.append(Color.reset())
            output.append(Color.rgb(220, 220, 230))
            output.append(line.strip()[2:])
            output.append(Color.reset())
            return output
        
        # Inline formatting
        formatted = self._format_inline(line)
        output.append(formatted)
        output.append(Color.reset())
        
        return output
    
    def _format_inline(self, text: str) -> str:
        """Format inline markdown (bold, italic, code)"""
        result = text
        
        # Bold (**text**)
        result = re.sub(
            r'\*\*([^\*]+)\*\*',
            lambda m: Color.bold() + m.group(1) + Color.reset(),
            result
        )
        
        # Italic (*text*)
        result = re.sub(
            r'\*([^\*]+)\*',
            lambda m: Color.italic() + m.group(1) + Color.reset(),
            result
        )
        
        # Inline code (`code`)
        result = re.sub(
            r'`([^`]+)`',
            lambda m: Color.bg_rgb(40, 45, 50) + Color.rgb(200, 255, 200) + m.group(1) + Color.reset(),
            result
        )
        
        # Links [text](url)
        result = re.sub(
            r'\[([^\]]+)\]\(([^\)]+)\)',
            lambda m: Color.rgb(100, 180, 255) + Color.underline() + m.group(1) + Color.reset(),
            result
        )
        
        return result

# ============================================================================
# MORE BUILT-IN PLUGINS
# ============================================================================

class GitPlugin(Plugin):
    """Git integration plugin"""
    
    def __init__(self):
        super().__init__("git", "1.0")
        self.current_branch = self._get_current_branch()
        self.has_changes = False
    
    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""
    
    def _check_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return bool(result.stdout.strip())
        except:
            pass
        return False
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Render git status"""
        if not self.current_branch:
            return []
        
        output = []
        width = context.get('width', 80)
        height = context.get('height', 24)
        
        # Update status
        self.has_changes = self._check_changes()
        
        # Position in top-left corner
        x = 5
        y = 2
        
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(150, 200, 255))
        output.append("⎇  ")
        output.append(Color.rgb(255, 255, 255))
        output.append(self.current_branch)
        
        if self.has_changes:
            output.append(" ")
            output.append(Color.rgb(255, 200, 100))
            output.append("●")
        
        output.append(Color.reset())
        
        return output
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle git commands"""
        if command.startswith("git "):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Update branch info
                self.current_branch = self._get_current_branch()
                
                output = ""
                if result.stdout:
                    output += result.stdout
                if result.stderr:
                    output += result.stderr
                
                return output if output else "Command executed successfully"
            except subprocess.TimeoutExpired:
                return "Git command timed out"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return None

class NetworkMonitorPlugin(Plugin):
    """Network monitoring plugin"""
    
    def __init__(self):
        super().__init__("netmon", "1.0")
        self.last_check = 0.0
        self.interfaces: Dict[str, Dict[str, int]] = {}
        self.update_interval = 2.0
    
    def _get_network_stats(self) -> Dict[str, Dict[str, int]]:
        """Get network statistics"""
        stats = {}
        
        try:
            # Read /proc/net/dev
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip headers
                
                for line in lines:
                    parts = line.split(':')
                    if len(parts) != 2:
                        continue
                    
                    interface = parts[0].strip()
                    values = parts[1].split()
                    
                    if len(values) >= 9:
                        stats[interface] = {
                            'rx_bytes': int(values[0]),
                            'tx_bytes': int(values[8])
                        }
        except:
            pass
        
        return stats
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle network monitoring commands"""
        if command.strip() == "netmon":
            stats = self._get_network_stats()
            
            if not stats:
                return "No network statistics available"
            
            lines = ["Network Interfaces:"]
            for interface, data in stats.items():
                rx_mb = data['rx_bytes'] / (1024 * 1024)
                tx_mb = data['tx_bytes'] / (1024 * 1024)
                lines.append(f"  {interface}: RX={rx_mb:.2f}MB TX={tx_mb:.2f}MB")
            
            return "\n".join(lines)
        
        return None

class CPUMonitorPlugin(Plugin):
    """CPU monitoring plugin"""
    
    def __init__(self):
        super().__init__("cpumon", "1.0")
        self.position = (0.5, 0.05)
        self.history: deque = deque(maxlen=50)
        self.last_update = 0.0
        self.update_interval = 1.0
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                values = [int(x) for x in line.split()[1:]]
                
                total = sum(values)
                idle = values[3]
                
                if hasattr(self, '_last_total'):
                    total_diff = total - self._last_total
                    idle_diff = idle - self._last_idle
                    
                    if total_diff > 0:
                        usage = 100 * (total_diff - idle_diff) / total_diff
                    else:
                        usage = 0
                else:
                    usage = 0
                
                self._last_total = total
                self._last_idle = idle
                
                return usage
        except:
            return 0.0
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Render CPU monitor"""
        current_time = context.get('time', 0)
        
        # Update if needed
        if current_time - self.last_update >= self.update_interval:
            usage = self._get_cpu_usage()
            self.history.append(usage)
            self.last_update = current_time
        
        if not self.history:
            return []
        
        output = []
        width = context.get('width', 80)
        height = context.get('height', 24)
        
        x = int(width * self.position[0]) - 10
        y = int(height * self.position[1])
        
        # Current usage
        current_usage = self.history[-1] if self.history else 0
        
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(200, 150, 255))
        output.append("CPU: ")
        
        # Color based on usage
        if current_usage < 50:
            color = (100, 255, 150)
        elif current_usage < 80:
            color = (255, 200, 100)
        else:
            color = (255, 100, 100)
        
        output.append(Color.rgb(*color))
        output.append(Color.bold())
        output.append(f"{current_usage:.1f}%")
        output.append(Color.reset())
        
        # Mini graph
        graph_width = 20
        if len(self.history) > 1:
            output.append(Cursor.move(x, y + 1))
            
            for i, usage in enumerate(list(self.history)[-graph_width:]):
                bar_height = int(usage / 100 * 3)
                
                if bar_height >= 3:
                    char = '█'
                elif bar_height >= 2:
                    char = '▓'
                elif bar_height >= 1:
                    char = '▒'
                else:
                    char = '░'
                
                t = usage / 100
                color = Color.gradient((100, 255, 150), (255, 100, 100), t)
                output.append(Color.rgb(*color))
                output.append(char)
        
        output.append(Color.reset())
        return output
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle CPU monitor commands"""
        if command.strip() == "cpu":
            if self.history:
                avg = sum(self.history) / len(self.history)
                current = self.history[-1]
                max_usage = max(self.history)
                
                return f"CPU Usage: Current={current:.1f}% Avg={avg:.1f}% Max={max_usage:.1f}%"
            return "No CPU data available"
        
        return None

class MemoryMonitorPlugin(Plugin):
    """Memory monitoring plugin"""
    
    def __init__(self):
        super().__init__("memmon", "1.0")
        self.position = (0.7, 0.05)
        self.last_update = 0.0
        self.update_interval = 2.0
        self.mem_usage = 0.0
    
    def _get_memory_usage(self) -> Tuple[float, int, int]:
        """Get memory usage (percentage, used MB, total MB)"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                
                mem_total = 0
                mem_available = 0
                
                for line in lines:
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1])
                
                if mem_total > 0:
                    mem_used = mem_total - mem_available
                    percentage = (mem_used / mem_total) * 100
                    return percentage, mem_used // 1024, mem_total // 1024
        except:
            pass
        
        return 0.0, 0, 0
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Render memory monitor"""
        current_time = context.get('time', 0)
        
        # Update if needed
        if current_time - self.last_update >= self.update_interval:
            self.mem_usage, used_mb, total_mb = self._get_memory_usage()
            self.last_update = current_time
        
        output = []
        width = context.get('width', 80)
        height = context.get('height', 24)
        
        x = int(width * self.position[0])
        y = int(height * self.position[1])
        
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(150, 200, 255))
        output.append("MEM: ")
        
        # Color based on usage
        if self.mem_usage < 50:
            color = (100, 255, 150)
        elif self.mem_usage < 80:
            color = (255, 200, 100)
        else:
            color = (255, 100, 100)
        
        output.append(Color.rgb(*color))
        output.append(Color.bold())
        output.append(f"{self.mem_usage:.1f}%")
        output.append(Color.reset())
        
        output.append(Color.reset())
        return output
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle memory monitor commands"""
        if command.strip() == "mem":
            percentage, used_mb, total_mb = self._get_memory_usage()
            return f"Memory: {used_mb}MB / {total_mb}MB ({percentage:.1f}%)"
        
        return None

class TodoPlugin(Plugin):
    """TODO list plugin"""
    
    def __init__(self):
        super().__init__("todo", "1.0")
        self.todos: List[Tuple[str, bool]] = []
        self.visible = False
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle TODO commands"""
        parts = command.strip().split(maxsplit=1)
        
        if not parts or parts[0] != "todo":
            return None
        
        if len(parts) == 1:
            # List todos
            if not self.todos:
                return "No TODOs"
            
            lines = ["TODO List:"]
            for i, (task, done) in enumerate(self.todos):
                status = "✓" if done else " "
                lines.append(f"  [{status}] {i+1}. {task}")
            
            return "\n".join(lines)
        
        action = parts[1].split()[0] if parts[1] else ""
        
        if action == "add" and len(parts[1].split(maxsplit=1)) > 1:
            task = parts[1].split(maxsplit=1)[1]
            self.todos.append((task, False))
            return f"Added TODO: {task}"
        
        elif action == "done" and len(parts[1].split()) > 1:
            try:
                index = int(parts[1].split()[1]) - 1
                if 0 <= index < len(self.todos):
                    task, _ = self.todos[index]
                    self.todos[index] = (task, True)
                    return f"Marked as done: {task}"
                return "Invalid TODO number"
            except ValueError:
                return "Invalid number"
        
        elif action == "remove" and len(parts[1].split()) > 1:
            try:
                index = int(parts[1].split()[1]) - 1
                if 0 <= index < len(self.todos):
                    task, _ = self.todos.pop(index)
                    return f"Removed TODO: {task}"
                return "Invalid TODO number"
            except ValueError:
                return "Invalid number"
        
        elif action == "clear":
            count = len(self.todos)
            self.todos.clear()
            return f"Cleared {count} TODOs"
        
        return "Usage: todo [add TEXT|done N|remove N|clear]"

class TimerPlugin(Plugin):
    """Timer/stopwatch plugin"""
    
    def __init__(self):
        super().__init__("timer", "1.0")
        self.start_time: Optional[float] = None
        self.elapsed = 0.0
        self.running = False
        self.position = (0.9, 0.9)
    
    def on_command(self, command: str) -> Optional[str]:
        """Handle timer commands"""
        parts = command.strip().split()
        
        if not parts or parts[0] != "timer":
            return None
        
        if len(parts) == 1:
            if self.running:
                elapsed = time.time() - self.start_time + self.elapsed
                return f"Timer running: {self._format_time(elapsed)}"
            else:
                return f"Timer stopped: {self._format_time(self.elapsed)}"
        
        action = parts[1]
        
        if action == "start":
            if not self.running:
                self.start_time = time.time()
                self.running = True
                return "Timer started"
            return "Timer already running"
        
        elif action == "stop":
            if self.running:
                self.elapsed += time.time() - self.start_time
                self.running = False
                return f"Timer stopped: {self._format_time(self.elapsed)}"
            return "Timer not running"
        
        elif action == "reset":
            self.start_time = time.time() if self.running else None
            self.elapsed = 0.0
            return "Timer reset"
        
        return "Usage: timer [start|stop|reset]"
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def on_render(self, context: Dict[str, Any]) -> List[str]:
        """Render timer"""
        if not self.running and self.elapsed == 0:
            return []
        
        output = []
        width = context.get('width', 80)
        height = context.get('height', 24)
        
        x = int(width * self.position[0]) - 10
        y = int(height * self.position[1])
        
        if self.running:
            elapsed = time.time() - self.start_time + self.elapsed
        else:
            elapsed = self.elapsed
        
        time_str = self._format_time(elapsed)
        
        output.append(Cursor.move(x, y))
        output.append(Color.rgb(255, 200, 100))
        output.append("⏱  ")
        output.append(Color.rgb(255, 255, 255))
        output.append(Color.bold())
        output.append(time_str)
        output.append(Color.reset())
        
        return output

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_bytes(bytes_value: int) -> str:
    """Format bytes as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def format_duration(seconds: float) -> str:
    """Format duration as human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def truncate_string(s: str, max_length: int, ellipsis: str = "...") -> str:
    """Truncate string if too long"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(ellipsis)] + ellipsis

def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to specified width"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_len = len(word) + (1 if current_line else 0)
        
        if current_length + word_len <= width:
            current_line.append(word)
            current_length += word_len
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def parse_color(color_string: str) -> Optional[Tuple[int, int, int]]:
    """Parse color from string (hex or rgb format)"""
    color_string = color_string.strip()
    
    # Hex format (#RRGGBB or #RGB)
    if color_string.startswith('#'):
        hex_str = color_string[1:]
        
        if len(hex_str) == 6:
            try:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return (r, g, b)
            except ValueError:
                pass
        elif len(hex_str) == 3:
            try:
                r = int(hex_str[0] * 2, 16)
                g = int(hex_str[1] * 2, 16)
                b = int(hex_str[2] * 2, 16)
                return (r, g, b)
            except ValueError:
                pass
    
    # RGB format (r,g,b)
    if ',' in color_string:
        try:
            parts = [int(p.strip()) for p in color_string.split(',')]
            if len(parts) == 3:
                r, g, b = parts
                if all(0 <= c <= 255 for c in [r, g, b]):
                    return (r, g, b)
        except ValueError:
            pass
    
    return None

def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate 2D distance between two points"""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)

def angle_between(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle between two points (in radians)"""
    return math.atan2(y2 - y1, x2 - x1)

def rotate_point(x: float, y: float, cx: float, cy: float, angle: float) -> Tuple[float, float]:
    """Rotate point around center"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate to origin
    dx = x - cx
    dy = y - cy
    
    # Rotate
    rx = dx * cos_a - dy * sin_a
    ry = dx * sin_a + dy * cos_a
    
    # Translate back
    return (rx + cx, ry + cy)

def bezier_curve(points: List[Tuple[float, float]], t: float) -> Tuple[float, float]:
    """Calculate point on Bezier curve"""
    n = len(points) - 1
    
    if n == 0:
        return points[0]
    
    # De Casteljau's algorithm
    temp_points = points.copy()
    
    for i in range(n):
        new_points = []
        for j in range(len(temp_points) - 1):
            x1, y1 = temp_points[j]
            x2, y2 = temp_points[j + 1]
            
            x = x1 * (1 - t) + x2 * t
            y = y1 * (1 - t) + y2 * t
            
            new_points.append((x, y))
        
        temp_points = new_points
    
    return temp_points[0]

def generate_gradient_palette(color1: Tuple[int, int, int], color2: Tuple[int, int, int], steps: int) -> List[Tuple[int, int, int]]:
    """Generate a gradient color palette"""
    palette = []
    
    for i in range(steps):
        t = i / max(steps - 1, 1)
        color = Color.gradient(color1, color2, t)
        palette.append(color)
    
    return palette

def create_rainbow_palette(steps: int) -> List[Tuple[int, int, int]]:
    """Create a rainbow color palette"""
    palette = []
    
    for i in range(steps):
        hue = (i / steps) * 360
        
        # Convert HSV to RGB (S=1, V=1)
        h = hue / 60.0
        i_part = int(h)
        f = h - i_part
        
        if i_part == 0:
            r, g, b = 1.0, f, 0.0
        elif i_part == 1:
            r, g, b = 1.0 - f, 1.0, 0.0
        elif i_part == 2:
            r, g, b = 0.0, 1.0, f
        elif i_part == 3:
            r, g, b = 0.0, 1.0 - f, 1.0
        elif i_part == 4:
            r, g, b = f, 0.0, 1.0
        else:
            r, g, b = 1.0, 0.0, 1.0 - f
        
        palette.append((int(r * 255), int(g * 255), int(b * 255)))
    
    return palette

# ============================================================================
# COMPREHENSIVE DOCUMENTATION AND EXAMPLES
# ============================================================================

"""
ADVANCED TERMINAL UI - COMPREHENSIVE FEATURE GUIDE

This is a feature-rich terminal user interface application with extensive capabilities.

## CORE FEATURES:

1. **Terminal Emulation**
   - Full command execution with persistent output
   - Command history with navigation (Up/Down arrows)
   - Intelligent autocomplete with suggestions
   - Multi-line output support with scrolling
   - Search functionality through output history

2. **Menu System**
   - Persistent menu bar (always visible)
   - Gradient-styled borders
   - Context-sensitive menu items
   - Keyboard shortcuts for all actions

3. **Visual Effects**
   - GLSL/HLSL-inspired shader system
   - Multi-layer parallax star field background
   - 3D Christmas tree with:
     * Realistic lighting and shadows
     * Animated glowing lights
     * Falling snow particles
     * Rotating directional lighting
   - Bloom and vignette post-processing effects
   - Smooth animations and transitions

4. **Input System**
   - Full cursor movement (arrows, Home, End, Ctrl+arrows)
   - Word-based navigation
   - Line editing commands (Ctrl+U, Ctrl+W)
   - Macro recording and playback
   - Custom keybinding support

5. **Plugin System**
   - Extensible plugin architecture
   - Built-in plugins:
     * Clock display
     * Weather information
     * Git status indicator
     * CPU/Memory monitors
     * TODO list manager
     * Timer/Stopwatch
     * System information
     * Network monitoring

6. **Session Management**
   - Multiple terminal sessions
   - Tab support with switching
   - Per-session history and environment
   - Session persistence

7. **Theme System**
   - Multiple built-in themes:
     * Default
     * Dark
     * Light
     * Christmas
     * Cyberpunk
   - Custom theme support
   - Runtime theme switching

8. **Configuration**
   - JSON-based configuration file
   - Runtime configuration changes
   - Persistent settings
   - Per-user customization

9. **Advanced Components**
   - File browser with navigation
   - Text editor with syntax highlighting
   - Progress bars and indicators
   - Modal dialogs
   - Context menus
   - Tooltips
   - Notifications

10. **Rendering System**
    - Multi-layer rendering engine
    - Braille graphics for high-resolution drawing
    - ASCII art support with coloring
    - Markdown rendering
    - Chart and graph rendering
    - Syntax highlighting for code

## KEYBOARD SHORTCUTS:

Global:
- F8              - Toggle menu bar
- F9              - Toggle autocorrect panel
- F10             - Clear screen
- Ctrl+C          - Exit application

Navigation:
- Up/Down         - Command history
- Left/Right      - Move cursor
- Home/End        - Start/End of line
- Ctrl+Left/Right - Jump by word
- Ctrl+A          - Beginning of line
- Ctrl+E          - End of line

Editing:
- Backspace       - Delete character
- Delete          - Delete forward
- Ctrl+U          - Clear line
- Ctrl+W          - Delete word
- Tab             - Accept suggestion
- Enter           - Execute command

## BUILT-IN COMMANDS:

System:
- help            - Show command help
- clear           - Clear terminal output
- exit            - Exit application
- about           - About this application

Configuration:
- theme [name]    - Change theme
- config get KEY  - Get configuration value
- config set KEY VALUE - Set configuration value
- fps [value]     - Show/set frame rate

Session Management:
- session         - List sessions
- session new [name] - Create new session
- session switch ID  - Switch to session
- tab             - List tabs
- tab new [name]  - Create new tab
- tab next/prev   - Switch tabs

Utilities:
- search QUERY    - Search through output
- copy TEXT       - Copy to clipboard
- paste           - Paste from clipboard
- notify MESSAGE [type] - Show notification
- history         - Show command history

Plugins:
- plugin list     - List loaded plugins
- sysinfo         - Show system information
- cpu             - Show CPU usage
- mem             - Show memory usage
- netmon          - Show network statistics
- todo [action]   - Manage TODO list
- timer [action]  - Control timer

Macros and Scripts:
- macro record NAME - Start recording macro
- macro stop TRIGGER - Stop recording
- script load FILE  - Load script file
- script run NAME   - Run loaded script

## ADVANCED FEATURES:

### Shader System
The application uses a custom shader system inspired by GLSL/HLSL for advanced visual effects:

- **Parallax Shader**: Multi-layer star field with depth and movement
- **Christmas Tree Shader**: 3D-lit tree with realistic shading
- **Snow Shader**: Particle-based snow effect
- **Post-Processing**: Bloom, vignette, and other effects

### Particle System
Fully-featured particle system with:
- Multiple emitters
- Physics simulation (gravity, velocity)
- Particle life management
- Color and size control
- Custom rendering

### Rendering Pipeline
Multi-stage rendering with:
- Layer-based composition
- Z-index sorting
- Alpha blending
- Multiple blend modes
- Efficient caching

### Plugin Development
Create custom plugins by extending the Plugin class:

```python
class MyPlugin(Plugin):
    def __init__(self):
        super().__init__("myplugin", "1.0")
    
    def on_command(self, command):
        # Handle custom commands
        pass
    
    def on_render(self, context):
        # Render custom content
        return []
    
    def on_input(self, key):
        # Handle custom input
        return False
```

### Custom Commands
Add custom commands by extending ExtendedCommandExecutor:

```python
def my_custom_command(self, command: Command) -> str:
    # Process command
    return "Result"

# Register command
self.commands['mycommand'] = my_custom_command
```

## CONFIGURATION FILE FORMAT:

~/.tui_config.json:
```json
{
  "theme": "default",
  "fps": 60,
  "enable_shaders": true,
  "enable_particles": true,
  "enable_animations": true,
  "show_welcome": true,
  "shell": "/bin/bash"
}
```

## PERFORMANCE CONSIDERATIONS:

- Adaptive FPS control
- Efficient rendering with dirty rectangles
- Layer caching
- Shader optimization
- Particle count management
- Memory usage monitoring

## TROUBLESHOOTING:

1. **Menu bar not visible**:
   - Press F8 to toggle
   - Check Config.MENU_ALWAYS_VISIBLE setting

2. **Commands not executing**:
   - Check shell configuration
   - Verify PATH environment variable
   - Review error logs in /tmp/tui_error.log

3. **Visual glitches**:
   - Reduce FPS with 'fps' command
   - Disable shaders in config
   - Resize terminal window

4. **Performance issues**:
   - Disable particle effects
   - Reduce parallax layers
   - Lower update rate for plugins
   - Check CPU/memory usage

## DEVELOPMENT:

Architecture:
- Component-based design
- Event-driven input handling
- Modular plugin system
- Extensible theming
- Clean separation of concerns

Code Structure:
- Config: Global configuration
- Color/Cursor/Screen: Terminal utilities
- Shader System: Visual effects
- UI Components: Reusable widgets
- Managers: Session, Theme, Plugin, etc.
- Application: Main orchestration

## CREDITS:

- Braille graphics system
- ANSI escape sequence handling
- Terminal manipulation
- Event-driven architecture
- Plugin system design
- Rendering pipeline
- Shader concept adaptation

## LICENSE:

This software is provided as-is for educational and demonstration purposes.

## VERSION HISTORY:

v2.0:
- Complete rewrite with advanced features
- Shader system implementation
- Plugin architecture
- Multi-session support
- Enhanced theming
- Improved performance

v1.0:
- Initial release
- Basic terminal emulation
- Simple Christmas tree animation

## FUTURE ENHANCEMENTS:

Planned features:
- Remote session support (SSH)
- Split-pane terminal
- Recording and playback
- Advanced scripting language
- More built-in plugins
- Custom widget system
- Network-based themes
- Cloud synchronization
- AI-powered suggestions
- Collaborative editing
"""

# ============================================================================
# ERROR HANDLING AND DEBUGGING
# ============================================================================

class DebugOverlay:
    """Debug information overlay"""
    
    def __init__(self):
        self.visible = False
        self.metrics: Dict[str, Any] = {}
    
    def toggle(self):
        """Toggle debug overlay"""
        self.visible = not self.visible
    
    def update_metric(self, key: str, value: Any):
        """Update a debug metric"""
        self.metrics[key] = value
    
    def render(self, x: int, y: int) -> List[str]:
        """Render debug overlay"""
        if not self.visible:
            return []
        
        output = []
        current_y = y
        
        # Background
        output.append(Cursor.move(x, current_y))
        output.append(Color.bg_rgb(20, 20, 30))
        output.append(Color.rgb(200, 200, 220))
        output.append(" DEBUG INFO ")
        output.append(Color.reset())
        current_y += 1
        
        # Metrics
        for key, value in self.metrics.items():
            output.append(Cursor.move(x, current_y))
            output.append(Color.bg_rgb(15, 15, 25))
            output.append(Color.rgb(150, 180, 200))
            output.append(f" {key}: {value} ")
            output.append(Color.reset())
            current_y += 1
        
        return output

class ErrorHandler:
    """Global error handler"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.errors: deque = deque(maxlen=100)
    
    def handle_error(self, error: Exception, context: str = ""):
        """Handle an error"""
        error_info = {
            'timestamp': time.time(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.errors.append(error_info)
        self.logger.error(f"{context}: {str(error)}")
    
    def get_recent_errors(self, count: int = 10) -> List[Dict]:
        """Get recent errors"""
        return list(self.errors)[-count:]
    
    def clear_errors(self):
        """Clear error history"""
        self.errors.clear()

# ============================================================================
# DATA PERSISTENCE
# ============================================================================

class DataStore:
    """Simple key-value data store with persistence"""
    
    def __init__(self, filename: str = "~/.tui_data.json"):
        self.filename = os.path.expanduser(filename)
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load data from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.data = json.load(f)
        except Exception:
            self.data = {}
    
    def save(self):
        """Save data to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set value"""
        self.data[key] = value
        self.save()
    
    def delete(self, key: str):
        """Delete value"""
        if key in self.data:
            del self.data[key]
            self.save()
    
    def keys(self) -> List[str]:
        """Get all keys"""
        return list(self.data.keys())
    
    def clear(self):
        """Clear all data"""
        self.data.clear()
        self.save()

# ============================================================================
# EXTENDED UTILITY FUNCTIONS
# ============================================================================

def calculate_text_width(text: str) -> int:
    """Calculate display width of text (handling ANSI codes)"""
    # Remove ANSI escape sequences
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    clean_text = ansi_pattern.sub('', text)
    return len(clean_text)

def pad_string(text: str, width: int, align: str = 'left', fill_char: str = ' ') -> str:
    """Pad string to specified width"""
    text_width = calculate_text_width(text)
    padding_needed = max(0, width - text_width)
    
    if align == 'left':
        return text + fill_char * padding_needed
    elif align == 'right':
        return fill_char * padding_needed + text
    elif align == 'center':
        left_pad = padding_needed // 2
        right_pad = padding_needed - left_pad
        return fill_char * left_pad + text + fill_char * right_pad
    
    return text

def create_table(headers: List[str], rows: List[List[str]], 
                col_widths: Optional[List[int]] = None) -> List[str]:
    """Create formatted table"""
    if not headers or not rows:
        return []
    
    # Calculate column widths if not provided
    if col_widths is None:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Create table
    table_lines = []
    
    # Top border
    table_lines.append('┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐')
    
    # Headers
    header_row = '│'
    for i, header in enumerate(headers):
        if i < len(col_widths):
            header_row += f" {header:<{col_widths[i]}} │"
    table_lines.append(header_row)
    
    # Header separator
    table_lines.append('├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤')
    
    # Data rows
    for row in rows:
        row_str = '│'
        for i, cell in enumerate(row):
            if i < len(col_widths):
                row_str += f" {str(cell):<{col_widths[i]}} │"
        table_lines.append(row_str)
    
    # Bottom border
    table_lines.append('└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘')
    
    return table_lines

def format_table_for_display(headers: List[str], rows: List[List[str]], 
                             x: int, y: int, colors: Optional[Dict[str, Tuple[int, int, int]]] = None) -> List[str]:
    """Format table with colors for terminal display"""
    if colors is None:
        colors = {
            'header': (100, 180, 255),
            'border': (150, 150, 170),
            'data': (220, 220, 230)
        }
    
    output = []
    table_lines = create_table(headers, rows)
    
    for i, line in enumerate(table_lines):
        output.append(Cursor.move(x, y + i))
        
        if i == 0 or i == len(table_lines) - 1:
            # Borders
            output.append(Color.rgb(*colors['border']))
        elif i == 1:
            # Header
            output.append(Color.rgb(*colors['header']))
            output.append(Color.bold())
        elif i == 2:
            # Header separator
            output.append(Color.rgb(*colors['border']))
        else:
            # Data
            output.append(Color.rgb(*colors['data']))
        
        output.append(line)
        output.append(Color.reset())
    
    return output

def create_ascii_box(width: int, height: int, title: str = "", style: str = "double") -> List[str]:
    """Create ASCII box with title"""
    if style == "double":
        chars = {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 'h': '═', 'v': '║'}
    elif style == "rounded":
        chars = {'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'h': '─', 'v': '│'}
    else:
        chars = {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'h': '─', 'v': '│'}
    
    lines = []
    
    # Top line with title
    if title:
        title_str = f" {title} "
        padding = (width - 2 - len(title_str)) // 2
        top_line = chars['tl'] + chars['h'] * padding + title_str
        top_line += chars['h'] * (width - 2 - padding - len(title_str)) + chars['tr']
    else:
        top_line = chars['tl'] + chars['h'] * (width - 2) + chars['tr']
    
    lines.append(top_line)
    
    # Middle lines
    for _ in range(height - 2):
        lines.append(chars['v'] + ' ' * (width - 2) + chars['v'])
    
    # Bottom line
    lines.append(chars['bl'] + chars['h'] * (width - 2) + chars['br'])
    
    return lines

def parse_ansi_color(code: str) -> Optional[Tuple[int, int, int]]:
    """Parse ANSI color code to RGB"""
    # Parse sequences like \x1b[38;2;R;G;Bm
    match = re.match(r'\\x1b\[38;2;(\d+);(\d+);(\d+)m', code)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return None

def generate_box_drawing_art(text: str, padding: int = 2) -> List[str]:
    """Generate box drawing art around text"""
    lines = text.split('\n')
    max_width = max(len(line) for line in lines) if lines else 0
    box_width = max_width + (padding * 2)
    
    art_lines = []
    
    # Top
    art_lines.append('╔' + '═' * box_width + '╗')
    
    # Padding top
    for _ in range(padding):
        art_lines.append('║' + ' ' * box_width + '║')
    
    # Content
    for line in lines:
        padded_line = ' ' * padding + line.ljust(max_width) + ' ' * padding
        art_lines.append('║' + padded_line + '║')
    
    # Padding bottom
    for _ in range(padding):
        art_lines.append('║' + ' ' * box_width + '║')
    
    # Bottom
    art_lines.append('╚' + '═' * box_width + '╝')
    
    return art_lines

def create_progress_indicator(percentage: float, width: int, style: str = "bar") -> str:
    """Create progress indicator string"""
    percentage = clamp(percentage, 0.0, 1.0)
    
    if style == "bar":
        filled = int(width * percentage)
        empty = width - filled
        return '█' * filled + '░' * empty
    
    elif style == "dots":
        dots = ['⠀', '⠁', '⠃', '⠇', '⠏', '⠟', '⠿', '⡿', '⣿']
        filled = int(width * percentage)
        partial = int((width * percentage - filled) * len(dots))
        
        result = '⣿' * filled
        if partial > 0 and filled < width:
            result += dots[partial]
        result += '⠀' * max(0, width - filled - 1)
        
        return result
    
    elif style == "blocks":
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        result = ''
        
        for i in range(width):
            pos = i / width
            if pos < percentage:
                block_index = int((percentage - pos) * width / len(blocks))
                block_index = min(block_index, len(blocks) - 1)
                result += blocks[block_index]
            else:
                result += ' '
        
        return result
    
    return '█' * int(width * percentage) + '░' * (width - int(width * percentage))

def create_sparkline(data: List[float], width: int) -> str:
    """Create sparkline visualization"""
    if not data or width <= 0:
        return ''
    
    # Normalize data
    min_val = min(data)
    max_val = max(data)
    value_range = max_val - min_val
    
    if value_range == 0:
        value_range = 1
    
    # Sparkline characters (0-7 height levels)
    chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    # Sample data to fit width
    if len(data) > width:
        step = len(data) / width
        sampled_data = [data[int(i * step)] for i in range(width)]
    else:
        sampled_data = data
    
    # Create sparkline
    result = ''
    for value in sampled_data:
        normalized = (value - min_val) / value_range
        char_index = int(normalized * (len(chars) - 1))
        char_index = clamp(char_index, 0, len(chars) - 1)
        result += chars[char_index]
    
    return result

def create_histogram(data: List[float], bins: int = 10, width: int = 50, height: int = 10) -> List[str]:
    """Create ASCII histogram"""
    if not data:
        return []
    
    # Calculate bins
    min_val = min(data)
    max_val = max(data)
    value_range = max_val - min_val
    
    if value_range == 0:
        return ['No variation in data']
    
    bin_width = value_range / bins
    bin_counts = [0] * bins
    
    # Count values in each bin
    for value in data:
        bin_index = int((value - min_val) / bin_width)
        bin_index = min(bin_index, bins - 1)
        bin_counts[bin_index] += 1
    
    # Normalize to height
    max_count = max(bin_counts)
    if max_count == 0:
        max_count = 1
    
    # Create histogram
    lines = []
    
    for h in range(height, 0, -1):
        line = ''
        threshold = (h / height) * max_count
        
        for count in bin_counts:
            if count >= threshold:
                line += '█'
            else:
                line += ' '
        
        lines.append(line)
    
    # Add axis
    lines.append('─' * bins)
    
    # Add labels
    label_line = f"{min_val:.1f}"
    label_line += ' ' * (bins - len(f"{min_val:.1f}") - len(f"{max_val:.1f}"))
    label_line += f"{max_val:.1f}"
    lines.append(label_line)
    
    return lines

def interpolate(a: float, b: float, t: float, method: str = 'linear') -> float:
    """Interpolate between two values using various methods"""
    t = clamp(t, 0.0, 1.0)
    
    if method == 'linear':
        return a + (b - a) * t
    elif method == 'smooth':
        return a + (b - a) * smoothstep(0, 1, t)
    elif method == 'ease_in':
        return a + (b - a) * (t * t)
    elif method == 'ease_out':
        return a + (b - a) * (t * (2 - t))
    elif method == 'ease_in_out':
        if t < 0.5:
            return a + (b - a) * (2 * t * t)
        else:
            return a + (b - a) * (-1 + (4 - 2 * t) * t)
    else:
        return lerp(a, b, t)

def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Map value from one range to another"""
    return out_min + (out_max - out_min) * ((value - in_min) / (in_max - in_min))

def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to 0-1 range"""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

def denormalize_value(normalized: float, min_val: float, max_val: float) -> float:
    """Convert normalized value back to original range"""
    return min_val + (max_val - min_val) * normalized

def calculate_checksum(data: str) -> str:
    """Calculate checksum of data"""
    return hashlib.sha256(data.encode()).hexdigest()[:8]

def validate_json(text: str) -> bool:
    """Validate JSON string"""
    try:
        json.loads(text)
        return True
    except:
        return False

def format_json(text: str, indent: int = 2) -> str:
    """Format JSON with indentation"""
    try:
        data = json.loads(text)
        return json.dumps(data, indent=indent)
    except:
        return text

def escape_string(text: str) -> str:
    """Escape special characters in string"""
    replacements = {
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '"': '\\"',
        '\\': '\\\\',
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result

def unescape_string(text: str) -> str:
    """Unescape special characters in string"""
    replacements = {
        '\\n': '\n',
        '\\r': '\r',
        '\\t': '\t',
        '\\"': '"',
        '\\\\': '\\',
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result

# ===========================================================================
# COMPREHENSIVE EXAMPLES AND TEST DATA
# ============================================================================

# Example ASCII art for demonstration
EXAMPLE_ASCII_ART = {
    'tree': """
        *
       /|\\
      /*|O\\
     /*/|\\*\\
    /X/O|*\\X\\
       |X|
       |X|
    """,
    
    'welcome': """
╔══════════════════════════════════════════╗
║   WELCOME TO ADVANCED TERMINAL UI   ║
║                                          ║
║   Type 'help' for available commands     ║
╚══════════════════════════════════════════╝
    """,
    
    'logo': """
 ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌ ▀▀▀▀█░█▀▀▀▀ 
▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌     
▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌     ▐░▌     
▐░░░░░░░░░░░▌▐░▌       ▐░▌     ▐░▌     
▐░█▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌     ▐░▌     
▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌     
▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄█░▌ ▄▄▄▄█░█▄▄▄▄ 
▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀ 
    """,
}

# Example color palettes
COLOR_PALETTES = {
    'ocean': [
        (13, 27, 42),
        (27, 38, 59),
        (65, 90, 119),
        (119, 141, 169),
        (224, 251, 252)
    ],
    'sunset': [
        (25, 25, 112),
        (138, 43, 226),
        (255, 99, 71),
        (255, 165, 0),
        (255, 215, 0)
    ],
    'forest': [
        (34, 139, 34),
        (85, 107, 47),
        (107, 142, 35),
        (154, 205, 50),
        (173, 255, 47)
    ],
    'fire': [
        (139, 0, 0),
        (178, 34, 34),
        (220, 20, 60),
        (255, 69, 0),
        (255, 140, 0)
    ],
}

# Example command templates
COMMAND_TEMPLATES = {
    'git': [
        'git status',
        'git add .',
        'git commit -m "message"',
        'git push origin main',
        'git pull',
        'git log --oneline',
        'git diff',
        'git branch',
    ],
    'docker': [
        'docker ps',
        'docker images',
        'docker build -t name .',
        'docker run -it name',
        'docker exec -it container sh',
        'docker logs container',
        'docker stop container',
    ],
    'system': [
        'ps aux',
        'top',
        'df -h',
        'du -sh *',
        'free -h',
        'uname -a',
        'uptime',
        'who',
    ],
}

# Example keybinding configurations
KEYBINDING_PRESETS = {
    'vim': {
        'h': 'cursor_left',
        'j': 'cursor_down',
        'k': 'cursor_up',
        'l': 'cursor_right',
        '0': 'line_start',
        '$': 'line_end',
        'i': 'insert_mode',
        'a': 'append_mode',
        'dd': 'delete_line',
        'yy': 'copy_line',
        'p': 'paste',
    },
    'emacs': {
        '\x01': 'line_start',  # Ctrl+A
        '\x05': 'line_end',    # Ctrl+E
        '\x02': 'cursor_left',  # Ctrl+B
        '\x06': 'cursor_right', # Ctrl+F
        '\x10': 'history_prev', # Ctrl+P
        '\x0e': 'history_next', # Ctrl+N
        '\x0b': 'delete_to_end', # Ctrl+K
        '\x19': 'paste',        # Ctrl+Y
    },
}

# Example theme configurations
THEME_EXAMPLES = {
    'monokai': {
        'background': (39, 40, 34),
        'foreground': (248, 248, 242),
        'black': (39, 40, 34),
        'red': (249, 38, 114),
        'green': (166, 226, 46),
        'yellow': (244, 191, 117),
        'blue': (102, 217, 239),
        'magenta': (174, 129, 255),
        'cyan': (161, 239, 228),
        'white': (248, 248, 242),
    },
    'solarized_dark': {
        'background': (0, 43, 54),
        'foreground': (131, 148, 150),
        'black': (7, 54, 66),
        'red': (220, 50, 47),
        'green': (133, 153, 0),
        'yellow': (181, 137, 0),
        'blue': (38, 139, 210),
        'magenta': (211, 54, 130),
        'cyan': (42, 161, 152),
        'white': (238, 232, 213),
    },
    'nord': {
        'background': (46, 52, 64),
        'foreground': (216, 222, 233),
        'black': (59, 66, 82),
        'red': (191, 97, 106),
        'green': (163, 190, 140),
        'yellow': (235, 203, 139),
        'blue': (129, 161, 193),
        'magenta': (180, 142, 173),
        'cyan': (136, 192, 208),
        'white': (229, 233, 240),
    },
}

# Example plugin configurations
PLUGIN_EXAMPLES = {
    'weather': {
        'api_key': 'your_api_key',
        'location': 'auto',
        'units': 'metric',
        'update_interval': 3600,
        'display_format': '{temp}°C {condition}',
    },
    'git_status': {
        'show_branch': True,
        'show_changes': True,
        'update_interval': 5,
        'position': (0.05, 0.05),
    },
    'system_monitor': {
        'show_cpu': True,
        'show_memory': True,
        'show_network': False,
        'update_interval': 2,
        'history_size': 50,
    },
}

# Example scripts for automation
SCRIPT_EXAMPLES = {
    'backup': [
        '# Backup script',
        'echo "Starting backup..."',
        'tar -czf backup.tar.gz /important/data',
        'echo "Backup complete!"',
    ],
    'deploy': [
        '# Deployment script',
        'git pull',
        'npm install',
        'npm run build',
        'pm2 restart app',
        'echo "Deployment complete!"',
    ],
    'test': [
        '# Test script',
        'echo "Running tests..."',
        'pytest tests/',
        'npm test',
        'echo "Tests complete!"',
    ],
}

# =======================================================================
# ADDITIONAL HELPER CLASSES
# ============================================================================

class EventBus:
    """Simple event bus for inter-component communication"""
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_name: str, callback: Callable):
        """Subscribe to an event"""
        self.listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """Unsubscribe from an event"""
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)
    
    def emit(self, event_name: str, *args, **kwargs):
        """Emit an event"""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    pass

class TaskQueue:
    """Simple task queue for background operations"""
    
    def __init__(self):
        self.queue: queue.Queue = queue.Queue()
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
    
    def add_task(self, task: Callable, *args, **kwargs):
        """Add a task to the queue"""
        self.queue.put((task, args, kwargs))
    
    def start(self):
        """Start processing tasks"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker)
            self.worker_thread.daemon = True
            self.worker_thread.start()
    
    def stop(self):
        """Stop processing tasks"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
    
    def _worker(self):
        """Worker thread"""
        while self.running:
            try:
                task, args, kwargs = self.queue.get(timeout=0.1)
                task(*args, **kwargs)
            except queue.Empty:
                continue
            except Exception:
                pass

class Cache:
    """Simple LRU cache"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_order: deque = deque()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self.cache:
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value"""
        if key in self.cache:
            # Update existing
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Evict oldest
            oldest = self.access_order.popleft()
            del self.cache[oldest]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

class RateLimiter:
    """Rate limiter for operations"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: deque = deque()
    
    def can_proceed(self) -> bool:
        """Check if operation can proceed"""
        current_time = time.time()
        
        # Remove old calls outside time window
        while self.calls and current_time - self.calls[0] > self.time_window:
            self.calls.popleft()
        
        # Check if under limit
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a call"""
        self.calls.append(time.time())
    
    def try_call(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Try to execute function with rate limiting"""
        if self.can_proceed():
            self.record_call()
            return func(*args, **kwargs)
        return None

class CircularBuffer:
    """Circular buffer implementation"""
    
    def __init__(self, size: int):
        self.size = size
        self.buffer: List[Any] = [None] * size
        self.head = 0
        self.tail = 0
        self.count = 0
    
    def push(self, item: Any):
        """Push item to buffer"""
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.size
        
        if self.count < self.size:
            self.count += 1
        else:
            self.head = (self.head + 1) % self.size
    
    def pop(self) -> Optional[Any]:
        """Pop item from buffer"""
        if self.count == 0:
            return None
        
        item = self.buffer[self.head]
        self.head = (self.head + 1) % self.size
        self.count -= 1
        return item
    
    def peek(self) -> Optional[Any]:
        """Peek at next item without removing"""
        if self.count == 0:
            return None
        return self.buffer[self.head]
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return self.count == 0
    
    def is_full(self) -> bool:
        """Check if buffer is full"""
        return self.count == self.size
    
    def get_all(self) -> List[Any]:
        """Get all items in order"""
        result = []
        idx = self.head
        for _ in range(self.count):
            result.append(self.buffer[idx])
            idx = (idx + 1) % self.size
        return result

class StateMachine:
    """Simple state machine"""
    
    def __init__(self, initial_state: str):
        self.current_state = initial_state
        self.states: Dict[str, Dict[str, Any]] = {}
        self.transitions: Dict[str, Dict[str, str]] = defaultdict(dict)
    
    def add_state(self, name: str, on_enter: Optional[Callable] = None, 
                 on_exit: Optional[Callable] = None):
        """Add a state"""
        self.states[name] = {
            'on_enter': on_enter,
            'on_exit': on_exit,
        }
    
    def add_transition(self, from_state: str, to_state: str, event: str):
        """Add a transition"""
        self.transitions[from_state][event] = to_state
    
    def trigger(self, event: str) -> bool:
        """Trigger an event"""
        if self.current_state in self.transitions:
            if event in self.transitions[self.current_state]:
                new_state = self.transitions[self.current_state][event]
                
                # Exit current state
                if self.current_state in self.states:
                    on_exit = self.states[self.current_state]['on_exit']
                    if on_exit:
                        on_exit()
                
                # Enter new state
                self.current_state = new_state
                if new_state in self.states:
                    on_enter = self.states[new_state]['on_enter']
                    if on_enter:
                        on_enter()
                
                return True
        
        return False
    
    def get_state(self) -> str:
        """Get current state"""
        return self.current_state

class Timer:
    """Simple timer class"""
    
    def __init__(self, duration: float, callback: Optional[Callable] = None):
        self.duration = duration
        self.callback = callback
        self.start_time: Optional[float] = None
        self.remaining = duration
        self.running = False
        self.paused = False
    
    def start(self):
        """Start timer"""
        self.start_time = time.time()
        self.running = True
        self.paused = False
    
    def stop(self):
        """Stop timer"""
        self.running = False
        self.paused = False
        self.remaining = self.duration
    
    def pause(self):
        """Pause timer"""
        if self.running and not self.paused:
            elapsed = time.time() - self.start_time
            self.remaining = max(0, self.duration - elapsed)
            self.paused = True
    
    def resume(self):
        """Resume timer"""
        if self.paused:
            self.start_time = time.time()
            self.duration = self.remaining
            self.paused = False
    
    def update(self) -> bool:
        """Update timer, returns True if finished"""
        if not self.running or self.paused:
            return False
        
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.duration:
            self.running = False
            if self.callback:
                self.callback()
            return True
        
        return False
    
    def get_remaining(self) -> float:
        """Get remaining time"""
        if not self.running:
            return self.remaining
        
        if self.paused:
            return self.remaining
        
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)
    
    def get_progress(self) -> float:
        """Get progress (0.0 to 1.0)"""
        if self.duration == 0:
            return 1.0
        
        remaining = self.get_remaining()
        return 1.0 - (remaining / self.duration)

class Stopwatch:
    """Stopwatch class"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.elapsed_time = 0.0
        self.running = False
        self.laps: List[float] = []
    
    def start(self):
        """Start stopwatch"""
        if not self.running:
            self.start_time = time.time()
            self.running = True
    
    def stop(self):
        """Stop stopwatch"""
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False
    
    def reset(self):
        """Reset stopwatch"""
        self.start_time = time.time() if self.running else None
        self.elapsed_time = 0.0
        self.laps.clear()
    
    def lap(self) -> float:
        """Record lap time"""
        elapsed = self.get_elapsed()
        self.laps.append(elapsed)
        return elapsed
    
    def get_elapsed(self) -> float:
        """Get elapsed time"""
        if self.running:
            return self.elapsed_time + (time.time() - self.start_time)
        return self.elapsed_time
    
    def get_laps(self) -> List[float]:
        """Get lap times"""
        return self.laps.copy()

# ============================================================================
# COMPREHENSIVE COMMAND DOCUMENTATION
# ============================================================================

COMMAND_HELP_DETAILED = {
    'help': {
        'description': 'Show help for available commands',
        'usage': 'help [command]',
        'examples': [
            'help',
            'help theme',
            'help config',
        ],
        'aliases': ['?', 'h'],
    },
    'clear': {
        'description': 'Clear terminal output',
        'usage': 'clear',
        'examples': ['clear'],
        'aliases': ['cls'],
    },
    'exit': {
        'description': 'Exit the application',
        'usage': 'exit',
        'examples': ['exit'],
        'aliases': ['quit', 'q'],
    },
    'theme': {
        'description': 'Manage application themes',
        'usage': 'theme [name]',
        'examples': [
            'theme',
            'theme dark',
            'theme christmas',
        ],
        'available_themes': ['default', 'dark', 'light', 'christmas', 'cyberpunk'],
    },
    'config': {
        'description': 'Manage configuration settings',
        'usage': 'config [get|set] KEY [VALUE]',
        'examples': [
            'config',
            'config get fps',
            'config set fps 120',
        ],
        'settings': ['fps', 'theme', 'enable_shaders', 'enable_particles'],
    },
    'plugin': {
        'description': 'Manage plugins',
        'usage': 'plugin [list|load|unload] [name]',
        'examples': [
            'plugin list',
            'plugin load weather',
            'plugin unload clock',
        ],
    },
    'session': {
        'description': 'Manage terminal sessions',
        'usage': 'session [new|switch|close] [id/name]',
        'examples': [
            'session',
            'session new work',
            'session switch abc123',
        ],
    },
    'tab': {
        'description': 'Manage terminal tabs',
        'usage': 'tab [new|next|prev|close] [name]',
        'examples': [
            'tab',
            'tab new logs',
            'tab next',
            'tab close',
        ],
    },
}

# ============================================================================
# ADDITIONAL COMPREHENSIVE UTILITIES AND EXTENSIONS
# ============================================================================

class AdvancedTextFormatter:
    """Advanced text formatting utilities"""
    
    @staticmethod
    def center_multiline(text: str, width: int) -> List[str]:
        """Center multiple lines of text"""
        lines = text.split('\n')
        centered = []
        for line in lines:
            padding = (width - len(line)) // 2
            centered.append(' ' * padding + line)
        return centered
    
    @staticmethod
    def justify_text(text: str, width: int) -> str:
        """Justify text to width"""
        words = text.split()
        if len(words) <= 1:
            return text
        
        total_chars = sum(len(word) for word in words)
        total_spaces = width - total_chars
        gaps = len(words) - 1
        
        if gaps == 0:
            return text
        
        space_per_gap = total_spaces // gaps
        extra_spaces = total_spaces % gaps
        
        result = []
        for i, word in enumerate(words[:-1]):
            result.append(word)
            result.append(' ' * space_per_gap)
            if i < extra_spaces:
                result.append(' ')
        result.append(words[-1])
        
        return ''.join(result)
    
    @staticmethod
    def word_wrap_advanced(text: str, width: int, indent: int = 0, 
                          first_line_indent: Optional[int] = None) -> List[str]:
        """Advanced word wrapping with indentation"""
        if first_line_indent is None:
            first_line_indent = indent
        
        words = text.split()
        lines = []
        current_line = []
        current_length = first_line_indent
        is_first_line = True
        
        for word in words:
            word_len = len(word)
            space_len = 1 if current_line else 0
            
            if current_length + space_len + word_len <= width:
                if current_line:
                    current_line.append(' ')
                    current_length += 1
                current_line.append(word)
                current_length += word_len
            else:
                if current_line:
                    line_indent = first_line_indent if is_first_line else indent
                    lines.append(' ' * line_indent + ''.join(current_line))
                    is_first_line = False
                
                current_line = [word]
                current_length = indent + word_len
        
        if current_line:
            line_indent = first_line_indent if is_first_line else indent
            lines.append(' ' * line_indent + ''.join(current_line))
        
        return lines
    
    @staticmethod
    def create_columns(data: List[List[str]], widths: List[int], 
                      spacing: int = 2) -> List[str]:
        """Create columnar layout"""
        lines = []
        
        for row in data:
            line_parts = []
            for i, cell in enumerate(row):
                if i < len(widths):
                    # Truncate or pad
                    cell_str = str(cell)
                    if len(cell_str) > widths[i]:
                        cell_str = cell_str[:widths[i]-3] + '...'
                    else:
                        cell_str = cell_str.ljust(widths[i])
                    line_parts.append(cell_str)
            
            lines.append((' ' * spacing).join(line_parts))
        
        return lines
    
    @staticmethod
    def create_tree_view(data: Dict[str, Any], indent: str = "  ", 
                        prefix: str = "") -> List[str]:
        """Create tree view of nested data"""
        lines = []
        
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└─ " if is_last else "├─ "
            
            if isinstance(value, dict):
                lines.append(prefix + connector + str(key) + ":")
                extension = "   " if is_last else "│  "
                lines.extend(AdvancedTextFormatter.create_tree_view(
                    value, indent, prefix + extension
                ))
            else:
                lines.append(prefix + connector + f"{key}: {value}")
        
        return lines

class ColorConverter:
    """Convert between color formats"""
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV"""
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        # Saturation
        s = 0 if max_val == 0 else (diff / max_val)
        
        # Value
        v = max_val
        
        return (h, s, v)
    
    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
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
    
    @staticmethod
    def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSL"""
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Lightness
        l = (max_val + min_val) / 2
        
        # Saturation
        if diff == 0:
            s = 0
            h = 0
        else:
            s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)
            
            # Hue
            if max_val == r:
                h = (60 * ((g - b) / diff) + 360) % 360
            elif max_val == g:
                h = (60 * ((b - r) / diff) + 120) % 360
            else:
                h = (60 * ((r - g) / diff) + 240) % 360
        
        return (h, s, l)
    
    @staticmethod
    def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
        """Convert HSL to RGB"""
        h = h % 360
        
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        
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
    
    @staticmethod
    def complementary_color(r: int, g: int, b: int) -> Tuple[int, int, int]:
        """Get complementary color"""
        h, s, v = ColorConverter.rgb_to_hsv(r, g, b)
        h = (h + 180) % 360
        return ColorConverter.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def analogous_colors(r: int, g: int, b: int, angle: float = 30) -> List[Tuple[int, int, int]]:
        """Get analogous colors"""
        h, s, v = ColorConverter.rgb_to_hsv(r, g, b)
        colors = []
        
        for offset in [-angle, 0, angle]:
            new_h = (h + offset) % 360
            colors.append(ColorConverter.hsv_to_rgb(new_h, s, v))
        
        return colors
    
    @staticmethod
    def triadic_colors(r: int, g: int, b: int) -> List[Tuple[int, int, int]]:
        """Get triadic colors"""
        h, s, v = ColorConverter.rgb_to_hsv(r, g, b)
        colors = []
        
        for offset in [0, 120, 240]:
            new_h = (h + offset) % 360
            colors.append(ColorConverter.hsv_to_rgb(new_h, s, v))
        
        return colors

class MathUtils:
    """Advanced mathematical utilities"""
    
    @staticmethod
    def factorial(n: int) -> int:
        """Calculate factorial"""
        if n <= 1:
            return 1
        return n * MathUtils.factorial(n - 1)
    
    @staticmethod
    def fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b
    
    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        
        return True
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Greatest common divisor"""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Least common multiple"""
        return abs(a * b) // MathUtils.gcd(a, b)
    
    @staticmethod
    def distance_3d(x1: float, y1: float, z1: float, 
                   x2: float, y2: float, z2: float) -> float:
        """Calculate 3D distance"""
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    @staticmethod
    def dot_product(v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Calculate dot product of vectors"""
        return sum(a * b for a, b in zip(v1, v2))
    
    @staticmethod
    def cross_product(v1: Tuple[float, float, float], 
                     v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Calculate cross product of 3D vectors"""
        return (
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        )
    
    @staticmethod
    def normalize_vector(v: Tuple[float, ...]) -> Tuple[float, ...]:
        """Normalize a vector"""
        magnitude = math.sqrt(sum(x * x for x in v))
        if magnitude == 0:
            return v
        return tuple(x / magnitude for x in v)
    
    @staticmethod
    def vector_angle(v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Calculate angle between vectors (radians)"""
        dot = MathUtils.dot_product(v1, v2)
        mag1 = math.sqrt(sum(x * x for x in v1))
        mag2 = math.sqrt(sum(x * x for x in v2))
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        cos_angle = dot / (mag1 * mag2)
        cos_angle = clamp(cos_angle, -1, 1)
        return math.acos(cos_angle)

class StringUtils:
    """String manipulation utilities"""
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return StringUtils.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity(s1: str, s2: str) -> float:
        """Calculate similarity ratio between strings (0-1)"""
        distance = StringUtils.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        return 1.0 - (distance / max_len)
    
    @staticmethod
    def fuzzy_match(query: str, options: List[str], threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Fuzzy match query against options"""
        matches = []
        query_lower = query.lower()
        
        for option in options:
            option_lower = option.lower()
            
            # Exact match
            if query_lower == option_lower:
                matches.append((option, 1.0))
                continue
            
            # Substring match
            if query_lower in option_lower:
                ratio = len(query) / len(option)
                matches.append((option, 0.9 * ratio))
                continue
            
            # Fuzzy match
            similarity = StringUtils.similarity(query_lower, option_lower)
            if similarity >= threshold:
                matches.append((option, similarity))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    @staticmethod
    def camel_to_snake(text: str) -> str:
        """Convert camelCase to snake_case"""
        result = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', result).lower()
    
    @staticmethod
    def snake_to_camel(text: str) -> str:
        """Convert snake_case to camelCase"""
        components = text.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def kebab_to_title(text: str) -> str:
        """Convert kebab-case to Title Case"""
        return ' '.join(word.capitalize() for word in text.split('-'))
    
    @staticmethod
    def pluralize(word: str, count: int) -> str:
        """Simple English pluralization"""
        if count == 1:
            return word
        
        # Simple rules
        if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return word + 'es'
        else:
            return word + 's'
    
    @staticmethod
    def abbreviate(text: str, max_length: int, ellipsis: str = '...') -> str:
        """Abbreviate text to max length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(ellipsis)] + ellipsis
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.findall(text)
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return email_pattern.findall(text)
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences in text"""
        sentence_pattern = re.compile(r'[.!?]+')
        return len(sentence_pattern.findall(text))

class FileUtils:
    """File system utilities"""
    
    @staticmethod
    def get_file_size_human(filepath: str) -> str:
        """Get human-readable file size"""
        try:
            size = os.path.getsize(filepath)
            return format_bytes(size)
        except:
            return "Unknown"
    
    @staticmethod
    def get_file_extension(filepath: str) -> str:
        """Get file extension"""
        return os.path.splitext(filepath)[1].lstrip('.')
    
    @staticmethod
    def is_text_file(filepath: str, sample_size: int = 512) -> bool:
        """Check if file is text"""
        try:
            with open(filepath, 'rb') as f:
                sample = f.read(sample_size)
            
            # Check for null bytes
            if b'\x00' in sample:
                return False
            
            # Try to decode as UTF-8
            try:
                sample.decode('utf-8')
                return True
            except:
                return False
        except:
            return False
    
    @staticmethod
    def find_files(directory: str, pattern: str = '*', recursive: bool = True) -> List[str]:
        """Find files matching pattern"""
        import glob
        
        if recursive:
            pattern_path = os.path.join(directory, '**', pattern)
            return glob.glob(pattern_path, recursive=True)
        else:
            pattern_path = os.path.join(directory, pattern)
            return glob.glob(pattern_path)
    
    @staticmethod
    def create_backup(filepath: str) -> Optional[str]:
        """Create backup of file"""
        if not os.path.exists(filepath):
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{filepath}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            return backup_path
        except:
            return None
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Create safe filename"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        max_len = 255
        if len(filename) > max_len:
            name, ext = os.path.splitext(filename)
            name = name[:max_len - len(ext)]
            filename = name + ext
        
        return filename
    
    @staticmethod
    def get_mime_type(filepath: str) -> str:
        """Guess MIME type from filename"""
        ext = FileUtils.get_file_extension(filepath).lower()
        
        mime_types = {
            'txt': 'text/plain',
            'py': 'text/x-python',
            'js': 'application/javascript',
            'json': 'application/json',
            'html': 'text/html',
            'css': 'text/css',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'zip': 'application/zip',
        }
        
        return mime_types.get(ext, 'application/octet-stream')

class DateTimeUtils:
    """Date and time utilities"""
    
    @staticmethod
    def format_relative_time(timestamp: float) -> str:
        """Format timestamp as relative time (e.g., '2 hours ago')"""
        now = time.time()
        diff = now - timestamp
        
        if diff < 60:
            return "just now"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < 604800:
            days = int(diff / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif diff < 2592000:
            weeks = int(diff / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif diff < 31536000:
            months = int(diff / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(diff / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"
    
    @staticmethod
    def format_timestamp(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format timestamp with custom format"""
        return datetime.fromtimestamp(timestamp).strftime(format_str)
    
    @staticmethod
    def parse_duration(duration_str: str) -> float:
        """Parse duration string (e.g., '2h 30m') to seconds"""
        units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
        }
        
        total_seconds = 0.0
        pattern = re.compile(r'(\d+(?:\.\d+)?)\s*([smhdw])')
        
        for match in pattern.finditer(duration_str.lower()):
            value = float(match.group(1))
            unit = match.group(2)
            total_seconds += value * units.get(unit, 1)
        
        return total_seconds
    
    @staticmethod
    def is_weekend(timestamp: Optional[float] = None) -> bool:
        """Check if timestamp is weekend"""
        dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
        return dt.weekday() >= 5
    
    @staticmethod
    def get_week_number(timestamp: Optional[float] = None) -> int:
        """Get ISO week number"""
        dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
        return dt.isocalendar()[1]
    
    @staticmethod
    def get_quarter(timestamp: Optional[float] = None) -> int:
        """Get quarter of year (1-4)"""
        dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
        return (dt.month - 1) // 3 + 1

# ============================================================================
# COMPREHENSIVE TESTING AND VALIDATION
# ============================================================================

class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        return bool(pattern.match(url))
    
    @staticmethod
    def validate_ipv4(ip: str) -> bool:
        """Validate IPv4 address"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 0 < port <= 65535
    
    @staticmethod
    def validate_hex_color(color: str) -> bool:
        """Validate hex color code"""
        pattern = re.compile(r'^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$')
        return bool(pattern.match(color))
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """Validate password strength"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain a digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain special character")
        
        return (len(issues) == 0, issues)

# ============================================================================
# EXTENDED DOCUMENTATION AND USAGE EXAMPLES
# ============================================================================

"""
ADVANCED USAGE EXAMPLES AND PATTERNS

This section provides comprehensive examples of how to use and extend the TUI application.

## Example 1: Creating a Custom Plugin

```python
class CustomWeatherPlugin(Plugin):
    def __init__(self):
        super().__init__("custom_weather", "1.0")
        self.weather_data = {}
    
    def on_load(self):
        # Initialize plugin
        self.fetch_weather_data()
    
    def fetch_weather_data(self):
        # Fetch data from API
        pass
    
    def on_render(self, context):
        # Render weather information
        output = []
        if self.weather_data:
            output.append(Cursor.move(10, 5))
            output.append(Color.rgb(100, 200, 255))
            output.append(f"Temp: {self.weather_data.get('temp')}°C")
        return output
    
    def on_command(self, command):
        if command.startswith("weather"):
            return f"Current temperature: {self.weather_data.get('temp')}°C"
        return None
```

## Example 2: Custom Theme Creation

```python
custom_theme = Theme("my_theme")
custom_theme.colors = {
    'menu_bg': (30, 30, 40),
    'menu_fg': (220, 220, 240),
    'menu_active': (255, 200, 100),
    # ... more colors
}

# Apply theme
app.theme_manager.add_theme(custom_theme)
app.theme_manager.set_theme("my_theme")
```

## Example 3: Custom Command Handler

```python
def custom_command_handler(command: Command) -> str:
    if command.name == "mycommand":
        args = command.args
        kwargs = command.kwargs
        
        # Process command
        result = process_data(args, kwargs)
        
        return f"Result: {result}"
    
    return None

# Register command
app.command_executor.commands['mycommand'] = custom_command_handler
```

## Example 4: Using the Particle System

```python
# Create particle emitter
emitter = ParticleEmitter(x=50, y=10)
emitter.particle_life = 3.0
emitter.particle_color = (255, 100, 100)
emitter.particle_speed = 10.0
emitter.gravity = (0, 2.0)
emitter.emission_rate = 20.0

# Add to particle system
app.particle_system.add_emitter(emitter)
```

## Example 5: Creating Custom Animations

```python
# Create animation
fade_in = Animation(duration=2.0, loop=False)

# Use in rendering
def render_with_animation():
    progress = fade_in.update(dt)
    eased = EasingFunction.ease_in_out_cubic(progress)
    
    # Use eased value for opacity or position
    opacity = eased
    ...

# Add to controller
app.animation_controller.add_animation("fade_in", fade_in)
```

## Example 6: Advanced Text Rendering

```python
# Gradient text
gradient_text = TextRenderer.render_gradient_text(
    "Hello World",
    x=10, y=5,
    color1=(255, 100, 100),
    color2=(100, 100, 255)
)

# Rainbow text
rainbow_text = TextRenderer.render_rainbow_text(
    "Colorful!",
    x=10, y=6,
    time_offset=current_time
)

# Text with shadow
shadow_text = TextRenderer.render_text_with_shadow(
    "Shadowed",
    x=10, y=7,
    color=(255, 255, 255),
    shadow_color=(0, 0, 0),
    shadow_offset=(2, 1)
)
```

## Example 7: Using the Braille Canvas

```python
# Create canvas
canvas = BrailleCanvas(width=40, height=20)

# Draw shapes
canvas.fill_circle(20, 10, 5, (255, 100, 100))
canvas.draw_line(0, 0, 40, 20, (100, 255, 100))
canvas.draw_rect(5, 5, 10, 8, (100, 100, 255))

# Render
output = canvas.render(offset_x=10, offset_y=5)
```

## Example 8: Creating Interactive Dialogs

```python
# Create dialog
dialog = Dialog(
    title="Confirm Action",
    message="Are you sure you want to proceed?",
    buttons=["Yes", "No", "Cancel"]
)

# Show dialog
dialog.show()

# Handle input
if user_pressed_enter:
    result = dialog.activate_selected()
    if result == "Yes":
        # Proceed
        pass
```

## Example 9: File Browser Integration

```python
# Create file browser
browser = FileBrowser(width=60, height=20, x=10, y=5)
browser.visible = True

# Navigate
browser.navigate_down()  # Enter directory
browser.select_next()     # Select next file

# Get selected file
selected_path = browser.get_selected_path()
```

## Example 10: Custom Shader Implementation

```python
class CustomShader(Shader):
    def __init__(self):
        super().__init__(ShaderType.CUSTOM)
    
    def execute(self, input_data):
        time_val = input_data.time
        x, y = input_data.position
        width, height = input_data.resolution
        
        # Custom shader logic
        r = int(128 + 127 * math.sin(x * 0.1 + time_val))
        g = int(128 + 127 * math.sin(y * 0.1 + time_val))
        b = int(128 + 127 * math.sin((x + y) * 0.1 + time_val))
        
        return (r, g, b, 255)

# Add to shader manager
app.shader_manager.shaders['custom'] = CustomShader()
```

"""

# ============================================================================
# COMPREHENSIVE KEYBOARD SHORTCUTS REFERENCE
# ============================================================================

KEYBOARD_SHORTCUTS_REFERENCE = """
╔══════════════════════════════════════════════════════════════════╗
║                    KEYBOARD SHORTCUTS REFERENCE                   ║
╚══════════════════════════════════════════════════════════════════╝

NAVIGATION
  ↑ / ↓           - Navigate command history
  ← / →           - Move cursor in command
  Home / End      - Jump to line start/end
  Ctrl+← / Ctrl+→ - Jump by word
  PgUp / PgDn     - Scroll output

EDITING
  Backspace       - Delete character before cursor
  Delete          - Delete character at cursor
  Ctrl+U          - Clear entire line
  Ctrl+W          - Delete word before cursor
  Ctrl+K          - Delete from cursor to end
  Ctrl+A          - Move to line start
  Ctrl+E          - Move to line end

SELECTION
  Shift+←/→       - Select character
  Shift+Ctrl+←/→  - Select word
  Ctrl+A          - Select all (in text editor)
  Ctrl+C          - Copy selection
  Ctrl+X          - Cut selection
  Ctrl+V          - Paste from clipboard

APPLICATION
  F1              - Help
  F2              - Rename
  F3              - Search
  F4              - Replace
  F5              - Refresh
  F6              - Switch pane
  F7              - Toggle terminal/editor
  F8              - Toggle menu bar
  F9              - Toggle autocorrect
  F10             - Clear screen
  F11             - Fullscreen
  F12             - Developer tools

TABS AND SESSIONS
  Ctrl+T          - New tab
  Ctrl+W          - Close tab
  Ctrl+Tab        - Next tab
  Ctrl+Shift+Tab  - Previous tab
  Ctrl+N          - New session
  Ctrl+Shift+W    - Close session

VIEW
  Ctrl++          - Increase font size
  Ctrl+-          - Decrease font size
  Ctrl+0          - Reset font size
  Ctrl+B          - Toggle sidebar
  Ctrl+J          - Toggle output panel
  Ctrl+`          - Toggle terminal

SEARCH
  Ctrl+F          - Find
  Ctrl+H          - Find and replace
  F3 / Shift+F3   - Find next/previous
  Ctrl+G          - Go to line
  Ctrl+P          - Quick open file

TERMINAL
  Ctrl+L          - Clear terminal
  Ctrl+C          - Interrupt command
  Ctrl+D          - EOF / Exit shell
  Ctrl+Z          - Suspend process
  Ctrl+R          - Reverse search history

DEBUG
  F9              - Toggle breakpoint
  F5              - Start debugging
  F10             - Step over
  F11             - Step into
  Shift+F11       - Step out
  Shift+F5        - Stop debugging

MISCELLANEOUS
  Ctrl+/          - Toggle comment
  Ctrl+Space      - Trigger autocomplete
  Alt+↑/↓         - Move line up/down
  Ctrl+D          - Duplicate line
  Ctrl+Shift+K    - Delete line
"""

# ============================================================================
# PERFORMANCE OPTIMIZATION TIPS
# ============================================================================

PERFORMANCE_TIPS = """
╔══════════════════════════════════════════════════════════════════╗
║                     PERFORMANCE OPTIMIZATION                      ║
╚══════════════════════════════════════════════════════════════════╝

GENERAL TIPS
  • Reduce FPS to 30-60 for better battery life
  • Disable shaders if experiencing lag
  • Limit particle emission rates
  • Reduce parallax layer count
  • Use simpler border styles
  • Disable animations if not needed

SHADER OPTIMIZATION
  • Lower shader quality in config
  • Reduce sample rates
  • Simplify shader calculations
  • Use cached shader results
  • Disable unused shaders

RENDERING OPTIMIZATION
  • Limit visible layers
  • Use dirty rectangle rendering
  • Batch render operations
  • Cache frequently used renders
  • Reduce alpha blending operations

MEMORY OPTIMIZATION
  • Clear output buffer periodically
  • Limit command history size
  • Remove unused plugins
  • Clean up old notifications
  • Garbage collect when idle

CPU OPTIMIZATION
  • Use appropriate FPS setting
  • Optimize update loops
  • Defer expensive operations
  • Use background threads wisely
  • Profile and identify bottlenecks

TERMINAL OPTIMIZATION
  • Limit output buffer size
  • Use efficient text rendering
  • Avoid excessive redraws
  • Batch terminal writes
  • Use double buffering

CONFIG SETTINGS FOR PERFORMANCE
  fps: 30                    # Lower FPS
  enable_shaders: false      # Disable shaders
  enable_particles: false    # Disable particles
  parallax_layers: 2         # Fewer layers
  max_output_lines: 1000     # Smaller buffer
"""

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

TROUBLESHOOTING_GUIDE = """
╔══════════════════════════════════════════════════════════════════╗
║                      TROUBLESHOOTING GUIDE                        ║
╚══════════════════════════════════════════════════════════════════╝

COMMON ISSUES AND SOLUTIONS

1. APPLICATION WON'T START
   Problem: Application crashes on startup
   Solution:
   - Check Python version (3.7+ required)
   - Verify all dependencies installed
   - Check terminal compatibility
   - Review error logs in /tmp/tui_error.log
   - Try running with --debug flag

2. MENU BAR NOT VISIBLE
   Problem: Menu bar doesn't appear
   Solution:
   - Press F8 to toggle menu
   - Check Config.MENU_ALWAYS_VISIBLE setting
   - Verify terminal size is adequate
   - Reset configuration to defaults

3. COMMANDS NOT EXECUTING
   Problem: Commands don't run or hang
   Solution:
   - Check shell PATH configuration
   - Verify shell executable is valid
   - Test command in regular terminal
   - Check for permission issues
   - Review shell configuration files

4. VISUAL GLITCHES
   Problem: Screen flickers or displays incorrectly
   Solution:
   - Reduce FPS setting
   - Disable shaders and effects
   - Check terminal type (TERM variable)
   - Try different color scheme
   - Resize terminal window
   - Update terminal emulator

5. HIGH CPU USAGE
   Problem: Application uses too much CPU
   Solution:
   - Lower FPS to 30 or less
   - Disable shader effects
   - Reduce particle count
   - Limit parallax layers
   - Check for runaway processes
   - Review performance monitor

6. KEYBOARD INPUT NOT WORKING
   Problem: Keys don't respond
   Solution:
   - Check terminal input mode
   - Verify no conflicting keybindings
   - Reset keyboard configuration
   - Check for stuck modifier keys
   - Try alternate terminal

7. OUTPUT DISAPPEARS TOO QUICKLY
   Problem: Command output vanishes
   Solution:
   - Increase output buffer size
   - Check auto-clear settings
   - Disable doctor/health check
   - Verify scroll lock is off
   - Check notification settings

8. COLORS LOOK WRONG
   Problem: Colors display incorrectly
   Solution:
   - Check terminal color support
   - Verify TERM environment variable
   - Try different theme
   - Check color depth settings
   - Test with simple colors first

9. AUTOCOMPLETE NOT WORKING
   Problem: No suggestions appear
   Solution:
   - Check if panel is visible (F9)
   - Verify PATH is correct
   - Rebuild command cache
   - Check permissions on executables
   - Review autocomplete settings

10. CRASHES OR FREEZES
    Problem: Application becomes unresponsive
    Solution:
    - Check available memory
    - Review recent commands
    - Disable plugins one by one
    - Clear output buffer
    - Check for infinite loops in scripts
    - Review error logs

GETTING HELP
  • Check documentation: help command
  • Review logs: /tmp/tui_app.log
  • Error details: /tmp/tui_error.log
  • Configuration: ~/.tui_config.json
  • Report issues with full context

DIAGNOSTIC COMMANDS
  • sysinfo  - System information
  • cpu      - CPU usage
  • mem      - Memory usage
  • fps      - Current frame rate
  • config   - Current configuration
"""

# ============================================================================
# ADVANCED CONFIGURATION EXAMPLES
# ============================================================================

CONFIGURATION_EXAMPLES = """
╔══════════════════════════════════════════════════════════════════╗
║                   CONFIGURATION FILE EXAMPLES                     ║
╚══════════════════════════════════════════════════════════════════╝

MINIMAL CONFIGURATION
{
  "theme": "default",
  "fps": 60,
  "shell": "/bin/bash"
}

PERFORMANCE-FOCUSED
{
  "theme": "dark",
  "fps": 30,
  "enable_shaders": false,
  "enable_particles": false,
  "enable_animations": false,
  "parallax_layers": 0,
  "max_output_lines": 500,
  "update_interval": 100
}

VISUAL-FOCUSED
{
  "theme": "christmas",
  "fps": 120,
  "enable_shaders": true,
  "shader_quality": "ultra",
  "enable_particles": true,
  "enable_animations": true,
  "parallax_layers": 5,
  "bloom_intensity": 0.8,
  "vignette_strength": 0.5
}

DEVELOPER CONFIGURATION
{
  "theme": "cyberpunk",
  "fps": 60,
  "show_debug_overlay": true,
  "enable_profiler": true,
  "log_level": "debug",
  "max_output_lines": 10000,
  "syntax_highlighting": true,
  "auto_format_json": true,
  "plugins": ["git", "docker", "systeminfo"]
}

ACCESSIBILITY-FOCUSED
{
  "theme": "high_contrast",
  "fps": 30,
  "enable_shaders": false,
  "enable_particles": false,
  "enable_animations": false,
  "large_cursor": true,
  "screen_reader_mode": true,
  "keyboard_only": true
}

COMPLETE CONFIGURATION
{
  // Display settings
  "theme": "default",
  "fps": 60,
  "font_size": 12,
  
  // Feature toggles
  "enable_shaders": true,
  "shader_quality": "high",
  "enable_particles": true,
  "enable_animations": true,
  "show_welcome": true,
  
  // Visual effects
  "parallax_layers": 5,
  "parallax_speed": 1.0,
  "bloom_enabled": true,
  "bloom_intensity": 0.5,
  "vignette_enabled": true,
  "vignette_strength": 0.3,
  
  // Terminal settings
  "shell": "/bin/bash",
  "max_output_lines": 10000,
  "history_size": 1000,
  "auto_clear_output": false,
  
  // UI settings
  "menu_always_visible": true,
  "show_status_bar": true,
  "show_autocorrect": true,
  "show_tabs": true,
  
  // Plugin settings
  "plugins": ["clock", "weather", "git"],
  "plugin_update_interval": 5,
  
  // Advanced settings
  "debug_mode": false,
  "profiling_enabled": false,
  "log_file": "/tmp/tui_app.log",
  "backup_config": true
}
"""

# ============================================================================
# API REFERENCE AND EXTENSION GUIDE
# ============================================================================

API_REFERENCE = """
╔══════════════════════════════════════════════════════════════════╗
║                          API REFERENCE                            ║
╚══════════════════════════════════════════════════════════════════╝

PLUGIN API
  class Plugin(name, version):
    def on_load()          - Called when plugin loaded
    def on_unload()        - Called when plugin unloaded
    def on_command(cmd)    - Handle custom commands
    def on_render(ctx)     - Render custom content
    def on_input(key)      - Handle input events
    def on_update(dt)      - Update plugin state

SHADER API
  class Shader(shader_type):
    def execute(input)     - Execute shader
    def set_uniform(k, v)  - Set shader parameter
    def get_uniform(k)     - Get shader parameter

THEME API
  class Theme(name):
    def set_color(k, rgb)  - Set color value
    def get_color(k)       - Get color value
    def apply()            - Apply theme

COMMAND API
  class Command:
    name: str              - Command name
    args: List[str]        - Arguments
    kwargs: Dict           - Keyword arguments

EVENT API
  EventBus:
    subscribe(event, cb)   - Subscribe to event
    unsubscribe(event, cb) - Unsubscribe
    emit(event, *args)     - Emit event

UTILITY API
  Color:
    rgb(r, g, b)          - Create RGB color
    gradient(c1, c2, t)   - Interpolate colors
    reset()               - Reset formatting
  
  Cursor:
    move(x, y)            - Move cursor
    hide/show()           - Toggle visibility
  
  Screen:
    clear()               - Clear screen
    get_size()            - Get dimensions
"""

# ============================================================================
# EXTENSIVE ADDITIONAL EXAMPLES AND PATTERNS
# ============================================================================

# Comprehensive plugin implementation examples
PLUGIN_IMPLEMENTATION_EXAMPLES = """
Example Plugin Implementations:

1. DATABASE MONITOR PLUGIN
   Monitor database connections and queries
   Show connection pool status
   Display slow query warnings
   Real-time performance metrics

2. CONTAINER ORCHESTRATION PLUGIN
   Monitor Docker/Kubernetes containers
   Display resource usage per container
   Show container health status
   Quick actions for container management

3. LOG AGGREGATOR PLUGIN
   Collect logs from multiple sources
   Filter and search capabilities
   Real-time log streaming
   Pattern matching and alerts

4. API TESTING PLUGIN
   Send HTTP requests
   Display response data
   Save request collections
   Performance timing

5. GIT WORKFLOW PLUGIN
   Enhanced git status display
   Quick commit and push
   Branch visualization
   Merge conflict helper

6. CODE FORMATTER PLUGIN
   Auto-format code on save
   Support multiple languages
   Customizable formatting rules
   Diff preview before formatting

7. SNIPPET MANAGER PLUGIN
   Store code snippets
   Quick insertion
   Template variables
   Snippet sharing

8. TASK RUNNER PLUGIN
   Execute predefined tasks
   Task dependencies
   Progress tracking
   Notification on completion

9. NETWORK ANALYZER PLUGIN
   Real-time bandwidth monitoring
   Connection tracking
   Port scanning
   Packet inspection

10. SYSTEM PROFILER PLUGIN
    CPU, Memory, Disk, Network
    Historical graphs
    Process monitoring
    Resource alerts
"""

# Advanced theming examples
ADVANCED_THEMING_EXAMPLES = """
Advanced Theme Creation:

1. TIME-BASED DYNAMIC THEME
   Changes based on time of day
   Morning: bright, cool colors
   Afternoon: neutral, balanced
   Evening: warm, sunset tones
   Night: dark, blue-shifted

2. SEASONAL THEMES
   Spring: pastels, greens
   Summer: bright, vibrant
   Autumn: warm, oranges/reds
   Winter: cool, blues/whites

3. MOOD-BASED THEMES
   Energetic: high contrast, bright
   Calm: low contrast, soft
   Focus: minimal, monochrome
   Creative: colorful, varied

4. ACCESSIBILITY THEMES
   High contrast for visibility
   Colorblind-friendly palettes
   Large UI elements
   Screen reader optimized

5. BRAND THEMES
   Company colors
   Logo-inspired palettes
   Consistent with brand guide
   Professional appearance
"""

# Performance benchmarking data
PERFORMANCE_BENCHMARKS = """
Performance Benchmarks (Average System):

RENDERING PERFORMANCE
  30 FPS:  ~33ms per frame
  60 FPS:  ~16ms per frame
  120 FPS: ~8ms per frame

SHADER EXECUTION TIMES
  Parallax (low):    <1ms
  Parallax (high):   ~3ms
  Tree shader:       ~5ms
  Snow shader:       ~2ms
  Post-processing:   ~4ms

MEMORY USAGE
  Base application:  ~50MB
  With all plugins:  ~80MB
  Large output buf:  +10MB per 1000 lines
  Shader data:       ~20MB

CPU USAGE
  Idle:             ~1-2%
  Active rendering: ~5-15%
  Heavy effects:    ~20-30%
  Command exec:     Varies by command

STARTUP TIME
  Cold start:       ~500ms
  With plugins:     ~800ms
  Config loading:   ~50ms
  Theme init:       ~100ms
"""

# Comprehensive keybinding customization
KEYBINDING_CUSTOMIZATION = """
Custom Keybinding Configuration:

BASIC SYNTAX
  {
    "keybindings": {
      "key_sequence": "action_name",
      "Ctrl+K": "clear_screen",
      "F1": "show_help"
    }
  }

MODIFIER KEYS
  Ctrl+X  - Control + X
  Alt+X   - Alt + X  
  Shift+X - Shift + X
  Ctrl+Shift+X - Multiple modifiers

FUNCTION KEYS
  F1-F12 supported
  Shift+F1-F12 supported

SPECIAL KEYS
  Enter, Tab, Escape
  Backspace, Delete
  Home, End, Insert
  PageUp, PageDown
  Arrow keys (Up, Down, Left, Right)

CUSTOM ACTIONS
  Create custom action handlers
  Bind to any key combination
  Chain multiple actions
  Conditional execution

CONTEXT-SPECIFIC BINDINGS
  Different bindings per mode
  Editor vs Terminal mode
  Plugin-specific bindings
  Override default bindings
"""

# Scripting automation examples  
AUTOMATION_SCRIPTS = """
Automation Script Examples:

1. DEPLOYMENT SCRIPT
   #!/bin/bash
   echo "Starting deployment..."
   git pull origin main
   npm install
   npm run build
   docker build -t app:latest .
   docker push app:latest
   kubectl rollout restart deployment/app
   echo "Deployment complete!"

2. BACKUP SCRIPT
   #!/bin/bash
   BACKUP_DIR="/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf $BACKUP_DIR/backup_$DATE.tar.gz /data
   find $BACKUP_DIR -type f -mtime +7 -delete
   echo "Backup created: backup_$DATE.tar.gz"

3. TESTING SCRIPT
   #!/bin/bash
   echo "Running tests..."
   pytest tests/ -v
   npm test
   echo "Lint checking..."
   flake8 .
   eslint src/
   echo "Tests complete!"

4. MONITORING SCRIPT
   #!/bin/bash
   while true; do
     cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
     mem=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
     echo "CPU: $cpu% | Memory: $mem%"
     sleep 5
   done

5. DATA PROCESSING SCRIPT
   #!/bin/bash
   for file in data/*.csv; do
     echo "Processing $file..."
     python process_data.py "$file"
   done
   echo "All files processed!"
"""

# Error handling patterns
ERROR_HANDLING_PATTERNS = """
Error Handling Best Practices:

1. GRACEFUL DEGRADATION
   - Continue with reduced functionality
   - Log errors for debugging
   - Notify user of issues
   - Provide fallback options

2. USER-FRIENDLY MESSAGES
   - Clear, concise error descriptions
   - Suggested solutions
   - Context about what went wrong
   - Contact information if needed

3. RECOVERY STRATEGIES
   - Automatic retry logic
   - State restoration
   - Cache invalidation
   - Configuration reset

4. LOGGING AND DEBUGGING
   - Structured log messages
   - Stack traces in debug mode
   - Performance metrics
   - User action history

5. VALIDATION AND PREVENTION
   - Input validation
   - Type checking
   - Range checking
   - Permission verification
"""

# Testing strategies
TESTING_STRATEGIES = """
Testing Strategy Recommendations:

UNIT TESTING
  - Test individual functions
  - Mock external dependencies
  - Cover edge cases
  - Aim for >80% coverage

INTEGRATION TESTING
  - Test component interactions
  - Verify data flow
  - Check error propagation
  - Test with real dependencies

UI TESTING
  - Test rendering output
  - Verify user interactions
  - Check responsiveness
  - Test various screen sizes

PERFORMANCE TESTING
  - Measure frame times
  - Monitor memory usage
  - Profile CPU usage
  - Load testing

REGRESSION TESTING
  - Test after changes
  - Automated test suite
  - Continuous integration
  - Version comparison

USER ACCEPTANCE TESTING
  - Real user scenarios
  - Usability evaluation
  - Feedback collection
  - Iterative improvement
"""

# Security considerations
SECURITY_CONSIDERATIONS = """
Security Best Practices:

1. INPUT VALIDATION
   - Sanitize all user input
   - Validate command arguments
   - Escape special characters
   - Prevent injection attacks

2. COMMAND EXECUTION
   - Use safe subprocess methods
   - Limit command timeout
   - Validate command paths
   - Restrict dangerous commands

3. FILE OPERATIONS
   - Check file permissions
   - Validate file paths
   - Prevent directory traversal
   - Secure temporary files

4. CONFIGURATION SECURITY
   - Protect config files
   - Encrypt sensitive data
   - Validate config values
   - Secure defaults

5. NETWORK SECURITY
   - HTTPS for remote connections
   - Validate certificates
   - Encrypt sensitive data
   - Rate limiting

6. PLUGIN SECURITY
   - Sandbox plugin execution
   - Verify plugin sources
   - Limit plugin permissions
   - Review plugin code
"""

# Migration and upgrade guide
MIGRATION_GUIDE = """
Version Migration Guide:

FROM v1.x TO v2.x:
  1. Backup configuration file
  2. Update dependencies
  3. Review breaking changes
  4. Update custom plugins
  5. Test thoroughly
  6. Migrate data files

BREAKING CHANGES:
  - Config format changed to JSON
  - Plugin API updated
  - Theme structure revised
  - Keybinding syntax modified

DEPRECATED FEATURES:
  - Old menu system (use new API)
  - Legacy shader format
  - Old plugin interface

NEW FEATURES:
  - Enhanced shader system
  - Plugin manager
  - Session management
  - Advanced theming

MIGRATION TOOLS:
  - Config converter script
  - Plugin updater
  - Theme migration tool
  - Data import/export
"""

# Community and contribution guide
CONTRIBUTION_GUIDE = """
Contributing to the Project:

CODE CONTRIBUTIONS
  1. Fork repository
  2. Create feature branch
  3. Write tests
  4. Document changes
  5. Submit pull request

CODE STYLE
  - Follow PEP 8
  - Use type hints
  - Write docstrings
  - Add comments for complex logic

PLUGIN DEVELOPMENT
  - Use plugin template
  - Follow naming conventions
  - Include documentation
  - Provide examples

THEME CREATION
  - Use theme template
  - Test in different modes
  - Ensure accessibility
  - Provide screenshots

BUG REPORTS
  - Clear description
  - Steps to reproduce
  - Expected vs actual behavior
  - System information
  - Error logs

FEATURE REQUESTS
  - Describe use case
  - Explain benefits
  - Consider alternatives
  - Implementation suggestions
"""

# Comprehensive FAQ
COMPREHENSIVE_FAQ = """
Frequently Asked Questions:

Q: How do I change the theme?
A: Use 'theme [name]' command or update config file.

Q: Can I create custom plugins?
A: Yes, extend the Plugin class and implement required methods.

Q: How do I improve performance?
A: Lower FPS, disable shaders, reduce particles, limit output buffer.

Q: Does it work on Windows?
A: Designed for Unix-like systems. Windows support via WSL.

Q: Can I customize keybindings?
A: Yes, edit keybindings in config file or use keybinding commands.

Q: How do I backup my configuration?
A: Config files are in ~/.tui_config.json. Copy to backup location.

Q: Can multiple instances run simultaneously?
A: Yes, but they share the same configuration file.

Q: How do I update to latest version?
A: Pull latest code, install dependencies, review changelog.

Q: Is there a mobile version?
A: No, requires terminal emulator with keyboard input.

Q: How do I report bugs?
A: Check error logs, gather system info, create detailed report.

Q: Can I use custom fonts?
A: Depends on terminal emulator. Configure in your terminal settings.

Q: How do I export command history?
A: History stored in session data. Use export commands.

Q: Can I run it over SSH?
A: Yes, works great over SSH connections.

Q: How do I disable specific features?
A: Update config file to disable unwanted features.

Q: Where are logs stored?
A: /tmp/tui_app.log and /tmp/tui_error.log by default.
"""

# ============================================================================
# FINAL COMPREHENSIVE ADDITIONS AND EXAMPLES
# ============================================================================

# Additional helper functions for advanced operations
def advanced_string_formatting(text: str, width: int, options: Dict[str, Any]) -> str:
    """
    Advanced string formatting with multiple options.
    
    Args:
        text: Input text to format
        width: Target width for formatting
        options: Formatting options dictionary
        
    Options:
        - align: 'left', 'right', 'center', 'justify'
        - case: 'upper', 'lower', 'title', 'capitalize'
        - trim: True/False
        - ellipsis: String to use for truncation
        - padding: Character for padding
        - indent: Number of spaces for indentation
        - wrap: True/False for word wrapping
        - strip_ansi: True/False to remove ANSI codes
    
    Returns:
        Formatted string
    
    Examples:
        >>> advanced_string_formatting("hello", 10, {'align': 'center'})
        '  hello   '
        
        >>> advanced_string_formatting("long text", 5, {'ellipsis': '...'})
        'lo...'
    """
    result = text
    
    # Strip ANSI codes if requested
    if options.get('strip_ansi', False):
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
        result = ansi_pattern.sub('', result)
    
    # Trim whitespace
    if options.get('trim', True):
        result = result.strip()
    
    # Change case
    case = options.get('case', 'none')
    if case == 'upper':
        result = result.upper()
    elif case == 'lower':
        result = result.lower()
    elif case == 'title':
        result = result.title()
    elif case == 'capitalize':
        result = result.capitalize()
    
    # Word wrap if needed
    if options.get('wrap', False) and len(result) > width:
        words = result.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_len = len(word) + (1 if current_line else 0)
            if current_length + word_len <= width:
                current_line.append(word)
                current_length += word_len
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        result = '\n'.join(lines)
    
    # Truncate if too long
    elif len(result) > width:
        ellipsis = options.get('ellipsis', '...')
        result = result[:width - len(ellipsis)] + ellipsis
    
    # Alignment and padding
    if len(result) < width:
        padding_char = options.get('padding', ' ')
        align = options.get('align', 'left')
        
        if align == 'center':
            left_pad = (width - len(result)) // 2
            right_pad = width - len(result) - left_pad
            result = padding_char * left_pad + result + padding_char * right_pad
        elif align == 'right':
            result = padding_char * (width - len(result)) + result
        elif align == 'justify' and ' ' in result:
            # Simple justify implementation
            words = result.split()
            if len(words) > 1:
                total_chars = sum(len(w) for w in words)
                total_spaces = width - total_chars
                gaps = len(words) - 1
                if gaps > 0:
                    space_per_gap = total_spaces // gaps
                    extra = total_spaces % gaps
                    justified_parts = []
                    for i, word in enumerate(words[:-1]):
                        justified_parts.append(word)
                        justified_parts.append(' ' * space_per_gap)
                        if i < extra:
                            justified_parts.append(' ')
                    justified_parts.append(words[-1])
                    result = ''.join(justified_parts)
        else:  # left
            result = result + padding_char * (width - len(result))
    
    # Indentation
    indent = options.get('indent', 0)
    if indent > 0:
        indent_str = ' ' * indent
        result = '\n'.join(indent_str + line for line in result.split('\n'))
    
    return result

def create_progress_animation(frame: int, total_frames: int, style: str = 'spinner') -> str:
    """
    Create animated progress indicator.
    
    Args:
        frame: Current frame number
        total_frames: Total animation frames
        style: Animation style ('spinner', 'dots', 'bar', 'bounce')
    
    Returns:
        Animation string for current frame
    
    Examples:
        >>> create_progress_animation(0, 4, 'spinner')
        '|'
        >>> create_progress_animation(1, 4, 'spinner')
        '/'
    """
    if style == 'spinner':
        chars = ['|', '/', '-', '\\']
        return chars[frame % len(chars)]
    
    elif style == 'dots':
        max_dots = 3
        dot_count = (frame % (max_dots + 1))
        return '.' * dot_count + ' ' * (max_dots - dot_count)
    
    elif style == 'bar':
        width = 20
        progress = (frame % total_frames) / total_frames
        filled = int(width * progress)
        return '[' + '=' * filled + ' ' * (width - filled) + ']'
    
    elif style == 'bounce':
        width = 10
        pos = frame % (width * 2)
        if pos >= width:
            pos = width * 2 - pos - 1
        return ' ' * pos + '●' + ' ' * (width - pos - 1)
    
    elif style == 'pulse':
        chars = ['○', '◔', '◑', '◕', '●', '◕', '◑', '◔']
        return chars[frame % len(chars)]
    
    elif style == 'arrow':
        chars = ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙']
        return chars[frame % len(chars)]
    
    return '...'

def generate_ascii_banner(text: str, font_style: str = 'standard') -> List[str]:
    """
    Generate ASCII art banner text.
    
    Args:
        text: Text to convert to banner
        font_style: Font style ('standard', 'block', 'mini', 'shadow')
    
    Returns:
        List of strings forming the banner
    
    Note:
        This is a simplified implementation. Full ASCII art
        would require font data files.
    """
    if font_style == 'block':
        # Simple block letters (3 rows)
        char_map = {
            'A': ['▄▀▄', '███', '█ █'],
            'B': ['██▄', '██▄', '███'],
            'C': ['▄▀▀', '█  ', '▀▀▄'],
            'D': ['██▄', '█ █', '███'],
            'E': ['███', '██ ', '███'],
            # ... more characters would be defined here
        }
        
        lines = ['', '', '']
        for char in text.upper():
            if char in char_map:
                char_lines = char_map[char]
                for i in range(3):
                    lines[i] += char_lines[i] + ' '
            elif char == ' ':
                for i in range(3):
                    lines[i] += '   '
        
        return lines
    
    elif font_style == 'mini':
        # Mini font (1 row)
        return [text]
    
    elif font_style == 'shadow':
        # Text with shadow effect
        return [
            text,
            '▀' * len(text)
        ]
    
    else:  # standard
        # Simple uppercase representation
        return [
            '═' * (len(text) + 4),
            f'║ {text} ║',
            '═' * (len(text) + 4)
        ]

def create_data_visualization(data: Dict[str, float], chart_type: str = 'bar', 
                             width: int = 40, height: int = 10) -> List[str]:
    """
    Create text-based data visualization.
    
    Args:
        data: Dictionary of label: value pairs
        chart_type: Type of chart ('bar', 'horizontal_bar', 'pie', 'line')
        width: Chart width in characters
        height: Chart height in lines
    
    Returns:
        List of strings forming the visualization
    """
    if not data:
        return ['No data to visualize']
    
    lines = []
    
    if chart_type == 'bar':
        # Vertical bar chart
        max_value = max(data.values())
        scale = (height - 2) / max_value if max_value > 0 else 1
        
        # Create bars
        bar_width = width // len(data)
        
        for h in range(height, 0, -1):
            line = ''
            for label, value in data.items():
                bar_height = value * scale
                if bar_height >= h:
                    line += '█' * (bar_width - 1) + ' '
                else:
                    line += ' ' * bar_width
            lines.append(line)
        
        # Add labels
        label_line = ''
        for label in data.keys():
            label_abbr = label[:bar_width-1].ljust(bar_width-1) + ' '
            label_line += label_abbr
        lines.append('─' * width)
        lines.append(label_line)
    
    elif chart_type == 'horizontal_bar':
        # Horizontal bar chart
        max_value = max(data.values())
        max_label_len = max(len(str(k)) for k in data.keys())
        bar_width = width - max_label_len - 3
        
        for label, value in data.items():
            bar_length = int((value / max_value) * bar_width) if max_value > 0 else 0
            label_str = str(label).rjust(max_label_len)
            bar = '█' * bar_length
            lines.append(f"{label_str} │{bar}")
    
    elif chart_type == 'pie':
        # Simple pie chart representation
        total = sum(data.values())
        if total == 0:
            return ['No data']
        
        lines.append('Pie Chart:')
        for label, value in data.items():
            percentage = (value / total) * 100
            bar_length = int((percentage / 100) * (width - 20))
            bar = '█' * bar_length
            lines.append(f"{label:15} {percentage:5.1f}% {bar}")
    
    elif chart_type == 'line':
        # Line graph
        values = list(data.values())
        labels = list(data.keys())
        
        if not values:
            return ['No data']
        
        min_val = min(values)
        max_val = max(values)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Create grid
        for h in range(height):
            line = ''
            threshold = max_val - (h / height) * value_range
            
            for i, value in enumerate(values):
                if value >= threshold:
                    if i > 0 and values[i-1] < threshold:
                        line += '/'
                    else:
                        line += '─'
                else:
                    line += ' '
            
            lines.append(line)
        
        # Add x-axis labels
        label_line = ''
        step = max(1, len(labels) // (width // 8))
        for i in range(0, len(labels), step):
            if i < len(labels):
                label_line += labels[i][:6].ljust(8)
        lines.append('─' * width)
        lines.append(label_line)
    
    return lines

def format_data_table_advanced(headers: List[str], rows: List[List[Any]], 
                               options: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Create advanced formatted data table.
    
    Args:
        headers: Column headers
        rows: Data rows
        options: Formatting options
        
    Options:
        - style: 'simple', 'grid', 'fancy'
        - alignment: List of 'left', 'right', 'center' per column
        - colors: List of color tuples per column
        - max_width: Maximum width for columns
        - show_index: Show row numbers
        - zebra: Alternate row colors
    
    Returns:
        List of strings forming the table
    """
    if options is None:
        options = {}
    
    style = options.get('style', 'grid')
    show_index = options.get('show_index', False)
    
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Apply max width constraint
    max_width = options.get('max_width')
    if max_width:
        col_widths = [min(w, max_width) for w in col_widths]
    
    lines = []
    
    # Select border characters based on style
    if style == 'fancy':
        border_chars = {
            'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
            'h': '═', 'v': '║', 'cross': '╬', 
            'top': '╦', 'bottom': '╩', 'left': '╠', 'right': '╣'
        }
    elif style == 'simple':
        border_chars = {
            'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
            'h': '-', 'v': '|', 'cross': '+',
            'top': '+', 'bottom': '+', 'left': '+', 'right': '+'
        }
    else:  # grid
        border_chars = {
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'h': '─', 'v': '│', 'cross': '┼',
            'top': '┬', 'bottom': '┴', 'left': '├', 'right': '┤'
        }
    
    # Top border
    top_line = border_chars['tl']
    for i, width in enumerate(col_widths):
        top_line += border_chars['h'] * (width + 2)
        if i < len(col_widths) - 1:
            top_line += border_chars['top']
    top_line += border_chars['tr']
    lines.append(top_line)
    
    # Header row
    header_line = border_chars['v']
    for i, header in enumerate(headers):
        if i < len(col_widths):
            header_str = str(header)[:col_widths[i]].center(col_widths[i])
            header_line += f" {header_str} {border_chars['v']}"
    lines.append(header_line)
    
    # Header separator
    sep_line = border_chars['left']
    for i, width in enumerate(col_widths):
        sep_line += border_chars['h'] * (width + 2)
        if i < len(col_widths) - 1:
            sep_line += border_chars['cross']
    sep_line += border_chars['right']
    lines.append(sep_line)
    
    # Data rows
    for row_idx, row in enumerate(rows):
        data_line = border_chars['v']
        
        if show_index:
            data_line += f" {row_idx:3d} {border_chars['v']}"
        
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)[:col_widths[i]].ljust(col_widths[i])
                data_line += f" {cell_str} {border_chars['v']}"
        
        lines.append(data_line)
    
    # Bottom border
    bottom_line = border_chars['bl']
    for i, width in enumerate(col_widths):
        bottom_line += border_chars['h'] * (width + 2)
        if i < len(col_widths) - 1:
            bottom_line += border_chars['bottom']
    bottom_line += border_chars['br']
    lines.append(bottom_line)
    
    return lines

def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive statistics for a dataset.
    
    Args:
        data: List of numeric values
    
    Returns:
        Dictionary with statistical measures
    """
    if not data:
        return {}
    
    n = len(data)
    sorted_data = sorted(data)
    
    # Basic statistics
    total = sum(data)
    mean = total / n
    
    # Variance and standard deviation
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = math.sqrt(variance)
    
    # Median
    if n % 2 == 0:
        median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        median = sorted_data[n//2]
    
    # Mode (simple implementation)
    from collections import Counter
    counts = Counter(data)
    mode_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == mode_count]
    mode = modes[0] if len(modes) == 1 else None
    
    # Quartiles
    q1_idx = n // 4
    q3_idx = 3 * n // 4
    q1 = sorted_data[q1_idx]
    q3 = sorted_data[q3_idx]
    iqr = q3 - q1
    
    # Min and Max
    min_val = min(data)
    max_val = max(data)
    range_val = max_val - min_val
    
    return {
        'count': n,
        'sum': total,
        'mean': mean,
        'median': median,
        'mode': mode,
        'std_dev': std_dev,
        'variance': variance,
        'min': min_val,
        'max': max_val,
        'range': range_val,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
    }

# Additional comprehensive utility functions for completeness
def create_loading_screen(message: str = "Loading...", width: int = 60) -> List[str]:
    """Create an attractive loading screen"""
    lines = []
    lines.append('')
    lines.append('╔' + '═' * (width - 2) + '╗')
    lines.append('║' + ' ' * (width - 2) + '║')
    centered_msg = message.center(width - 2)
    lines.append('║' + centered_msg + '║')
    lines.append('║' + ' ' * (width - 2) + '║')
    lines.append('╚' + '═' * (width - 2) + '╝')
    lines.append('')
    return lines

def validate_configuration(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate configuration dictionary"""
    errors = []
    
    # Check FPS
    if 'fps' in config:
        if not isinstance(config['fps'], (int, float)) or config['fps'] <= 0:
            errors.append("FPS must be a positive number")
    
    # Check theme
    if 'theme' in config:
        if not isinstance(config['theme'], str):
            errors.append("Theme must be a string")
    
    # Check boolean flags
    bool_flags = ['enable_shaders', 'enable_particles', 'enable_animations']
    for flag in bool_flags:
        if flag in config and not isinstance(config[flag], bool):
            errors.append(f"{flag} must be a boolean")
    
    return (len(errors) == 0, errors)

def merge_configurations(base_config: Dict, override_config: Dict) -> Dict:
    """Merge two configuration dictionaries"""
    result = base_config.copy()
    result.update(override_config)
    return result

def export_session_data(session, filepath: str) -> bool:
    """Export session data to file"""
    try:
        data = {
            'id': session.id,
            'name': session.name,
            'created_at': session.created_at,
            'working_directory': session.working_directory,
            'command_history': list(session.command_history.commands),
            'output_lines': [
                {
                    'text': line.text,
                    'timestamp': line.timestamp,
                    'type': line.type
                }
                for line in session.output_buffer.lines
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception:
        return False

def import_session_data(filepath: str) -> Optional[Dict]:
    """Import session data from file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception:
        return None

def generate_unique_id(prefix: str = "") -> str:
    """Generate unique identifier"""
    timestamp = str(time.time()).replace('.', '')
    random_part = ''.join(random.choices('0123456789abcdef', k=8))
    return f"{prefix}{timestamp}_{random_part}" if prefix else f"{timestamp}_{random_part}"

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division with default value for division by zero"""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def clamp_dict_values(data: Dict[str, float], min_val: float, max_val: float) -> Dict[str, float]:
    """Clamp all numeric values in dictionary to range"""
    return {k: clamp(v, min_val, max_val) for k, v in data.items()}

def filter_dict_by_keys(data: Dict, keys: List[str]) -> Dict:
    """Filter dictionary to only include specified keys"""
    return {k: v for k, v in data.items() if k in keys}

# ============================================================================
# ENTRY POINT
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
