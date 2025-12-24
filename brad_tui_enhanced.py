#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brad TUI (Enhanced): interactive terminal UI with animated background.

Goals (fixed vs old implementation):
- output is persistent (no screen-clearing redraw that nukes the log)
- input line supports full editing + cursor movement (arrows/home/end, etc.)
- keybinds are real and consistent
- menu bar is persistent; hidden only while a command is executing
- "autocorrect/suggestions" panel is anchored at the bottom (near utilities)
- background parallax/tree animation never writes into the text panes

Note on "HLSL/GLSL":
This is a pure terminal TUI. We implement a shader-like pipeline in Python
(buffer render + post-like effects) but do not use GPU shaders.
"""

from __future__ import annotations

import asyncio
import math
import os
import random
import signal
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Float, FloatContainer, HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import UIContent, UIControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea

# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def rgb_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_rgb(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def now_ms() -> int:
    return int(time.time() * 1000)


# ──────────────────────────────────────────────────────────────────────────────
# Render config & look
# ──────────────────────────────────────────────────────────────────────────────


class EntryKind(str, Enum):
    SYSTEM = "system"
    COMMAND = "command"
    STDOUT = "stdout"
    STDERR = "stderr"


@dataclass(frozen=True)
class Theme:
    # Base UI colors
    bg: Tuple[int, int, int] = (8, 10, 14)
    panel_bg: Tuple[int, int, int] = (10, 14, 20)
    panel_bg_2: Tuple[int, int, int] = (8, 12, 18)
    text: Tuple[int, int, int] = (220, 235, 255)
    muted: Tuple[int, int, int] = (145, 165, 190)

    # Gradient border colors (left->right)
    border_a: Tuple[int, int, int] = (255, 0, 170)
    border_b: Tuple[int, int, int] = (0, 190, 255)

    # Entry backgrounds (subtle tints per kind)
    cmd_bg_a: Tuple[int, int, int] = (30, 10, 35)
    cmd_bg_b: Tuple[int, int, int] = (10, 25, 40)
    out_bg_a: Tuple[int, int, int] = (8, 14, 22)
    out_bg_b: Tuple[int, int, int] = (8, 18, 18)
    err_bg_a: Tuple[int, int, int] = (40, 10, 12)
    err_bg_b: Tuple[int, int, int] = (16, 12, 26)
    sys_bg_a: Tuple[int, int, int] = (12, 12, 16)
    sys_bg_b: Tuple[int, int, int] = (10, 14, 18)

    # Cursor
    cursor_fg: Tuple[int, int, int] = (10, 14, 20)
    cursor_bg: Tuple[int, int, int] = (255, 240, 90)

    # Accent
    accent: Tuple[int, int, int] = (100, 220, 255)
    ok: Tuple[int, int, int] = (120, 240, 160)
    warn: Tuple[int, int, int] = (255, 210, 120)
    bad: Tuple[int, int, int] = (255, 120, 140)


@dataclass
class AppConfig:
    fps: int = 18
    max_log_lines: int = 2500
    max_line_chars: int = 4000
    snowflakes: int = 90
    stars: int = 160
    show_background: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Background: parallax + tree (rendered into ANSI-like fragments)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Star:
    x: float
    y: float
    z: float
    twinkle: float
    hue: float


class ParallaxField:
    """
    Layer-0 parallax that never interferes with text panes: it renders only
    in the background window.
    """

    def __init__(self, cfg: AppConfig, theme: Theme, seed: int = 1337) -> None:
        self.cfg = cfg
        self.theme = theme
        self._rnd = random.Random(seed)
        self._stars: List[Star] = []
        self._last_size: Tuple[int, int] = (0, 0)

    def _regen(self, w: int, h: int) -> None:
        self._stars.clear()
        for _ in range(self.cfg.stars):
            # z = depth; higher z -> slower movement and dimmer
            z = self._rnd.uniform(0.25, 1.0)
            self._stars.append(
                Star(
                    x=self._rnd.uniform(0, w),
                    y=self._rnd.uniform(0, h),
                    z=z,
                    twinkle=self._rnd.uniform(0.6, 1.4),
                    hue=self._rnd.uniform(0.0, 1.0),
                )
            )
        self._last_size = (w, h)

    def render(self, w: int, h: int, t: float) -> List[List[Optional[Tuple[int, int, int]]]]:
        """
        Returns a low-res color buffer (h x w) with None for "no pixel".
        """
        if w <= 0 or h <= 0:
            return []
        if (w, h) != self._last_size:
            self._regen(w, h)

        buf: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(w)] for _ in range(h)]

        # Subtle drift; use a couple sin waves so it doesn't look like text shimmer.
        drift_x = math.sin(t * 0.25) * 1.2 + math.sin(t * 0.07) * 0.6
        drift_y = math.cos(t * 0.20) * 0.8 + math.sin(t * 0.09) * 0.4

        for s in self._stars:
            # Parallax per depth
            px = (s.x + drift_x * (1.0 / s.z)) % w
            py = (s.y + drift_y * (1.0 / s.z)) % h
            ix, iy = int(px), int(py)

            tw = 0.65 + 0.35 * math.sin(t * (1.0 + 1.5 * (1 - s.z)) + s.twinkle * 10.0)
            base = (35, 50, 70)
            tint = lerp_rgb((180, 220, 255), (255, 180, 230), s.hue)
            col = (
                int(clamp(base[0] + tint[0] * tw * (1 - s.z) * 0.45, 0, 255)),
                int(clamp(base[1] + tint[1] * tw * (1 - s.z) * 0.45, 0, 255)),
                int(clamp(base[2] + tint[2] * tw * (1 - s.z) * 0.45, 0, 255)),
            )
            buf[iy][ix] = col
        return buf


class TreeRenderer:
    """
    A "shader-like" 2D renderer: it outputs a color buffer (not ANSI text).
    We keep it low-res (text cells), then composite with background.
    """

    def __init__(self, cfg: AppConfig, theme: Theme, seed: int = 42) -> None:
        self.cfg = cfg
        self.theme = theme
        self._rnd = random.Random(seed)
        self._bulbs: List[Tuple[float, float, float]] = []
        self._last_dims: Tuple[int, int] = (0, 0)

    def _regen_bulbs(self, w: int, h: int) -> None:
        self._bulbs.clear()
        cx = w * 0.72
        cy = h * 0.62
        height = h * 0.62
        radius = w * 0.22

        bands = 10
        for band in range(2, bands + 1):
            k = band / (bands + 1)
            y = cy - height * k
            r = radius * (1 - k)
            count = 5 + band // 2
            for i in range(count):
                ang = (i / count) * math.tau + band * 0.9
                x = cx + math.cos(ang) * r
                # pseudo-depth for flicker variety
                z = math.sin(ang) * 0.35
                self._bulbs.append((x, y, z))

        self._last_dims = (w, h)

    def render(self, w: int, h: int, t: float) -> List[List[Optional[Tuple[int, int, int]]]]:
        if w <= 0 or h <= 0:
            return []
        if (w, h) != self._last_dims:
            self._regen_bulbs(w, h)

        buf: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(w)] for _ in range(h)]

        cx = w * 0.72
        cy = h * 0.62
        height = h * 0.62
        radius = w * 0.22

        # Wind sway
        sway = math.sin(t * 0.9) * 0.9 + math.sin(t * 0.31) * 0.35

        # "Cone" shading with cheap normals
        for iy in range(h):
            y = iy
            k = (cy - y) / max(height, 1.0)  # 1 at tip, 0 at base
            if k < 0 or k > 1:
                continue
            r = radius * (1 - k)
            # trunk area is below; skip
            for ix in range(w):
                dx = (ix - (cx + sway * (1 - k)))
                if abs(dx) > r:
                    continue

                # Normal-ish shading: brighter towards one side + towards tip
                nx = dx / max(r, 1.0)
                light = 0.55 + 0.35 * (-nx) + 0.25 * k + 0.15 * math.sin(t * 0.8 + k * 5)
                light = clamp(light, 0.25, 1.0)

                base = (14, 88, 34)
                tip = (60, 210, 90)
                col = lerp_rgb(base, tip, k)
                col = (int(col[0] * light), int(col[1] * light), int(col[2] * light))
                buf[iy][ix] = col

        # Trunk
        trunk_h = max(2, int(h * 0.10))
        trunk_w = max(2, int(w * 0.03))
        for iy in range(int(cy) + 1, min(h, int(cy) + 1 + trunk_h)):
            for ix in range(int(cx - trunk_w), int(cx + trunk_w) + 1):
                if 0 <= ix < w:
                    ndotl = 0.55 + 0.45 * math.cos((ix - cx) * 0.9)
                    col = (int(95 * ndotl), int(62 * ndotl), int(35 * ndotl))
                    buf[iy][ix] = col

        # Star
        sx, sy = int(cx + sway), int(cy - height) - 1
        pulse = 0.65 + 0.35 * math.sin(t * 3.0)
        star = (int(255 * pulse), int(230 * pulse), int(120 + 80 * pulse))
        for dy in range(-1, 2):
            for dx in range(-2, 3):
                x, y = sx + dx, sy + dy
                if 0 <= x < w and 0 <= y < h and (abs(dx) + abs(dy) <= 3):
                    buf[y][x] = star

        # Bulbs (flicker) + small halo
        for i, (bx, by, bz) in enumerate(self._bulbs):
            ix = int(bx + sway * 0.7)
            iy = int(by)
            if not (0 <= ix < w and 0 <= iy < h):
                continue
            phase = t * (3.0 + (i % 4) * 0.35) + i * 0.37 + bz * 2.0
            flick = 0.55 + 0.45 * math.sin(phase)
            hue = (i / max(len(self._bulbs), 1)) % 1.0
            base = lerp_rgb((255, 60, 90), (80, 210, 255), hue)
            col = (int(base[0] * flick), int(base[1] * flick), int(base[2] * flick))
            buf[iy][ix] = col

            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    x, y = ix + dx, iy + dy
                    if 0 <= x < w and 0 <= y < h and buf[y][x] is not None:
                        br, bg, bb = buf[y][x]
                        buf[y][x] = (
                            min(255, int(br * 0.78 + col[0] * 0.22)),
                            min(255, int(bg * 0.78 + col[1] * 0.22)),
                            min(255, int(bb * 0.78 + col[2] * 0.22)),
                        )
        return buf


@dataclass
class Snow:
    x: float
    y: float
    vx: float
    vy: float
    depth: float


class SnowSystem:
    def __init__(self, cfg: AppConfig, seed: int = 999) -> None:
        self.cfg = cfg
        self._rnd = random.Random(seed)
        self._flakes: List[Snow] = []
        self._last_dims: Tuple[int, int] = (0, 0)

    def _reset(self, w: int, h: int) -> None:
        self._flakes.clear()
        for _ in range(self.cfg.snowflakes):
            self._flakes.append(
                Snow(
                    x=self._rnd.uniform(0, w),
                    y=self._rnd.uniform(0, h),
                    vx=self._rnd.uniform(-0.25, 0.25),
                    vy=self._rnd.uniform(0.65, 1.25),
                    depth=self._rnd.uniform(0.2, 1.0),
                )
            )
        self._last_dims = (w, h)

    def update_and_render(self, w: int, h: int, dt: float, t: float) -> List[List[Optional[Tuple[int, int, int]]]]:
        if w <= 0 or h <= 0:
            return []
        if (w, h) != self._last_dims:
            self._reset(w, h)

        buf: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(w)] for _ in range(h)]
        wind = math.sin(t * 0.7) * 0.75 + math.sin(t * 0.13) * 0.35

        for flake in self._flakes:
            flake.vx = clamp(flake.vx + wind * 0.02 * (1 - flake.depth), -1.2, 1.2)
            flake.x += flake.vx * dt * (3.0 - 2.0 * flake.depth)
            flake.y += flake.vy * dt * (3.0 - 2.0 * flake.depth)
            if flake.y >= h + 2:
                flake.y = -2
                flake.x = self._rnd.uniform(0, w)
                flake.vx = self._rnd.uniform(-0.25, 0.25)
                flake.vy = self._rnd.uniform(0.65, 1.25)
                flake.depth = self._rnd.uniform(0.2, 1.0)

            ix, iy = int(flake.x) % w, int(flake.y)
            if 0 <= iy < h:
                bright = int(190 + (1 - flake.depth) * 60)
                col = (bright, bright, min(255, bright + 20))
                buf[iy][ix] = col
        return buf


class BackgroundComposer:
    def __init__(self, cfg: AppConfig, theme: Theme) -> None:
        self.cfg = cfg
        self.theme = theme
        self.parallax = ParallaxField(cfg, theme)
        self.tree = TreeRenderer(cfg, theme)
        self.snow = SnowSystem(cfg)

    def composite(self, w: int, h: int, t: float, dt: float) -> List[List[Tuple[int, int, int]]]:
        base = [[self.theme.bg for _ in range(w)] for _ in range(h)]
        if not self.cfg.show_background:
            return base

        stars = self.parallax.render(w, h, t)
        tree = self.tree.render(w, h, t)
        snow = self.snow.update_and_render(w, h, dt, t)

        def blend(dst: Tuple[int, int, int], src: Optional[Tuple[int, int, int]], a: float) -> Tuple[int, int, int]:
            if src is None:
                return dst
            return (
                int(dst[0] * (1 - a) + src[0] * a),
                int(dst[1] * (1 - a) + src[1] * a),
                int(dst[2] * (1 - a) + src[2] * a),
            )

        for y in range(h):
            for x in range(w):
                c = base[y][x]
                c = blend(c, stars[y][x], 0.65)
                c = blend(c, tree[y][x], 0.92)
                c = blend(c, snow[y][x], 0.80)
                base[y][x] = c
        return base


# ──────────────────────────────────────────────────────────────────────────────
# Terminal model: persistent log + suggestions
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class LogEntry:
    kind: EntryKind
    text: str
    ts_ms: int = field(default_factory=now_ms)


@dataclass
class TerminalModel:
    cfg: AppConfig
    theme: Theme
    cwd: str = field(default_factory=os.getcwd)
    executing: bool = False
    last_status: Optional[int] = None
    last_command: str = ""
    log: List[LogEntry] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    def add(self, kind: EntryKind, text: str) -> None:
        # Keep full output; never auto-clear after commands.
        if not text:
            return
        # Keep text sane.
        if len(text) > self.cfg.max_line_chars:
            text = text[: self.cfg.max_line_chars] + "…"
        self.log.append(LogEntry(kind=kind, text=text))
        if len(self.log) > self.cfg.max_log_lines:
            self.log = self.log[-self.cfg.max_log_lines :]

    def add_lines(self, kind: EntryKind, blob: str) -> None:
        for line in blob.splitlines():
            self.add(kind, line)

    def add_banner(self) -> None:
        self.add(EntryKind.SYSTEM, "Welcome to Brad TUI (Enhanced).")
        self.add(EntryKind.SYSTEM, "Tip: TAB switches focus (input/output). Ctrl+K opens keybinds help.")
        self.add(EntryKind.SYSTEM, f"cwd: {self.cwd}")

    def suggestions_for(self, text: str, limit: int = 6) -> List[str]:
        """
        Anchored suggestions panel (no overlay). This is intentionally simple:
        - command history prefix matches
        - common command typo correction
        """
        s = text.strip()
        if not s:
            return []

        # prefix matches from history (most recent first)
        out: List[str] = []
        seen = set()
        for cmd in reversed(self.history[-300:]):
            if cmd.startswith(s) and cmd not in seen:
                out.append(cmd)
                seen.add(cmd)
                if len(out) >= limit:
                    return out

        # lightweight "autocorrect" for first token
        token = s.split()[0]
        common = [
            "ls",
            "cd",
            "pwd",
            "cat",
            "echo",
            "clear",
            "git status",
            "git log --oneline -n 10",
            "python3 --version",
            "pip --version",
        ]
        import difflib

        matches = difflib.get_close_matches(token, [c.split()[0] for c in common], n=limit, cutoff=0.72)
        for m in matches:
            if m not in seen:
                out.append(m)
                seen.add(m)
                if len(out) >= limit:
                    break
        return out


# ──────────────────────────────────────────────────────────────────────────────
# UI Controls: gradient boxes (per line), output view, background
# ──────────────────────────────────────────────────────────────────────────────


def _entry_palette(theme: Theme, kind: EntryKind) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    if kind == EntryKind.COMMAND:
        return (theme.cmd_bg_a, theme.cmd_bg_b)
    if kind == EntryKind.STDERR:
        return (theme.err_bg_a, theme.err_bg_b)
    if kind == EntryKind.SYSTEM:
        return (theme.sys_bg_a, theme.sys_bg_b)
    return (theme.out_bg_a, theme.out_bg_b)


class GradientLogControl(UIControl):
    """
    Scrollable log viewer that renders every entry as its own "boxed line"
    with a gradient border.
    """

    def __init__(self, model: TerminalModel) -> None:
        self.model = model
        self._get_app: Optional[Callable[[], Application]] = None

    def set_app(self, get_app: Callable[[], Application]) -> None:
        self._get_app = get_app

    def is_focusable(self) -> bool:
        return True

    def _style(self, fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> str:
        return f"fg:{rgb_hex(*fg)} bg:{rgb_hex(*bg)}"

    def _render_line(self, width: int, entry: LogEntry) -> StyleAndTextTuples:
        theme = self.model.theme
        txt = entry.text.replace("\t", "    ")
        txt = txt[: max(0, width - 4)]
        pad = " " * max(0, (width - 4) - len(txt))

        bg_a, bg_b = _entry_palette(theme, entry.kind)
        border_a, border_b = theme.border_a, theme.border_b

        # left border "┃" and right border "┃" with gradient across x
        parts: StyleAndTextTuples = []
        for x in range(width):
            t = x / max(1, width - 1)
            border = lerp_rgb(border_a, border_b, t)
            inside_bg = lerp_rgb(bg_a, bg_b, t)
            if x == 0:
                parts.append((self._style(border, theme.panel_bg), "┃"))
            elif x == width - 1:
                parts.append((self._style(border, theme.panel_bg), "┃"))
            else:
                # entry kind affects fg
                if entry.kind == EntryKind.COMMAND:
                    fg = theme.accent
                elif entry.kind == EntryKind.STDERR:
                    fg = theme.bad
                elif entry.kind == EntryKind.SYSTEM:
                    fg = theme.warn
                else:
                    fg = theme.text
                parts.append((self._style(fg, inside_bg), " "))

        # Inject text over the middle cells (1..width-2)
        content = " " + txt + pad + " "
        # content length should be width-2, we place it starting at x=1
        # We rebuild fragments so styles stay consistent.
        rendered: StyleAndTextTuples = [parts[0]]
        for i, ch in enumerate(content[: max(0, width - 2)]):
            x = i + 1
            t = x / max(1, width - 1)
            inside_bg = lerp_rgb(bg_a, bg_b, t)
            if entry.kind == EntryKind.COMMAND:
                fg = theme.accent
            elif entry.kind == EntryKind.STDERR:
                fg = theme.bad
            elif entry.kind == EntryKind.SYSTEM:
                fg = theme.warn
            else:
                fg = theme.text
            rendered.append((self._style(fg, inside_bg), ch))
        if width >= 2:
            rendered.append(parts[-1])
        return rendered

    def create_content(self, width: int, height: int) -> UIContent:
        # Fit log to visible height; keep newest at bottom.
        entries = self.model.log
        lines = entries[-height:] if height > 0 else []

        def get_line(i: int) -> StyleAndTextTuples:
            if i < 0 or i >= len(lines):
                return [("", "")]
            return self._render_line(width, lines[i])

        return UIContent(get_line=get_line, line_count=len(lines), show_cursor=False)

    def mouse_handler(self, mouse_event) -> None:
        # Let Window handle scrolling with ScrollbarMargin; no special logic.
        return None


class BackgroundControl(UIControl):
    def __init__(self, composer: BackgroundComposer) -> None:
        self.composer = composer
        self._t = time.time()
        self._last = time.time()
        self._cached: List[List[Tuple[int, int, int]]] = []
        self._cache_size: Tuple[int, int] = (0, 0)

    def is_focusable(self) -> bool:
        return False

    def create_content(self, width: int, height: int) -> UIContent:
        t = time.time()
        dt = clamp(t - self._last, 0.0, 0.25)
        self._last = t

        if (width, height) != self._cache_size:
            self._cached = []
            self._cache_size = (width, height)

        if not self._cached:
            self._cached = self.composer.composite(width, height, t, dt)
        else:
            # Always update; but keep this cheap.
            self._cached = self.composer.composite(width, height, t, dt)

        def get_line(y: int) -> StyleAndTextTuples:
            if y < 0 or y >= height:
                return [("", "")]
            row = self._cached[y]
            out: StyleAndTextTuples = []
            for x in range(width):
                c = row[x]
                out.append((f"bg:{rgb_hex(*c)}", " "))
            return out

        return UIContent(get_line=get_line, line_count=height, show_cursor=False)


class SuggestionsControl(UIControl):
    def __init__(self, model: TerminalModel, get_input_text: Callable[[], str]) -> None:
        self.model = model
        self.get_input_text = get_input_text

    def is_focusable(self) -> bool:
        return False

    def create_content(self, width: int, height: int) -> UIContent:
        theme = self.model.theme
        suggestions = self.model.suggestions_for(self.get_input_text(), limit=max(1, height - 2))

        title = " autocorect "
        border_a, border_b = theme.border_a, theme.border_b
        bg = theme.panel_bg_2

        def border_line() -> StyleAndTextTuples:
            out: StyleAndTextTuples = []
            for x in range(width):
                t = x / max(1, width - 1)
                b = lerp_rgb(border_a, border_b, t)
                ch = "━"
                out.append((f"fg:{rgb_hex(*b)} bg:{rgb_hex(*bg)}", ch))
            return out

        def pad_text(s: str) -> str:
            if len(s) > width - 4:
                return s[: width - 5] + "…"
            return s + " " * max(0, (width - 4) - len(s))

        rows: List[StyleAndTextTuples] = []
        # top
        rows.append(border_line())
        # title row
        mid = pad_text(title)
        rows.append(
            [
                (f"fg:{rgb_hex(*theme.muted)} bg:{rgb_hex(*bg)}", "┃ "),
                (f"fg:{rgb_hex(*theme.muted)} bg:{rgb_hex(*bg)}", mid),
                (f"fg:{rgb_hex(*theme.muted)} bg:{rgb_hex(*bg)}", " ┃"),
            ]
        )
        # body
        if suggestions:
            for s in suggestions[: max(0, height - 3)]:
                line = pad_text(s)
                rows.append(
                    [
                        (f"fg:{rgb_hex(*theme.accent)} bg:{rgb_hex(*bg)}", "┃ "),
                        (f"fg:{rgb_hex(*theme.text)} bg:{rgb_hex(*bg)}", line),
                        (f"fg:{rgb_hex(*theme.accent)} bg:{rgb_hex(*bg)}", " ┃"),
                    ]
                )
        else:
            for _ in range(max(0, height - 3)):
                rows.append(
                    [
                        (f"fg:{rgb_hex(*theme.muted)} bg:{rgb_hex(*bg)}", "┃ "),
                        (f"fg:{rgb_hex(*theme.muted)} bg:{rgb_hex(*bg)}", pad_text("")),
                        (f"fg:{rgb_hex(*theme.muted)} bg:{rgb_hex(*bg)}", " ┃"),
                    ]
                )
        # bottom
        rows.append(border_line())

        # normalize to requested height
        rows = rows[:height] + [border_line() for _ in range(max(0, height - len(rows)))]

        def get_line(i: int) -> StyleAndTextTuples:
            if i < 0 or i >= len(rows):
                return [("", "")]
            return rows[i]

        return UIContent(get_line=get_line, line_count=len(rows), show_cursor=False)


# ──────────────────────────────────────────────────────────────────────────────
# Shell runner (async, persistent output)
# ──────────────────────────────────────────────────────────────────────────────


async def _stream_reader(stream: asyncio.StreamReader, cb: Callable[[str], None]) -> None:
    while True:
        line = await stream.readline()
        if not line:
            break
        try:
            s = line.decode(errors="replace").rstrip("\n")
        except Exception:
            s = repr(line)
        cb(s)


async def run_shell_command(model: TerminalModel, cmd: str, refresh: Callable[[], None]) -> int:
    """
    Run a command via /bin/bash -lc, stream stdout/stderr into model log.
    """
    model.executing = True
    model.last_command = cmd
    model.add(EntryKind.COMMAND, f"$ {cmd}")
    refresh()

    if cmd.strip() == "clear":
        # User asked for it explicitly; do not auto-clear elsewhere.
        model.log.clear()
        model.executing = False
        refresh()
        return 0

    proc = await asyncio.create_subprocess_exec(
        "/bin/bash",
        "-lc",
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=model.cwd,
        env=os.environ.copy(),
    )

    assert proc.stdout is not None
    assert proc.stderr is not None

    def on_out(s: str) -> None:
        model.add(EntryKind.STDOUT, s)
        refresh()

    def on_err(s: str) -> None:
        model.add(EntryKind.STDERR, s)
        refresh()

    await asyncio.gather(_stream_reader(proc.stdout, on_out), _stream_reader(proc.stderr, on_err))
    code = await proc.wait()
    model.last_status = code
    model.executing = False
    refresh()
    return code


# ──────────────────────────────────────────────────────────────────────────────
# Application wiring
# ──────────────────────────────────────────────────────────────────────────────


def build_style(theme: Theme) -> Style:
    return Style.from_dict(
        {
            "root": f"bg:{rgb_hex(*theme.bg)} fg:{rgb_hex(*theme.text)}",
            "status": f"bg:{rgb_hex(*theme.panel_bg)} fg:{rgb_hex(*theme.muted)}",
            "menu": f"bg:{rgb_hex(*theme.panel_bg)} fg:{rgb_hex(*theme.text)}",
            "input": f"bg:{rgb_hex(*theme.panel_bg)} fg:{rgb_hex(*theme.text)}",
            # prompt_toolkit cursor uses the global "cursor" style.
            "cursor": f"bg:{rgb_hex(*theme.cursor_bg)} fg:{rgb_hex(*theme.cursor_fg)}",
            "selection": f"bg:{rgb_hex(*theme.panel_bg_2)} fg:{rgb_hex(*theme.text)}",
        }
    )


def main() -> None:
    cfg = AppConfig()
    theme = Theme()
    model = TerminalModel(cfg=cfg, theme=theme)
    model.add_banner()

    composer = BackgroundComposer(cfg, theme)
    background = Window(content=BackgroundControl(composer), style="root")

    # Output: custom log control with gradient "box per line"
    log_control = GradientLogControl(model)
    output_window = Window(
        content=log_control,
        style="root",
        right_margins=[ScrollbarMargin(display_arrows=True)],
        always_hide_cursor=True,
        wrap_lines=False,
    )

    # Input
    input_buffer = Buffer()
    input_area = TextArea(
        height=1,
        prompt="> ",
        style="class:input",
        multiline=False,
        wrap_lines=False,
        scrollbar=False,
        focusable=True,
        buffer=input_buffer,
    )

    # Suggestions bottom-right, anchored (never overlays typing)
    suggestions = Window(
        content=SuggestionsControl(model, get_input_text=lambda: input_buffer.text),
        width=D(preferred=38, min=26),
        height=D(preferred=7, min=5),
        style="root",
        dont_extend_width=True,
        dont_extend_height=True,
    )

    # Menu bar (persistent; hidden only during command execution)
    def menu_text() -> StyleAndTextTuples:
        items = [
            ("F2", "bg toggle"),
            ("TAB", "switch focus"),
            ("Ctrl+K", "keybinds"),
            ("Ctrl+C", "quit"),
        ]
        segs: StyleAndTextTuples = []
        segs.append(("class:menu", "  Brad TUI  "))
        for k, v in items:
            segs.append(("class:menu", f"[{k}] "))
            segs.append(("class:menu", f"{v}   "))
        return segs

    # Utility/status bar (always visible, dynamic)
    class StatusRowControl(UIControl):
        def is_focusable(self) -> bool:
            return False

        def create_content(self, width: int, height: int) -> UIContent:
            if height <= 0:
                return UIContent(get_line=lambda _: [("", "")], line_count=0)

            def get_line(_: int) -> StyleAndTextTuples:
                cwd = model.cwd
                status = "RUNNING" if model.executing else "IDLE"
                code = "" if model.last_status is None else f" exit={model.last_status}"
                right = f"{status}{code}"
                left = f"cwd: {cwd}"
                s = f" {left}    {right} "
                if len(s) < width:
                    s = s + (" " * (width - len(s)))
                else:
                    s = s[:width]
                return [("class:status", s)]

            return UIContent(get_line=get_line, line_count=1, show_cursor=False)

    status_bar = Window(height=1, content=StatusRowControl(), style="class:status", dont_extend_height=True)

    # Body is the persistent log. Suggestions are anchored as a bottom-right float.
    body = output_window

    # We'll render the top row dynamically to avoid layout "jumping".
    class MenuRowControl(UIControl):
        def is_focusable(self) -> bool:
            return False

        def create_content(self, width: int, height: int) -> UIContent:
            if height <= 0:
                return UIContent(get_line=lambda _: [("", "")], line_count=0)

            def get_line(_: int) -> StyleAndTextTuples:
                if model.executing:
                    return [("class:menu", " " * width)]
                # pad menu to width
                raw = menu_text()
                plain = "".join(t for _, t in raw)
                if len(plain) < width:
                    raw = raw + [("class:menu", " " * (width - len(plain)))]
                else:
                    raw = [("class:menu", plain[:width])]
                return raw

            return UIContent(get_line=get_line, line_count=1, show_cursor=False)

    menu_row = Window(height=1, content=MenuRowControl(), style="class:menu", dont_extend_height=True)

    foreground = HSplit(
        [
            menu_row,
            body,
            input_area,
            status_bar,
        ],
        padding=0,
    )

    container = FloatContainer(
        content=background,
        floats=[
            Float(content=foreground),
            # Autocorrect panel pinned near the utility bar (bottom-right).
            Float(content=suggestions, right=1, bottom=2),
        ],
    )

    kb = KeyBindings()

    def refresh(app: Application) -> None:
        # fast refresh without clearing output; prompt_toolkit handles diffs.
        app.invalidate()

    @kb.add("c-c")
    def _(event) -> None:
        event.app.exit()

    @kb.add("tab")
    def _(event) -> None:
        event.app.layout.focus_next()

    @kb.add("s-tab")
    def _(event) -> None:
        event.app.layout.focus_previous()

    @kb.add("f2")
    def _(event) -> None:
        cfg.show_background = not cfg.show_background
        model.add(EntryKind.SYSTEM, f"background: {'on' if cfg.show_background else 'off'}")
        refresh(event.app)

    @kb.add("c-k")
    def _(event) -> None:
        model.add(EntryKind.SYSTEM, "Keybinds: TAB focus | F2 bg | Ctrl+L clear | Ctrl+C quit | PgUp/PgDn scroll")
        refresh(event.app)

    @kb.add("c-l")
    def _(event) -> None:
        model.log.clear()
        model.add(EntryKind.SYSTEM, "cleared.")
        refresh(event.app)

    async def accept_command() -> None:
        cmd = input_buffer.text
        input_buffer.text = ""
        cmd = cmd.rstrip()
        if not cmd:
            return
        model.history.append(cmd)
        if cmd.startswith("cd "):
            # Built-in cd so cwd persists across commands.
            target = cmd[3:].strip()
            target = os.path.expanduser(target)
            if not os.path.isabs(target):
                target = os.path.join(model.cwd, target)
            try:
                os.chdir(target)
                model.cwd = os.getcwd()
                model.add(EntryKind.SYSTEM, f"cwd -> {model.cwd}")
            except Exception as e:
                model.add(EntryKind.STDERR, f"cd: {e}")
            return

        await run_shell_command(model, cmd, refresh=lambda: refresh(app))

    @kb.add("enter")
    def _(event) -> None:
        if model.executing:
            return
        # Only accept if focus is in input.
        if event.app.layout.current_control == input_area.control:
            event.app.create_background_task(accept_command())
        else:
            # If user hits enter in output pane, focus input.
            event.app.layout.focus(input_area)

    # Scroll helpers for output pane (cursor movement through text)
    @kb.add("pageup")
    def _(event) -> None:
        if event.app.layout.current_control == output_window.content:
            output_window.vertical_scroll = max(0, output_window.vertical_scroll + 5)
            refresh(event.app)

    @kb.add("pagedown")
    def _(event) -> None:
        if event.app.layout.current_control == output_window.content:
            output_window.vertical_scroll = max(0, output_window.vertical_scroll - 5)
            refresh(event.app)

    @kb.add("home")
    def _(event) -> None:
        if event.app.layout.current_control == output_window.content:
            output_window.vertical_scroll = 10**9
            refresh(event.app)

    @kb.add("end")
    def _(event) -> None:
        if event.app.layout.current_control == output_window.content:
            output_window.vertical_scroll = 0
            refresh(event.app)

    style = build_style(theme)

    # Build app
    app = Application(
        layout=Layout(container, focused_element=input_area),
        key_bindings=kb,
        mouse_support=True,
        full_screen=True,
        style=style,
        refresh_interval=1.0 / max(5, cfg.fps),
    )

    log_control.set_app(lambda: app)

    # Proper signal handling; do not clear screen (tmux-friendly).
    def _sig_exit(*_args) -> None:
        try:
            app.exit()
        except Exception:
            raise SystemExit(0)

    signal.signal(signal.SIGTERM, _sig_exit)
    signal.signal(signal.SIGINT, _sig_exit)

    app.run()


if __name__ == "__main__":
    main()
