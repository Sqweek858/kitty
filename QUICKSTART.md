# 🎄 Brad TUI Ultra - Quick Start Guide

Get up and running with Brad TUI Ultra in 5 minutes!

---

## 🚀 Installation

### One-Line Install

```bash
bash install_brad_ultra.sh
```

That's it! The installer will:
- ✅ Check dependencies (Python 3, tmux)
- ✅ Install all components
- ✅ Configure tmux integration
- ✅ Set up shell aliases
- ✅ Create desktop entry

### Manual Installation

If you prefer manual installation:

```bash
# 1. Copy executables
mkdir -p ~/bin
cp brad_tui_*.py ~/bin/
chmod +x ~/bin/brad_tui_*.py

# 2. Add to PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
echo 'alias brad="python3 ~/bin/brad_tui_ultra.py"' >> ~/.zshrc

# 3. Reload shell
source ~/.zshrc
```

---

## 🎮 First Run

### Launch Brad TUI Ultra

```bash
brad
```

Or with custom options:

```bash
python3 ~/bin/brad_tui_ultra.py
```

### What You'll See

1. **Welcome Animation** 🎄
   - Festive intro sequence
   - Christmas tree animation
   - Snow falling effect

2. **Main Interface**
   - Persistent menu bar at top
   - Command input area
   - Output display area
   - Status bar at bottom
   - Autocorrect panel (when needed)

3. **Visual Effects**
   - Parallax star background
   - Animated Christmas tree
   - Falling snow
   - Gradient borders on all elements

---

## ⌨️ Essential Keyboard Shortcuts

### Navigation
- `↑/↓` - Command history
- `←/→` - Move cursor
- `Ctrl+←/→` - Move by word
- `Home/End` - Jump to line start/end

### Editing
- `Backspace` - Delete character
- `Delete` - Delete forward
- `Ctrl+W` - Delete word
- `Ctrl+U` - Clear line before cursor
- `Ctrl+K` - Clear line after cursor

### Functions
- `F1` - Show help
- `F3` - Show history
- `F4` - Clear screen
- `F5` - Toggle parallax
- `F6` - Toggle Christmas tree
- `F7` - Toggle snow
- `Tab` - Accept autocomplete

### Control
- `Ctrl+C` - Exit
- `Ctrl+L` - Clear screen

---

## 🎨 Quick Theme Change

```bash
# Switch to Matrix theme
brad_theme_switch matrix

# Available themes:
# - cyberpunk_christmas (default)
# - matrix
# - ocean
# - sunset
# - nord
# - dracula
# - gruvbox
# - tokyo_night
# - solarized_dark
# - monokai
```

---

## ⚙️ Quick Configuration

### Performance Presets

```bash
# Low performance mode (CPU friendly)
brad_performance low

# Medium (balanced)
brad_performance medium

# High (all effects)
brad_performance high

# Ultra (maximum)
brad_performance ultra
```

### Feature Toggles

```bash
# Disable parallax
brad-parallax-off

# Enable snow
brad-snow-on

# Disable tree
brad-tree-off
```

---

## 🔧 Customization

### Edit Configuration

```bash
brad-config
```

This opens `~/.config/brad_tui/config.toml` in your editor.

### Common Settings

```toml
[general]
theme = "cyberpunk_christmas"
fps = 30

[features]
parallax = true
tree = true
snow = true

[parallax]
stars = 200  # Reduce for better performance

[snow]
flakes = 100  # Reduce for better performance
```

---

## 🐛 Troubleshooting

### Colors Don't Display Correctly

```bash
# Enable true color
export COLORTERM=truecolor
```

Add to `~/.zshrc` to make permanent.

### Performance is Slow

```bash
# Use low performance preset
brad_performance low

# Or edit config
brad-config
# Then set: fps = 15, stars = 50, flakes = 30
```

### Menu Bar Not Visible

- Check terminal size: minimum 80x24
- Try maximizing terminal window
- Verify tmux integration: `echo $TMUX`

### Output Disappearing

This was Issue #5 and is now fixed. If you still experience this:

```bash
# Check version
python3 ~/bin/brad_tui_ultra.py --version

# Reinstall if needed
bash install_brad_ultra.sh
```

---

## 💡 Tips & Tricks

### 1. Use Shell Aliases

```bash
# Add to ~/.zshrc
alias b='brad'
alias bt='brad_theme_switch'
alias bp='brad_performance'
```

### 2. Check Status

```bash
brad_status
```

Shows current configuration and enabled features.

### 3. View Logs

```bash
# Live logs
brad-logs

# Error logs only
brad-errors
```

### 4. Clear Cache

If experiencing issues:

```bash
brad-clear-cache
```

### 5. Launch with Minimal Effects

```bash
brad_launch --minimal
```

Great for slower systems or SSH sessions.

### 6. Launch Without Specific Effects

```bash
brad_launch --no-snow --no-parallax
```

---

## 🔥 Advanced Usage

### Custom Launch

```bash
# Custom theme and FPS
brad_launch --theme matrix --fps 60

# Full effects mode
brad_launch --full

# No welcome animation
brad_launch --no-welcome
```

### Plugin Development

Create `~/.config/brad_tui/plugins/my_plugin.py`:

```python
from brad_tui_plugins import BradPlugin, PluginMetadata

class MyPlugin(BradPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="My Plugin",
            version="1.0.0",
            author="Me",
            description="My custom plugin"
        )
    
    def on_load(self):
        print("Plugin loaded!")
        return True
```

### Custom Theme

Create `~/.config/brad_tui/themes/my_theme.json`:

```json
{
  "name": "My Theme",
  "colors": {
    "background": [10, 10, 20],
    "foreground": [200, 200, 255],
    "accent": [255, 100, 200]
  }
}
```

Then:

```bash
brad_theme_switch my_theme
```

---

## 📚 Learn More

- **Full Documentation**: `README_ULTRA.md`
- **Changelog**: `CHANGELOG.md`
- **Configuration**: `brad-config`
- **Help Command**: `brad_help`
- **Check Installation**: `brad_check_install`

---

## 🎓 Examples

### Example 1: List Files with Beautiful Output

```bash
brad
ls -la
# Output displayed with gradient borders
```

### Example 2: Long Running Command

```bash
brad
find / -name "*.py"
# Output persists, never disappears
# Scroll up/down to view
```

### Example 3: Interactive Python

```bash
brad
python3
>>> print("Hello from Brad TUI!")
```

### Example 4: Git Operations

```bash
brad
git status
git log --oneline
# All output beautifully formatted
```

---

## 🆘 Getting Help

### Built-in Help

```bash
# Press F1 in Brad TUI
# Or run:
brad_help
```

### Check Installation

```bash
brad_check_install
```

### Report Issues

If you find bugs or have feature requests:

1. Check logs: `brad-logs`
2. Check errors: `brad-errors`
3. Check status: `brad_status`
4. Report on GitHub Issues

---

## 🎁 What's Fixed

All 12 reported issues are now fixed:

- ✅ Persistent menu bar
- ✅ Autocorrect panel positioning
- ✅ Keybindings working
- ✅ Full cursor movement
- ✅ Output persistence
- ✅ Parallax no overlap
- ✅ Clean code (no duplicates)
- ✅ Welcome animation (tmux-compatible)
- ✅ Christmas tree display
- ✅ Star randomness
- ✅ Cursor colors
- ✅ Gradient borders

---

## 🚀 Next Steps

1. **Explore Themes**: Try all 10 built-in themes
2. **Customize Settings**: Adjust to your preferences
3. **Create Plugins**: Extend functionality
4. **Join Community**: Share feedback and tips
5. **Enjoy**: Have fun with your enhanced terminal! 🎄

---

## 📞 Quick Reference Card

```
┌─────────────────────────────────────────┐
│         Brad TUI Ultra v3.0             │
├─────────────────────────────────────────┤
│ Launch:         brad                    │
│ Theme:          brad_theme_switch       │
│ Performance:    brad_performance        │
│ Config:         brad-config             │
│ Status:         brad_status             │
│ Help:           F1 or brad_help         │
│ Exit:           Ctrl+C                  │
├─────────────────────────────────────────┤
│ Parallax:       F5                      │
│ Tree:           F6                      │
│ Snow:           F7                      │
│ History:        F3 or ↑/↓               │
│ Clear:          F4 or Ctrl+L            │
└─────────────────────────────────────────┘
```

---

**Happy Terminal-ing! 🎄✨**
