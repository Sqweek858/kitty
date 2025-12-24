#!/usr/bin/env bash
# ============================================================================
# Brad TUI Ultra - Installation Script
# ============================================================================
# This script installs and configures Brad TUI Ultra
# Run with: bash install_brad_ultra.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════╗
║                                                      ║
║         🎄  BRAD TUI ULTRA INSTALLER  🎄            ║
║                                                      ║
║          Enhanced Terminal Experience                ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please do not run this script as root${RESET}"
    exit 1
fi

echo -e "${BLUE}🔍 Checking system requirements...${RESET}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${RESET}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $(python3 --version | cut -d' ' -f2) found${RESET}"

# Check for required Python packages
echo -e "${BLUE}📦 Checking Python dependencies...${RESET}"

REQUIRED_PACKAGES=("asyncio")
MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $pkg" &> /dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing packages: ${MISSING_PACKAGES[*]}${RESET}"
    echo -e "${BLUE}Installing missing packages...${RESET}"
    # asyncio is built-in since Python 3.4, so this shouldn't happen
fi

# Check for tmux
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}⚠️  tmux not found. Installing is recommended for full experience${RESET}"
    read -p "Install tmux? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y tmux
        elif command -v yay &> /dev/null; then
            yay -S tmux
        elif command -v pacman &> /dev/null; then
            sudo pacman -S tmux
        else
            echo -e "${RED}❌ Could not install tmux automatically. Please install it manually.${RESET}"
        fi
    fi
else
    echo -e "${GREEN}✓ tmux $(tmux -V) found${RESET}"
fi

# Create directories
echo -e "${BLUE}📁 Creating directories...${RESET}"

mkdir -p ~/bin
mkdir -p ~/.config/brad_tui
mkdir -p ~/.local/share/brad_tui
mkdir -p ~/.cache/brad_tui

echo -e "${GREEN}✓ Directories created${RESET}"

# Copy files
echo -e "${BLUE}📋 Installing Brad TUI Ultra...${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy main TUI
if [ -f "$SCRIPT_DIR/brad_tui_ultra.py" ]; then
    cp "$SCRIPT_DIR/brad_tui_ultra.py" ~/bin/brad_tui_ultra.py
    chmod +x ~/bin/brad_tui_ultra.py
    echo -e "${GREEN}✓ Installed brad_tui_ultra.py${RESET}"
else
    echo -e "${RED}❌ brad_tui_ultra.py not found in $SCRIPT_DIR${RESET}"
    exit 1
fi

# Copy visualization TUI if exists
if [ -f "$SCRIPT_DIR/brad_tui.py" ]; then
    cp "$SCRIPT_DIR/brad_tui.py" ~/bin/brad_tui.py
    chmod +x ~/bin/brad_tui.py
    echo -e "${GREEN}✓ Installed brad_tui.py (visualization)${RESET}"
fi

# Copy enhanced TUI if exists
if [ -f "$SCRIPT_DIR/brad_tui_enhanced.py" ]; then
    cp "$SCRIPT_DIR/brad_tui_enhanced.py" ~/bin/brad_tui_enhanced.py
    chmod +x ~/bin/brad_tui_enhanced.py
    echo -e "${GREEN}✓ Installed brad_tui_enhanced.py${RESET}"
fi

# Install tmux config
echo -e "${BLUE}⚙️  Installing tmux configuration...${RESET}"

if [ -f "$SCRIPT_DIR/.tmux_ultra.conf" ]; then
    # Backup existing tmux conf
    if [ -f ~/.tmux.conf ]; then
        cp ~/.tmux.conf ~/.tmux.conf.backup.$(date +%Y%m%d_%H%M%S)
        echo -e "${YELLOW}📦 Backed up existing ~/.tmux.conf${RESET}"
    fi
    
    cp "$SCRIPT_DIR/.tmux_ultra.conf" ~/.tmux.conf
    echo -e "${GREEN}✓ Installed tmux configuration${RESET}"
fi

# Update shell configuration
echo -e "${BLUE}🐚 Updating shell configuration...${RESET}"

# Detect shell
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ -f ~/.zshrc ]; then
    SHELL_RC=~/.zshrc
    SHELL_NAME="zsh"
elif [ -f ~/.bashrc ]; then
    SHELL_RC=~/.bashrc
    SHELL_NAME="bash"
fi

if [ -n "$SHELL_RC" ]; then
    # Add Brad TUI Ultra to PATH
    if ! grep -q "# Brad TUI Ultra" "$SHELL_RC"; then
        cat >> "$SHELL_RC" << 'EOL'

# ============================================================================
# Brad TUI Ultra Configuration
# ============================================================================

# Add Brad TUI Ultra to PATH
export PATH="$HOME/bin:$PATH"

# Brad TUI Ultra aliases
alias brad='python3 ~/bin/brad_tui_ultra.py'
alias brad-ultra='python3 ~/bin/brad_tui_ultra.py'
alias brad-viz='python3 ~/bin/brad_tui.py'

# Auto-start Brad TUI Ultra in new terminals (optional)
# Uncomment the following line to auto-start:
# if [[ -z "$TMUX" && -z "$BRAD_TUI_RUNNING" ]]; then
#     export BRAD_TUI_RUNNING=1
#     python3 ~/bin/brad_tui_ultra.py
# fi

# ============================================================================
EOL
        echo -e "${GREEN}✓ Updated $SHELL_RC${RESET}"
    else
        echo -e "${YELLOW}⚠️  Brad TUI Ultra already configured in $SHELL_RC${RESET}"
    fi
fi

# Create desktop entry (for GUI systems)
echo -e "${BLUE}🖥️  Creating desktop entry...${RESET}"

if [ -d ~/.local/share/applications ]; then
    cat > ~/.local/share/applications/brad-tui-ultra.desktop << EOL
[Desktop Entry]
Name=Brad TUI Ultra
Comment=Enhanced Terminal Interface with Christmas Theme
Exec=bash -c "cd ~ && python3 ~/bin/brad_tui_ultra.py"
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=System;TerminalEmulator;
Keywords=terminal;shell;command;cli;
EOL
    echo -e "${GREEN}✓ Desktop entry created${RESET}"
fi

# Create uninstall script
echo -e "${BLUE}📝 Creating uninstall script...${RESET}"

cat > ~/bin/uninstall_brad_ultra.sh << 'EOL'
#!/usr/bin/env bash
# Uninstall Brad TUI Ultra

echo "Uninstalling Brad TUI Ultra..."

# Remove binaries
rm -f ~/bin/brad_tui_ultra.py
rm -f ~/bin/brad_tui.py
rm -f ~/bin/brad_tui_enhanced.py
rm -f ~/.local/share/applications/brad-tui-ultra.desktop

# Remove directories (keeping configs and data)
echo "Note: Configuration files in ~/.config/brad_tui and data in ~/.local/share/brad_tui are preserved"
echo "Remove them manually if needed"

# Remove from shell config
for rc in ~/.zshrc ~/.bashrc; do
    if [ -f "$rc" ]; then
        sed -i '/# Brad TUI Ultra Configuration/,/# ============================================================================/d' "$rc"
    fi
done

echo "✓ Brad TUI Ultra uninstalled"
echo "Restart your shell or source your shell config to complete"
EOL

chmod +x ~/bin/uninstall_brad_ultra.sh
echo -e "${GREEN}✓ Uninstall script created at ~/bin/uninstall_brad_ultra.sh${RESET}"

# Completion
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════╗
║                                                      ║
║         ✅  INSTALLATION COMPLETE!  ✅              ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"

echo -e "${CYAN}🎄 Brad TUI Ultra has been installed successfully!${RESET}"
echo ""
echo -e "${YELLOW}Next steps:${RESET}"
echo -e "  1. Restart your shell or run: ${GREEN}source $SHELL_RC${RESET}"
echo -e "  2. Start Brad TUI Ultra: ${GREEN}brad${RESET}"
echo -e "  3. Or with tmux: ${GREEN}tmux new-session -s brad${RESET}"
echo ""
echo -e "${CYAN}Tips:${RESET}"
echo -e "  • Use ${GREEN}F1-F7${RESET} for quick functions"
echo -e "  • Press ${GREEN}Tab${RESET} for autocompletion"
echo -e "  • Use ${GREEN}Ctrl+C${RESET} to exit"
echo -e "  • Full cursor navigation with arrow keys, Home/End, Ctrl+arrows"
echo ""
echo -e "${MAGENTA}Enjoy your enhanced terminal experience! 🎄${RESET}"
echo ""

# Optional: Test run
read -p "Would you like to test Brad TUI Ultra now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 ~/bin/brad_tui_ultra.py
fi
