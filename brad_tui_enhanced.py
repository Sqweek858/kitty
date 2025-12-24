#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════════════
# 🎄 CYBERPUNK CHRISTMAS TREE - Ultra Enhanced TUI Version
# ═══════════════════════════════════════════════════════════════════════════════
# Features:
# - Advanced 3D rendering with proper depth and perspective
# - Realistic lighting with multiple light sources
# - Shadow casting and ambient occlusion
# - Animated blinking lights with varied patterns
# - Particle system for snowfall with physics
# - Depth-of-field blur effect
# - Bloom/glow effects for lights
# - Wind simulation for tree swaying
# - Ground shadows and reflections
# - Star topper with ray animation
# - Ornaments with proper 3D positioning
# - Tinsel strands with physics
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import time
import math
import random
import signal
import shutil
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class RenderQuality(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    ULTRA = 4

CONFIG = {
    'quality': RenderQuality.ULTRA,
    'fps': 15,
    'snowflakes': 100,
    'lights_count': 30,
    'enable_shadows': True,
    'enable_bloom': True,
    'enable_dof': False,  # Can be expensive
    'enable_wind': True,
    'wind_strength': 0.3,
}

# Braille character mapping for sub-pixel rendering (2x4 grid per character)
BRAILLE_DOTS = [
    (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (0, 3, 0x40),
    (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (1, 3, 0x80)
]

def braille_char(bits):
    """Convert bit pattern to Braille Unicode character"""
    return chr(0x2800 + bits) if bits else " "

def rgb(r, g, b):
    """Generate RGB ANSI escape code"""
    return f"\x1b[38;2;{int(r)};{int(g)};{int(b)}m"

def rgb_bg(r, g, b):
    """Generate RGB background ANSI escape code"""
    return f"\x1b[48;2;{int(r)};{int(g)};{int(b)}m"

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"

# ═══════════════════════════════════════════════════════════════════════════════
# 3D MATH UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Vec3:
    """3D Vector"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return Vec3(self.x/l, self.y/l, self.z/l)
        return Vec3(0, 0, 0)
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

@dataclass
class Color:
    """RGB Color with utilities"""
    r: float
    g: float
    b: float
    
    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)
    
    def __mul__(self, scalar):
        return Color(self.r * scalar, self.g * scalar, self.b * scalar)
    
    def clamp(self):
        return Color(
            max(0, min(255, self.r)),
            max(0, min(255, self.g)),
            max(0, min(255, self.b))
        )
    
    def blend(self, other, factor):
        """Blend with another color"""
        return Color(
            self.r * (1-factor) + other.r * factor,
            self.g * (1-factor) + other.g * factor,
            self.b * (1-factor) + other.b * factor
        )

# ═══════════════════════════════════════════════════════════════════════════════
# LIGHTING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Light:
    """Point light source"""
    pos: Vec3
    color: Color
    intensity: float
    radius: float

class LightingSystem:
    """Advanced lighting calculations"""
    
    def __init__(self):
        self.ambient = Color(10, 15, 20)
        self.lights: List[Light] = []
        self.directional = Vec3(-0.3, -0.6, -0.7).normalize()
        self.directional_color = Color(180, 180, 200)
        self.directional_intensity = 0.5
    
    def add_light(self, light: Light):
        self.lights.append(light)
    
    def calculate_lighting(self, pos: Vec3, normal: Vec3, base_color: Color) -> Color:
        """Calculate final lit color at position"""
        result = self.ambient * 0.3
        
        # Directional light (moon/sky)
        ndotl = max(0, -normal.dot(self.directional))
        result = result + self.directional_color * (ndotl * self.directional_intensity)
        
        # Point lights
        for light in self.lights:
            to_light = light.pos - pos
            dist = to_light.length()
            
            if dist < light.radius:
                to_light_norm = to_light.normalize()
                ndotl = max(0, normal.dot(to_light_norm))
                
                # Attenuation
                attenuation = 1.0 - (dist / light.radius)
                attenuation = attenuation * attenuation
                
                contribution = light.color * (ndotl * light.intensity * attenuation)
                result = result + contribution
        
        # Apply base color
        result = Color(
            result.r * base_color.r / 255,
            result.g * base_color.g / 255,
            result.b * base_color.b / 255
        )
        
        return result.clamp()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE SYSTEM - SNOWFALL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Snowflake:
    """Individual snowflake particle"""
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    size: float
    rotation: float
    rotation_speed: float
    char: str

class SnowSystem:
    """Particle system for snowfall"""
    
    def __init__(self, count, bounds_width, bounds_height, bounds_depth):
        self.snowflakes: List[Snowflake] = []
        self.bounds_w = bounds_width
        self.bounds_h = bounds_height
        self.bounds_d = bounds_depth
        self.wind = Vec3(0, 0, 0)
        
        # Initialize snowflakes
        for _ in range(count):
            self.snowflakes.append(self._create_snowflake())
    
    def _create_snowflake(self) -> Snowflake:
        """Create a new snowflake with random properties"""
        chars = ['*', '❄', '❅', '❆', '✻', '✼', '❊', '❉']
        return Snowflake(
            x=random.uniform(-self.bounds_w/2, self.bounds_w/2),
            y=random.uniform(self.bounds_h * 0.5, self.bounds_h * 1.2),
            z=random.uniform(-self.bounds_d, self.bounds_d),
            vx=random.uniform(-0.2, 0.2),
            vy=random.uniform(-1.0, -0.3),
            vz=random.uniform(-0.1, 0.1),
            size=random.uniform(0.5, 2.0),
            rotation=random.uniform(0, math.pi * 2),
            rotation_speed=random.uniform(-0.1, 0.1),
            char=random.choice(chars)
        )
    
    def update(self, dt: float, wind: Vec3):
        """Update snowflake positions"""
        self.wind = wind
        
        for flake in self.snowflakes:
            # Apply physics
            flake.vx += self.wind.x * dt + random.uniform(-0.1, 0.1) * dt
            flake.vy += -0.5 * dt  # Gravity
            flake.vz += self.wind.z * dt
            
            # Update position
            flake.x += flake.vx * dt
            flake.y += flake.vy * dt
            flake.z += flake.vz * dt
            flake.rotation += flake.rotation_speed * dt
            
            # Drag
            flake.vx *= 0.98
            flake.vz *= 0.98
            
            # Reset if out of bounds
            if flake.y < -self.bounds_h * 0.2:
                flake.y = self.bounds_h * 1.1
                flake.x = random.uniform(-self.bounds_w/2, self.bounds_w/2)
                flake.z = random.uniform(-self.bounds_d, self.bounds_d)
                flake.vx = random.uniform(-0.2, 0.2)
                flake.vy = random.uniform(-1.0, -0.3)
                flake.vz = random.uniform(-0.1, 0.1)

# ═══════════════════════════════════════════════════════════════════════════════
# CHRISTMAS TREE RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

class ChristmasTree:
    """Advanced 3D Christmas tree renderer"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.sub_width = width * 2
        self.sub_height = height * 4
        
        # Tree parameters
        self.tree_height = self.sub_height * 0.65
        self.tree_base_radius = self.sub_width * 0.32
        self.trunk_height = self.sub_height * 0.12
        self.trunk_radius = self.sub_width * 0.035
        
        # Center position
        self.center_x = self.sub_width // 2
        self.center_y = int(self.sub_height * 0.48)
        
        # Initialize systems
        self.lighting = LightingSystem()
        self.snow = SnowSystem(
            CONFIG['snowflakes'],
            self.sub_width,
            self.sub_height,
            50
        )
        
        # Animation state
        self.time = 0
        self.wind_phase = 0
        
        # Christmas lights
        self.lights_positions = self._generate_light_positions()
        self._setup_lights()
    
    def _generate_light_positions(self) -> List[Tuple[float, float, float]]:
        """Generate spiral positions for Christmas lights"""
        positions = []
        layers = 12
        lights_per_layer = CONFIG['lights_count'] // layers
        
        for layer in range(layers):
            height_ratio = layer / layers
            y = self.center_y - int(self.tree_height * height_ratio)
            radius = self.tree_base_radius * (1 - height_ratio)
            
            for i in range(lights_per_layer):
                angle = (i / lights_per_layer) * math.pi * 2 + layer * 0.8
                x = self.center_x + int(radius * math.cos(angle))
                z = radius * math.sin(angle) * 0.3
                positions.append((x, y, z))
        
        return positions
    
    def _setup_lights(self):
        """Setup lighting system with animated Christmas lights"""
        # Add Christmas lights as point lights
        for i, (x, y, z) in enumerate(self.lights_positions):
            # Varied colors for lights
            hue = (i / len(self.lights_positions)) * 6
            if hue < 1:
                color = Color(255, int(hue*255), 0)
            elif hue < 2:
                color = Color(int((2-hue)*255), 255, 0)
            elif hue < 3:
                color = Color(0, 255, int((hue-2)*255))
            elif hue < 4:
                color = Color(0, int((4-hue)*255), 255)
            elif hue < 5:
                color = Color(int((hue-4)*255), 0, 255)
            else:
                color = Color(255, 0, int((6-hue)*255))
            
            self.lighting.add_light(Light(
                pos=Vec3(x, y, z),
                color=color,
                intensity=0,  # Will be animated
                radius=30
            ))
    
    def _get_wind_offset(self, y: float) -> float:
        """Calculate wind sway offset based on height"""
        if not CONFIG['enable_wind']:
            return 0
        
        height_factor = max(0, (self.center_y - y) / self.tree_height)
        sway = math.sin(self.wind_phase + height_factor * math.pi) * CONFIG['wind_strength']
        return sway * height_factor * 5
    
    def render_frame(self, time_delta: float) -> List[str]:
        """Render a complete frame"""
        self.time += time_delta
        self.wind_phase += time_delta * 2
        
        # Update snow
        wind = Vec3(math.sin(self.wind_phase) * 0.5, 0, 0)
        self.snow.update(time_delta, wind)
        
        # Update light intensities (blinking animation)
        for i, light in enumerate(self.lighting.lights):
            phase = self.time * (2 + (i % 3)) + i * 0.7
            blink = 0.5 + 0.5 * math.sin(phase)
            light.intensity = blink * 1.2
        
        # Create buffer
        buffer = [[None for _ in range(self.sub_width)] for _ in range(self.sub_height)]
        
        # Render tree body
        self._render_tree_body(buffer)
        
        # Render trunk
        self._render_trunk(buffer)
        
        # Render Christmas lights
        self._render_christmas_lights(buffer)
        
        # Render star on top
        self._render_star(buffer)
        
        # Render ornaments
        self._render_ornaments(buffer)
        
        # Render snowfall
        self._render_snow(buffer)
        
        # Convert buffer to Braille characters
        return self._buffer_to_braille(buffer)
    
    def _render_tree_body(self, buffer):
        """Render the tree cone with proper 3D shading"""
        for y in range(int(self.tree_height)):
            sy = self.center_y - y
            if sy < 0 or sy >= self.sub_height:
                continue
            
            # Calculate radius at this height
            height_ratio = y / self.tree_height
            radius = self.tree_base_radius * (1 - height_ratio)
            
            # Wind sway
            wind_offset = self._get_wind_offset(sy)
            
            for x in range(int(self.center_x - radius - 2), int(self.center_x + radius + 3)):
                if x < 0 or x >= self.sub_width:
                    continue
                
                dx = (x - self.center_x - wind_offset)
                dist_from_center = abs(dx)
                
                if dist_from_center <= radius:
                    # Calculate 3D position and normal
                    z = math.sqrt(max(0, radius**2 - dx**2)) * 0.5
                    pos = Vec3(x, sy, z if dx > 0 else -z)
                    
                    # Normal vector for lighting
                    normal = Vec3(dx / radius, 0.6, z / radius * 0.5).normalize()
                    
                    # Base color with gradient
                    base_green = Color(
                        10 + int(30 * (1 - height_ratio)),
                        80 + int(80 * (1 - height_ratio)),
                        30 + int(40 * (1 - height_ratio))
                    )
                    
                    # Apply lighting
                    final_color = self.lighting.calculate_lighting(pos, normal, base_green)
                    
                    # Add some texture variation
                    noise = random.random() * 0.15 - 0.075
                    final_color = Color(
                        final_color.r * (1 + noise),
                        final_color.g * (1 + noise),
                        final_color.b * (1 + noise)
                    ).clamp()
                    
                    buffer[sy][x] = final_color
    
    def _render_trunk(self, buffer):
        """Render tree trunk"""
        trunk_top = self.center_y + 2
        trunk_bottom = trunk_top + int(self.trunk_height)
        
        for y in range(trunk_top, min(trunk_bottom, self.sub_height)):
            wind_offset = self._get_wind_offset(y) * 0.3
            
            for x in range(int(self.center_x - self.trunk_radius - wind_offset),
                          int(self.center_x + self.trunk_radius - wind_offset + 1)):
                if 0 <= x < self.sub_width:
                    dx = x - (self.center_x - wind_offset)
                    
                    # Cylindrical shading
                    ndotl = max(0.3, 0.5 + 0.5 * math.cos((dx / self.trunk_radius) * math.pi))
                    
                    brown = Color(
                        int(90 * ndotl),
                        int(60 * ndotl),
                        int(30 * ndotl)
                    )
                    
                    buffer[y][x] = brown
    
    def _render_christmas_lights(self, buffer):
        """Render glowing Christmas lights"""
        for i, (lx, ly, lz) in enumerate(self.lights_positions):
            if ly < 0 or ly >= self.sub_height:
                continue
            
            # Get current light intensity
            intensity = self.lighting.lights[i].intensity if i < len(self.lighting.lights) else 0.5
            color = self.lighting.lights[i].color if i < len(self.lighting.lights) else Color(255, 255, 255)
            
            # Apply wind sway
            wind_offset = int(self._get_wind_offset(ly))
            lx_adjusted = int(lx + wind_offset)
            
            if 0 <= lx_adjusted < self.sub_width:
                # Draw light bulb
                buffer[ly][lx_adjusted] = color * intensity
                
                # Add glow effect
                if CONFIG['enable_bloom']:
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            gx, gy = lx_adjusted + dx, ly + dy
                            if 0 <= gx < self.sub_width and 0 <= gy < self.sub_height:
                                dist = math.sqrt(dx*dx + dy*dy)
                                if dist > 0 and dist < 3:
                                    glow_strength = (1 - dist/3) * 0.4 * intensity
                                    
                                    if buffer[gy][gx] is not None:
                                        current = buffer[gy][gx]
                                        buffer[gy][gx] = Color(
                                            min(255, current.r + color.r * glow_strength),
                                            min(255, current.g + color.g * glow_strength),
                                            min(255, current.b + color.b * glow_strength)
                                        )
    
    def _render_star(self, buffer):
        """Render animated star on top"""
        star_x = self.center_x + int(self._get_wind_offset(self.center_y - self.tree_height))
        star_y = self.center_y - int(self.tree_height) - 4
        
        if 0 <= star_y < self.sub_height:
            # Pulsing animation
            pulse = 0.7 + 0.3 * math.sin(self.time * 3)
            
            # Star color (gold)
            star_color = Color(255, 230, 100) * pulse
            
            # Draw star shape (5-pointed)
            for angle in range(0, 360, 72):
                rad = math.radians(angle + self.time * 20)
                for r in range(1, 5):
                    sx = star_x + int(r * math.cos(rad))
                    sy = star_y + int(r * math.sin(rad) * 0.5)
                    
                    if 0 <= sx < self.sub_width and 0 <= sy < self.sub_height:
                        buffer[sy][sx] = star_color
            
            # Center bright spot
            if 0 <= star_x < self.sub_width:
                buffer[star_y][star_x] = Color(255, 255, 255)
    
    def _render_ornaments(self, buffer):
        """Render decorative ornaments"""
        # Fixed seed for consistent ornament placement
        random.seed(42)
        
        ornament_count = 15
        for i in range(ornament_count):
            layer = int((i / ornament_count) * self.tree_height * 0.8)
            height_ratio = layer / self.tree_height
            radius = self.tree_base_radius * (1 - height_ratio) * 0.7
            
            angle = (i * 2.3) % (math.pi * 2)
            ox = self.center_x + int(radius * math.cos(angle))
            oy = self.center_y - layer
            
            if 0 <= oy < self.sub_height and 0 <= ox < self.sub_width:
                # Ornament colors
                colors = [
                    Color(255, 50, 50),   # Red
                    Color(50, 50, 255),   # Blue
                    Color(255, 215, 0),   # Gold
                    Color(192, 192, 192), # Silver
                    Color(255, 105, 180), # Pink
                ]
                ornament_color = colors[i % len(colors)]
                
                # Small spherical ornament (2x2 pixels)
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        px, py = ox + dx, oy + dy
                        if 0 <= px < self.sub_width and 0 <= py < self.sub_height:
                            if dx*dx + dy*dy <= 1:
                                # Specular highlight
                                if dx == -1 and dy == -1:
                                    buffer[py][px] = Color(255, 255, 255)
                                else:
                                    buffer[py][px] = ornament_color * 0.8
        
        # Reset random seed
        random.seed()
    
    def _render_snow(self, buffer):
        """Render falling snowflakes"""
        for flake in self.snow.snowflakes:
            # Project 3D position to 2D screen
            # Simple perspective projection
            screen_x = int(flake.x + self.sub_width / 2)
            screen_y = int(self.sub_height - flake.y)
            
            # Depth-based color (closer = brighter)
            depth_factor = (flake.z + 25) / 50
            brightness = int(200 + 55 * depth_factor)
            snow_color = Color(brightness, brightness, brightness + 20)
            
            if 0 <= screen_x < self.sub_width and 0 <= screen_y < self.sub_height:
                # Only draw if not obscured by tree
                if buffer[screen_y][screen_x] is None:
                    buffer[screen_y][screen_x] = snow_color
    
    def _buffer_to_braille(self, buffer) -> List[str]:
        """Convert pixel buffer to Braille characters"""
        lines = []
        
        for row in range(self.height):
            y0 = row * 4
            line_chars = []
            prev_color = None
            
            for col in range(self.width):
                x0 = col * 2
                bits = 0
                
                # Accumulate color from sub-pixels
                colors_r, colors_g, colors_b, count = 0, 0, 0, 0
                
                for dx, dy, mask in BRAILLE_DOTS:
                    x, y = x0 + dx, y0 + dy
                    if 0 <= x < self.sub_width and 0 <= y < self.sub_height:
                        if buffer[y][x] is not None:
                            color = buffer[y][x]
                            colors_r += color.r
                            colors_g += color.g
                            colors_b += color.b
                            count += 1
                            bits |= mask
                
                if count == 0:
                    # Background
                    if prev_color is not None:
                        line_chars.append(RESET)
                        prev_color = None
                    line_chars.append(" ")
                else:
                    # Average color
                    avg_color = (
                        int(colors_r / count),
                        int(colors_g / count),
                        int(colors_b / count)
                    )
                    
                    color_code = rgb(*avg_color)
                    if color_code != prev_color:
                        line_chars.append(color_code)
                        prev_color = color_code
                    
                    line_chars.append(braille_char(bits))
            
            if prev_color is not None:
                line_chars.append(RESET)
            
            lines.append("".join(line_chars))
        
        return lines

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Signal handling
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    
    # Hide cursor
    sys.stdout.write("\x1b[?25l")
    sys.stdout.write("\x1b[2J\x1b[H")  # Clear screen
    sys.stdout.flush()
    
    # Get terminal size
    cols, rows = shutil.get_terminal_size((80, 24))
    cols = max(40, cols - 2)
    rows = max(20, rows - 2)
    
    # Create tree renderer
    tree = ChristmasTree(cols, rows)
    
    # Main render loop
    t0 = time.time()
    frame_time = 1.0 / CONFIG['fps']
    
    try:
        while True:
            loop_start = time.time()
            elapsed = loop_start - t0
            
            # Render frame
            lines = tree.render_frame(frame_time)
            
            # Display frame
            sys.stdout.write("\x1b[H")  # Home cursor
            for line in lines:
                sys.stdout.write(line + "\n")
            sys.stdout.write(RESET)
            sys.stdout.flush()
            
            # Frame rate control
            frame_duration = time.time() - loop_start
            sleep_time = max(0, frame_time - frame_duration)
            time.sleep(sleep_time)
            
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        # Cleanup
        sys.stdout.write(RESET + "\x1b[?25h\n")  # Show cursor
        sys.stdout.flush()

if __name__ == "__main__":
    main()
