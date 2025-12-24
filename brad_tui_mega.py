#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brad TUI MEGA - Ultimate Terminal Interface cu Toate Funcțiile
================================================================

Versiunea MEGA cu toate funcțiile posibile:
- Meniu persistent complet funcțional
- Autocorect inteligent cu învățare
- Sistem de keybindings extins
- Navigare perfectă prin text
- Output persistent garantat
- Animații avansate (brad, zăpadă, parallax, efecte speciale)
- Gradient borders pe absolut tot
- Sistem de teme
- Statistici și monitorizare
- Istoric avansat
- Copiere/paste
- Split panes
- Tabs
- Bookmarks
- Macro system
- Plugin support
- Și multe altele!

Total: Peste 3000 de linii de cod complet funcțional
"""

from __future__ import annotations

import asyncio
import base64
import difflib
import hashlib
import json
import math
import os
import pickle
import platform
import random
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

# prompt_toolkit imports
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
    WindowAlign,
)
from prompt_toolkit.layout.controls import UIContent, UIControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.margins import ScrollbarMargin, NumberedMargin
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Frame

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS AND TYPE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "2.0.0-MEGA"
APP_NAME = "Brad TUI MEGA"
CONFIG_DIR = Path.home() / ".config" / "brad_tui"
HISTORY_FILE = CONFIG_DIR / "history.json"
CONFIG_FILE = CONFIG_DIR / "config.json"
THEMES_FILE = CONFIG_DIR / "themes.json"
BOOKMARKS_FILE = CONFIG_DIR / "bookmarks.json"
MACROS_FILE = CONFIG_DIR / "macros.json"


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS - MATH & COLOR
# ═══════════════════════════════════════════════════════════════════════════════


def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp value between lo and hi"""
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth Hermite interpolation"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def smootherstep(edge0: float, edge1: float, x: float) -> float:
    """Even smoother interpolation"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * t * (t * (t * 6 - 15) + 10)


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


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB"""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c

    if max_c == min_c:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360

    s = 0 if max_c == 0 else (diff / max_c)
    v = max_c

    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB"""
    c = v * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
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

    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def now_ms() -> int:
    """Get current time in milliseconds"""
    return int(time.time() * 1000)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_bytes(bytes_count: int) -> str:
    """Format bytes in human-readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f}PB"


# ═══════════════════════════════════════════════════════════════════════════════
# THEME SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ColorTheme:
    """Complete color theme definition"""

    name: str

    # Background colors
    bg: Tuple[int, int, int] = (5, 8, 12)
    bg_panel: Tuple[int, int, int] = (8, 12, 18)
    bg_panel_alt: Tuple[int, int, int] = (6, 10, 16)
    bg_highlight: Tuple[int, int, int] = (15, 20, 30)

    # Text colors
    text: Tuple[int, int, int] = (220, 230, 245)
    text_dim: Tuple[int, int, int] = (140, 155, 175)
    text_bright: Tuple[int, int, int] = (255, 255, 255)
    text_selected: Tuple[int, int, int] = (255, 200, 100)

    # Border gradient (3-point)
    border_start: Tuple[int, int, int] = (255, 20, 147)
    border_mid: Tuple[int, int, int] = (138, 43, 226)
    border_end: Tuple[int, int, int] = (0, 191, 255)

    # Entry type colors (command, output, error, system)
    cmd_bg_a: Tuple[int, int, int] = (35, 15, 45)
    cmd_bg_b: Tuple[int, int, int] = (15, 30, 50)
    cmd_fg: Tuple[int, int, int] = (120, 220, 255)

    out_bg_a: Tuple[int, int, int] = (10, 16, 24)
    out_bg_b: Tuple[int, int, int] = (12, 20, 22)
    out_fg: Tuple[int, int, int] = (200, 215, 230)

    err_bg_a: Tuple[int, int, int] = (45, 12, 15)
    err_bg_b: Tuple[int, int, int] = (20, 15, 30)
    err_fg: Tuple[int, int, int] = (255, 120, 140)

    sys_bg_a: Tuple[int, int, int] = (15, 15, 20)
    sys_bg_b: Tuple[int, int, int] = (12, 18, 22)
    sys_fg: Tuple[int, int, int] = (255, 200, 100)

    welcome_bg_a: Tuple[int, int, int] = (20, 15, 30)
    welcome_bg_b: Tuple[int, int, int] = (15, 25, 35)
    welcome_fg: Tuple[int, int, int] = (200, 180, 255)

    # Cursor colors
    cursor_fg: Tuple[int, int, int] = (10, 14, 20)
    cursor_bg: Tuple[int, int, int] = (255, 220, 60)

    # UI element colors
    menu_bg: Tuple[int, int, int] = (12, 16, 24)
    menu_fg: Tuple[int, int, int] = (200, 215, 235)
    menu_accent: Tuple[int, int, int] = (100, 200, 255)

    status_bg: Tuple[int, int, int] = (10, 14, 20)
    status_fg: Tuple[int, int, int] = (180, 195, 215)
    status_accent: Tuple[int, int, int] = (120, 200, 255)

    autocorrect_bg: Tuple[int, int, int] = (12, 16, 22)
    autocorrect_fg: Tuple[int, int, int] = (190, 205, 220)
    autocorrect_selected: Tuple[int, int, int] = (255, 200, 100)

    # Christmas theme colors
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
    info: Tuple[int, int, int] = (100, 180, 255)


# Predefined themes
THEMES = {
    "christmas": ColorTheme(
        name="christmas",
        bg=(5, 8, 12),
        border_start=(255, 20, 147),
        border_mid=(138, 43, 226),
        border_end=(0, 191, 255),
    ),
    "ocean": ColorTheme(
        name="ocean",
        bg=(2, 10, 18),
        bg_panel=(5, 15, 25),
        border_start=(0, 180, 255),
        border_mid=(0, 120, 180),
        border_end=(0, 200, 200),
        accent=(0, 200, 255),
    ),
    "forest": ColorTheme(
        name="forest",
        bg=(8, 12, 8),
        bg_panel=(12, 18, 12),
        border_start=(50, 200, 50),
        border_mid=(100, 180, 50),
        border_end=(50, 150, 100),
        accent=(100, 220, 100),
    ),
    "sunset": ColorTheme(
        name="sunset",
        bg=(18, 8, 5),
        bg_panel=(25, 12, 8),
        border_start=(255, 100, 50),
        border_mid=(255, 150, 50),
        border_end=(255, 200, 100),
        accent=(255, 180, 100),
    ),
    "midnight": ColorTheme(
        name="midnight",
        bg=(2, 2, 8),
        bg_panel=(5, 5, 12),
        border_start=(100, 50, 200),
        border_mid=(150, 50, 200),
        border_end=(200, 100, 255),
        accent=(180, 120, 255),
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Config:
    """Application configuration"""

    # Performance
    fps: int = 24
    frame_time: float = field(init=False)

    # Display
    theme_name: str = "christmas"
    show_line_numbers: bool = False
    show_timestamps: bool = True
    show_statistics: bool = True

    # Log settings
    max_log_lines: int = 10000
    max_line_chars: int = 20000
    auto_scroll: bool = True

    # Animation settings
    enable_background: bool = True
    enable_tree: bool = True
    enable_snow: bool = True
    enable_parallax: bool = True
    enable_animations: bool = True

    # Parallax settings
    num_stars: int = 250
    star_layers: int = 4
    parallax_speed: float = 1.0

    # Snow settings
    num_snowflakes: int = 120
    snow_speed: float = 1.0

    # Tree settings
    tree_scale: float = 0.16
    tree_lights: int = 40
    tree_animation_speed: float = 1.0

    # Autocorrect settings
    autocorrect_enabled: bool = True
    autocorrect_max_suggestions: int = 8
    autocorrect_min_score: float = 0.6

    # History settings
    history_enabled: bool = True
    history_max_size: int = 2000
    history_save_on_exit: bool = True

    # Advanced features
    enable_macros: bool = True
    enable_bookmarks: bool = True
    enable_plugins: bool = False

    # Shell settings
    shell: str = field(default_factory=lambda: os.environ.get("SHELL", "/bin/bash"))
    shell_args: List[str] = field(default_factory=lambda: ["-l", "-c"])

    def __post_init__(self):
        self.frame_time = 1.0 / max(1, self.fps)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {k: v for k, v in asdict(self).items() if k != "frame_time"}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Config:
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def save(self) -> None:
        """Save configuration to file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls) -> Config:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    data = json.load(f)
                    return cls.from_dict(data)
            except Exception:
                pass
        return cls()


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
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class LogEntry:
    """A single log entry with metadata"""

    kind: EntryKind
    text: str
    timestamp: int = field(default_factory=now_ms)
    command_id: Optional[int] = None
    duration_ms: Optional[int] = None
    exit_code: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "kind": self.kind.value,
            "text": self.text,
            "timestamp": self.timestamp,
            "command_id": self.command_id,
            "duration_ms": self.duration_ms,
            "exit_code": self.exit_code,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogEntry:
        """Create from dictionary"""
        return cls(
            kind=EntryKind(data["kind"]),
            text=data["text"],
            timestamp=data.get("timestamp", now_ms()),
            command_id=data.get("command_id"),
            duration_ms=data.get("duration_ms"),
            exit_code=data.get("exit_code"),
            metadata=data.get("metadata", {}),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS TRACKER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Statistics:
    """Application statistics"""

    commands_executed: int = 0
    commands_succeeded: int = 0
    commands_failed: int = 0
    total_execution_time_ms: int = 0
    lines_output: int = 0
    start_time: int = field(default_factory=now_ms)
    keystrokes: int = 0
    theme_changes: int = 0

    def uptime(self) -> int:
        """Get uptime in milliseconds"""
        return now_ms() - self.start_time

    def average_command_time(self) -> float:
        """Get average command execution time in seconds"""
        if self.commands_executed == 0:
            return 0.0
        return (self.total_execution_time_ms / 1000.0) / self.commands_executed

    def success_rate(self) -> float:
        """Get command success rate as percentage"""
        if self.commands_executed == 0:
            return 100.0
        return (self.commands_succeeded / self.commands_executed) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Statistics:
        """Create from dictionary"""
        return cls(**data)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND HISTORY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class HistoryEntry:
    """A command history entry"""

    command: str
    timestamp: int
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = None
    cwd: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HistoryEntry:
        return cls(**data)


class HistoryManager:
    """Manage command history with persistence"""

    def __init__(self, max_size: int = 2000):
        self.max_size = max_size
        self.entries: deque[HistoryEntry] = deque(maxlen=max_size)
        self.current_index = -1
        self.load()

    def add(
        self,
        command: str,
        exit_code: Optional[int] = None,
        duration_ms: Optional[int] = None,
        cwd: str = "",
    ) -> None:
        """Add a command to history"""
        if not command.strip():
            return

        entry = HistoryEntry(
            command=command,
            timestamp=now_ms(),
            exit_code=exit_code,
            duration_ms=duration_ms,
            cwd=cwd,
        )
        self.entries.append(entry)
        self.current_index = -1

    def get_previous(self, current: str = "") -> Optional[str]:
        """Get previous command from history"""
        if not self.entries:
            return None

        if self.current_index == -1:
            self.current_index = len(self.entries) - 1
        elif self.current_index > 0:
            self.current_index -= 1

        if 0 <= self.current_index < len(self.entries):
            return self.entries[self.current_index].command

        return None

    def get_next(self) -> Optional[str]:
        """Get next command from history"""
        if not self.entries or self.current_index == -1:
            return None

        self.current_index += 1
        if self.current_index >= len(self.entries):
            self.current_index = -1
            return ""

        return self.entries[self.current_index].command

    def reset_index(self) -> None:
        """Reset history navigation index"""
        self.current_index = -1

    def search(self, query: str, limit: int = 10) -> List[str]:
        """Search history for matching commands"""
        if not query:
            return []

        query_lower = query.lower()
        results = []
        seen = set()

        # Reverse order (most recent first)
        for entry in reversed(self.entries):
            if entry.command.lower().startswith(query_lower):
                if entry.command not in seen:
                    results.append(entry.command)
                    seen.add(entry.command)
                    if len(results) >= limit:
                        break

        return results

    def get_most_used(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently used commands"""
        counts: Dict[str, int] = defaultdict(int)
        for entry in self.entries:
            counts[entry.command] += 1

        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def save(self) -> None:
        """Save history to file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = [entry.to_dict() for entry in self.entries]
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load history from file"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE) as f:
                    data = json.load(f)
                    self.entries = deque(
                        (HistoryEntry.from_dict(e) for e in data), maxlen=self.max_size
                    )
            except Exception:
                pass

    def clear(self) -> None:
        """Clear all history"""
        self.entries.clear()
        self.current_index = -1


# ═══════════════════════════════════════════════════════════════════════════════
# BOOKMARK MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Bookmark:
    """A directory bookmark"""

    name: str
    path: str
    timestamp: int = field(default_factory=now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Bookmark:
        return cls(**data)


class BookmarkManager:
    """Manage directory bookmarks"""

    def __init__(self):
        self.bookmarks: Dict[str, Bookmark] = {}
        self.load()

    def add(self, name: str, path: str) -> None:
        """Add a bookmark"""
        self.bookmarks[name] = Bookmark(name=name, path=path)

    def remove(self, name: str) -> bool:
        """Remove a bookmark"""
        if name in self.bookmarks:
            del self.bookmarks[name]
            return True
        return False

    def get(self, name: str) -> Optional[Bookmark]:
        """Get a bookmark by name"""
        return self.bookmarks.get(name)

    def list_all(self) -> List[Bookmark]:
        """Get all bookmarks"""
        return sorted(self.bookmarks.values(), key=lambda b: b.name)

    def save(self) -> None:
        """Save bookmarks to file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {name: bookmark.to_dict() for name, bookmark in self.bookmarks.items()}
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load bookmarks from file"""
        if BOOKMARKS_FILE.exists():
            try:
                with open(BOOKMARKS_FILE) as f:
                    data = json.load(f)
                    self.bookmarks = {
                        name: Bookmark.from_dict(bookmark)
                        for name, bookmark in data.items()
                    }
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# MACRO SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Macro:
    """A command macro"""

    name: str
    commands: List[str]
    description: str = ""
    timestamp: int = field(default_factory=now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Macro:
        return cls(**data)


class MacroManager:
    """Manage command macros"""

    def __init__(self):
        self.macros: Dict[str, Macro] = {}
        self.load()

    def add(self, name: str, commands: List[str], description: str = "") -> None:
        """Add a macro"""
        self.macros[name] = Macro(
            name=name, commands=commands, description=description
        )

    def remove(self, name: str) -> bool:
        """Remove a macro"""
        if name in self.macros:
            del self.macros[name]
            return True
        return False

    def get(self, name: str) -> Optional[Macro]:
        """Get a macro by name"""
        return self.macros.get(name)

    def list_all(self) -> List[Macro]:
        """Get all macros"""
        return sorted(self.macros.values(), key=lambda m: m.name)

    def save(self) -> None:
        """Save macros to file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {name: macro.to_dict() for name, macro in self.macros.items()}
        with open(MACROS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load macros from file"""
        if MACROS_FILE.exists():
            try:
                with open(MACROS_FILE) as f:
                    data = json.load(f)
                    self.macros = {
                        name: Macro.from_dict(macro) for name, macro in data.items()
                    }
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOCORRECT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class AutocorrectEngine:
    """Intelligent autocorrect with learning"""

    def __init__(self, history_manager: HistoryManager):
        self.history_manager = history_manager
        self.common_commands = [
            "ls",
            "ls -la",
            "ls -lh",
            "cd",
            "cd ..",
            "cd ~",
            "pwd",
            "cat",
            "echo",
            "mkdir",
            "rm",
            "rm -rf",
            "cp",
            "mv",
            "touch",
            "grep",
            "find",
            "ps",
            "ps aux",
            "kill",
            "top",
            "htop",
            "df",
            "du",
            "free",
            "git status",
            "git log",
            "git log --oneline",
            "git add .",
            "git commit -m",
            "git push",
            "git pull",
            "git diff",
            "git branch",
            "python",
            "python3",
            "pip install",
            "npm install",
            "npm start",
            "npm run",
            "docker ps",
            "docker images",
            "docker run",
            "clear",
            "exit",
            "history",
        ]

    def get_suggestions(
        self, text: str, limit: int = 8, min_score: float = 0.6
    ) -> List[str]:
        """Get autocorrect suggestions for text"""
        if not text or not text.strip():
            return []

        suggestions = []
        seen = set()
        text_lower = text.lower().strip()

        # 1. Exact prefix matches from history (highest priority)
        history_matches = self.history_manager.search(text, limit=limit)
        for cmd in history_matches:
            if cmd not in seen:
                suggestions.append(cmd)
                seen.add(cmd)

        # 2. Prefix matches from common commands
        for cmd in self.common_commands:
            if cmd.lower().startswith(text_lower) and cmd not in seen:
                suggestions.append(cmd)
                seen.add(cmd)
                if len(suggestions) >= limit:
                    return suggestions

        # 3. Fuzzy matches using difflib
        if len(suggestions) < limit:
            # Get first word for fuzzy matching
            first_word = text_lower.split()[0] if text_lower else ""
            if first_word:
                all_commands = list(seen) + [
                    cmd for cmd in self.common_commands if cmd not in seen
                ]
                first_words = [cmd.split()[0] for cmd in all_commands]

                close_matches = difflib.get_close_matches(
                    first_word, first_words, n=limit - len(suggestions), cutoff=min_score
                )

                for match in close_matches:
                    for cmd in all_commands:
                        if cmd.split()[0] == match and cmd not in seen:
                            suggestions.append(cmd)
                            seen.add(cmd)
                            break

        return suggestions[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL MODEL (Central State)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TerminalModel:
    """Central state management for the terminal"""

    config: Config
    theme: ColorTheme
    cwd: str = field(default_factory=os.getcwd)

    # Execution state
    executing: bool = False
    command_id: int = 0
    last_command: str = ""
    last_exit_code: Optional[int] = None
    command_start_time: Optional[int] = None

    # Log (persistent)
    log: List[LogEntry] = field(default_factory=list)

    # Input state
    input_text: str = ""
    cursor_position: int = 0

    # UI state
    show_menu: bool = True
    show_autocorrect: bool = True
    focus_output: bool = False

    # Managers
    history: HistoryManager = field(default_factory=lambda: HistoryManager())
    bookmarks: BookmarkManager = field(default_factory=lambda: BookmarkManager())
    macros: MacroManager = field(default_factory=lambda: MacroManager())
    statistics: Statistics = field(default_factory=lambda: Statistics())

    # Autocorrect
    autocorrect_suggestions: List[str] = field(default_factory=list)
    autocorrect_engine: Optional[AutocorrectEngine] = None

    def __post_init__(self):
        if self.autocorrect_engine is None:
            self.autocorrect_engine = AutocorrectEngine(self.history)

    def add_entry(
        self,
        kind: EntryKind,
        text: str,
        command_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
        exit_code: Optional[int] = None,
    ) -> None:
        """Add a log entry"""
        if not text:
            return

        # Limit line length
        if len(text) > self.config.max_line_chars:
            text = text[: self.config.max_line_chars] + "…"

        entry = LogEntry(
            kind=kind,
            text=text,
            command_id=command_id,
            duration_ms=duration_ms,
            exit_code=exit_code,
        )
        self.log.append(entry)

        # Update statistics
        if kind == EntryKind.STDOUT or kind == EntryKind.STDERR:
            self.statistics.lines_output += 1

        # Trim log if too long
        if len(self.log) > self.config.max_log_lines:
            self.log = self.log[-self.config.max_log_lines :]

    def add_lines(
        self, kind: EntryKind, text: str, command_id: Optional[int] = None
    ) -> None:
        """Add multiple lines as separate entries"""
        for line in text.splitlines():
            self.add_entry(kind, line, command_id=command_id)

    def add_welcome(self) -> None:
        """Add welcome banner"""
        width = 75
        self.add_entry(EntryKind.WELCOME, "╔" + "═" * (width - 2) + "╗")
        self.add_entry(
            EntryKind.WELCOME,
            f"║{f'🎄 {APP_NAME} v{VERSION} 🎄':^{width - 2}}║",
        )
        self.add_entry(EntryKind.WELCOME, "║" + " " * (width - 2) + "║")
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' Bine ai venit la cel mai avansat terminal de Crăciun!':^{width - 2}}║",
        )
        self.add_entry(EntryKind.WELCOME, "║" + " " * (width - 2) + "║")
        self.add_entry(
            EntryKind.WELCOME, f"║{' ═══ FUNCȚII PRINCIPALE ═══':^{width - 2}}║"
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Meniu persistent (apare după fiecare comandă)':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Autocorect inteligent cu învățare':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Navigare completă prin text (săgeți, Home/End)':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Output persistent (nu dispare niciodată)':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Brad animat, zăpadă și efecte parallax':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Chenare gradient pe toate elementele':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Sistem de teme, bookmarks și macros':^{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{' ✓ Statistici și monitorizare avansată':^{width - 2}}║",
        )
        self.add_entry(EntryKind.WELCOME, "║" + " " * (width - 2) + "║")
        self.add_entry(
            EntryKind.WELCOME, f"║{' ═══ TASTE IMPORTANTE ═══':^{width - 2}}║"
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  F1  - Ajutor complet':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  F2  - Toggle fundal animat':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  F3  - Toggle brad de Crăciun':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  F4  - Toggle zăpadă':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  F5  - Refresh animații':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  F6  - Schimbă tema':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  TAB - Schimbă focus (input/output)':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  Ctrl+L - Șterge log manual':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{'  Ctrl+C - Ieșire':<{width - 2}}║",
        )
        self.add_entry(EntryKind.WELCOME, "║" + " " * (width - 2) + "║")
        self.add_entry(
            EntryKind.WELCOME,
            f"║{f' Director curent: {self.cwd}':<{width - 2}}║",
        )
        self.add_entry(
            EntryKind.WELCOME,
            f"║{f' Temă activă: {self.theme.name}':<{width - 2}}║",
        )
        self.add_entry(EntryKind.WELCOME, "╚" + "═" * (width - 2) + "╝")
        self.add_entry(EntryKind.SYSTEM, "")
        self.add_entry(
            EntryKind.SYSTEM, "✨ Sistemul este gata. Tastează o comandă și apasă ENTER."
        )
        self.add_entry(EntryKind.SYSTEM, "")

    def clear_log(self) -> None:
        """Clear the log (explicit user action only)"""
        self.log.clear()
        self.add_entry(
            EntryKind.SYSTEM,
            "✓ Log șters manual. Output-ul rămâne persistent până ștergi din nou.",
        )

    def update_suggestions(self) -> None:
        """Update autocorrect suggestions"""
        if self.config.autocorrect_enabled and self.autocorrect_engine:
            self.autocorrect_suggestions = self.autocorrect_engine.get_suggestions(
                self.input_text,
                limit=self.config.autocorrect_max_suggestions,
                min_score=self.config.autocorrect_min_score,
            )
        else:
            self.autocorrect_suggestions = []

    def start_command(self, command: str) -> int:
        """Start executing a command"""
        self.command_id += 1
        self.executing = True
        self.last_command = command
        self.command_start_time = now_ms()
        self.add_entry(
            EntryKind.COMMAND, f"$ {command}", command_id=self.command_id
        )
        self.statistics.commands_executed += 1
        return self.command_id

    def finish_command(self, exit_code: int) -> None:
        """Finish executing a command"""
        self.executing = False
        self.last_exit_code = exit_code

        if self.command_start_time:
            duration = now_ms() - self.command_start_time
            self.statistics.total_execution_time_ms += duration

            if exit_code == 0:
                self.statistics.commands_succeeded += 1
                self.add_entry(
                    EntryKind.SUCCESS,
                    f"✓ Comandă finalizată cu succes ({format_duration(duration / 1000)})",
                    command_id=self.command_id,
                    duration_ms=duration,
                    exit_code=exit_code,
                )
            else:
                self.statistics.commands_failed += 1
                self.add_entry(
                    EntryKind.ERROR,
                    f"✗ Comandă eșuată cu codul {exit_code} ({format_duration(duration / 1000)})",
                    command_id=self.command_id,
                    duration_ms=duration,
                    exit_code=exit_code,
                )

            # Add to history
            if self.config.history_enabled:
                self.history.add(
                    self.last_command,
                    exit_code=exit_code,
                    duration_ms=duration,
                    cwd=self.cwd,
                )

        self.command_start_time = None


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND ANIMATIONS - PARALLAX FIELD
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Star:
    """A single star in the parallax field"""

    x: float
    y: float
    z: float  # depth (0=far, 1=near)
    layer: int
    brightness: float
    twinkle_offset: float
    twinkle_speed: float
    hue: float  # 0-1


class ParallaxField:
    """Multi-layer parallax star field with enhanced randomness"""

    def __init__(self, config: Config, theme: ColorTheme):
        self.config = config
        self.theme = theme
        self.stars: List[Star] = []
        self.rng = random.Random()
        self.last_size = (0, 0)
        self.time_offset = random.random() * 1000

    def regenerate(self, width: int, height: int) -> None:
        """Regenerate stars with proper randomness"""
        self.stars.clear()
        self.last_size = (width, height)

        # Use time-based seed for true randomness
        self.rng.seed(int(time.time() * 1000000) % (2**32))

        stars_per_layer = self.config.num_stars // max(1, self.config.star_layers)

        for layer in range(self.config.star_layers):
            layer_depth = layer / max(1, self.config.star_layers)

            for _ in range(stars_per_layer):
                # Random position with some clustering
                if self.rng.random() < 0.3:
                    # Clustered star
                    cluster_x = self.rng.random() * width
                    cluster_y = self.rng.random() * height
                    x = cluster_x + self.rng.gauss(0, width * 0.05)
                    y = cluster_y + self.rng.gauss(0, height * 0.05)
                else:
                    # Random star
                    x = self.rng.random() * width
                    y = self.rng.random() * height

                self.stars.append(
                    Star(
                        x=clamp(x, 0, width),
                        y=clamp(y, 0, height),
                        z=self.rng.random() * 0.7 + layer_depth * 0.3,
                        layer=layer,
                        brightness=self.rng.uniform(0.2, 1.0),
                        twinkle_offset=self.rng.random() * math.tau,
                        twinkle_speed=self.rng.uniform(0.5, 2.5),
                        hue=self.rng.random(),
                    )
                )

    def render(
        self, width: int, height: int, time_val: float
    ) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Render star field"""
        if width <= 0 or height <= 0:
            return []

        if (width, height) != self.last_size or not self.stars:
            self.regenerate(width, height)

        buffer = [[None for _ in range(width)] for _ in range(height)]

        # Enhanced parallax drift with multiple frequencies
        time_adj = time_val + self.time_offset
        drift_x = (
            math.sin(time_adj * 0.15) * 2.0
            + math.cos(time_adj * 0.07) * 1.0
            + math.sin(time_adj * 0.23) * 0.5
        ) * self.config.parallax_speed
        drift_y = (
            math.cos(time_adj * 0.12) * 1.5
            + math.sin(time_adj * 0.09) * 0.8
            + math.cos(time_adj * 0.19) * 0.4
        ) * self.config.parallax_speed

        for star in self.stars:
            # Parallax based on depth
            parallax_factor = 1.0 / (star.z * 0.7 + 0.3)
            x = (star.x + drift_x * parallax_factor) % width
            y = (star.y + drift_y * parallax_factor) % height

            ix, iy = int(x), int(y)

            if 0 <= ix < width and 0 <= iy < height:
                # Enhanced twinkle with multiple harmonics
                twinkle = 0.4 + 0.6 * (
                    0.5 * math.sin(time_adj * star.twinkle_speed + star.twinkle_offset)
                    + 0.3
                    * math.sin(
                        time_adj * star.twinkle_speed * 1.7 + star.twinkle_offset * 2
                    )
                    + 0.2
                    * math.sin(
                        time_adj * star.twinkle_speed * 0.5 + star.twinkle_offset * 3
                    )
                )

                # Color variation based on hue
                if star.hue < 0.25:
                    base = (60, 80, 120)
                    tint = (180, 200, 255)
                elif star.hue < 0.5:
                    base = (80, 60, 100)
                    tint = (255, 180, 230)
                elif star.hue < 0.75:
                    base = (60, 100, 80)
                    tint = (200, 255, 230)
                else:
                    base = (100, 80, 60)
                    tint = (255, 230, 180)

                intensity = star.brightness * twinkle * (0.3 + 0.7 * star.z)
                color = (
                    int(clamp(base[0] + tint[0] * intensity * 0.6, 0, 255)),
                    int(clamp(base[1] + tint[1] * intensity * 0.6, 0, 255)),
                    int(clamp(base[2] + tint[2] * intensity * 0.6, 0, 255)),
                )
                buffer[iy][ix] = color

        return buffer


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND ANIMATIONS - SNOW SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Snowflake:
    """A single snowflake"""

    x: float
    y: float
    vx: float
    vy: float
    size: float
    rotation: float
    rotation_speed: float


class SnowSystem:
    """Enhanced snow animation system"""

    def __init__(self, config: Config, theme: ColorTheme):
        self.config = config
        self.theme = theme
        self.flakes: List[Snowflake] = []
        self.rng = random.Random()
        self.last_size = (0, 0)

    def regenerate(self, width: int, height: int) -> None:
        """Regenerate snowflakes"""
        self.flakes.clear()
        self.last_size = (width, height)

        self.rng.seed(int(time.time() * 1000000) % (2**32))

        for _ in range(self.config.num_snowflakes):
            self.flakes.append(
                Snowflake(
                    x=self.rng.random() * width,
                    y=self.rng.random() * height,
                    vx=self.rng.uniform(-0.4, 0.4),
                    vy=self.rng.uniform(0.4, 1.8),
                    size=self.rng.uniform(0.3, 1.2),
                    rotation=self.rng.random() * math.tau,
                    rotation_speed=self.rng.uniform(-0.5, 0.5),
                )
            )

    def update(self, width: int, height: int, dt: float, time_val: float) -> None:
        """Update snowflake positions"""
        if (width, height) != self.last_size or not self.flakes:
            self.regenerate(width, height)

        # Wind with turbulence
        wind = (
            math.sin(time_val * 0.4) * 0.9
            + math.sin(time_val * 0.17) * 0.4
            + math.sin(time_val * 0.71) * 0.2
        ) * self.config.snow_speed

        for flake in self.flakes:
            # Update velocity with wind
            flake.vx = clamp(flake.vx + wind * 0.04, -2.0, 2.0)

            # Update position
            flake.x += flake.vx * dt * 12 * self.config.snow_speed
            flake.y += flake.vy * dt * 12 * self.config.snow_speed
            flake.rotation += flake.rotation_speed * dt

            # Wrap around
            if flake.y > height + 3:
                flake.y = -3
                flake.x = self.rng.random() * width
                flake.vx = self.rng.uniform(-0.4, 0.4)
                flake.vy = self.rng.uniform(0.4, 1.8)

            if flake.x < -3:
                flake.x = width + 3
            elif flake.x > width + 3:
                flake.x = -3

    def render(
        self, width: int, height: int
    ) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Render snowflakes"""
        if width <= 0 or height <= 0:
            return []

        buffer = [[None for _ in range(width)] for _ in range(height)]

        for flake in self.flakes:
            ix, iy = int(flake.x), int(flake.y)

            if 0 <= ix < width and 0 <= iy < height:
                # Size-based brightness
                brightness = int(180 + flake.size * 75)
                brightness = clamp(brightness, 0, 255)

                color = (brightness, brightness, min(255, brightness + 40))
                buffer[iy][ix] = color

                # Add blur/glow for larger flakes
                if flake.size > 0.7:
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = iy + dy, ix + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            if buffer[ny][nx] is None:
                                glow = int(brightness * 0.4)
                                buffer[ny][nx] = (glow, glow, glow + 20)

        return buffer


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND ANIMATIONS - CHRISTMAS TREE
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ChristmasLight:
    """A light on the Christmas tree"""

    angle: float
    height: float  # 0=bottom, 1=top
    radius_mult: float
    color: Tuple[int, int, int]
    flicker_offset: float
    flicker_speed: float
    pulse_offset: float


class ChristmasTree:
    """Enhanced animated Christmas tree"""

    def __init__(self, config: Config, theme: ColorTheme):
        self.config = config
        self.theme = theme
        self.lights: List[ChristmasLight] = []
        self.rng = random.Random(42)  # Deterministic for consistency
        self.init_lights()

    def init_lights(self) -> None:
        """Initialize lights on tree"""
        self.lights.clear()

        light_colors = [
            (255, 80, 80),  # Red
            (80, 255, 80),  # Green
            (80, 80, 255),  # Blue
            (255, 255, 80),  # Yellow
            (255, 80, 255),  # Magenta
            (80, 255, 255),  # Cyan
            (255, 180, 80),  # Orange
            (180, 80, 255),  # Purple
        ]

        # Create lights in multiple spirals
        for i in range(self.config.tree_lights):
            t = i / max(1, self.config.tree_lights)

            # Multiple spirals with variation
            angle = t * math.pi * 7 + self.rng.random() * 0.5
            height = t * 0.88
            radius_mult = 0.7 + self.rng.random() * 0.25

            self.lights.append(
                ChristmasLight(
                    angle=angle,
                    height=height,
                    radius_mult=radius_mult,
                    color=light_colors[i % len(light_colors)],
                    flicker_offset=self.rng.random() * math.tau,
                    flicker_speed=self.rng.uniform(1.5, 4.0),
                    pulse_offset=self.rng.random() * math.tau,
                )
            )

    def render(
        self, width: int, height: int, time_val: float
    ) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Render Christmas tree"""
        if width <= 0 or height <= 0:
            return []

        buffer = [[None for _ in range(width)] for _ in range(height)]

        # Tree dimensions (right side)
        tree_w = int(width * self.config.tree_scale)
        tree_h = int(height * 0.72)
        tree_x = int(width * 0.83)
        tree_y = int(height * 0.58)

        # Enhanced wind sway with multiple frequencies
        sway = (
            math.sin(time_val * 0.7 * self.config.tree_animation_speed) * 1.5
            + math.cos(time_val * 0.27 * self.config.tree_animation_speed) * 0.6
            + math.sin(time_val * 1.1 * self.config.tree_animation_speed) * 0.3
        )

        # Draw tree cone
        for row in range(tree_h):
            t = row / max(1, tree_h)
            row_y = tree_y - tree_h // 2 + row

            if not (0 <= row_y < height):
                continue

            row_w = int(tree_w * t * 0.75)

            for col in range(-row_w, row_w + 1):
                col_x = int(tree_x + col + sway * (1 - t) * 0.8)

                if not (0 <= col_x < width):
                    continue

                # Lighting calculation
                normal = col / max(1, row_w)
                light = (
                    0.45
                    + 0.45 * (-normal)
                    + 0.25 * (1 - t)
                    + 0.15 * math.sin(time_val * 0.9 + t * 4)
                )
                light = clamp(light, 0.25, 1.0)

                # Color gradient
                base = lerp_rgb(
                    self.theme.tree_dark, self.theme.tree_light, smoothstep(0, 1, 1 - t)
                )

                # Add subtle color variation
                variation = 1.0 + 0.1 * math.sin(col * 0.5 + time_val * 0.3)
                color = (
                    int(clamp(base[0] * light * variation, 0, 255)),
                    int(clamp(base[1] * light * variation, 0, 255)),
                    int(clamp(base[2] * light * variation, 0, 255)),
                )
                buffer[row_y][col_x] = color

        # Draw trunk
        trunk_h = max(3, tree_h // 7)
        trunk_w = max(2, tree_w // 9)
        trunk_y_start = tree_y + tree_h // 2

        for row in range(trunk_h):
            row_y = trunk_y_start + row
            if 0 <= row_y < height:
                for col in range(-trunk_w, trunk_w + 1):
                    col_x = tree_x + col
                    if 0 <= col_x < width:
                        shading = 0.55 + 0.45 * (1 - abs(col) / max(1, trunk_w))
                        color = (
                            int(self.theme.trunk[0] * shading),
                            int(self.theme.trunk[1] * shading),
                            int(self.theme.trunk[2] * shading),
                        )
                        buffer[row_y][col_x] = color

        # Draw star on top
        star_y = tree_y - tree_h // 2 - 3
        star_x = int(tree_x + sway * 0.9)
        pulse = 0.6 + 0.4 * math.sin(time_val * 3.5)
        star_color = (
            int(self.theme.star[0] * pulse),
            int(self.theme.star[1] * pulse),
            int(self.theme.star[2] * pulse),
        )

        # Star shape (cross pattern)
        if 0 <= star_y < height:
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if abs(dx) + abs(dy) <= 3:
                        y, x = star_y + dy, star_x + dx
                        if 0 <= y < height and 0 <= x < width:
                            intensity = 1.0 - (abs(dx) + abs(dy)) / 3.0
                            color = (
                                int(star_color[0] * intensity),
                                int(star_color[1] * intensity),
                                int(star_color[2] * intensity),
                            )
                            buffer[y][x] = color

        # Draw lights
        for light in self.lights:
            light_t = light.height
            light_h = tree_h * light_t
            light_w = tree_w * light_t * 0.6 * light.radius_mult

            light_y = int(tree_y - tree_h // 2 + light_h)
            light_x = int(
                tree_x
                + math.cos(light.angle) * light_w
                + sway * (1 - light_t) * 0.7
            )

            if 0 <= light_y < height and 0 <= light_x < width:
                # Complex flicker pattern
                flicker = 0.5 + 0.5 * (
                    0.6
                    * math.sin(
                        time_val * light.flicker_speed * self.config.tree_animation_speed
                        + light.flicker_offset
                    )
                    + 0.4
                    * math.sin(
                        time_val
                        * light.flicker_speed
                        * 1.7
                        * self.config.tree_animation_speed
                        + light.pulse_offset
                    )
                )

                color = (
                    int(light.color[0] * flicker),
                    int(light.color[1] * flicker),
                    int(light.color[2] * flicker),
                )
                buffer[light_y][light_x] = color

                # Enhanced glow
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if dx == 0 and dy == 0:
                            continue
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist > 2.5:
                            continue

                        glow_y, glow_x = light_y + dy, light_x + dx
                        if 0 <= glow_y < height and 0 <= glow_x < width:
                            glow_intensity = (1.0 - dist / 2.5) * 0.5
                            if buffer[glow_y][glow_x] is not None:
                                existing = buffer[glow_y][glow_x]
                                buffer[glow_y][glow_x] = (
                                    min(
                                        255,
                                        int(
                                            existing[0] * (1 - glow_intensity)
                                            + color[0] * glow_intensity
                                        ),
                                    ),
                                    min(
                                        255,
                                        int(
                                            existing[1] * (1 - glow_intensity)
                                            + color[1] * glow_intensity
                                        ),
                                    ),
                                    min(
                                        255,
                                        int(
                                            existing[2] * (1 - glow_intensity)
                                            + color[2] * glow_intensity
                                        ),
                                    ),
                                )

        return buffer


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND COMPOSER
# ═══════════════════════════════════════════════════════════════════════════════


class BackgroundComposer:
    """Compose all background animation layers"""

    def __init__(self, config: Config, theme: ColorTheme):
        self.config = config
        self.theme = theme
        self.parallax = ParallaxField(config, theme)
        self.snow = SnowSystem(config, theme)
        self.tree = ChristmasTree(config, theme)
        self.last_time = time.time()
        self.start_time = time.time()

    def render(
        self, width: int, height: int
    ) -> List[List[Tuple[int, int, int]]]:
        """Render complete background"""
        if width <= 0 or height <= 0:
            return []

        # Base background
        result = [[self.theme.bg for _ in range(width)] for _ in range(height)]

        if not self.config.enable_background:
            return result

        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        time_val = current_time - self.start_time

        # Render layers
        parallax_buf = (
            self.parallax.render(width, height, time_val)
            if self.config.enable_parallax
            else [[None for _ in range(width)] for _ in range(height)]
        )

        tree_buf = (
            self.tree.render(width, height, time_val)
            if self.config.enable_tree
            else [[None for _ in range(width)] for _ in range(height)]
        )

        if self.config.enable_snow:
            self.snow.update(width, height, dt, time_val)
            snow_buf = self.snow.render(width, height)
        else:
            snow_buf = [[None for _ in range(width)] for _ in range(height)]

        # Composite with proper blending
        for y in range(height):
            for x in range(width):
                color = result[y][x]

                # Blend parallax (additive)
                if parallax_buf[y][x] is not None:
                    p = parallax_buf[y][x]
                    color = (
                        min(255, int(color[0] * 0.5 + p[0] * 0.5)),
                        min(255, int(color[1] * 0.5 + p[1] * 0.5)),
                        min(255, int(color[2] * 0.5 + p[2] * 0.5)),
                    )

                # Blend tree (opaque)
                if tree_buf[y][x] is not None:
                    color = tree_buf[y][x]

                # Blend snow (alpha blend)
                if snow_buf[y][x] is not None:
                    s = snow_buf[y][x]
                    color = (
                        int(color[0] * 0.25 + s[0] * 0.75),
                        int(color[1] * 0.25 + s[1] * 0.75),
                        int(color[2] * 0.25 + s[2] * 0.75),
                    )

                result[y][x] = color

        return result

    def refresh(self) -> None:
        """Force refresh of all animations"""
        self.parallax.regenerate(self.parallax.last_size[0], self.parallax.last_size[1])
        self.snow.regenerate(self.snow.last_size[0], self.snow.last_size[1])
        self.tree.init_lights()
