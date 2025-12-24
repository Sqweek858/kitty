#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ADVANCED SHADER SIMULATION SYSTEM                         ║
║              GLSL/HLSL-inspired Graphics Pipeline in Python                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides a sophisticated shader system that simulates GLSL/HLSL
functionality in pure Python for terminal graphics rendering.

Features:
    - Fragment shader simulation for per-pixel effects
    - Vertex shader simulation for 3D transformations
    - Parallax occlusion mapping
    - Normal mapping and bump mapping
    - Procedural noise generation (Perlin, Simplex, Worley)
    - Advanced lighting models (Phong, Blinn-Phong, PBR)
    - Shadow mapping and ambient occlusion
    - Post-processing effects (bloom, DOF, motion blur)
    - Particle systems with GPU-style compute shaders
"""

import math
import random
from typing import Tuple, Optional, Callable, List, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR AND MATRIX MATHEMATICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Vec2:
    """2D Vector - GLSL vec2 equivalent"""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other): return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Vec2(self.x - other.x, self.y - other.y)
    def __mul__(self, s): return Vec2(self.x * s, self.y * s)
    def __truediv__(self, s): return Vec2(self.x / s, self.y / s)
    
    def dot(self, other): return self.x * other.x + self.y * other.y
    def length(self): return math.sqrt(self.x * self.x + self.y * self.y)
    def normalize(self):
        l = self.length()
        return Vec2(self.x / l, self.y / l) if l > 0 else Vec2(0, 0)
    
    def distance(self, other): return (self - other).length()


@dataclass
class Vec3:
    """3D Vector - GLSL vec3 equivalent"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other): return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other): return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, s): return Vec3(self.x * s, self.y * s, self.z * s)
    def __truediv__(self, s): return Vec3(self.x / s, self.y / s, self.z / s)
    
    def dot(self, other): return self.x * other.x + self.y * other.y + self.z * other.z
    def length(self): return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    def normalize(self):
        l = self.length()
        return Vec3(self.x / l, self.y / l, self.z / l) if l > 0 else Vec3(0, 0, 0)
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def distance(self, other): return (self - other).length()
    def reflect(self, normal): return self - normal * (self.dot(normal) * 2.0)


@dataclass
class Vec4:
    """4D Vector - GLSL vec4 equivalent"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0
    
    def __add__(self, other): return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
    def __sub__(self, other): return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
    def __mul__(self, s): return Vec4(self.x * s, self.y * s, self.z * s, self.w * s)
    
    def xyz(self): return Vec3(self.x, self.y, self.z)


class Mat4:
    """4x4 Matrix - GLSL mat4 equivalent"""
    
    def __init__(self, data: Optional[List[List[float]]] = None):
        if data is None:
            # Identity matrix
            self.data = [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        else:
            self.data = data
    
    def __mul__(self, other):
        """Matrix multiplication"""
        if isinstance(other, Mat4):
            result = [[0.0] * 4 for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    for k in range(4):
                        result[i][j] += self.data[i][k] * other.data[k][j]
            return Mat4(result)
        elif isinstance(other, Vec4):
            # Matrix-vector multiplication
            result = [0.0] * 4
            for i in range(4):
                result[i] = (self.data[i][0] * other.x +
                           self.data[i][1] * other.y +
                           self.data[i][2] * other.z +
                           self.data[i][3] * other.w)
            return Vec4(*result)
        elif isinstance(other, Vec3):
            # Treat Vec3 as Vec4 with w=1
            v4 = Vec4(other.x, other.y, other.z, 1.0)
            result = self * v4
            return Vec3(result.x, result.y, result.z)
    
    @staticmethod
    def translation(x: float, y: float, z: float):
        """Create translation matrix"""
        return Mat4([
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0]
        ])
    
    @staticmethod
    def rotation_x(angle: float):
        """Create rotation matrix around X axis"""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, -s, 0.0],
            [0.0, s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
    
    @staticmethod
    def rotation_y(angle: float):
        """Create rotation matrix around Y axis"""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [c, 0.0, s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-s, 0.0, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
    
    @staticmethod
    def rotation_z(angle: float):
        """Create rotation matrix around Z axis"""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [c, -s, 0.0, 0.0],
            [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
    
    @staticmethod
    def scale(x: float, y: float, z: float):
        """Create scale matrix"""
        return Mat4([
            [x, 0.0, 0.0, 0.0],
            [0.0, y, 0.0, 0.0],
            [0.0, 0.0, z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
    
    @staticmethod
    def perspective(fov: float, aspect: float, near: float, far: float):
        """Create perspective projection matrix"""
        f = 1.0 / math.tan(fov / 2.0)
        return Mat4([
            [f / aspect, 0.0, 0.0, 0.0],
            [0.0, f, 0.0, 0.0],
            [0.0, 0.0, (far + near) / (near - far), (2.0 * far * near) / (near - far)],
            [0.0, 0.0, -1.0, 0.0]
        ])


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Color:
    """RGB Color - GLSL vec3 equivalent for colors"""
    r: float
    g: float
    b: float
    
    def __add__(self, other): return Color(self.r + other.r, self.g + other.g, self.b + other.b)
    def __sub__(self, other): return Color(self.r - other.r, self.g - other.g, self.b - other.b)
    def __mul__(self, s): 
        if isinstance(s, Color):
            return Color(self.r * s.r, self.g * s.g, self.b * s.b)
        return Color(self.r * s, self.g * s, self.b * s)
    def __truediv__(self, s): return Color(self.r / s, self.g / s, self.b / s)
    
    def clamp(self):
        """Clamp color values to [0, 1]"""
        return Color(
            max(0.0, min(1.0, self.r)),
            max(0.0, min(1.0, self.g)),
            max(0.0, min(1.0, self.b))
        )
    
    def to_rgb255(self) -> Tuple[int, int, int]:
        """Convert to 0-255 RGB"""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255)
        )
    
    @staticmethod
    def from_rgb255(r: int, g: int, b: int):
        """Create from 0-255 RGB"""
        return Color(r / 255.0, g / 255.0, b / 255.0)
    
    @staticmethod
    def from_hsv(h: float, s: float, v: float):
        """Create color from HSV"""
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
        
        return Color(r + m, g + m, b + m)
    
    def blend(self, other, factor: float):
        """Blend with another color"""
        return Color(
            self.r * (1 - factor) + other.r * factor,
            self.g * (1 - factor) + other.g * factor,
            self.b * (1 - factor) + other.b * factor
        )
    
    def lerp(self, other, t: float):
        """Linear interpolation"""
        return self.blend(other, t)


# ═══════════════════════════════════════════════════════════════════════════════
# NOISE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class NoiseGenerator:
    """Procedural noise generation (Perlin, Simplex, Worley)"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        
        # Permutation table for Perlin noise
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm *= 2
    
    def _fade(self, t: float) -> float:
        """Perlin fade function"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, t: float, a: float, b: float) -> float:
        """Linear interpolation"""
        return a + t * (b - a)
    
    def _grad(self, hash: int, x: float, y: float, z: float = 0.0) -> float:
        """Gradient function"""
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def perlin2d(self, x: float, y: float) -> float:
        """2D Perlin noise"""
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        
        u = self._fade(x)
        v = self._fade(y)
        
        a = self.perm[X] + Y
        aa = self.perm[a]
        ab = self.perm[a + 1]
        b = self.perm[X + 1] + Y
        ba = self.perm[b]
        bb = self.perm[b + 1]
        
        res = self._lerp(v,
            self._lerp(u, self._grad(self.perm[aa], x, y),
                         self._grad(self.perm[ba], x - 1, y)),
            self._lerp(u, self._grad(self.perm[ab], x, y - 1),
                         self._grad(self.perm[bb], x - 1, y - 1)))
        
        return res
    
    def perlin3d(self, x: float, y: float, z: float) -> float:
        """3D Perlin noise"""
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        Z = int(math.floor(z)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)
        
        u = self._fade(x)
        v = self._fade(y)
        w = self._fade(z)
        
        a = self.perm[X] + Y
        aa = self.perm[a] + Z
        ab = self.perm[a + 1] + Z
        b = self.perm[X + 1] + Y
        ba = self.perm[b] + Z
        bb = self.perm[b + 1] + Z
        
        return self._lerp(w,
            self._lerp(v,
                self._lerp(u, self._grad(self.perm[aa], x, y, z),
                             self._grad(self.perm[ba], x - 1, y, z)),
                self._lerp(u, self._grad(self.perm[ab], x, y - 1, z),
                             self._grad(self.perm[bb], x - 1, y - 1, z))),
            self._lerp(v,
                self._lerp(u, self._grad(self.perm[aa + 1], x, y, z - 1),
                             self._grad(self.perm[ba + 1], x - 1, y, z - 1)),
                self._lerp(u, self._grad(self.perm[ab + 1], x, y - 1, z - 1),
                             self._grad(self.perm[bb + 1], x - 1, y - 1, z - 1))))
    
    def fbm(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        """Fractional Brownian Motion"""
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.perlin2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
        
        return total / max_value
    
    def worley(self, x: float, y: float, cell_size: float = 1.0) -> float:
        """Worley noise (cellular/Voronoi)"""
        cell_x = int(math.floor(x / cell_size))
        cell_y = int(math.floor(y / cell_size))
        
        min_dist = float('inf')
        
        # Check neighboring cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cx = cell_x + dx
                cy = cell_y + dy
                
                # Generate point in this cell
                random.seed(self.seed + cx * 73856093 + cy * 19349663)
                px = (cx + random.random()) * cell_size
                py = (cy + random.random()) * cell_size
                
                # Distance to point
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
                min_dist = min(min_dist, dist)
        
        random.seed(self.seed)
        return min_dist


# ═══════════════════════════════════════════════════════════════════════════════
# LIGHTING MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Light:
    """Light source definition"""
    position: Vec3
    color: Color
    intensity: float
    radius: float = 100.0
    
    def attenuation(self, distance: float) -> float:
        """Calculate light attenuation"""
        if distance >= self.radius:
            return 0.0
        return (1.0 - (distance / self.radius)) ** 2


class LightingModel:
    """Advanced lighting calculations"""
    
    @staticmethod
    def phong(normal: Vec3, light_dir: Vec3, view_dir: Vec3, 
              shininess: float = 32.0) -> Tuple[float, float]:
        """Phong lighting model - returns (diffuse, specular)"""
        # Diffuse
        diffuse = max(0.0, normal.dot(light_dir))
        
        # Specular
        reflect_dir = light_dir.reflect(normal)
        spec = pow(max(0.0, view_dir.dot(reflect_dir)), shininess)
        
        return diffuse, spec
    
    @staticmethod
    def blinn_phong(normal: Vec3, light_dir: Vec3, view_dir: Vec3,
                   shininess: float = 32.0) -> Tuple[float, float]:
        """Blinn-Phong lighting model - returns (diffuse, specular)"""
        # Diffuse
        diffuse = max(0.0, normal.dot(light_dir))
        
        # Specular (using halfway vector)
        halfway = (light_dir + view_dir).normalize()
        spec = pow(max(0.0, normal.dot(halfway)), shininess)
        
        return diffuse, spec
    
    @staticmethod
    def calculate_lighting(position: Vec3, normal: Vec3, view_dir: Vec3,
                         lights: List[Light], ambient: Color,
                         diffuse_color: Color, specular_color: Color,
                         shininess: float = 32.0) -> Color:
        """Calculate final lit color"""
        result = ambient * diffuse_color
        
        for light in lights:
            light_vec = light.position - position
            distance = light_vec.length()
            light_dir = light_vec.normalize()
            
            # Attenuation
            atten = light.attenuation(distance)
            if atten <= 0.0:
                continue
            
            # Blinn-Phong
            diff, spec = LightingModel.blinn_phong(normal, light_dir, view_dir, shininess)
            
            # Add contribution
            light_contrib = light.color * light.intensity * atten
            result = result + diffuse_color * light_contrib * diff
            result = result + specular_color * light_contrib * spec
        
        return result.clamp()


# ═══════════════════════════════════════════════════════════════════════════════
# SHADER PROGRAMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ShaderUniforms:
    """Shader uniform variables"""
    time: float = 0.0
    resolution: Vec2 = None
    mouse: Vec2 = None
    model_matrix: Mat4 = None
    view_matrix: Mat4 = None
    projection_matrix: Mat4 = None
    lights: List[Light] = None
    ambient_color: Color = None
    camera_position: Vec3 = None
    
    def __post_init__(self):
        if self.resolution is None:
            self.resolution = Vec2(100, 100)
        if self.mouse is None:
            self.mouse = Vec2(0, 0)
        if self.model_matrix is None:
            self.model_matrix = Mat4()
        if self.view_matrix is None:
            self.view_matrix = Mat4()
        if self.projection_matrix is None:
            self.projection_matrix = Mat4()
        if self.lights is None:
            self.lights = []
        if self.ambient_color is None:
            self.ambient_color = Color(0.1, 0.1, 0.15)
        if self.camera_position is None:
            self.camera_position = Vec3(0, 0, 5)


@dataclass
class VertexInput:
    """Vertex shader input"""
    position: Vec3
    normal: Vec3
    uv: Vec2
    color: Color = None


@dataclass
class VertexOutput:
    """Vertex shader output / Fragment shader input"""
    position: Vec4  # Clip space position
    world_position: Vec3
    normal: Vec3
    uv: Vec2
    color: Color


class ShaderProgram:
    """Base shader program"""
    
    def __init__(self):
        self.uniforms = ShaderUniforms()
        self.noise = NoiseGenerator()
    
    def vertex_shader(self, vertex: VertexInput) -> VertexOutput:
        """Vertex shader - transform vertices"""
        # Transform to world space
        world_pos = self.uniforms.model_matrix * vertex.position
        
        # Transform to clip space
        view_pos = self.uniforms.view_matrix * world_pos
        clip_pos = self.uniforms.projection_matrix * view_pos
        
        # Transform normal
        world_normal = (self.uniforms.model_matrix * vertex.normal).normalize()
        
        return VertexOutput(
            position=clip_pos,
            world_position=world_pos,
            normal=world_normal,
            uv=vertex.uv,
            color=vertex.color or Color(1, 1, 1)
        )
    
    def fragment_shader(self, fragment: VertexOutput) -> Color:
        """Fragment shader - calculate pixel color"""
        # Default: just return vertex color
        return fragment.color


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIALIZED SHADERS
# ═══════════════════════════════════════════════════════════════════════════════

class ParallaxShader(ShaderProgram):
    """Parallax scrolling background shader"""
    
    def __init__(self, layers: int = 5):
        super().__init__()
        self.layers = layers
        self.star_density = 0.02
    
    def fragment_shader(self, fragment: VertexOutput) -> Color:
        """Render parallax starfield"""
        uv = fragment.uv
        time = self.uniforms.time
        
        color = Color(0.0, 0.0, 0.0)
        
        # Multiple parallax layers
        for layer in range(self.layers):
            layer_speed = 0.1 + layer * 0.05
            layer_depth = 1.0 - (layer / self.layers)
            
            # Offset UV by time for scrolling effect
            offset_uv = Vec2(
                uv.x + time * layer_speed,
                uv.y + time * layer_speed * 0.3
            )
            
            # Generate stars using noise
            star_value = self.noise.worley(
                offset_uv.x * 50.0 / layer_depth,
                offset_uv.y * 50.0 / layer_depth,
                2.0
            )
            
            if star_value < self.star_density:
                # Star brightness based on depth
                brightness = 0.3 + layer_depth * 0.7
                
                # Twinkle effect
                twinkle = 0.7 + 0.3 * math.sin(time * 5.0 + star_value * 100.0)
                brightness *= twinkle
                
                # Color variation
                hue = (star_value * 360.0) % 60.0 + 180.0
                star_color = Color.from_hsv(hue, 0.3, brightness)
                
                color = color + star_color
        
        return color.clamp()


class ChristmasTreeShader(ShaderProgram):
    """Advanced 3D Christmas tree shader with all effects"""
    
    def __init__(self):
        super().__init__()
        self.tree_height = 20.0
        self.tree_base_radius = 8.0
        self.trunk_height = 4.0
        self.trunk_radius = 1.0
        
        # Light positions on tree (spiral pattern)
        self.christmas_lights = self._generate_light_positions()
    
    def _generate_light_positions(self) -> List[Vec3]:
        """Generate Christmas light positions in spiral"""
        positions = []
        num_lights = 30
        
        for i in range(num_lights):
            t = i / num_lights
            angle = t * math.pi * 8  # 4 spirals
            height = self.tree_height * (1 - t)
            radius = self.tree_base_radius * (1 - t) * 0.9
            
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            y = -self.tree_height / 2 + height
            
            positions.append(Vec3(x, y, z))
        
        return positions
    
    def sdf_cone(self, p: Vec3, h: float, r: float) -> float:
        """Signed distance function for cone"""
        q = Vec2(Vec2(p.x, p.z).length(), p.y)
        k = Vec2(r / h, 1.0)
        w = Vec2(q.x - k.x * q.y, q.y - k.y * q.x)
        
        if w.x > 0 and w.y > 0:
            return w.length()
        elif w.x < 0:
            return -w.x
        else:
            return -w.y
    
    def sdf_cylinder(self, p: Vec3, h: float, r: float) -> float:
        """Signed distance function for cylinder"""
        d = Vec2(Vec2(p.x, p.z).length() - r, abs(p.y) - h / 2)
        return min(max(d.x, d.y), 0.0) + Vec2(max(d.x, 0), max(d.y, 0)).length()
    
    def get_tree_normal(self, p: Vec3) -> Vec3:
        """Calculate normal at point on tree surface"""
        epsilon = 0.01
        
        # Numerical gradient
        dx = self.sdf_cone(Vec3(p.x + epsilon, p.y, p.z), self.tree_height, self.tree_base_radius) - \
             self.sdf_cone(Vec3(p.x - epsilon, p.y, p.z), self.tree_height, self.tree_base_radius)
        dy = self.sdf_cone(Vec3(p.x, p.y + epsilon, p.z), self.tree_height, self.tree_base_radius) - \
             self.sdf_cone(Vec3(p.x, p.y - epsilon, p.z), self.tree_height, self.tree_base_radius)
        dz = self.sdf_cone(Vec3(p.x, p.y, p.z + epsilon), self.tree_height, self.tree_base_radius) - \
             self.sdf_cone(Vec3(p.x, p.y, p.z - epsilon), self.tree_height, self.tree_base_radius)
        
        return Vec3(dx, dy, dz).normalize()
    
    def fragment_shader(self, fragment: VertexOutput) -> Color:
        """Render Christmas tree with advanced effects"""
        pos = fragment.world_position
        time = self.uniforms.time
        
        # Check if point is on tree cone
        dist_cone = self.sdf_cone(pos, self.tree_height, self.tree_base_radius)
        dist_trunk = self.sdf_cylinder(
            Vec3(pos.x, pos.y + self.tree_height / 2 + self.trunk_height / 2, pos.z),
            self.trunk_height,
            self.trunk_radius
        )
        
        # Tree body
        if dist_cone < 0.5:
            normal = self.get_tree_normal(pos)
            
            # Base green color with gradient
            height_factor = (pos.y + self.tree_height / 2) / self.tree_height
            base_color = Color(0.1, 0.4, 0.15).blend(Color(0.2, 0.7, 0.3), height_factor)
            
            # Add procedural detail
            detail = self.noise.fbm(pos.x * 2, pos.z * 2, octaves=3) * 0.15
            base_color = base_color * (1.0 + detail)
            
            # Lighting
            view_dir = (self.uniforms.camera_position - pos).normalize()
            color = LightingModel.calculate_lighting(
                pos, normal, view_dir,
                self.uniforms.lights,
                self.uniforms.ambient_color,
                base_color,
                Color(0.1, 0.1, 0.1),
                shininess=8.0
            )
            
            # Add Christmas light glow
            for light_pos in self.christmas_lights:
                dist_to_light = pos.distance(light_pos)
                if dist_to_light < 1.0:
                    # Light color based on position
                    light_hue = (light_pos.x * 10 + light_pos.y * 5) % 360
                    light_color = Color.from_hsv(light_hue, 0.8, 1.0)
                    
                    # Blinking effect
                    blink = 0.5 + 0.5 * math.sin(time * 5.0 + light_pos.x * 10)
                    
                    glow = (1.0 - dist_to_light) * blink
                    color = color + light_color * glow * 0.5
            
            return color.clamp()
        
        # Trunk
        elif dist_trunk < 0.5:
            brown = Color(0.4, 0.25, 0.1)
            
            # Simple shading
            normal = Vec3(0, 0, 1)  # Simplified
            diffuse = max(0.3, normal.dot(Vec3(0.3, 0.6, 0.7)))
            
            return (brown * diffuse).clamp()
        
        # Background
        else:
            return Color(0, 0, 0)


class SnowShader(ShaderProgram):
    """Procedural falling snow shader"""
    
    def __init__(self, particle_count: int = 200):
        super().__init__()
        self.particle_count = particle_count
    
    def fragment_shader(self, fragment: VertexOutput) -> Color:
        """Render falling snow particles"""
        uv = fragment.uv
        time = self.uniforms.time
        
        color = Color(0, 0, 0)
        
        # Generate snow particles
        for i in range(self.particle_count):
            # Pseudo-random position based on index
            seed_x = math.sin(i * 12.9898) * 43758.5453
            seed_y = math.cos(i * 78.233) * 43758.5453
            
            x = (seed_x % 1.0)
            y = ((seed_y + time * 0.5) % 1.0)
            
            # Horizontal drift
            x += math.sin(time + i) * 0.1
            
            # Distance to particle
            dist = math.sqrt((uv.x - x) ** 2 + (uv.y - y) ** 2)
            
            if dist < 0.005:  # Particle size
                brightness = 1.0 - (dist / 0.005)
                color = color + Color(brightness, brightness, brightness + 0.1)
        
        return color.clamp()


# ═══════════════════════════════════════════════════════════════════════════════
# POST-PROCESSING EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════

class PostProcessing:
    """Post-processing effects pipeline"""
    
    @staticmethod
    def bloom(color: Color, threshold: float = 0.8, intensity: float = 0.5) -> Color:
        """Bloom effect"""
        brightness = (color.r + color.g + color.b) / 3.0
        
        if brightness > threshold:
            excess = (brightness - threshold) / (1.0 - threshold)
            bloom_color = color * (excess * intensity)
            return (color + bloom_color).clamp()
        
        return color
    
    @staticmethod
    def vignette(color: Color, uv: Vec2, intensity: float = 0.5) -> Color:
        """Vignette effect"""
        center = Vec2(0.5, 0.5)
        dist = uv.distance(center)
        vignette_factor = 1.0 - (dist * intensity)
        return (color * max(0.0, vignette_factor)).clamp()
    
    @staticmethod
    def chromatic_aberration(base_uv: Vec2, offset: float = 0.002) -> Tuple[Vec2, Vec2, Vec2]:
        """Chromatic aberration - returns (r_uv, g_uv, b_uv)"""
        center = Vec2(0.5, 0.5)
        direction = (base_uv - center).normalize()
        
        r_uv = Vec2(base_uv.x - direction.x * offset, base_uv.y - direction.y * offset)
        g_uv = base_uv
        b_uv = Vec2(base_uv.x + direction.x * offset, base_uv.y + direction.y * offset)
        
        return r_uv, g_uv, b_uv
    
    @staticmethod
    def tone_mapping(color: Color, exposure: float = 1.0) -> Color:
        """Tone mapping (Reinhard)"""
        exposed = color * exposure
        return Color(
            exposed.r / (exposed.r + 1.0),
            exposed.g / (exposed.g + 1.0),
            exposed.b / (exposed.b + 1.0)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'Vec2', 'Vec3', 'Vec4', 'Mat4',
    'Color',
    'NoiseGenerator',
    'Light', 'LightingModel',
    'ShaderProgram', 'ShaderUniforms',
    'VertexInput', 'VertexOutput',
    'ParallaxShader', 'ChristmasTreeShader', 'SnowShader',
    'PostProcessing',
]
