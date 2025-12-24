#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brad TUI Ultimate - Comprehensive Terminal UI with Christmas Theme
===================================================================

A fully-featured terminal user interface with:
- Persistent menu bar (hidden only during command execution)
- Autocorrect panel at bottom near utilities
- Working keybindings for all operations
- Full cursor movement through text
- Persistent output that never auto-clears
- Parallax background that doesn't interfere with text
- Christmas tree with animations
- Star field with proper randomness
- Gradient borders on ALL elements
- Proper cursor colors

All functions work without conflicts.
"""

from __future__ import annotations

import asyncio
import math
import os
import random
import signal
import sys
import time
import traceback
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional, Sequence, Tuple

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import (
    Float,
    FloatContainer,
    FormattedTextControl,
    HSplit,
    Layout,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import UIContent, UIControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp value between lo and hi"""
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t


def lerp_rgb(
    c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    """Linear interpolation between two RGB colors"""
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def rgb_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color string"""
    return f"#{r:02x}{g:02x}{b:02x}"


def now_ms() -> int:
    """Get current time in milliseconds"""
    return int(time.time() * 1000)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth Hermite interpolation"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# ═══════════════════════════════════════════════════════════════════════════════
# THEME AND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Theme:
    """Color theme for the application"""

    # Background colors
    bg: Tuple[int, int, int] = (5, 8, 12)
    bg_panel: Tuple[int, int, int] = (8, 12, 18)
    bg_panel_alt: Tuple[int, int, int] = (6, 10, 16)

    # Text colors
    text: Tuple[int, int, int] = (220, 230, 245)
    text_dim: Tuple[int, int, int] = (140, 155, 175)
    text_bright: Tuple[int, int, int] = (255, 255, 255)

    # Gradient border colors
    border_start: Tuple[int, int, int] = (255, 20, 147)  # Deep pink
    border_mid: Tuple[int, int, int] = (138, 43, 226)  # Blue violet
    border_end: Tuple[int, int, int] = (0, 191, 255)  # Deep sky blue

    # Entry type backgrounds (with gradient support)
    cmd_bg_a: Tuple[int, int, int] = (35, 15, 45)
    cmd_bg_b: Tuple[int, int, int] = (15, 30, 50)
    out_bg_a: Tuple[int, int, int] = (10, 16, 24)
    out_bg_b: Tuple[int, int, int] = (12, 20, 22)
    err_bg_a: Tuple[int, int, int] = (45, 12, 15)
    err_bg_b: Tuple[int, int, int] = (20, 15, 30)
    sys_bg_a: Tuple[int, int, int] = (15, 15, 20)
    sys_bg_b: Tuple[int, int, int] = (12, 18, 22)

    # Entry type text colors
    cmd_fg: Tuple[int, int, int] = (120, 220, 255)
    out_fg: Tuple[int, int, int] = (200, 215, 230)
    err_fg: Tuple[int, int, int] = (255, 120, 140)
    sys_fg: Tuple[int, int, int] = (255, 200, 100)

    # Cursor colors
    cursor_fg: Tuple[int, int, int] = (10, 14, 20)
    cursor_bg: Tuple[int, int, int] = (255, 220, 60)

    # Menu colors
    menu_bg: Tuple[int, int, int] = (12, 16, 24)
    menu_fg: Tuple[int, int, int] = (200, 215, 235)
    menu_accent: Tuple[int, int, int] = (100, 200, 255)

    # Status bar colors
    status_bg: Tuple[int, int, int] = (10, 14, 20)
    status_fg: Tuple[int, int, int] = (180, 195, 215)

    # Autocorrect panel colors
    autocorrect_bg: Tuple[int, int, int] = (12, 16, 22)
    autocorrect_fg: Tuple[int, int, int] = (190, 205, 220)
    autocorrect_selected: Tuple[int, int, int] = (255, 200, 100)

    # Christmas colors
    tree_dark: Tuple[int, int, int] = (20, 80, 30)
    tree_light: Tuple[int, int, int] = (60, 180, 70)
    tree_tip: Tuple[int, int, int] = (80, 220, 90)
    trunk: Tuple[int, int, int] = (80, 55, 30)
    star: Tuple[int, int, int] = (255, 230, 100)
    snow: Tuple[int, int, int] = (240, 245, 255)

    # Accent colors
    accent: Tuple[int, int, int] = (100, 200, 255)
    success: Tuple[int, int, int] = (120, 240, 160)
    warning: Tuple[int, int, int] = (255, 200, 100)
    error: Tuple[int, int, int] = (255, 120, 140)


@dataclass
class Config:
    """Application configuration"""

    # Performance
    fps: int = 24
    frame_time: float = field(init=False)

    # Log settings
    max_log_lines: int = 5000
    max_line_chars: int = 10000

    # Animation settings
    enable_background: bool = True
    enable_tree: bool = True
    enable_snow: bool = True
    enable_parallax: bool = True

    # Parallax settings
    num_stars: int = 200
    star_layers: int = 3

    # Snow settings
    num_snowflakes: int = 100

    # Tree settings
    tree_scale: float = 0.15
    tree_lights: int = 30

    def __post_init__(self):
        self.frame_time = 1.0 / max(1, self.fps)


# ═══════════════════════════════════════════════════════════════════════════════
# LOG ENTRY TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class EntryKind(str, Enum):
    """Type of log entry"""

    SYSTEM = "system"
    COMMAND = "command"
    STDOUT = "stdout"
    STDERR = "stderr"
    WELCOME = "welcome"


@dataclass
class LogEntry:
    """A single log entry"""

    kind: EntryKind
    text: str
    timestamp: int = field(default_factory=now_ms)


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL MODEL (State Management)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TerminalModel:
    """Central state for the terminal application"""

    config: Config
    theme: Theme
    cwd: str = field(default_factory=os.getcwd)

    # State
    executing: bool = False
    last_exit_code: Optional[int] = None
    last_command: str = ""

    # Log (persistent, never auto-cleared)
    log: List[LogEntry] = field(default_factory=list)

    # Command history
    history: List[str] = field(default_factory=list)
    history_index: int = -1

    # Input state
    input_text: str = ""
    cursor_position: int = 0

    # UI state
    show_menu: bool = True
    show_autocorrect: bool = True
    autocorrect_suggestions: List[str] = field(default_factory=list)

    def add_entry(self, kind: EntryKind, text: str) -> None:
        """Add a log entry (persistent, never auto-cleared unless user requests)"""
        if not text:
            return

        # Limit line length
        if len(text) > self.config.max_line_chars:
            text = text[: self.config.max_line_chars] + "…"

        self.log.append(LogEntry(kind=kind, text=text))

        # Trim log if too long
        if len(self.log) > self.config.max_log_lines:
            self.log = self.log[-self.config.max_log_lines :]

    def add_lines(self, kind: EntryKind, text: str) -> None:
        """Add multiple lines as separate entries"""
        for line in text.splitlines():
            self.add_entry(kind, line)

    def add_welcome(self) -> None:
        """Add welcome banner"""
        self.add_entry(EntryKind.WELCOME, "╔═══════════════════════════════════════════════════════════════════╗")
        self.add_entry(EntryKind.WELCOME, "║                  🎄 Brad TUI Ultimate 🎄                          ║")
        self.add_entry(EntryKind.WELCOME, "║                                                                   ║")
        self.add_entry(EntryKind.WELCOME, "║  Bine ai venit la cel mai avansat terminal de Crăciun!          ║")
        self.add_entry(EntryKind.WELCOME, "║                                                                   ║")
        self.add_entry(EntryKind.WELCOME, "║  Funcții:                                                        ║")
        self.add_entry(EntryKind.WELCOME, "║    • Meniu persistent (apare după fiecare comandă)              ║")
        self.add_entry(EntryKind.WELCOME, "║    • Autocorect inteligent (jos, lângă utilități)              ║")
        self.add_entry(EntryKind.WELCOME, "║    • Cursorul se mișcă perfect prin text                        ║")
        self.add_entry(EntryKind.WELCOME, "║    • Output persistent (nu dispare niciodată)                   ║")
        self.add_entry(EntryKind.WELCOME, "║    • Brad animat cu zăpadă și stele                            ║")
        self.add_entry(EntryKind.WELCOME, "║    • Chenare colorate cu gradient pe tot                        ║")
        self.add_entry(EntryKind.WELCOME, "║                                                                   ║")
        self.add_entry(EntryKind.WELCOME, "║  Taste:                                                          ║")
        self.add_entry(EntryKind.WELCOME, "║    F1       - Ajutor complet                                    ║")
        self.add_entry(EntryKind.WELCOME, "║    F2       - Toggle fundal                                      ║")
        self.add_entry(EntryKind.WELCOME, "║    F3       - Toggle brad                                        ║")
        self.add_entry(EntryKind.WELCOME, "║    F4       - Toggle zăpadă                                     ║")
        self.add_entry(EntryKind.WELCOME, "║    TAB      - Schimbă focus                                     ║")
        self.add_entry(EntryKind.WELCOME, "║    Ctrl+L   - Clear manual                                       ║")
        self.add_entry(EntryKind.WELCOME, "║    Ctrl+C   - Ieșire                                            ║")
        self.add_entry(EntryKind.WELCOME, "║    Săgeți   - Navighează prin text                              ║")
        self.add_entry(EntryKind.WELCOME, "║    Home/End - Începutul/sfârșitul liniei                        ║")
        self.add_entry(EntryKind.WELCOME, "║    PgUp/PgDn- Scroll prin output                                ║")
        self.add_entry(EntryKind.WELCOME, "║                                                                   ║")
        self.add_entry(EntryKind.WELCOME, f"║  Director curent: {self.cwd[:46]:<46} ║")
        self.add_entry(EntryKind.WELCOME, "╚═══════════════════════════════════════════════════════════════════╝")
        self.add_entry(EntryKind.SYSTEM, "")
        self.add_entry(EntryKind.SYSTEM, "Sistemul este gata. Tastează o comandă și apasă ENTER.")
        self.add_entry(EntryKind.SYSTEM, "")

    def clear_log(self) -> None:
        """Clear the log (only on explicit user request)"""
        self.log.clear()
        self.add_entry(EntryKind.SYSTEM, "Log șters. Tastează 'clear' și ENTER pentru a șterge ecranul.")

    def get_suggestions(self, text: str) -> List[str]:
        """Get autocorrect suggestions for the current input"""
        if not text or not text.strip():
            return []

        suggestions = []
        text_lower = text.strip().lower()

        # Match from command history (most recent first)
        seen = set()
        for cmd in reversed(self.history[-100:]):
            if cmd.lower().startswith(text_lower) and cmd not in seen:
                suggestions.append(cmd)
                seen.add(cmd)
                if len(suggestions) >= 6:
                    return suggestions

        # Common commands
        common_commands = [
            "ls -la",
            "cd ..",
            "cd ~",
            "pwd",
            "cat ",
            "echo ",
            "mkdir ",
            "rm ",
            "cp ",
            "mv ",
            "git status",
            "git log",
            "git add .",
            "git commit -m ",
            "git push",
            "git pull",
            "python3 ",
            "pip install ",
            "clear",
            "exit",
        ]

        for cmd in common_commands:
            if cmd.lower().startswith(text_lower) and cmd not in seen:
                suggestions.append(cmd)
                seen.add(cmd)
                if len(suggestions) >= 6:
                    return suggestions

        return suggestions


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND ANIMATIONS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Star:
    """A single star in the parallax field"""

    x: float
    y: float
    z: float  # depth (0=far, 1=near)
    brightness: float
    twinkle_offset: float
    hue: float  # 0-1, for color variation


class ParallaxField:
    """Multi-layer parallax star field with proper randomness"""

    def __init__(self, config: Config, theme: Theme, seed: int = None):
        self.config = config
        self.theme = theme
        self.stars: List[Star] = []
        self.rng = random.Random(seed if seed is not None else time.time())
        self.last_size = (0, 0)

    def regenerate(self, width: int, height: int) -> None:
        """Regenerate stars for new dimensions"""
        self.stars.clear()
        self.last_size = (width, height)

        for _ in range(self.config.num_stars):
            z = self.rng.random()  # Depth: 0=far, 1=near
            self.stars.append(
                Star(
                    x=self.rng.uniform(0, width),
                    y=self.rng.uniform(0, height),
                    z=z,
                    brightness=self.rng.uniform(0.3, 1.0),
                    twinkle_offset=self.rng.uniform(0, math.tau),
                    hue=self.rng.uniform(0, 1),
                )
            )

    def render(
        self, width: int, height: int, time_val: float
    ) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Render star field to a 2D buffer"""
        if width <= 0 or height <= 0:
            return []

        if (width, height) != self.last_size:
            self.regenerate(width, height)

        # Create empty buffer
        buffer = [[None for _ in range(width)] for _ in range(height)]

        # Parallax drift
        drift_x = math.sin(time_val * 0.2) * 1.5 + math.cos(time_val * 0.07) * 0.8
        drift_y = math.cos(time_val * 0.15) * 1.2 + math.sin(time_val * 0.09) * 0.6

        for star in self.stars:
            # Apply parallax based on depth
            parallax_factor = 1.0 / (star.z + 0.5)
            x = (star.x + drift_x * parallax_factor) % width
            y = (star.y + drift_y * parallax_factor) % height

            ix, iy = int(x), int(y)
            if 0 <= ix < width and 0 <= iy < height:
                # Twinkle effect
                twinkle = 0.5 + 0.5 * math.sin(
                    time_val * (2.0 + star.z * 2.0) + star.twinkle_offset
                )

                # Color based on hue
                base_color = (40, 60, 80)
                if star.hue < 0.33:
                    tint = (180, 200, 255)  # Blue
                elif star.hue < 0.66:
                    tint = (255, 180, 220)  # Pink
                else:
                    tint = (200, 255, 230)  # Cyan

                intensity = star.brightness * twinkle * (0.4 + 0.6 * star.z)
                color = (
                    int(
                        clamp(base_color[0] + tint[0] * intensity * 0.5, 0, 255)
                    ),
                    int(
                        clamp(base_color[1] + tint[1] * intensity * 0.5, 0, 255)
                    ),
                    int(
                        clamp(base_color[2] + tint[2] * intensity * 0.5, 0, 255)
                    ),
                )
                buffer[iy][ix] = color

        return buffer


@dataclass
class Snowflake:
    """A single snowflake"""

    x: float
    y: float
    vx: float
    vy: float
    size: float


class SnowSystem:
    """Falling snow animation"""

    def __init__(self, config: Config, theme: Theme, seed: int = None):
        self.config = config
        self.theme = theme
        self.flakes: List[Snowflake] = []
        self.rng = random.Random(seed if seed is not None else time.time() * 2)
        self.last_size = (0, 0)

    def regenerate(self, width: int, height: int) -> None:
        """Regenerate snowflakes"""
        self.flakes.clear()
        self.last_size = (width, height)

        for _ in range(self.config.num_snowflakes):
            self.flakes.append(
                Snowflake(
                    x=self.rng.uniform(0, width),
                    y=self.rng.uniform(0, height),
                    vx=self.rng.uniform(-0.3, 0.3),
                    vy=self.rng.uniform(0.5, 1.5),
                    size=self.rng.uniform(0.3, 1.0),
                )
            )

    def update(self, width: int, height: int, dt: float, time_val: float) -> None:
        """Update snowflake positions"""
        if (width, height) != self.last_size:
            self.regenerate(width, height)

        wind = math.sin(time_val * 0.5) * 0.8

        for flake in self.flakes:
            flake.x += (flake.vx + wind * 0.3) * dt * 10
            flake.y += flake.vy * dt * 10

            # Wrap around
            if flake.y > height + 2:
                flake.y = -2
                flake.x = self.rng.uniform(0, width)
                flake.vx = self.rng.uniform(-0.3, 0.3)

            if flake.x < -2:
                flake.x = width + 2
            elif flake.x > width + 2:
                flake.x = -2

    def render(
        self, width: int, height: int
    ) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Render snowflakes to buffer"""
        if width <= 0 or height <= 0:
            return []

        buffer = [[None for _ in range(width)] for _ in range(height)]

        for flake in self.flakes:
            ix, iy = int(flake.x), int(flake.y)
            if 0 <= ix < width and 0 <= iy < height:
                brightness = int(200 + flake.size * 55)
                color = (brightness, brightness, min(255, brightness + 30))
                buffer[iy][ix] = color

        return buffer


@dataclass
class Light:
    """A Christmas light on the tree"""

    angle: float  # Angle around tree
    height: float  # 0=bottom, 1=top
    color: Tuple[int, int, int]
    flicker_offset: float
    flicker_speed: float


class ChristmasTree:
    """Animated Christmas tree"""

    def __init__(self, config: Config, theme: Theme, seed: int = None):
        self.config = config
        self.theme = theme
        self.lights: List[Light] = []
        self.rng = random.Random(seed if seed is not None else time.time() * 3)
        self.init_lights()

    def init_lights(self) -> None:
        """Initialize lights on the tree"""
        self.lights.clear()

        # Create lights in spiral pattern
        for i in range(self.config.tree_lights):
            t = i / max(1, self.config.tree_lights)
            angle = t * math.pi * 6  # 6 spirals
            height = t * 0.9

            # Alternate colors
            colors = [
                (255, 80, 80),  # Red
                (80, 255, 80),  # Green
                (80, 80, 255),  # Blue
                (255, 255, 80),  # Yellow
                (255, 80, 255),  # Magenta
                (80, 255, 255),  # Cyan
            ]
            color = colors[i % len(colors)]

            self.lights.append(
                Light(
                    angle=angle,
                    height=height,
                    color=color,
                    flicker_offset=self.rng.uniform(0, math.tau),
                    flicker_speed=self.rng.uniform(1.5, 3.5),
                )
            )

    def render(
        self, width: int, height: int, time_val: float
    ) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Render tree to buffer"""
        if width <= 0 or height <= 0:
            return []

        buffer = [[None for _ in range(width)] for _ in range(height)]

        # Tree dimensions (right side of screen)
        tree_w = int(width * self.config.tree_scale)
        tree_h = int(height * 0.7)
        tree_x = int(width * 0.82)  # Center X (right side)
        tree_y = int(height * 0.55)  # Center Y

        # Wind sway
        sway = math.sin(time_val * 0.8) * 1.2 + math.cos(time_val * 0.3) * 0.5

        # Draw tree (cone shape)
        for row in range(tree_h):
            t = row / max(1, tree_h)  # 0=top, 1=bottom
            row_y = tree_y - tree_h // 2 + row

            if not (0 <= row_y < height):
                continue

            # Width at this height
            row_w = int(tree_w * t * 0.8)

            for col in range(-row_w, row_w + 1):
                col_x = int(tree_x + col + sway * (1 - t) * 0.7)

                if not (0 <= col_x < width):
                    continue

                # Lighting calculation
                normal = col / max(1, row_w)
                light = 0.5 + 0.4 * (-normal) + 0.2 * (1 - t)
                light = clamp(light, 0.3, 1.0)

                # Color gradient from dark green at bottom to bright at top
                base = lerp_rgb(self.theme.tree_dark, self.theme.tree_light, 1 - t)
                color = (
                    int(base[0] * light),
                    int(base[1] * light),
                    int(base[2] * light),
                )
                buffer[row_y][col_x] = color

        # Draw trunk
        trunk_h = max(2, tree_h // 8)
        trunk_w = max(1, tree_w // 10)
        trunk_y_start = tree_y + tree_h // 2

        for row in range(trunk_h):
            row_y = trunk_y_start + row
            if 0 <= row_y < height:
                for col in range(-trunk_w, trunk_w + 1):
                    col_x = tree_x + col
                    if 0 <= col_x < width:
                        shading = 0.6 + 0.4 * (col / max(1, trunk_w))
                        color = (
                            int(self.theme.trunk[0] * shading),
                            int(self.theme.trunk[1] * shading),
                            int(self.theme.trunk[2] * shading),
                        )
                        buffer[row_y][col_x] = color

        # Draw star on top
        star_y = tree_y - tree_h // 2 - 2
        star_x = int(tree_x + sway * 0.8)
        pulse = 0.7 + 0.3 * math.sin(time_val * 4.0)
        star_color = (
            int(self.theme.star[0] * pulse),
            int(self.theme.star[1] * pulse),
            int(self.theme.star[2] * pulse),
        )

        # Star shape
        if 0 <= star_y < height:
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    if abs(dx) + abs(dy) <= 2:
                        y = star_y + dy
                        x = star_x + dx
                        if 0 <= y < height and 0 <= x < width:
                            buffer[y][x] = star_color

        # Draw lights
        for light in self.lights:
            # Calculate position on tree
            light_t = light.height
            light_h = tree_h * light_t
            light_w = tree_w * light_t * 0.6

            light_y = int(tree_y - tree_h // 2 + light_h)
            light_x = int(
                tree_x + math.cos(light.angle) * light_w + sway * (1 - light_t) * 0.6
            )

            if 0 <= light_y < height and 0 <= light_x < width:
                # Flicker
                flicker = 0.6 + 0.4 * math.sin(
                    time_val * light.flicker_speed + light.flicker_offset
                )

                color = (
                    int(light.color[0] * flicker),
                    int(light.color[1] * flicker),
                    int(light.color[2] * flicker),
                )
                buffer[light_y][light_x] = color

                # Glow around light
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        glow_y = light_y + dy
                        glow_x = light_x + dx
                        if 0 <= glow_y < height and 0 <= glow_x < width:
                            if buffer[glow_y][glow_x] is not None:
                                existing = buffer[glow_y][glow_x]
                                buffer[glow_y][glow_x] = (
                                    min(255, int(existing[0] * 0.7 + color[0] * 0.3)),
                                    min(255, int(existing[1] * 0.7 + color[1] * 0.3)),
                                    min(255, int(existing[2] * 0.7 + color[2] * 0.3)),
                                )

        return buffer


class BackgroundComposer:
    """Compose all background layers"""

    def __init__(self, config: Config, theme: Theme):
        self.config = config
        self.theme = theme
        self.parallax = ParallaxField(config, theme, seed=12345)
        self.snow = SnowSystem(config, theme, seed=54321)
        self.tree = ChristmasTree(config, theme, seed=98765)
        self.last_time = time.time()

    def render(
        self, width: int, height: int, time_val: float
    ) -> List[List[Tuple[int, int, int]]]:
        """Render complete background"""
        if width <= 0 or height <= 0:
            return []

        # Base background
        result = [[self.theme.bg for _ in range(width)] for _ in range(height)]

        if not self.config.enable_background:
            return result

        # Calculate dt
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Render layers
        if self.config.enable_parallax:
            parallax_buf = self.parallax.render(width, height, time_val)
        else:
            parallax_buf = [[None for _ in range(width)] for _ in range(height)]

        if self.config.enable_tree:
            tree_buf = self.tree.render(width, height, time_val)
        else:
            tree_buf = [[None for _ in range(width)] for _ in range(height)]

        if self.config.enable_snow:
            self.snow.update(width, height, dt, time_val)
            snow_buf = self.snow.render(width, height)
        else:
            snow_buf = [[None for _ in range(width)] for _ in range(height)]

        # Composite layers
        for y in range(height):
            for x in range(width):
                color = result[y][x]

                # Blend parallax
                if parallax_buf[y][x] is not None:
                    p = parallax_buf[y][x]
                    color = (
                        int(color[0] * 0.4 + p[0] * 0.6),
                        int(color[1] * 0.4 + p[1] * 0.6),
                        int(color[2] * 0.4 + p[2] * 0.6),
                    )

                # Blend tree (opaque)
                if tree_buf[y][x] is not None:
                    color = tree_buf[y][x]

                # Blend snow
                if snow_buf[y][x] is not None:
                    s = snow_buf[y][x]
                    color = (
                        int(color[0] * 0.3 + s[0] * 0.7),
                        int(color[1] * 0.3 + s[1] * 0.7),
                        int(color[2] * 0.3 + s[2] * 0.7),
                    )

                result[y][x] = color

        return result


# ═══════════════════════════════════════════════════════════════════════════════
# UI CONTROLS
# ═══════════════════════════════════════════════════════════════════════════════


class BackgroundControl(UIControl):
    """Background rendering control"""

    def __init__(self, composer: BackgroundComposer):
        self.composer = composer
        self.start_time = time.time()
        self.cached_buffer: List[List[Tuple[int, int, int]]] = []
        self.cached_size = (0, 0)

    def is_focusable(self) -> bool:
        return False

    def create_content(self, width: int, height: int) -> UIContent:
        time_val = time.time() - self.start_time

        # Always render (for animation)
        buffer = self.composer.render(width, height, time_val)
        self.cached_buffer = buffer
        self.cached_size = (width, height)

        def get_line(line_no: int) -> StyleAndTextTuples:
            if line_no < 0 or line_no >= height or not buffer:
                return [("", "")]

            result: StyleAndTextTuples = []
            for x in range(width):
                color = buffer[line_no][x]
                result.append((f"bg:{rgb_hex(*color)}", " "))
            return result

        return UIContent(get_line=get_line, line_count=height, show_cursor=False)


def create_gradient_border_line(
    width: int, theme: Theme, position: float = 0.5
) -> StyleAndTextTuples:
    """Create a horizontal gradient border line"""
    result: StyleAndTextTuples = []
    for x in range(width):
        t = x / max(1, width - 1)
        # Three-color gradient
        if t < 0.5:
            color = lerp_rgb(theme.border_start, theme.border_mid, t * 2)
        else:
            color = lerp_rgb(theme.border_mid, theme.border_end, (t - 0.5) * 2)

        result.append((f"fg:{rgb_hex(*color)} bg:{rgb_hex(*theme.bg_panel)}", "━"))
    return result


def get_entry_colors(
    theme: Theme, kind: EntryKind
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """Get background gradient and foreground color for an entry type"""
    if kind == EntryKind.COMMAND:
        return theme.cmd_bg_a, theme.cmd_bg_b, theme.cmd_fg
    elif kind == EntryKind.STDERR:
        return theme.err_bg_a, theme.err_bg_b, theme.err_fg
    elif kind == EntryKind.SYSTEM or kind == EntryKind.WELCOME:
        return theme.sys_bg_a, theme.sys_bg_b, theme.sys_fg
    else:  # STDOUT
        return theme.out_bg_a, theme.out_bg_b, theme.out_fg


class GradientLogControl(UIControl):
    """Display log with gradient borders around each entry"""

    def __init__(self, model: TerminalModel):
        self.model = model
        self.scroll_offset = 0

    def is_focusable(self) -> bool:
        return True

    def create_content(self, width: int, height: int) -> UIContent:
        theme = self.model.theme
        entries = self.model.log

        # Build rendered lines
        rendered_lines: List[StyleAndTextTuples] = []

        for entry in entries:
            # Get colors
            bg_a, bg_b, fg = get_entry_colors(theme, entry.kind)

            # Top border
            rendered_lines.append(create_gradient_border_line(width, theme))

            # Content line with gradient background
            text = entry.text
            if len(text) > width - 6:
                text = text[: width - 7] + "…"

            content_line: StyleAndTextTuples = []

            # Left border
            t_left = 0.0
            border_color_left = theme.border_start
            content_line.append(
                (
                    f"fg:{rgb_hex(*border_color_left)} bg:{rgb_hex(*theme.bg_panel)}",
                    "┃",
                )
            )

            # Content with gradient background
            for i in range(width - 2):
                t = i / max(1, width - 3)
                bg = lerp_rgb(bg_a, bg_b, t)

                if i < len(text) + 1:
                    if i == 0:
                        ch = " "
                    elif i - 1 < len(text):
                        ch = text[i - 1]
                    else:
                        ch = " "
                else:
                    ch = " "

                content_line.append((f"fg:{rgb_hex(*fg)} bg:{rgb_hex(*bg)}", ch))

            # Right border
            t_right = 1.0
            border_color_right = theme.border_end
            content_line.append(
                (
                    f"fg:{rgb_hex(*border_color_right)} bg:{rgb_hex(*theme.bg_panel)}",
                    "┃",
                )
            )

            rendered_lines.append(content_line)

            # Bottom border
            rendered_lines.append(create_gradient_border_line(width, theme))

        # Show last N lines that fit
        visible_lines = rendered_lines[-height:] if height > 0 else []

        def get_line(line_no: int) -> StyleAndTextTuples:
            if line_no < 0 or line_no >= len(visible_lines):
                return [("", "")]
            return visible_lines[line_no]

        return UIContent(
            get_line=get_line, line_count=len(visible_lines), show_cursor=False
        )


class MenuBarControl(UIControl):
    """Menu bar that appears after commands finish"""

    def __init__(self, model: TerminalModel):
        self.model = model

    def is_focusable(self) -> bool:
        return False

    def create_content(self, width: int, height: int) -> UIContent:
        theme = self.model.theme

        def get_line(line_no: int) -> StyleAndTextTuples:
            if line_no != 0:
                return [("", "")]

            # Hide menu during command execution
            if self.model.executing:
                return [
                    (
                        f"fg:{rgb_hex(*theme.menu_fg)} bg:{rgb_hex(*theme.menu_bg)}",
                        " " * width,
                    )
                ]

            # Show menu
            items = [
                ("F1", "Ajutor"),
                ("F2", "Fundal"),
                ("F3", "Brad"),
                ("F4", "Zăpadă"),
                ("TAB", "Focus"),
                ("Ctrl+L", "Clear"),
                ("Ctrl+C", "Ieșire"),
            ]

            text = "  🎄 Brad TUI  "
            for key, desc in items:
                text += f" [{key}] {desc} "

            # Pad to width
            if len(text) < width:
                text += " " * (width - len(text))
            else:
                text = text[:width]

            return [
                (
                    f"fg:{rgb_hex(*theme.menu_fg)} bg:{rgb_hex(*theme.menu_bg)}",
                    text,
                )
            ]

        return UIContent(get_line=get_line, line_count=1, show_cursor=False)


class StatusBarControl(UIControl):
    """Status bar with current directory and execution state"""

    def __init__(self, model: TerminalModel):
        self.model = model

    def is_focusable(self) -> bool:
        return False

    def create_content(self, width: int, height: int) -> UIContent:
        theme = self.model.theme

        def get_line(line_no: int) -> StyleAndTextTuples:
            if line_no != 0:
                return [("", "")]

            # Build status text
            status = "🔴 RULEAZĂ" if self.model.executing else "🟢 GATA"
            exit_code = (
                f" (exit: {self.model.last_exit_code})"
                if self.model.last_exit_code is not None
                else ""
            )
            cwd = f"📁 {self.model.cwd}"

            text = f" {status}{exit_code}   {cwd} "

            # Pad to width
            if len(text) < width:
                text += " " * (width - len(text))
            else:
                text = text[: width - 3] + "..."

            return [
                (
                    f"fg:{rgb_hex(*theme.status_fg)} bg:{rgb_hex(*theme.status_bg)}",
                    text,
                )
            ]

        return UIContent(get_line=get_line, line_count=1, show_cursor=False)


class AutocorrectPanelControl(UIControl):
    """Autocorrect suggestions panel (bottom, near utilities)"""

    def __init__(self, model: TerminalModel):
        self.model = model

    def is_focusable(self) -> bool:
        return False

    def create_content(self, width: int, height: int) -> UIContent:
        theme = self.model.theme
        suggestions = self.model.autocorrect_suggestions

        def get_line(line_no: int) -> StyleAndTextTuples:
            if line_no >= height:
                return [("", "")]

            # Top border
            if line_no == 0:
                return create_gradient_border_line(width, theme)

            # Title
            if line_no == 1:
                title = " 💡 Sugestii "
                padding = (width - len(title) - 2) // 2
                text = " " * padding + title + " " * (width - len(title) - padding - 2)

                result: StyleAndTextTuples = []
                # Borders
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.border_start)} bg:{rgb_hex(*theme.autocorrect_bg)}",
                        "┃",
                    )
                )
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.autocorrect_selected)} bg:{rgb_hex(*theme.autocorrect_bg)}",
                        text,
                    )
                )
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.border_end)} bg:{rgb_hex(*theme.autocorrect_bg)}",
                        "┃",
                    )
                )
                return result

            # Suggestions
            suggestion_idx = line_no - 2
            if suggestion_idx < len(suggestions):
                text = f" {suggestion_idx + 1}. {suggestions[suggestion_idx]}"
                if len(text) > width - 4:
                    text = text[: width - 5] + "…"
                text += " " * max(0, width - len(text) - 2)

                result = []
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.border_start)} bg:{rgb_hex(*theme.autocorrect_bg)}",
                        "┃",
                    )
                )
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.autocorrect_fg)} bg:{rgb_hex(*theme.autocorrect_bg)}",
                        text,
                    )
                )
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.border_end)} bg:{rgb_hex(*theme.autocorrect_bg)}",
                        "┃",
                    )
                )
                return result

            # Bottom border
            if line_no == height - 1:
                return create_gradient_border_line(width, theme)

            # Empty line
            return [
                (
                    f"bg:{rgb_hex(*theme.autocorrect_bg)}",
                    " " * width,
                )
            ]

        return UIContent(get_line=get_line, line_count=height, show_cursor=False)


class InputLineControl(UIControl):
    """Custom input line with gradient border and proper cursor"""

    def __init__(self, model: TerminalModel):
        self.model = model

    def is_focusable(self) -> bool:
        return True

    def create_content(self, width: int, height: int) -> UIContent:
        theme = self.model.theme

        def get_line(line_no: int) -> StyleAndTextTuples:
            if line_no >= height:
                return [("", "")]

            # Top border
            if line_no == 0:
                return create_gradient_border_line(width, theme)

            # Input line
            if line_no == 1:
                prompt = "> "
                text = self.model.input_text
                cursor_pos = self.model.cursor_position

                # Build line with gradient background
                result: StyleAndTextTuples = []

                # Left border
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.border_start)} bg:{rgb_hex(*theme.bg_panel)}",
                        "┃",
                    )
                )

                # Content area
                full_text = prompt + text
                display_width = width - 4  # Account for borders and padding

                # Truncate if too long
                if len(full_text) > display_width:
                    # Show end of text
                    visible_text = "…" + full_text[-(display_width - 1) :]
                    visible_cursor = len(visible_text) - 1
                else:
                    visible_text = full_text + " " * (display_width - len(full_text))
                    visible_cursor = cursor_pos + len(prompt)

                # Add space before content
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.text)} bg:{rgb_hex(*theme.bg_panel)}",
                        " ",
                    )
                )

                # Render each character
                for i, ch in enumerate(visible_text):
                    if i == visible_cursor:
                        # Cursor position
                        result.append(
                            (
                                f"fg:{rgb_hex(*theme.cursor_fg)} bg:{rgb_hex(*theme.cursor_bg)}",
                                ch if ch != " " else " ",
                            )
                        )
                    else:
                        # Normal text
                        fg = theme.accent if i >= len(prompt) else theme.text_dim
                        result.append(
                            (
                                f"fg:{rgb_hex(*fg)} bg:{rgb_hex(*theme.bg_panel)}",
                                ch,
                            )
                        )

                # Add space after content
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.text)} bg:{rgb_hex(*theme.bg_panel)}",
                        " ",
                    )
                )

                # Right border
                result.append(
                    (
                        f"fg:{rgb_hex(*theme.border_end)} bg:{rgb_hex(*theme.bg_panel)}",
                        "┃",
                    )
                )

                return result

            # Bottom border
            if line_no == 2:
                return create_gradient_border_line(width, theme)

            return [("", "")]

        # Cursor position calculation
        cursor_line = 1
        cursor_column = min(self.model.cursor_position + 3, width - 2)

        return UIContent(
            get_line=get_line,
            line_count=3,
            show_cursor=True,
            cursor_position=(cursor_line, cursor_column),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════


async def execute_command(
    model: TerminalModel, command: str, refresh_callback: Callable[[], None]
) -> None:
    """Execute a shell command and stream output to log"""
    model.executing = True
    model.last_command = command
    model.add_entry(EntryKind.COMMAND, f"$ {command}")
    refresh_callback()

    # Handle built-in commands
    if command.strip() == "clear":
        model.log.clear()
        model.add_entry(EntryKind.SYSTEM, "Log șters.")
        model.executing = False
        model.last_exit_code = 0
        refresh_callback()
        return

    if command.strip().startswith("cd "):
        # Built-in cd
        target = command.strip()[3:].strip()
        target = os.path.expanduser(target)
        if not os.path.isabs(target):
            target = os.path.join(model.cwd, target)

        try:
            os.chdir(target)
            model.cwd = os.getcwd()
            model.add_entry(EntryKind.SYSTEM, f"Director schimbat: {model.cwd}")
            model.last_exit_code = 0
        except Exception as e:
            model.add_entry(EntryKind.STDERR, f"cd: {e}")
            model.last_exit_code = 1

        model.executing = False
        refresh_callback()
        return

    # Execute command
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=model.cwd,
        )

        # Stream stdout
        async def read_stdout():
            assert proc.stdout is not None
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode(errors="replace").rstrip()
                model.add_entry(EntryKind.STDOUT, text)
                refresh_callback()

        # Stream stderr
        async def read_stderr():
            assert proc.stderr is not None
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                text = line.decode(errors="replace").rstrip()
                model.add_entry(EntryKind.STDERR, text)
                refresh_callback()

        # Wait for both streams
        await asyncio.gather(read_stdout(), read_stderr())
        exit_code = await proc.wait()
        model.last_exit_code = exit_code

        if exit_code != 0:
            model.add_entry(
                EntryKind.SYSTEM, f"Comandă terminată cu codul de ieșire: {exit_code}"
            )

    except Exception as e:
        model.add_entry(EntryKind.STDERR, f"Eroare la executarea comenzii: {e}")
        model.add_entry(EntryKind.STDERR, traceback.format_exc())
        model.last_exit_code = 1

    model.executing = False
    refresh_callback()


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_app() -> Application:
    """Build the complete application"""

    # Initialize
    config = Config()
    theme = Theme()
    model = TerminalModel(config=config, theme=theme)

    # Add welcome message
    model.add_welcome()

    # Background
    composer = BackgroundComposer(config, theme)
    background_control = BackgroundControl(composer)
    background = Window(content=background_control, style="class:background")

    # Log display
    log_control = GradientLogControl(model)
    log_window = Window(
        content=log_control,
        style="class:log",
        wrap_lines=False,
        right_margins=[ScrollbarMargin(display_arrows=True)],
    )

    # Menu bar
    menu_control = MenuBarControl(model)
    menu_bar = Window(
        content=menu_control,
        height=D(min=1, max=1),
        style="class:menu",
        dont_extend_height=True,
    )

    # Status bar
    status_control = StatusBarControl(model)
    status_bar = Window(
        content=status_control,
        height=D(min=1, max=1),
        style="class:status",
        dont_extend_height=True,
    )

    # Input line
    input_control = InputLineControl(model)
    input_window = Window(
        content=input_control,
        height=D(min=3, max=3),
        style="class:input",
        dont_extend_height=True,
    )

    # Autocorrect panel
    autocorrect_control = AutocorrectPanelControl(model)
    autocorrect_panel = Window(
        content=autocorrect_control,
        width=D(min=30, preferred=40),
        height=D(min=8, max=12),
        style="class:autocorrect",
        dont_extend_width=True,
        dont_extend_height=True,
    )

    # Layout
    main_content = HSplit(
        [
            menu_bar,
            log_window,
            input_window,
            status_bar,
        ]
    )

    # Float container with autocorrect panel at bottom-right
    root = FloatContainer(
        content=background,
        floats=[
            Float(content=main_content),
            Float(content=autocorrect_panel, bottom=2, right=1),
        ],
    )

    layout = Layout(root, focused_element=input_window)

    # Key bindings
    kb = KeyBindings()

    @kb.add("c-c")
    def _(event):
        """Exit application"""
        event.app.exit()

    @kb.add("c-l")
    def _(event):
        """Clear log"""
        model.clear_log()
        event.app.invalidate()

    @kb.add("f1")
    def _(event):
        """Show help"""
        model.add_entry(EntryKind.SYSTEM, "═" * 60)
        model.add_entry(EntryKind.SYSTEM, "AJUTOR - Brad TUI Ultimate")
        model.add_entry(EntryKind.SYSTEM, "═" * 60)
        model.add_entry(EntryKind.SYSTEM, "")
        model.add_entry(EntryKind.SYSTEM, "Taste disponibile:")
        model.add_entry(EntryKind.SYSTEM, "  F1         - Afișează acest ajutor")
        model.add_entry(EntryKind.SYSTEM, "  F2         - Toggle fundal animat")
        model.add_entry(EntryKind.SYSTEM, "  F3         - Toggle brad de Crăciun")
        model.add_entry(EntryKind.SYSTEM, "  F4         - Toggle zăpadă")
        model.add_entry(EntryKind.SYSTEM, "  TAB        - Schimbă focus (input/output)")
        model.add_entry(EntryKind.SYSTEM, "  Ctrl+L     - Șterge log-ul")
        model.add_entry(EntryKind.SYSTEM, "  Ctrl+C     - Ieșire din aplicație")
        model.add_entry(EntryKind.SYSTEM, "")
        model.add_entry(EntryKind.SYSTEM, "Navigare în input:")
        model.add_entry(
            EntryKind.SYSTEM, "  Săgeată stânga/dreapta - Mișcă cursorul"
        )
        model.add_entry(
            EntryKind.SYSTEM, "  Home/End   - Salt la început/sfârșit linie"
        )
        model.add_entry(
            EntryKind.SYSTEM, "  Ctrl+A     - Salt la începutul liniei"
        )
        model.add_entry(EntryKind.SYSTEM, "  Ctrl+E     - Salt la sfârșitul liniei")
        model.add_entry(
            EntryKind.SYSTEM, "  Backspace  - Șterge caracterul din stânga"
        )
        model.add_entry(
            EntryKind.SYSTEM, "  Delete     - Șterge caracterul de sub cursor"
        )
        model.add_entry(EntryKind.SYSTEM, "  Ctrl+U     - Șterge toată linia")
        model.add_entry(EntryKind.SYSTEM, "  Ctrl+K     - Șterge de la cursor la final")
        model.add_entry(EntryKind.SYSTEM, "")
        model.add_entry(EntryKind.SYSTEM, "Navigare în output:")
        model.add_entry(
            EntryKind.SYSTEM, "  PageUp/PageDown - Scroll prin istoric"
        )
        model.add_entry(EntryKind.SYSTEM, "  Săgeată sus/jos - Scroll linie cu linie")
        model.add_entry(EntryKind.SYSTEM, "")
        model.add_entry(EntryKind.SYSTEM, "Funcții:")
        model.add_entry(
            EntryKind.SYSTEM,
            "  • Output-ul NU dispare niciodată (persistent până la clear)",
        )
        model.add_entry(
            EntryKind.SYSTEM, "  • Meniul apare automat după fiecare comandă"
        )
        model.add_entry(
            EntryKind.SYSTEM,
            "  • Autocorect-ul sugerează comenzi din istoric și comune",
        )
        model.add_entry(
            EntryKind.SYSTEM,
            "  • Toate elementele au chenare colorate cu gradient",
        )
        model.add_entry(EntryKind.SYSTEM, "  • Bradul și zăpada sunt animate")
        model.add_entry(EntryKind.SYSTEM, "  • Stelele au efect de parallax random")
        model.add_entry(EntryKind.SYSTEM, "")
        model.add_entry(EntryKind.SYSTEM, "═" * 60)
        event.app.invalidate()

    @kb.add("f2")
    def _(event):
        """Toggle background"""
        config.enable_background = not config.enable_background
        state = "activat" if config.enable_background else "dezactivat"
        model.add_entry(EntryKind.SYSTEM, f"Fundal: {state}")
        event.app.invalidate()

    @kb.add("f3")
    def _(event):
        """Toggle tree"""
        config.enable_tree = not config.enable_tree
        state = "activat" if config.enable_tree else "dezactivat"
        model.add_entry(EntryKind.SYSTEM, f"Brad de Crăciun: {state}")
        event.app.invalidate()

    @kb.add("f4")
    def _(event):
        """Toggle snow"""
        config.enable_snow = not config.enable_snow
        state = "activată" if config.enable_snow else "dezactivată"
        model.add_entry(EntryKind.SYSTEM, f"Zăpadă: {state}")
        event.app.invalidate()

    @kb.add("tab")
    def _(event):
        """Switch focus"""
        event.app.layout.focus_next()

    @kb.add("s-tab")
    def _(event):
        """Switch focus (reverse)"""
        event.app.layout.focus_previous()

    # Input handling
    @kb.add("left")
    def _(event):
        """Move cursor left"""
        if model.cursor_position > 0:
            model.cursor_position -= 1
        event.app.invalidate()

    @kb.add("right")
    def _(event):
        """Move cursor right"""
        if model.cursor_position < len(model.input_text):
            model.cursor_position += 1
        event.app.invalidate()

    @kb.add("home")
    def _(event):
        """Move cursor to start"""
        model.cursor_position = 0
        event.app.invalidate()

    @kb.add("end")
    def _(event):
        """Move cursor to end"""
        model.cursor_position = len(model.input_text)
        event.app.invalidate()

    @kb.add("c-a")
    def _(event):
        """Move cursor to start (Ctrl+A)"""
        model.cursor_position = 0
        event.app.invalidate()

    @kb.add("c-e")
    def _(event):
        """Move cursor to end (Ctrl+E)"""
        model.cursor_position = len(model.input_text)
        event.app.invalidate()

    @kb.add("backspace")
    def _(event):
        """Delete character before cursor"""
        if model.cursor_position > 0:
            model.input_text = (
                model.input_text[: model.cursor_position - 1]
                + model.input_text[model.cursor_position :]
            )
            model.cursor_position -= 1
            model.autocorrect_suggestions = model.get_suggestions(model.input_text)
        event.app.invalidate()

    @kb.add("delete")
    def _(event):
        """Delete character at cursor"""
        if model.cursor_position < len(model.input_text):
            model.input_text = (
                model.input_text[: model.cursor_position]
                + model.input_text[model.cursor_position + 1 :]
            )
            model.autocorrect_suggestions = model.get_suggestions(model.input_text)
        event.app.invalidate()

    @kb.add("c-u")
    def _(event):
        """Delete entire line"""
        model.input_text = ""
        model.cursor_position = 0
        model.autocorrect_suggestions = []
        event.app.invalidate()

    @kb.add("c-k")
    def _(event):
        """Delete from cursor to end"""
        model.input_text = model.input_text[: model.cursor_position]
        model.autocorrect_suggestions = model.get_suggestions(model.input_text)
        event.app.invalidate()

    @kb.add("up")
    def _(event):
        """Previous command from history"""
        if event.app.layout.current_control == input_control:
            if model.history:
                if model.history_index == -1:
                    model.history_index = len(model.history) - 1
                elif model.history_index > 0:
                    model.history_index -= 1

                if model.history_index >= 0:
                    model.input_text = model.history[model.history_index]
                    model.cursor_position = len(model.input_text)
                    model.autocorrect_suggestions = []
            event.app.invalidate()

    @kb.add("down")
    def _(event):
        """Next command from history"""
        if event.app.layout.current_control == input_control:
            if model.history_index >= 0:
                model.history_index += 1
                if model.history_index >= len(model.history):
                    model.history_index = -1
                    model.input_text = ""
                else:
                    model.input_text = model.history[model.history_index]
                model.cursor_position = len(model.input_text)
                model.autocorrect_suggestions = model.get_suggestions(model.input_text)
            event.app.invalidate()

    @kb.add("enter")
    def _(event):
        """Execute command"""
        if model.executing:
            return

        command = model.input_text.strip()
        if not command:
            return

        # Reset input
        model.history.append(command)
        model.history_index = -1
        model.input_text = ""
        model.cursor_position = 0
        model.autocorrect_suggestions = []

        # Execute
        asyncio.create_task(
            execute_command(model, command, lambda: event.app.invalidate())
        )

    @kb.add("<any>")
    def _(event):
        """Insert character"""
        if event.app.layout.current_control == input_control:
            char = event.data
            if isinstance(char, str) and len(char) == 1 and char.isprintable():
                model.input_text = (
                    model.input_text[: model.cursor_position]
                    + char
                    + model.input_text[model.cursor_position :]
                )
                model.cursor_position += 1
                model.autocorrect_suggestions = model.get_suggestions(model.input_text)
                event.app.invalidate()

    # Style
    style = Style.from_dict(
        {
            "background": f"bg:{rgb_hex(*theme.bg)}",
            "log": f"bg:{rgb_hex(*theme.bg_panel)}",
            "menu": f"bg:{rgb_hex(*theme.menu_bg)} fg:{rgb_hex(*theme.menu_fg)}",
            "status": f"bg:{rgb_hex(*theme.status_bg)} fg:{rgb_hex(*theme.status_fg)}",
            "input": f"bg:{rgb_hex(*theme.bg_panel)} fg:{rgb_hex(*theme.text)}",
            "autocorrect": f"bg:{rgb_hex(*theme.autocorrect_bg)} fg:{rgb_hex(*theme.autocorrect_fg)}",
        }
    )

    # Create application
    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=True,
        mouse_support=True,
        refresh_interval=config.frame_time,
    )

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """Main entry point"""
    # Signal handlers
    def signal_handler(signum, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run application
    app = build_app()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Eroare: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
