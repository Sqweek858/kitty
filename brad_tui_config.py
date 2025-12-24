#!/usr/bin/env python3
"""
Brad TUI Ultra - Configuration Management Module
================================================

This module handles all configuration loading, saving, and validation for Brad TUI Ultra.
Supports TOML, JSON, and YAML configuration files with schema validation and defaults.

Features:
- Multi-format support (TOML, JSON, YAML)
- Schema validation
- Environment variable overrides
- Live configuration reloading
- Configuration migration
- Theme management
- Plugin configuration
- Performance profiling integration
"""

import os
import sys
import json
import re
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import copy


# =============================================================================
# CONFIGURATION SCHEMA
# =============================================================================

class ConfigFormat(Enum):
    """Supported configuration formats"""
    TOML = "toml"
    JSON = "json"
    YAML = "yaml"
    ENV = "env"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BorderStyle(Enum):
    """Border rendering styles"""
    NONE = "none"
    SIMPLE = "simple"
    DOUBLE = "double"
    ROUNDED = "rounded"
    GRADIENT = "gradient"
    RAINBOW = "rainbow"


class Theme(Enum):
    """Available themes"""
    CYBERPUNK_CHRISTMAS = "cyberpunk_christmas"
    CLASSIC = "classic"
    MATRIX = "matrix"
    OCEAN = "ocean"
    SUNSET = "sunset"
    NORD = "nord"
    DRACULA = "dracula"
    GRUVBOX = "gruvbox"
    SOLARIZED_LIGHT = "solarized_light"
    SOLARIZED_DARK = "solarized_dark"
    MONOKAI = "monokai"
    ONE_DARK = "one_dark"
    TOKYO_NIGHT = "tokyo_night"


# =============================================================================
# CONFIGURATION DATA CLASSES
# =============================================================================

@dataclass
class GeneralConfig:
    """General application configuration"""
    theme: str = "cyberpunk_christmas"
    fps: int = 30
    log_level: str = "INFO"
    log_file: str = "~/.cache/brad_tui/logs/brad_tui_ultra.log"
    config_watch: bool = True
    auto_save: bool = True
    backup_config: bool = True
    language: str = "en"
    timezone: str = "UTC"


@dataclass
class FeaturesConfig:
    """Feature toggles"""
    parallax: bool = True
    tree: bool = True
    snow: bool = True
    welcome: bool = True
    menu: bool = True
    autocorrect: bool = True
    syntax_highlight: bool = True
    auto_complete: bool = True
    command_history: bool = True
    shortcuts: bool = True
    animations: bool = True
    sounds: bool = False
    notifications: bool = True


@dataclass
class ParallaxConfig:
    """Parallax effect configuration"""
    stars: int = 200
    layers: int = 3
    speed_multiplier: float = 1.0
    twinkle: bool = True
    twinkle_speed: float = 0.5
    color_variation: bool = True
    depth_blur: bool = False
    star_shapes: List[str] = field(default_factory=lambda: [".", "*", "+", "·"])


@dataclass
class TreeConfig:
    """Christmas tree configuration"""
    height: int = 20
    lights: int = 50
    animation_speed: float = 1.0
    sway_enabled: bool = True
    sway_amount: float = 0.3
    light_colors: List[str] = field(default_factory=lambda: [
        "red", "green", "blue", "yellow", "cyan", "magenta", "white"
    ])
    ornaments: bool = True
    star_on_top: bool = True
    presents: bool = True


@dataclass
class SnowConfig:
    """Snow effect configuration"""
    flakes: int = 100
    wind: float = 0.3
    gravity: float = 0.5
    accumulation: bool = False
    melt: bool = False
    flake_chars: List[str] = field(default_factory=lambda: ["❄", "❅", "❆", "*", "·"])


@dataclass
class UIConfig:
    """UI layout configuration"""
    menu_height: int = 1
    status_height: int = 1
    autocorrect_height: int = 5
    border_style: str = "gradient"
    padding: int = 1
    margin: int = 0
    min_width: int = 80
    min_height: int = 24
    max_output_lines: int = 1000
    scroll_speed: int = 3
    cursor_blink: bool = True
    cursor_shape: str = "block"  # block, underline, bar


@dataclass
class ColorConfig:
    """Color theme configuration"""
    background: List[int] = field(default_factory=lambda: [8, 10, 14])
    foreground: List[int] = field(default_factory=lambda: [180, 200, 255])
    accent: List[int] = field(default_factory=lambda: [0, 255, 255])
    success: List[int] = field(default_factory=lambda: [0, 255, 100])
    warning: List[int] = field(default_factory=lambda: [255, 200, 0])
    error: List[int] = field(default_factory=lambda: [255, 50, 50])
    info: List[int] = field(default_factory=lambda: [100, 150, 255])
    menu_bg: List[int] = field(default_factory=lambda: [15, 20, 30])
    menu_fg: List[int] = field(default_factory=lambda: [0, 255, 255])
    input_bg: List[int] = field(default_factory=lambda: [10, 15, 25])
    input_fg: List[int] = field(default_factory=lambda: [200, 220, 255])
    output_bg: List[int] = field(default_factory=lambda: [5, 8, 12])
    output_fg: List[int] = field(default_factory=lambda: [180, 200, 255])
    border_color_1: List[int] = field(default_factory=lambda: [255, 0, 100])
    border_color_2: List[int] = field(default_factory=lambda: [0, 200, 255])
    cursor: List[int] = field(default_factory=lambda: [0, 255, 255])
    selection: List[int] = field(default_factory=lambda: [50, 100, 150])


@dataclass
class KeybindingsConfig:
    """Keybinding configuration"""
    exit: List[str] = field(default_factory=lambda: ["ctrl+c", "ctrl+d"])
    clear: List[str] = field(default_factory=lambda: ["ctrl+l", "f4"])
    help: List[str] = field(default_factory=lambda: ["f1"])
    history: List[str] = field(default_factory=lambda: ["f3"])
    toggle_parallax: List[str] = field(default_factory=lambda: ["f5"])
    toggle_tree: List[str] = field(default_factory=lambda: ["f6"])
    toggle_snow: List[str] = field(default_factory=lambda: ["f7"])
    toggle_menu: List[str] = field(default_factory=lambda: ["f8"])
    autocomplete: List[str] = field(default_factory=lambda: ["tab"])
    cancel: List[str] = field(default_factory=lambda: ["esc"])


@dataclass
class PerformanceConfig:
    """Performance tuning configuration"""
    preset: str = "medium"  # low, medium, high, ultra
    frame_skip: bool = False
    lazy_render: bool = True
    cache_enabled: bool = True
    cache_size: int = 100
    async_rendering: bool = True
    thread_pool_size: int = 4
    max_fps: int = 60
    vsync: bool = False


@dataclass
class PluginConfig:
    """Plugin system configuration"""
    enabled: bool = True
    plugin_dir: str = "~/.config/brad_tui/plugins"
    auto_load: bool = True
    safe_mode: bool = True
    allowed_plugins: List[str] = field(default_factory=list)
    blocked_plugins: List[str] = field(default_factory=list)


@dataclass
class Config:
    """Main configuration container"""
    general: GeneralConfig = field(default_factory=GeneralConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    parallax: ParallaxConfig = field(default_factory=ParallaxConfig)
    tree: TreeConfig = field(default_factory=TreeConfig)
    snow: SnowConfig = field(default_factory=SnowConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    colors: ColorConfig = field(default_factory=ColorConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)


# =============================================================================
# CONFIGURATION MANAGER
# =============================================================================

class ConfigManager:
    """
    Configuration manager for Brad TUI Ultra
    
    Handles loading, saving, validation, and live reloading of configuration files.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = self._resolve_config_path(config_path)
        self.config = Config()
        self.callbacks: List[Callable] = []
        self.watchers: Dict[str, Any] = {}
        self._load_config()
        self._apply_env_overrides()
    
    def _resolve_config_path(self, config_path: Optional[str]) -> Path:
        """Resolve configuration file path"""
        if config_path:
            return Path(config_path).expanduser().resolve()
        
        # Try standard locations
        locations = [
            "~/.config/brad_tui/config.toml",
            "~/.config/brad_tui/config.json",
            "~/.config/brad_tui/config.yaml",
            "~/.brad_tui.toml",
            "~/.brad_tui.json",
        ]
        
        for loc in locations:
            path = Path(loc).expanduser()
            if path.exists():
                return path
        
        # Default to TOML
        return Path("~/.config/brad_tui/config.toml").expanduser()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            # Create default config
            self._save_config()
            return
        
        try:
            format_type = self._detect_format(self.config_path)
            
            if format_type == ConfigFormat.TOML:
                self._load_toml()
            elif format_type == ConfigFormat.JSON:
                self._load_json()
            elif format_type == ConfigFormat.YAML:
                self._load_yaml()
            else:
                raise ValueError(f"Unsupported config format: {format_type}")
                
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
    
    def _detect_format(self, path: Path) -> ConfigFormat:
        """Detect configuration file format"""
        suffix = path.suffix.lower()
        
        if suffix in ['.toml', '.tml']:
            return ConfigFormat.TOML
        elif suffix in ['.json', '.js']:
            return ConfigFormat.JSON
        elif suffix in ['.yaml', '.yml']:
            return ConfigFormat.YAML
        else:
            # Try to detect from content
            try:
                with open(path, 'r') as f:
                    content = f.read().strip()
                    if content.startswith('{'):
                        return ConfigFormat.JSON
                    elif content.startswith('[') and '=' in content:
                        return ConfigFormat.TOML
                    else:
                        return ConfigFormat.YAML
            except:
                return ConfigFormat.TOML
    
    def _load_toml(self) -> None:
        """Load TOML configuration"""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print("TOML support requires tomllib (Python 3.11+) or tomli")
                return
        
        with open(self.config_path, 'rb') as f:
            data = tomllib.load(f)
            self._apply_config_dict(data)
    
    def _load_json(self) -> None:
        """Load JSON configuration"""
        with open(self.config_path, 'r') as f:
            data = json.load(f)
            self._apply_config_dict(data)
    
    def _load_yaml(self) -> None:
        """Load YAML configuration"""
        try:
            import yaml
        except ImportError:
            print("YAML support requires PyYAML: pip install pyyaml")
            return
        
        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)
            self._apply_config_dict(data)
    
    def _apply_config_dict(self, data: Dict[str, Any]) -> None:
        """Apply configuration dictionary to config object"""
        for section, values in data.items():
            if hasattr(self.config, section):
                section_obj = getattr(self.config, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        env_prefix = "BRAD_TUI_"
        
        # Map of environment variables to config paths
        env_map = {
            'THEME': ('general', 'theme'),
            'FPS': ('general', 'fps'),
            'PARALLAX_STARS': ('parallax', 'stars'),
            'SNOWFLAKES': ('snow', 'flakes'),
            'ENABLE_PARALLAX': ('features', 'parallax'),
            'ENABLE_TREE': ('features', 'tree'),
            'ENABLE_SNOW': ('features', 'snow'),
            'ENABLE_WELCOME': ('features', 'welcome'),
            'ENABLE_MENU': ('features', 'menu'),
            'ENABLE_AUTOCORRECT': ('features', 'autocorrect'),
        }
        
        for env_key, (section, attr) in env_map.items():
            env_var = env_prefix + env_key
            value = os.environ.get(env_var)
            
            if value is not None:
                section_obj = getattr(self.config, section)
                current_value = getattr(section_obj, attr)
                
                # Convert value to appropriate type
                if isinstance(current_value, bool):
                    value = value.lower() in ['1', 'true', 'yes', 'on']
                elif isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, float):
                    value = float(value)
                
                setattr(section_obj, attr, value)
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config.general.backup_config and self.config_path.exists():
            backup_path = self.config_path.with_suffix(
                self.config_path.suffix + '.backup'
            )
            import shutil
            shutil.copy2(self.config_path, backup_path)
        
        # Convert config to dictionary
        config_dict = self._config_to_dict()
        
        # Save in appropriate format
        format_type = self._detect_format(self.config_path)
        
        if format_type == ConfigFormat.TOML:
            self._save_toml(config_dict)
        elif format_type == ConfigFormat.JSON:
            self._save_json(config_dict)
        elif format_type == ConfigFormat.YAML:
            self._save_yaml(config_dict)
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert config object to dictionary"""
        return {
            'general': asdict(self.config.general),
            'features': asdict(self.config.features),
            'parallax': asdict(self.config.parallax),
            'tree': asdict(self.config.tree),
            'snow': asdict(self.config.snow),
            'ui': asdict(self.config.ui),
            'colors': asdict(self.config.colors),
            'keybindings': asdict(self.config.keybindings),
            'performance': asdict(self.config.performance),
            'plugins': asdict(self.config.plugins),
        }
    
    def _save_toml(self, data: Dict[str, Any]) -> None:
        """Save as TOML"""
        try:
            import tomli_w
        except ImportError:
            print("TOML writing requires tomli-w: pip install tomli-w")
            return
        
        with open(self.config_path, 'wb') as f:
            tomli_w.dump(data, f)
    
    def _save_json(self, data: Dict[str, Any]) -> None:
        """Save as JSON"""
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_yaml(self, data: Dict[str, Any]) -> None:
        """Save as YAML"""
        try:
            import yaml
        except ImportError:
            print("YAML support requires PyYAML: pip install pyyaml")
            return
        
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by path
        
        Example: config.get('general.theme')
        """
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any, save: bool = True) -> None:
        """
        Set configuration value by path
        
        Example: config.set('general.theme', 'matrix')
        """
        parts = path.split('.')
        obj = self.config
        
        # Navigate to parent
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise ValueError(f"Invalid config path: {path}")
        
        # Set value
        attr = parts[-1]
        if hasattr(obj, attr):
            setattr(obj, attr, value)
            
            if save and self.config.general.auto_save:
                self._save_config()
            
            # Notify callbacks
            self._notify_callbacks(path, value)
        else:
            raise ValueError(f"Invalid config attribute: {attr}")
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback for configuration changes"""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, path: str, value: Any) -> None:
        """Notify all registered callbacks of configuration change"""
        for callback in self.callbacks:
            try:
                callback(path, value)
            except Exception as e:
                print(f"Error in config callback: {e}")
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
        self._apply_env_overrides()
        self._notify_callbacks('*', None)
    
    def save(self) -> None:
        """Save current configuration"""
        self._save_config()
    
    def reset(self, section: Optional[str] = None) -> None:
        """Reset configuration to defaults"""
        if section is None:
            self.config = Config()
        else:
            if hasattr(self.config, section):
                # Get default for section
                default_config = Config()
                setattr(
                    self.config,
                    section,
                    getattr(default_config, section)
                )
        
        if self.config.general.auto_save:
            self._save_config()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate FPS
        if not (1 <= self.config.general.fps <= 120):
            errors.append("FPS must be between 1 and 120")
        
        # Validate parallax stars
        if not (0 <= self.config.parallax.stars <= 1000):
            errors.append("Parallax stars must be between 0 and 1000")
        
        # Validate snowflakes
        if not (0 <= self.config.snow.flakes <= 500):
            errors.append("Snowflakes must be between 0 and 500")
        
        # Validate colors (RGB values)
        color_attrs = [
            'background', 'foreground', 'accent', 'success',
            'warning', 'error', 'info'
        ]
        
        for attr in color_attrs:
            color = getattr(self.config.colors, attr)
            if not isinstance(color, list) or len(color) != 3:
                errors.append(f"Color {attr} must be [R, G, B] list")
            elif not all(0 <= c <= 255 for c in color):
                errors.append(f"Color {attr} values must be 0-255")
        
        # Validate UI dimensions
        if self.config.ui.min_width < 40:
            errors.append("Minimum width must be at least 40")
        
        if self.config.ui.min_height < 10:
            errors.append("Minimum height must be at least 10")
        
        return errors
    
    def export_json(self) -> str:
        """Export configuration as JSON string"""
        return json.dumps(self._config_to_dict(), indent=2)
    
    def import_json(self, json_str: str) -> None:
        """Import configuration from JSON string"""
        data = json.loads(json_str)
        self._apply_config_dict(data)
    
    def merge(self, other_config: Union['Config', Dict[str, Any]]) -> None:
        """Merge another configuration into this one"""
        if isinstance(other_config, dict):
            self._apply_config_dict(other_config)
        elif isinstance(other_config, Config):
            self._apply_config_dict(self._config_to_dict())


# =============================================================================
# THEME MANAGER
# =============================================================================

class ThemeManager:
    """Manage color themes for Brad TUI Ultra"""
    
    THEMES = {
        'cyberpunk_christmas': ColorConfig(
            background=[8, 10, 14],
            foreground=[180, 200, 255],
            accent=[0, 255, 255],
            success=[0, 255, 100],
            warning=[255, 200, 0],
            error=[255, 50, 50],
            border_color_1=[255, 0, 100],
            border_color_2=[0, 200, 255],
        ),
        'matrix': ColorConfig(
            background=[0, 0, 0],
            foreground=[0, 255, 0],
            accent=[0, 255, 0],
            success=[0, 255, 0],
            warning=[255, 255, 0],
            error=[255, 0, 0],
            border_color_1=[0, 255, 0],
            border_color_2=[0, 200, 0],
        ),
        'ocean': ColorConfig(
            background=[10, 20, 40],
            foreground=[200, 220, 255],
            accent=[0, 150, 255],
            success=[0, 200, 200],
            warning=[255, 180, 0],
            error=[255, 100, 100],
            border_color_1=[0, 100, 200],
            border_color_2=[0, 200, 255],
        ),
        'dracula': ColorConfig(
            background=[40, 42, 54],
            foreground=[248, 248, 242],
            accent=[255, 121, 198],
            success=[80, 250, 123],
            warning=[241, 250, 140],
            error=[255, 85, 85],
            border_color_1=[189, 147, 249],
            border_color_2=[255, 121, 198],
        ),
    }
    
    @classmethod
    def get_theme(cls, name: str) -> Optional[ColorConfig]:
        """Get theme by name"""
        return copy.deepcopy(cls.THEMES.get(name))
    
    @classmethod
    def list_themes(cls) -> List[str]:
        """List available themes"""
        return list(cls.THEMES.keys())


# =============================================================================
# GLOBAL CONFIGURATION INSTANCE
# =============================================================================

_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config


def reload_config() -> None:
    """Reload global configuration"""
    global _global_config
    if _global_config is not None:
        _global_config.reload()


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - Configuration Module")
    print("=" * 50)
    
    # Create config manager
    config = get_config()
    
    # Display current configuration
    print(f"Theme: {config.config.general.theme}")
    print(f"FPS: {config.config.general.fps}")
    print(f"Parallax enabled: {config.config.features.parallax}")
    print(f"Stars: {config.config.parallax.stars}")
    
    # Validate
    errors = config.validate()
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration is valid")
    
    # List themes
    print("\nAvailable themes:")
    for theme in ThemeManager.list_themes():
        print(f"  - {theme}")
    
    # Save config
    print(f"\nConfiguration saved to: {config.config_path}")
    config.save()
