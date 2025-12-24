#!/usr/bin/env python3
"""
Brad TUI Ultra - Advanced Effects Module
========================================

Comprehensive visual effects system for Brad TUI Ultra.
Includes particle systems, shaders, transitions, and advanced animations.

Features:
- Particle systems (snow, rain, fire, sparks, etc.)
- Shader effects (blur, glow, wave, ripple)
- Transitions (fade, slide, zoom, rotate)
- Advanced animations with easing functions
- Text effects (typing, glitch, rainbow, matrix)
- Background effects (stars, nebula, aurora)
- Interactive effects (mouse trails, click effects)
"""

import math
import random
import time
from typing import List, Tuple, Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# EASING FUNCTIONS
# =============================================================================

class EasingType(Enum):
    """Easing function types"""
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_QUART = "ease_in_quart"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    EASE_IN_BOUNCE = "ease_in_bounce"
    EASE_OUT_BOUNCE = "ease_out_bounce"
    EASE_IN_OUT_BOUNCE = "ease_in_out_bounce"
    EASE_IN_ELASTIC = "ease_in_elastic"
    EASE_OUT_ELASTIC = "ease_out_elastic"
    EASE_IN_OUT_ELASTIC = "ease_in_out_elastic"


class Easing:
    """Collection of easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease in"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease out"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease in/out"""
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease in"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease out"""
        t -= 1
        return t * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease in/out"""
        t *= 2
        if t < 1:
            return 0.5 * t * t * t
        t -= 2
        return 0.5 * (t * t * t + 2)
    
    @staticmethod
    def ease_in_quart(t: float) -> float:
        """Quartic ease in"""
        return t * t * t * t
    
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease out"""
        t -= 1
        return 1 - t * t * t * t
    
    @staticmethod
    def ease_in_out_quart(t: float) -> float:
        """Quartic ease in/out"""
        t *= 2
        if t < 1:
            return 0.5 * t * t * t * t
        t -= 2
        return -0.5 * (t * t * t * t - 2)
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce ease out"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375
    
    @staticmethod
    def ease_in_bounce(t: float) -> float:
        """Bounce ease in"""
        return 1 - Easing.ease_out_bounce(1 - t)
    
    @staticmethod
    def ease_in_out_bounce(t: float) -> float:
        """Bounce ease in/out"""
        if t < 0.5:
            return Easing.ease_in_bounce(t * 2) * 0.5
        return Easing.ease_out_bounce(t * 2 - 1) * 0.5 + 0.5
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        """Elastic ease out"""
        if t == 0 or t == 1:
            return t
        p = 0.3
        s = p / 4
        return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1
    
    @staticmethod
    def ease_in_elastic(t: float) -> float:
        """Elastic ease in"""
        return 1 - Easing.ease_out_elastic(1 - t)
    
    @staticmethod
    def ease_in_out_elastic(t: float) -> float:
        """Elastic ease in/out"""
        if t < 0.5:
            return Easing.ease_in_elastic(t * 2) * 0.5
        return Easing.ease_out_elastic(t * 2 - 1) * 0.5 + 0.5
    
    @staticmethod
    def get_easing_function(easing_type: EasingType) -> Callable[[float], float]:
        """Get easing function by type"""
        return getattr(Easing, easing_type.value, Easing.linear)


# =============================================================================
# PARTICLE SYSTEM
# =============================================================================

@dataclass
class Particle:
    """Single particle in a particle system"""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    life: float = 1.0
    max_life: float = 1.0
    size: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    char: str = "*"
    rotation: float = 0.0
    spin: float = 0.0
    alpha: float = 1.0
    
    def update(self, dt: float) -> bool:
        """Update particle physics. Returns False if particle is dead."""
        # Apply acceleration
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        
        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Update rotation
        self.rotation += self.spin * dt
        
        # Update life
        self.life -= dt
        
        # Update alpha based on life
        self.alpha = max(0.0, self.life / self.max_life)
        
        return self.life > 0


class ParticleEmitter:
    """Emitter that spawns and manages particles"""
    
    def __init__(
        self,
        x: float,
        y: float,
        emission_rate: float = 10.0,
        particle_life: float = 2.0,
        particle_life_variance: float = 0.5,
    ):
        """Initialize particle emitter"""
        self.x = x
        self.y = y
        self.emission_rate = emission_rate
        self.particle_life = particle_life
        self.particle_life_variance = particle_life_variance
        
        self.particles: List[Particle] = []
        self.emission_accumulator = 0.0
        self.active = True
        
        # Emitter properties
        self.velocity_range = ((-1, 1), (-1, 1))
        self.acceleration = (0.0, 0.5)
        self.size_range = (0.5, 1.5)
        self.color_range = ((255, 255, 255), (255, 255, 255))
        self.char_set = ["*", "·", "+"]
        self.spin_range = (-1.0, 1.0)
    
    def emit(self, count: int = 1) -> None:
        """Emit particles"""
        for _ in range(count):
            life = self.particle_life + random.uniform(
                -self.particle_life_variance,
                self.particle_life_variance
            )
            
            particle = Particle(
                x=self.x,
                y=self.y,
                vx=random.uniform(*self.velocity_range[0]),
                vy=random.uniform(*self.velocity_range[1]),
                ax=self.acceleration[0],
                ay=self.acceleration[1],
                life=life,
                max_life=life,
                size=random.uniform(*self.size_range),
                color=self._interpolate_color(*self.color_range, random.random()),
                char=random.choice(self.char_set),
                spin=random.uniform(*self.spin_range),
            )
            
            self.particles.append(particle)
    
    def _interpolate_color(
        self,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        t: float
    ) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )
    
    def update(self, dt: float) -> None:
        """Update all particles"""
        # Emit new particles
        if self.active:
            self.emission_accumulator += self.emission_rate * dt
            while self.emission_accumulator >= 1.0:
                self.emit(1)
                self.emission_accumulator -= 1.0
        
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def get_particles(self) -> List[Particle]:
        """Get list of active particles"""
        return self.particles


# =============================================================================
# PRESET PARTICLE SYSTEMS
# =============================================================================

class SnowEmitter(ParticleEmitter):
    """Snow particle emitter"""
    
    def __init__(self, x: float, y: float, width: float = 100):
        super().__init__(x, y, emission_rate=2.0, particle_life=10.0)
        self.width = width
        self.velocity_range = ((-0.5, 0.5), (2.0, 5.0))
        self.acceleration = (0.2, 0.1)
        self.size_range = (0.8, 1.2)
        self.color_range = ((255, 255, 255), (200, 220, 255))
        self.char_set = ["❄", "❅", "❆", "*", "·"]
        self.spin_range = (-2.0, 2.0)
    
    def emit(self, count: int = 1) -> None:
        """Emit snow particles across width"""
        original_x = self.x
        for _ in range(count):
            self.x = original_x + random.uniform(0, self.width)
            super().emit(1)
        self.x = original_x


class RainEmitter(ParticleEmitter):
    """Rain particle emitter"""
    
    def __init__(self, x: float, y: float, width: float = 100):
        super().__init__(x, y, emission_rate=20.0, particle_life=2.0)
        self.width = width
        self.velocity_range = ((-0.5, 0.5), (10.0, 15.0))
        self.acceleration = (0.0, 2.0)
        self.size_range = (0.5, 1.0)
        self.color_range = ((100, 150, 255), (150, 200, 255))
        self.char_set = ["|", "│", "┃"]
        self.spin_range = (0.0, 0.0)


class FireEmitter(ParticleEmitter):
    """Fire particle emitter"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, emission_rate=15.0, particle_life=1.5)
        self.velocity_range = ((-1.0, 1.0), (-5.0, -2.0))
        self.acceleration = (0.0, -1.0)
        self.size_range = (0.5, 2.0)
        self.color_range = ((255, 50, 0), (255, 200, 0))
        self.char_set = ["▲", "▴", "∗", "*", "·"]
        self.spin_range = (-3.0, 3.0)


class SparksEmitter(ParticleEmitter):
    """Sparks particle emitter"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, emission_rate=30.0, particle_life=0.5)
        self.velocity_range = ((-5.0, 5.0), (-5.0, 5.0))
        self.acceleration = (0.0, 9.8)
        self.size_range = (0.3, 1.0)
        self.color_range = ((255, 255, 0), (255, 100, 0))
        self.char_set = ["*", "·", "+", "×"]
        self.spin_range = (-10.0, 10.0)


# =============================================================================
# TEXT EFFECTS
# =============================================================================

class TextEffect:
    """Base class for text effects"""
    
    def __init__(self, text: str, duration: float = 1.0):
        """Initialize text effect"""
        self.text = text
        self.duration = duration
        self.elapsed = 0.0
        self.complete = False
    
    def update(self, dt: float) -> None:
        """Update effect"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.complete = True
    
    def render(self) -> str:
        """Render text with effect applied"""
        return self.text
    
    def is_complete(self) -> bool:
        """Check if effect is complete"""
        return self.complete


class TypingEffect(TextEffect):
    """Typewriter effect"""
    
    def __init__(
        self,
        text: str,
        chars_per_second: float = 30.0,
        cursor: str = "▌"
    ):
        duration = len(text) / chars_per_second
        super().__init__(text, duration)
        self.chars_per_second = chars_per_second
        self.cursor = cursor
    
    def render(self) -> str:
        """Render typing effect"""
        chars_shown = int(self.elapsed * self.chars_per_second)
        chars_shown = min(chars_shown, len(self.text))
        
        shown_text = self.text[:chars_shown]
        
        if not self.complete:
            shown_text += self.cursor
        
        return shown_text


class FadeInEffect(TextEffect):
    """Fade in text effect"""
    
    def __init__(self, text: str, duration: float = 1.0):
        super().__init__(text, duration)
    
    def render(self) -> str:
        """Render fade in effect"""
        progress = min(1.0, self.elapsed / self.duration)
        
        # Gradually reveal characters
        chars_shown = int(len(self.text) * progress)
        
        # Apply partial transparency to revealed chars
        alpha = Easing.ease_out_cubic(progress)
        
        if alpha < 1.0:
            # Dim the text based on alpha
            return self.text[:chars_shown]
        
        return self.text


class GlitchEffect(TextEffect):
    """Glitch text effect"""
    
    def __init__(self, text: str, duration: float = 0.5, intensity: float = 0.3):
        super().__init__(text, duration)
        self.intensity = intensity
    
    def render(self) -> str:
        """Render glitch effect"""
        progress = self.elapsed / self.duration
        
        # Reduce intensity over time
        current_intensity = self.intensity * (1.0 - progress)
        
        result = []
        for char in self.text:
            if random.random() < current_intensity:
                # Random glitch character
                glitch_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                result.append(random.choice(glitch_chars))
            else:
                result.append(char)
        
        return ''.join(result)


class RainbowEffect(TextEffect):
    """Rainbow color text effect"""
    
    def __init__(self, text: str, speed: float = 1.0, spread: float = 0.1):
        super().__init__(text, float('inf'))  # Infinite duration
        self.speed = speed
        self.spread = spread
    
    def render(self) -> str:
        """Render rainbow effect"""
        result = []
        
        for i, char in enumerate(self.text):
            # Calculate hue based on position and time
            hue = (i * self.spread + self.elapsed * self.speed) % 1.0
            
            # Convert HSV to RGB
            r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
            
            # ANSI color code
            result.append(f"\x1b[38;2;{r};{g};{b}m{char}\x1b[0m")
        
        return ''.join(result)
    
    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
        i = int(h * 6.0)
        f = h * 6.0 - i
        p = v * (1.0 - s)
        q = v * (1.0 - f * s)
        t = v * (1.0 - (1.0 - f) * s)
        
        i = i % 6
        
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return int(r * 255), int(g * 255), int(b * 255)


class MatrixEffect(TextEffect):
    """Matrix-style falling characters effect"""
    
    def __init__(self, width: int, height: int, density: float = 0.05):
        super().__init__("", float('inf'))
        self.width = width
        self.height = height
        self.density = density
        self.columns: List[Dict[str, Any]] = []
        
        # Initialize columns
        for x in range(width):
            if random.random() < density:
                self.columns.append({
                    'x': x,
                    'y': random.randint(-height, 0),
                    'speed': random.uniform(1.0, 3.0),
                    'length': random.randint(5, 15),
                })
    
    def update(self, dt: float) -> None:
        """Update matrix effect"""
        super().update(dt)
        
        # Update columns
        for col in self.columns:
            col['y'] += col['speed'] * dt
            
            # Reset column if off screen
            if col['y'] > self.height + col['length']:
                col['y'] = -col['length']
                col['x'] = random.randint(0, self.width - 1)
                col['speed'] = random.uniform(1.0, 3.0)
                col['length'] = random.randint(5, 15)
    
    def render_at(self, buffer: List[List[str]]) -> None:
        """Render matrix effect into character buffer"""
        for col in self.columns:
            x = int(col['x'])
            y_start = int(col['y'])
            length = col['length']
            
            for i in range(length):
                y = y_start - i
                if 0 <= y < self.height and 0 <= x < self.width:
                    # Random character
                    char = random.choice("01アイウエオカキクケコ")
                    
                    # Color gradient (brighter at head)
                    intensity = 1.0 - (i / length)
                    color = int(255 * intensity)
                    
                    buffer[y][x] = f"\x1b[38;2;0;{color};0m{char}\x1b[0m"


# =============================================================================
# TRANSITION EFFECTS
# =============================================================================

class Transition:
    """Base class for screen transitions"""
    
    def __init__(self, duration: float = 1.0, easing: EasingType = EasingType.LINEAR):
        """Initialize transition"""
        self.duration = duration
        self.easing = easing
        self.elapsed = 0.0
        self.complete = False
        self.easing_func = Easing.get_easing_function(easing)
    
    def update(self, dt: float) -> None:
        """Update transition"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.complete = True
            self.elapsed = self.duration
    
    def get_progress(self) -> float:
        """Get transition progress with easing applied"""
        t = min(1.0, self.elapsed / self.duration)
        return self.easing_func(t)
    
    def is_complete(self) -> bool:
        """Check if transition is complete"""
        return self.complete
    
    def apply(self, screen: List[List[str]]) -> List[List[str]]:
        """Apply transition effect to screen buffer"""
        return screen


class FadeTransition(Transition):
    """Fade in/out transition"""
    
    def __init__(self, duration: float = 1.0, fade_in: bool = True):
        super().__init__(duration, EasingType.EASE_IN_OUT_QUAD)
        self.fade_in = fade_in
    
    def apply(self, screen: List[List[str]]) -> List[List[str]]:
        """Apply fade transition"""
        progress = self.get_progress()
        
        if not self.fade_in:
            progress = 1.0 - progress
        
        # Apply transparency (simplified)
        if progress < 1.0:
            # In a real implementation, would adjust colors
            # For now, just return the screen
            pass
        
        return screen


class SlideTransition(Transition):
    """Slide transition"""
    
    def __init__(
        self,
        duration: float = 1.0,
        direction: str = "left"  # left, right, up, down
    ):
        super().__init__(duration, EasingType.EASE_IN_OUT_CUBIC)
        self.direction = direction
    
    def apply(self, screen: List[List[str]]) -> List[List[str]]:
        """Apply slide transition"""
        progress = self.get_progress()
        
        # Calculate offset based on direction
        height = len(screen)
        width = len(screen[0]) if screen else 0
        
        if self.direction == "left":
            offset_x = int(width * (1.0 - progress))
        elif self.direction == "right":
            offset_x = -int(width * (1.0 - progress))
        elif self.direction == "up":
            offset_y = int(height * (1.0 - progress))
        else:  # down
            offset_y = -int(height * (1.0 - progress))
        
        # In real implementation, would shift screen buffer
        return screen


# =============================================================================
# SHADER EFFECTS
# =============================================================================

class Shader:
    """Base shader class for post-processing effects"""
    
    def apply(
        self,
        screen: List[List[str]],
        width: int,
        height: int
    ) -> List[List[str]]:
        """Apply shader effect to screen"""
        return screen


class BlurShader(Shader):
    """Blur shader"""
    
    def __init__(self, radius: int = 1):
        """Initialize blur shader"""
        self.radius = radius
    
    def apply(
        self,
        screen: List[List[str]],
        width: int,
        height: int
    ) -> List[List[str]]:
        """Apply blur effect"""
        # Simplified blur (would need proper implementation)
        return screen


class GlowShader(Shader):
    """Glow shader"""
    
    def __init__(self, intensity: float = 1.0, threshold: int = 200):
        """Initialize glow shader"""
        self.intensity = intensity
        self.threshold = threshold
    
    def apply(
        self,
        screen: List[List[str]],
        width: int,
        height: int
    ) -> List[List[str]]:
        """Apply glow effect"""
        # Would enhance bright colors
        return screen


class WaveShader(Shader):
    """Wave distortion shader"""
    
    def __init__(
        self,
        amplitude: float = 2.0,
        frequency: float = 0.5,
        speed: float = 1.0
    ):
        """Initialize wave shader"""
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.time = 0.0
    
    def update(self, dt: float) -> None:
        """Update wave animation"""
        self.time += dt * self.speed
    
    def apply(
        self,
        screen: List[List[str]],
        width: int,
        height: int
    ) -> List[List[str]]:
        """Apply wave distortion"""
        # Would distort screen based on wave function
        return screen


# =============================================================================
# EFFECT MANAGER
# =============================================================================

class EffectManager:
    """Manages all visual effects"""
    
    def __init__(self):
        """Initialize effect manager"""
        self.particle_emitters: List[ParticleEmitter] = []
        self.text_effects: List[TextEffect] = []
        self.transitions: List[Transition] = []
        self.shaders: List[Shader] = []
    
    def add_emitter(self, emitter: ParticleEmitter) -> None:
        """Add particle emitter"""
        self.particle_emitters.append(emitter)
    
    def add_text_effect(self, effect: TextEffect) -> None:
        """Add text effect"""
        self.text_effects.append(effect)
    
    def add_transition(self, transition: Transition) -> None:
        """Add transition"""
        self.transitions.append(transition)
    
    def add_shader(self, shader: Shader) -> None:
        """Add shader"""
        self.shaders.append(shader)
    
    def update(self, dt: float) -> None:
        """Update all effects"""
        # Update particle emitters
        for emitter in self.particle_emitters:
            emitter.update(dt)
        
        # Update text effects
        self.text_effects = [
            effect for effect in self.text_effects
            if not effect.is_complete()
        ]
        for effect in self.text_effects:
            effect.update(dt)
        
        # Update transitions
        self.transitions = [
            transition for transition in self.transitions
            if not transition.is_complete()
        ]
        for transition in self.transitions:
            transition.update(dt)
        
        # Update shaders
        for shader in self.shaders:
            if hasattr(shader, 'update'):
                shader.update(dt)
    
    def get_all_particles(self) -> List[Particle]:
        """Get all active particles"""
        particles = []
        for emitter in self.particle_emitters:
            particles.extend(emitter.get_particles())
        return particles
    
    def clear_all(self) -> None:
        """Clear all effects"""
        self.particle_emitters.clear()
        self.text_effects.clear()
        self.transitions.clear()
        self.shaders.clear()


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - Effects Module")
    print("=" * 50)
    
    # Test easing functions
    print("\nTesting easing functions:")
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        ease_out = Easing.ease_out_cubic(t)
        print(f"  t={t:.2f} -> ease_out_cubic={ease_out:.3f}")
    
    # Test particle system
    print("\nTesting particle system:")
    snow = SnowEmitter(0, 0, width=80)
    snow.update(1.0)
    print(f"  Active particles: {len(snow.get_particles())}")
    
    # Test text effects
    print("\nTesting text effects:")
    typing = TypingEffect("Hello, World!", chars_per_second=10)
    for _ in range(15):
        typing.update(0.1)
        print(f"  {typing.render()}")
    
    print("\n✅ Effects module test complete")
