#!/usr/bin/env python3
"""
Brad TUI Ultra - Theme Management Module
========================================

Comprehensive theme system with color schemes, fonts, borders, and visual styles.
Includes built-in themes and support for custom theme creation.

Features:
- Pre-defined color themes
- Custom theme creation and import/export
- Color manipulation utilities
- Dynamic theme switching
- Theme inheritance
- Color palette generation
- Accessibility features (contrast checking)
"""

import json
import colorsys
import math
from typing import Tuple, List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


# =============================================================================
# COLOR UTILITIES
# =============================================================================

class ColorUtils:
    """Utilities for color manipulation and conversion"""
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB to hex color string"""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV"""
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    
    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)
    
    @staticmethod
    def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSL"""
        return colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    
    @staticmethod
    def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
        """Convert HSL to RGB"""
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)
    
    @staticmethod
    def interpolate_rgb(
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        t: float
    ) -> Tuple[int, int, int]:
        """Interpolate between two RGB colors"""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )
    
    @staticmethod
    def lighten(color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        """Lighten a color by amount (0.0 to 1.0)"""
        h, s, v = ColorUtils.rgb_to_hsv(*color)
        v = min(1.0, v + amount)
        return ColorUtils.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def darken(color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        """Darken a color by amount (0.0 to 1.0)"""
        h, s, v = ColorUtils.rgb_to_hsv(*color)
        v = max(0.0, v - amount)
        return ColorUtils.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def saturate(color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        """Increase saturation by amount"""
        h, s, v = ColorUtils.rgb_to_hsv(*color)
        s = min(1.0, s + amount)
        return ColorUtils.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def desaturate(color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        """Decrease saturation by amount"""
        h, s, v = ColorUtils.rgb_to_hsv(*color)
        s = max(0.0, s - amount)
        return ColorUtils.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def rotate_hue(color: Tuple[int, int, int], degrees: float) -> Tuple[int, int, int]:
        """Rotate hue by degrees"""
        h, s, v = ColorUtils.rgb_to_hsv(*color)
        h = (h + degrees / 360.0) % 1.0
        return ColorUtils.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def complementary(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get complementary color"""
        return ColorUtils.rotate_hue(color, 180)
    
    @staticmethod
    def triadic(color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get triadic color scheme"""
        return [
            color,
            ColorUtils.rotate_hue(color, 120),
            ColorUtils.rotate_hue(color, 240),
        ]
    
    @staticmethod
    def analogous(color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get analogous color scheme"""
        return [
            ColorUtils.rotate_hue(color, -30),
            color,
            ColorUtils.rotate_hue(color, 30),
        ]
    
    @staticmethod
    def split_complementary(color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get split-complementary color scheme"""
        return [
            color,
            ColorUtils.rotate_hue(color, 150),
            ColorUtils.rotate_hue(color, 210),
        ]
    
    @staticmethod
    def luminance(color: Tuple[int, int, int]) -> float:
        """Calculate relative luminance (0.0 to 1.0)"""
        r, g, b = [x / 255.0 for x in color]
        
        # Apply gamma correction
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate contrast ratio between two colors (WCAG)"""
        lum1 = ColorUtils.luminance(color1)
        lum2 = ColorUtils.luminance(color2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def meets_wcag_aa(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> bool:
        """Check if color pair meets WCAG AA standard (4.5:1)"""
        return ColorUtils.contrast_ratio(color1, color2) >= 4.5
    
    @staticmethod
    def meets_wcag_aaa(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> bool:
        """Check if color pair meets WCAG AAA standard (7:1)"""
        return ColorUtils.contrast_ratio(color1, color2) >= 7.0
    
    @staticmethod
    def generate_gradient(
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        steps: int
    ) -> List[Tuple[int, int, int]]:
        """Generate color gradient"""
        gradient = []
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            gradient.append(ColorUtils.interpolate_rgb(color1, color2, t))
        return gradient


# =============================================================================
# THEME DATA STRUCTURES
# =============================================================================

@dataclass
class ColorScheme:
    """Color scheme definition"""
    # Base colors
    background: Tuple[int, int, int] = (8, 10, 14)
    foreground: Tuple[int, int, int] = (180, 200, 255)
    
    # UI element colors
    primary: Tuple[int, int, int] = (0, 255, 255)
    secondary: Tuple[int, int, int] = (255, 0, 100)
    accent: Tuple[int, int, int] = (0, 255, 255)
    
    # Semantic colors
    success: Tuple[int, int, int] = (0, 255, 100)
    warning: Tuple[int, int, int] = (255, 200, 0)
    error: Tuple[int, int, int] = (255, 50, 50)
    info: Tuple[int, int, int] = (100, 150, 255)
    
    # UI components
    menu_bg: Tuple[int, int, int] = (15, 20, 30)
    menu_fg: Tuple[int, int, int] = (0, 255, 255)
    input_bg: Tuple[int, int, int] = (10, 15, 25)
    input_fg: Tuple[int, int, int] = (200, 220, 255)
    output_bg: Tuple[int, int, int] = (5, 8, 12)
    output_fg: Tuple[int, int, int] = (180, 200, 255)
    
    # Interactive states
    hover: Tuple[int, int, int] = (50, 100, 150)
    active: Tuple[int, int, int] = (100, 150, 200)
    disabled: Tuple[int, int, int] = (50, 50, 50)
    
    # Border and shadow
    border: Tuple[int, int, int] = (255, 0, 100)
    border_secondary: Tuple[int, int, int] = (0, 200, 255)
    shadow: Tuple[int, int, int] = (0, 0, 0)
    
    # Special effects
    glow: Tuple[int, int, int] = (0, 255, 255)
    cursor: Tuple[int, int, int] = (0, 255, 255)
    selection: Tuple[int, int, int] = (50, 100, 150)
    
    # Syntax highlighting (for code display)
    syntax_keyword: Tuple[int, int, int] = (255, 100, 200)
    syntax_string: Tuple[int, int, int] = (100, 255, 100)
    syntax_number: Tuple[int, int, int] = (255, 200, 100)
    syntax_comment: Tuple[int, int, int] = (100, 100, 100)
    syntax_function: Tuple[int, int, int] = (100, 200, 255)
    syntax_variable: Tuple[int, int, int] = (200, 200, 255)


@dataclass
class BorderStyle:
    """Border styling configuration"""
    type: str = "gradient"  # none, simple, double, rounded, gradient, rainbow
    characters: Dict[str, str] = field(default_factory=lambda: {
        'top_left': '╭',
        'top_right': '╮',
        'bottom_left': '╰',
        'bottom_right': '╯',
        'horizontal': '─',
        'vertical': '│',
    })
    thickness: int = 1
    padding: int = 1
    margin: int = 0


@dataclass
class TypographyStyle:
    """Typography configuration"""
    font_family: str = "monospace"
    font_size: int = 14
    line_height: float = 1.5
    letter_spacing: float = 0.0
    bold: bool = False
    italic: bool = False
    underline: bool = False


@dataclass
class Theme:
    """Complete theme definition"""
    # Metadata
    name: str = "Default"
    author: str = "Brad TUI Team"
    description: str = "Default theme"
    version: str = "1.0.0"
    
    # Color scheme
    colors: ColorScheme = field(default_factory=ColorScheme)
    
    # Visual styles
    border: BorderStyle = field(default_factory=BorderStyle)
    typography: TypographyStyle = field(default_factory=TypographyStyle)
    
    # Effects
    enable_transparency: bool = False
    enable_shadows: bool = True
    enable_gradients: bool = True
    enable_animations: bool = True
    animation_speed: float = 1.0
    
    # Layout
    border_radius: int = 0
    spacing: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary"""
        theme = Theme()
        
        if 'name' in data:
            theme.name = data['name']
        if 'author' in data:
            theme.author = data['author']
        if 'description' in data:
            theme.description = data['description']
        
        if 'colors' in data:
            theme.colors = ColorScheme(**data['colors'])
        
        return theme


# =============================================================================
# PRESET THEMES
# =============================================================================

class ThemePresets:
    """Collection of built-in themes"""
    
    @staticmethod
    def cyberpunk_christmas() -> Theme:
        """Cyberpunk Christmas theme"""
        theme = Theme(
            name="Cyberpunk Christmas",
            author="Brad TUI Team",
            description="Festive cyberpunk theme with neon colors"
        )
        
        theme.colors = ColorScheme(
            background=(8, 10, 14),
            foreground=(180, 200, 255),
            primary=(0, 255, 255),
            secondary=(255, 0, 100),
            accent=(0, 255, 255),
            success=(0, 255, 100),
            warning=(255, 200, 0),
            error=(255, 50, 50),
            border=(255, 0, 100),
            border_secondary=(0, 200, 255),
        )
        
        return theme
    
    @staticmethod
    def matrix() -> Theme:
        """Matrix theme"""
        theme = Theme(
            name="Matrix",
            author="Brad TUI Team",
            description="Green-on-black Matrix style"
        )
        
        theme.colors = ColorScheme(
            background=(0, 0, 0),
            foreground=(0, 255, 0),
            primary=(0, 255, 0),
            secondary=(0, 200, 0),
            accent=(0, 255, 0),
            success=(0, 255, 0),
            warning=(255, 255, 0),
            error=(255, 0, 0),
            border=(0, 255, 0),
            border_secondary=(0, 200, 0),
        )
        
        return theme
    
    @staticmethod
    def ocean() -> Theme:
        """Ocean theme"""
        theme = Theme(
            name="Ocean",
            author="Brad TUI Team",
            description="Deep ocean blues and teals"
        )
        
        theme.colors = ColorScheme(
            background=(10, 20, 40),
            foreground=(200, 220, 255),
            primary=(0, 150, 255),
            secondary=(0, 200, 200),
            accent=(0, 150, 255),
            success=(0, 200, 200),
            warning=(255, 180, 0),
            error=(255, 100, 100),
            border=(0, 100, 200),
            border_secondary=(0, 200, 255),
        )
        
        return theme
    
    @staticmethod
    def sunset() -> Theme:
        """Sunset theme"""
        theme = Theme(
            name="Sunset",
            author="Brad TUI Team",
            description="Warm sunset colors"
        )
        
        theme.colors = ColorScheme(
            background=(30, 20, 40),
            foreground=(255, 220, 200),
            primary=(255, 150, 50),
            secondary=(255, 100, 150),
            accent=(255, 150, 50),
            success=(100, 255, 150),
            warning=(255, 200, 0),
            error=(255, 50, 50),
            border=(255, 100, 50),
            border_secondary=(255, 150, 200),
        )
        
        return theme
    
    @staticmethod
    def nord() -> Theme:
        """Nord theme"""
        theme = Theme(
            name="Nord",
            author="Brad TUI Team",
            description="Arctic, north-bluish color palette"
        )
        
        theme.colors = ColorScheme(
            background=(46, 52, 64),
            foreground=(216, 222, 233),
            primary=(136, 192, 208),
            secondary=(129, 161, 193),
            accent=(136, 192, 208),
            success=(163, 190, 140),
            warning=(235, 203, 139),
            error=(191, 97, 106),
            border=(136, 192, 208),
            border_secondary=(129, 161, 193),
        )
        
        return theme
    
    @staticmethod
    def dracula() -> Theme:
        """Dracula theme"""
        theme = Theme(
            name="Dracula",
            author="Brad TUI Team",
            description="Dark theme with pastel colors"
        )
        
        theme.colors = ColorScheme(
            background=(40, 42, 54),
            foreground=(248, 248, 242),
            primary=(255, 121, 198),
            secondary=(189, 147, 249),
            accent=(255, 121, 198),
            success=(80, 250, 123),
            warning=(241, 250, 140),
            error=(255, 85, 85),
            border=(189, 147, 249),
            border_secondary=(255, 121, 198),
        )
        
        return theme
    
    @staticmethod
    def gruvbox() -> Theme:
        """Gruvbox theme"""
        theme = Theme(
            name="Gruvbox",
            author="Brad TUI Team",
            description="Retro groove warm theme"
        )
        
        theme.colors = ColorScheme(
            background=(40, 40, 40),
            foreground=(235, 219, 178),
            primary=(251, 184, 108),
            secondary=(184, 187, 38),
            accent=(251, 184, 108),
            success=(184, 187, 38),
            warning=(250, 189, 47),
            error=(251, 73, 52),
            border=(251, 184, 108),
            border_secondary=(184, 187, 38),
        )
        
        return theme
    
    @staticmethod
    def tokyo_night() -> Theme:
        """Tokyo Night theme"""
        theme = Theme(
            name="Tokyo Night",
            author="Brad TUI Team",
            description="Tokyo-inspired night theme"
        )
        
        theme.colors = ColorScheme(
            background=(26, 27, 38),
            foreground=(192, 202, 245),
            primary=(122, 162, 247),
            secondary=(187, 154, 247),
            accent=(122, 162, 247),
            success=(158, 206, 106),
            warning=(224, 175, 104),
            error=(247, 118, 142),
            border=(122, 162, 247),
            border_secondary=(187, 154, 247),
        )
        
        return theme
    
    @staticmethod
    def solarized_dark() -> Theme:
        """Solarized Dark theme"""
        theme = Theme(
            name="Solarized Dark",
            author="Brad TUI Team",
            description="Precision colors for machines and people"
        )
        
        theme.colors = ColorScheme(
            background=(0, 43, 54),
            foreground=(131, 148, 150),
            primary=(38, 139, 210),
            secondary=(108, 113, 196),
            accent=(42, 161, 152),
            success=(133, 153, 0),
            warning=(181, 137, 0),
            error=(220, 50, 47),
            border=(38, 139, 210),
            border_secondary=(42, 161, 152),
        )
        
        return theme
    
    @staticmethod
    def monokai() -> Theme:
        """Monokai theme"""
        theme = Theme(
            name="Monokai",
            author="Brad TUI Team",
            description="Vibrant monokai colors"
        )
        
        theme.colors = ColorScheme(
            background=(39, 40, 34),
            foreground=(248, 248, 242),
            primary=(102, 217, 239),
            secondary=(174, 129, 255),
            accent=(249, 38, 114),
            success=(166, 226, 46),
            warning=(253, 151, 31),
            error=(249, 38, 114),
            border=(102, 217, 239),
            border_secondary=(174, 129, 255),
        )
        
        return theme
    
    @staticmethod
    def get_all_themes() -> Dict[str, Theme]:
        """Get all preset themes"""
        return {
            'cyberpunk_christmas': ThemePresets.cyberpunk_christmas(),
            'matrix': ThemePresets.matrix(),
            'ocean': ThemePresets.ocean(),
            'sunset': ThemePresets.sunset(),
            'nord': ThemePresets.nord(),
            'dracula': ThemePresets.dracula(),
            'gruvbox': ThemePresets.gruvbox(),
            'tokyo_night': ThemePresets.tokyo_night(),
            'solarized_dark': ThemePresets.solarized_dark(),
            'monokai': ThemePresets.monokai(),
        }


# =============================================================================
# THEME MANAGER
# =============================================================================

class ThemeManager:
    """Manages themes and theme switching"""
    
    def __init__(self, themes_dir: Optional[str] = None):
        """Initialize theme manager"""
        if themes_dir:
            self.themes_dir = Path(themes_dir).expanduser()
        else:
            self.themes_dir = Path("~/.config/brad_tui/themes").expanduser()
        
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        self.themes: Dict[str, Theme] = {}
        self.current_theme_name: str = "cyberpunk_christmas"
        self.current_theme: Theme = ThemePresets.cyberpunk_christmas()
        
        # Load preset themes
        self.themes.update(ThemePresets.get_all_themes())
        
        # Load custom themes
        self.load_custom_themes()
    
    def load_custom_themes(self) -> None:
        """Load custom themes from themes directory"""
        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r') as f:
                    data = json.load(f)
                    theme = Theme.from_dict(data)
                    self.themes[theme_file.stem] = theme
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(name)
    
    def set_theme(self, name: str) -> bool:
        """Set current theme"""
        theme = self.get_theme(name)
        if theme:
            self.current_theme = theme
            self.current_theme_name = name
            return True
        return False
    
    def get_current_theme(self) -> Theme:
        """Get current theme"""
        return self.current_theme
    
    def list_themes(self) -> List[str]:
        """List available theme names"""
        return list(self.themes.keys())
    
    def save_theme(self, theme: Theme, name: Optional[str] = None) -> bool:
        """Save theme to file"""
        if name is None:
            name = theme.name.lower().replace(' ', '_')
        
        theme_file = self.themes_dir / f"{name}.json"
        
        try:
            with open(theme_file, 'w') as f:
                json.dump(theme.to_dict(), f, indent=2)
            
            self.themes[name] = theme
            return True
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
    
    def delete_theme(self, name: str) -> bool:
        """Delete custom theme"""
        theme_file = self.themes_dir / f"{name}.json"
        
        try:
            if theme_file.exists():
                theme_file.unlink()
            
            if name in self.themes:
                del self.themes[name]
            
            return True
        except Exception as e:
            print(f"Error deleting theme: {e}")
            return False
    
    def export_theme(self, name: str, output_path: str) -> bool:
        """Export theme to file"""
        theme = self.get_theme(name)
        if not theme:
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(theme.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, input_path: str) -> Optional[str]:
        """Import theme from file"""
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
                theme = Theme.from_dict(data)
                name = theme.name.lower().replace(' ', '_')
                self.themes[name] = theme
                return name
        except Exception as e:
            print(f"Error importing theme: {e}")
            return None
    
    def create_variant(
        self,
        base_theme_name: str,
        variant_name: str,
        modifications: Dict[str, Any]
    ) -> Optional[Theme]:
        """Create theme variant from base theme"""
        base_theme = self.get_theme(base_theme_name)
        if not base_theme:
            return None
        
        # Create copy
        import copy
        variant = copy.deepcopy(base_theme)
        variant.name = variant_name
        
        # Apply modifications
        # This is a simplified implementation
        # In practice, would need more sophisticated merging
        
        self.themes[variant_name.lower().replace(' ', '_')] = variant
        return variant


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - Theme Management Module")
    print("=" * 50)
    
    # Test color utilities
    print("\nColor Utilities:")
    red = (255, 0, 0)
    print(f"RGB: {red}")
    print(f"Hex: {ColorUtils.rgb_to_hex(*red)}")
    print(f"HSV: {ColorUtils.rgb_to_hsv(*red)}")
    print(f"Complementary: {ColorUtils.complementary(red)}")
    
    # Test contrast
    white = (255, 255, 255)
    black = (0, 0, 0)
    contrast = ColorUtils.contrast_ratio(white, black)
    print(f"\nContrast ratio (white/black): {contrast:.2f}")
    print(f"WCAG AA: {ColorUtils.meets_wcag_aa(white, black)}")
    print(f"WCAG AAA: {ColorUtils.meets_wcag_aaa(white, black)}")
    
    # Test theme manager
    print("\nTheme Manager:")
    manager = ThemeManager()
    
    print(f"Available themes: {len(manager.list_themes())}")
    for theme_name in manager.list_themes():
        print(f"  - {theme_name}")
    
    # Test theme switching
    print("\nSwitching to Matrix theme...")
    manager.set_theme('matrix')
    current = manager.get_current_theme()
    print(f"Current theme: {current.name}")
    print(f"Background: {current.colors.background}")
    print(f"Foreground: {current.colors.foreground}")
    
    print("\n✅ Theme module test complete")
