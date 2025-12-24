#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ADVANCED GRAPHICS ENGINE                              ║
║         Parallax Effects, 3D Rendering, Visual Effects Layer                ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides advanced graphics rendering:
    - Multi-layer parallax background system
    - 3D Christmas tree with advanced effects
    - Particle systems (snow, sparkles, embers)
    - Post-processing effects stack
    - Shader-based rendering pipeline
    - Frame composition and blending
"""

import math
import random
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field

from shader_system import (
    Vec2, Vec3, Color, 
    ParallaxShader, ChristmasTreeShader, SnowShader,
    NoiseGenerator, Light, ShaderUniforms,
    VertexInput, VertexOutput, PostProcessing
)


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Particle:
    """Base particle class"""
    position: Vec3
    velocity: Vec3
    life: float
    max_life: float
    size: float
    color: Color
    rotation: float = 0.0
    rotation_speed: float = 0.0


class ParticleSystem:
    """Generic particle system"""
    
    def __init__(self, max_particles: int = 100):
        self.particles: List[Particle] = []
        self.max_particles = max_particles
        self.emission_rate = 10.0  # Particles per second
        self.emission_accumulator = 0.0
    
    def emit_particle(self, position: Vec3, velocity: Vec3, 
                     life: float, size: float, color: Color) -> Particle:
        """Emit a new particle"""
        particle = Particle(
            position=position,
            velocity=velocity,
            life=life,
            max_life=life,
            size=size,
            color=color,
            rotation=random.uniform(0, math.pi * 2),
            rotation_speed=random.uniform(-2, 2)
        )
        
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
        else:
            # Replace oldest particle
            self.particles[0] = particle
        
        return particle
    
    def update(self, delta_time: float, gravity: Vec3 = Vec3(0, -9.8, 0)):
        """Update all particles"""
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Update existing particles
        for particle in self.particles:
            # Physics
            particle.velocity = particle.velocity + gravity * delta_time
            particle.position = particle.position + particle.velocity * delta_time
            particle.rotation += particle.rotation_speed * delta_time
            
            # Life
            particle.life -= delta_time
        
        # Emit new particles based on rate
        self.emission_accumulator += delta_time * self.emission_rate
        while self.emission_accumulator >= 1.0:
            self._emit_one()
            self.emission_accumulator -= 1.0
    
    def _emit_one(self):
        """Emit one particle - override in subclasses"""
        pass
    
    def render(self, screen, time: float, camera_pos: Vec3):
        """Render particles to screen buffer"""
        pass


class SnowParticleSystem(ParticleSystem):
    """Snow particle system"""
    
    def __init__(self, bounds_width: int, bounds_height: int, max_particles: int = 200):
        super().__init__(max_particles)
        self.bounds_width = bounds_width
        self.bounds_height = bounds_height
        self.emission_rate = 20.0
        self.wind = Vec3(0, 0, 0)
    
    def set_wind(self, wind: Vec3):
        """Set wind force"""
        self.wind = wind
    
    def _emit_one(self):
        """Emit a snowflake"""
        x = random.uniform(0, self.bounds_width)
        y = self.bounds_height
        z = random.uniform(-10, 10)
        
        position = Vec3(x, y, z)
        velocity = Vec3(
            random.uniform(-0.5, 0.5),
            random.uniform(-2, -1),
            random.uniform(-0.2, 0.2)
        )
        
        life = random.uniform(10, 20)
        size = random.uniform(0.5, 1.5)
        brightness = random.uniform(0.7, 1.0)
        color = Color(brightness, brightness, brightness)
        
        self.emit_particle(position, velocity, life, size, color)
    
    def update(self, delta_time: float, gravity: Vec3 = Vec3(0, -0.5, 0)):
        """Update snowflakes with wind"""
        # Apply wind to particles
        for particle in self.particles:
            particle.velocity = particle.velocity + self.wind * delta_time * 0.5
        
        super().update(delta_time, gravity)
        
        # Respawn particles that went out of bounds
        for particle in self.particles:
            if particle.position.y < 0:
                particle.position.y = self.bounds_height
                particle.position.x = random.uniform(0, self.bounds_width)
                particle.life = particle.max_life
    
    def render(self, screen, time: float, camera_pos: Vec3):
        """Render snowflakes"""
        snow_chars = ['*', '❄', '❅', '❆', '✻', '✼']
        
        for particle in self.particles:
            # Project to screen space
            screen_x = int(particle.position.x)
            screen_y = int(particle.position.y)
            
            if 0 <= screen_x < self.bounds_width and 0 <= screen_y < self.bounds_height:
                # Choose character based on size
                char_idx = int(particle.size * 2) % len(snow_chars)
                char = snow_chars[char_idx]
                
                # Fade based on life
                alpha = min(1.0, particle.life / particle.max_life)
                color = particle.color * alpha
                
                screen.set_char(screen_x, screen_y, char, color.to_rgb255())


class SparkleSystem(ParticleSystem):
    """Sparkle/twinkle particle system"""
    
    def __init__(self, bounds_width: int, bounds_height: int, max_particles: int = 50):
        super().__init__(max_particles)
        self.bounds_width = bounds_width
        self.bounds_height = bounds_height
        self.emission_rate = 5.0
    
    def _emit_one(self):
        """Emit a sparkle"""
        x = random.uniform(0, self.bounds_width)
        y = random.uniform(0, self.bounds_height)
        z = 0
        
        position = Vec3(x, y, z)
        velocity = Vec3(0, 0, 0)  # Stationary
        
        life = random.uniform(0.5, 1.5)
        size = random.uniform(1, 2)
        
        # Random bright color
        hue = random.uniform(0, 360)
        color = Color.from_hsv(hue, 0.7, 1.0)
        
        self.emit_particle(position, velocity, life, size, color)
    
    def render(self, screen, time: float, camera_pos: Vec3):
        """Render sparkles"""
        sparkle_chars = ['✦', '✧', '✨', '⭐', '★', '☆', '✪']
        
        for particle in self.particles:
            screen_x = int(particle.position.x)
            screen_y = int(particle.position.y)
            
            if 0 <= screen_x < self.bounds_width and 0 <= screen_y < self.bounds_height:
                # Pulse effect
                pulse = math.sin(time * 10 + particle.rotation) * 0.5 + 0.5
                alpha = (particle.life / particle.max_life) * pulse
                
                color = particle.color * alpha
                char = random.choice(sparkle_chars)
                
                screen.set_char(screen_x, screen_y, char, color.to_rgb255())


# ═══════════════════════════════════════════════════════════════════════════════
# PARALLAX BACKGROUND LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class ParallaxLayer:
    """Single parallax scrolling layer"""
    
    def __init__(self, width: int, height: int, depth: float, 
                 scroll_speed: Vec2 = Vec2(0.1, 0.05)):
        self.width = width
        self.height = height
        self.depth = depth  # 0.0 = far, 1.0 = near
        self.scroll_speed = scroll_speed
        self.offset = Vec2(0, 0)
        self.shader = ParallaxShader(layers=3)
        self.shader.uniforms.resolution = Vec2(width, height)
    
    def update(self, delta_time: float):
        """Update layer offset"""
        self.offset.x += self.scroll_speed.x * delta_time * self.depth
        self.offset.y += self.scroll_speed.y * delta_time * self.depth
        
        # Wrap around
        if self.offset.x > self.width:
            self.offset.x -= self.width
        if self.offset.y > self.height:
            self.offset.y -= self.height
    
    def render(self, screen, time: float):
        """Render parallax layer"""
        self.shader.uniforms.time = time
        
        for y in range(self.height):
            for x in range(self.width):
                # Calculate UV coordinates with offset
                uv = Vec2(
                    (x + self.offset.x) / self.width,
                    (y + self.offset.y) / self.height
                )
                
                # Create fragment
                fragment = VertexOutput(
                    position=Vec3(x, y, 0),
                    world_position=Vec3(x, y, 0),
                    normal=Vec3(0, 0, 1),
                    uv=uv,
                    color=Color(1, 1, 1)
                )
                
                # Run fragment shader
                color = self.shader.fragment_shader(fragment)
                
                # Only render if not completely transparent
                if color.r > 0.01 or color.g > 0.01 or color.b > 0.01:
                    screen.set_char(x, y, '·', color.to_rgb255())


class ParallaxBackground:
    """Multi-layer parallax background system"""
    
    def __init__(self, width: int, height: int, num_layers: int = 3):
        self.width = width
        self.height = height
        self.layers: List[ParallaxLayer] = []
        
        # Create layers with different depths
        for i in range(num_layers):
            depth = (i + 1) / num_layers
            speed = Vec2(0.05 + depth * 0.15, 0.02 + depth * 0.08)
            layer = ParallaxLayer(width, height, depth, speed)
            self.layers.append(layer)
    
    def update(self, delta_time: float):
        """Update all layers"""
        for layer in self.layers:
            layer.update(delta_time)
    
    def render(self, screen, time: float):
        """Render all layers back to front"""
        for layer in self.layers:
            layer.render(screen, time)


# ═══════════════════════════════════════════════════════════════════════════════
# 3D CHRISTMAS TREE RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

class ChristmasTree3D:
    """Advanced 3D Christmas tree with all effects"""
    
    def __init__(self, width: int, height: int, position: Vec3 = Vec3(0, 0, 0)):
        self.width = width
        self.height = height
        self.position = position
        self.shader = ChristmasTreeShader()
        self.rotation = 0.0
        self.scale = 1.0
        
        # Animation state
        self.time = 0.0
        self.wind_strength = 0.3
        self.wind_phase = 0.0
        
        # Lights
        self.setup_lights()
    
    def setup_lights(self):
        """Setup lighting"""
        self.shader.uniforms.ambient_color = Color(0.05, 0.08, 0.12)
        self.shader.uniforms.camera_position = Vec3(0, 0, 20)
        
        # Add Christmas lights as point lights
        for pos in self.shader.christmas_lights:
            # Cycle through colors
            hue = (pos.x * 30 + pos.y * 20) % 360
            color = Color.from_hsv(hue, 0.9, 1.0)
            
            light = Light(
                position=pos,
                color=color,
                intensity=1.0,
                radius=5.0
            )
            self.shader.uniforms.lights.append(light)
    
    def update(self, delta_time: float):
        """Update animation"""
        self.time += delta_time
        self.wind_phase += delta_time * 2.0
        
        # Update light intensities (blinking)
        for i, light in enumerate(self.shader.uniforms.lights):
            blink_speed = 3.0 + (i % 3)
            phase = self.time * blink_speed + i * 0.7
            light.intensity = 0.5 + 0.5 * math.sin(phase)
        
        self.shader.uniforms.time = self.time
    
    def render(self, screen, time: float):
        """Render 3D tree"""
        # Calculate tree position in screen space
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Simple 3D projection
        tree_width = int(self.width * 0.3)
        tree_height = int(self.height * 0.6)
        
        # Render tree using ASCII art with shading
        for y in range(tree_height):
            screen_y = center_y - tree_height // 2 + y
            if screen_y < 0 or screen_y >= self.height:
                continue
            
            # Calculate width at this height (cone shape)
            height_ratio = y / tree_height
            radius = int(tree_width * (1 - height_ratio) / 2)
            
            # Wind sway
            wind_offset = int(math.sin(self.wind_phase + height_ratio * math.pi) * 
                            self.wind_strength * height_ratio * 5)
            
            for x in range(-radius, radius + 1):
                screen_x = center_x + x + wind_offset
                if screen_x < 0 or screen_x >= self.width:
                    continue
                
                # Calculate 3D position
                z = math.sqrt(max(0, radius**2 - x**2)) * 0.3
                pos = Vec3(x, y - tree_height/2, z if x > 0 else -z)
                
                # Run shader
                fragment = VertexOutput(
                    position=pos,
                    world_position=pos,
                    normal=Vec3(x/radius if radius > 0 else 0, 0.6, z/radius if radius > 0 else 0),
                    uv=Vec2(x / tree_width + 0.5, y / tree_height),
                    color=Color(0.2, 0.6, 0.3)
                )
                
                color = self.shader.fragment_shader(fragment)
                
                # Choose character based on depth
                if abs(x) < radius * 0.3:
                    char = '▓'
                elif abs(x) < radius * 0.7:
                    char = '▒'
                else:
                    char = '░'
                
                # Add Christmas lights
                for light_pos in self.shader.christmas_lights:
                    dist = pos.distance(light_pos)
                    if dist < 0.5:
                        char = '●'
                        light_hue = (light_pos.x * 30 + light_pos.y * 20) % 360
                        light_color = Color.from_hsv(light_hue, 0.9, 1.0)
                        blink = 0.5 + 0.5 * math.sin(self.time * 5 + light_pos.x * 10)
                        color = light_color * blink
                
                screen.set_char(screen_x, screen_y, char, color.to_rgb255())
        
        # Render trunk
        trunk_height = int(tree_height * 0.15)
        trunk_width = 3
        trunk_start_y = center_y + tree_height // 2
        
        for y in range(trunk_height):
            screen_y = trunk_start_y + y
            if screen_y >= self.height:
                break
            
            for x in range(-trunk_width, trunk_width + 1):
                screen_x = center_x + x
                if 0 <= screen_x < self.width:
                    brown = Color(0.4, 0.25, 0.1)
                    shading = 0.7 + 0.3 * math.cos(x * 0.5)
                    color = brown * shading
                    screen.set_char(screen_x, screen_y, '█', color.to_rgb255())
        
        # Render star on top
        star_y = center_y - tree_height // 2 - 2
        star_x = center_x + wind_offset
        
        if 0 <= star_x < self.width and 0 <= star_y < self.height:
            pulse = 0.7 + 0.3 * math.sin(self.time * 3)
            star_color = Color(1.0, 0.9, 0.2) * pulse
            
            # Draw star
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if abs(dx) + abs(dy) <= 1:
                        sx, sy = star_x + dx, star_y + dy
                        if 0 <= sx < self.width and 0 <= sy < self.height:
                            screen.set_char(sx, sy, '★', star_color.to_rgb255())


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPHICS COMPOSITOR
# ═══════════════════════════════════════════════════════════════════════════════

class GraphicsCompositor:
    """Composites all graphics layers"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Layers
        self.parallax = ParallaxBackground(width, height, num_layers=3)
        self.tree = ChristmasTree3D(width, height)
        self.snow = SnowParticleSystem(width, height, max_particles=200)
        self.sparkles = SparkleSystem(width, height, max_particles=30)
        
        # Effects
        self.enable_parallax = True
        self.enable_tree = True
        self.enable_snow = True
        self.enable_sparkles = True
        self.enable_post_fx = True
        
        # Timing
        self.time = 0.0
    
    def update(self, delta_time: float):
        """Update all graphics systems"""
        self.time += delta_time
        
        if self.enable_parallax:
            self.parallax.update(delta_time)
        
        if self.enable_tree:
            self.tree.update(delta_time)
        
        if self.enable_snow:
            wind = Vec3(math.sin(self.time) * 0.3, 0, 0)
            self.snow.set_wind(wind)
            self.snow.update(delta_time)
        
        if self.enable_sparkles:
            self.sparkles.update(delta_time)
    
    def render(self, screen, time: float):
        """Render all layers in order"""
        # Layer 0: Parallax background (furthest)
        if self.enable_parallax:
            self.parallax.render(screen, time)
        
        # Layer 1: Christmas tree
        if self.enable_tree:
            self.tree.render(screen, time)
        
        # Layer 2: Snow particles
        if self.enable_snow:
            self.snow.render(screen, time, Vec3(0, 0, 0))
        
        # Layer 3: Sparkles (closest)
        if self.enable_sparkles:
            self.sparkles.render(screen, time, Vec3(0, 0, 0))
        
        # Post-processing effects would go here if needed


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'Particle', 'ParticleSystem',
    'SnowParticleSystem', 'SparkleSystem',
    'ParallaxLayer', 'ParallaxBackground',
    'ChristmasTree3D',
    'GraphicsCompositor',
]
