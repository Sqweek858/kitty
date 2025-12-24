#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     CONFIGURATION MANAGEMENT                                 ║
║                  User Configuration and Preferences                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module handles user configuration, themes, and preferences.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from terminal_core import RenderQuality


# ═══════════════════════════════════════════════════════════════════════════════
# THEME DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThemeColors:
    """Color scheme for a theme"""
    # UI Colors
    menu_gradient: str = "cyberpunk"
    output_gradient: str = "cyberpunk"
    input_gradient: str = "christmas"
    status_gradient: str = "cyberpunk"
    
    # Text Colors
    command_color: tuple = (100, 200, 255)
    output_color: tuple = (200, 200, 200)
    error_color: tuple = (255, 100, 100)
    success_color: tuple = (100, 255, 100)
    warning_color: tuple = (255, 200, 100)
    
    # Graphics
    background_color: tuple = (5, 8, 12)


# Predefined themes
THEMES = {
    "cyberpunk": ThemeColors(
        menu_gradient="cyberpunk",
        output_gradient="cyberpunk",
        input_gradient="cyberpunk",
        status_gradient="cyberpunk",
    ),
    "christmas": ThemeColors(
        menu_gradient="christmas",
        output_gradient="fire",
        input_gradient="christmas",
        status_gradient="christmas",
    ),
    "matrix": ThemeColors(
        menu_gradient="matrix",
        output_gradient="matrix",
        input_gradient="matrix",
        status_gradient="matrix",
        command_color=(0, 255, 0),
        output_color=(0, 200, 0),
        error_color=(255, 0, 0),
        success_color=(0, 255, 100),
    ),
    "ice": ThemeColors(
        menu_gradient="ice",
        output_gradient="ice",
        input_gradient="ice",
        status_gradient="ice",
        command_color=(100, 200, 255),
        output_color=(200, 220, 255),
    ),
    "fire": ThemeColors(
        menu_gradient="fire",
        output_gradient="fire",
        input_gradient="fire",
        status_gradient="fire",
        command_color=(255, 200, 100),
        output_color=(255, 220, 180),
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# USER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UserConfig:
    """User configuration settings"""
    # Appearance
    theme: str = "cyberpunk"
    render_quality: str = "ULTRA"
    target_fps: int = 60
    show_fps: bool = False
    
    # Graphics
    enable_parallax: bool = True
    enable_tree: bool = True
    enable_snow: bool = True
    enable_sparkles: bool = True
    particle_count: int = 200
    
    # Terminal
    max_history: int = 1000
    max_output_lines: int = 10000
    auto_scroll: bool = True
    show_timestamps: bool = False
    
    # Input
    cursor_blink_rate: float = 0.5
    tab_width: int = 4
    
    # Keybindings (can be customized)
    keybindings: Dict[str, str] = None
    
    def __post_init__(self):
        if self.keybindings is None:
            self.keybindings = {}


class ConfigManager:
    """Manages user configuration"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            self.config_dir = Path.home() / ".config" / "cyberpunk_terminal"
        else:
            self.config_dir = config_dir
        
        self.config_file = self.config_dir / "config.json"
        self.config = UserConfig()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> UserConfig:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                    # Update config with loaded data
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        return self.config
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_theme(self) -> ThemeColors:
        """Get current theme colors"""
        return THEMES.get(self.config.theme, THEMES["cyberpunk"])
    
    def set_theme(self, theme_name: str):
        """Set theme"""
        if theme_name in THEMES:
            self.config.theme = theme_name
            self.save()
    
    def get_render_quality(self) -> RenderQuality:
        """Get render quality enum"""
        quality_map = {
            "LOW": RenderQuality.LOW,
            "MEDIUM": RenderQuality.MEDIUM,
            "HIGH": RenderQuality.HIGH,
            "ULTRA": RenderQuality.ULTRA,
            "INSANE": RenderQuality.INSANE,
        }
        return quality_map.get(self.config.render_quality, RenderQuality.ULTRA)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'ThemeColors', 'THEMES',
    'UserConfig', 'ConfigManager',
]
