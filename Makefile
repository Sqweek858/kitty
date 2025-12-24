#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# 🎄 CYBERPUNK CHRISTMAS TREE - Installer
# ═══════════════════════════════════════════════════════════════════════════════

set -e

RED='\033[38;5;196m'
GREEN='\033[38;5;46m'
CYAN='\033[38;5;51m'
YELLOW='\033[38;5;226m'
MAGENTA='\033[38;5;201m'
RESET='\033[0m'

echo -e "${MAGENTA}"
echo "═══════════════════════════════════════════════════════════════"
echo "           🎄 CYBERPUNK CHRISTMAS TREE INSTALLER 🎄"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${RESET}"

# Detect distro
if command -v pacman &>/dev/null; then
    PKG_MANAGER="pacman"
    PKG_INSTALL="sudo pacman -S --needed --noconfirm"
    DEPS="glew glfw-x11 mesa base-devel"
    DEPS_WAYLAND="glew glfw-wayland mesa base-devel"
elif command -v apt &>/dev/null; then
    PKG_MANAGER="apt"
    PKG_INSTALL="sudo apt install -y"
    DEPS="libglew-dev libglfw3-dev libgl1-mesa-dev build-essential"
    DEPS_WAYLAND="$DEPS"
elif command -v dnf &>/dev/null; then
    PKG_MANAGER="dnf"
    PKG_INSTALL="sudo dnf install -y"
    DEPS="glew-devel glfw-devel mesa-libGL-devel gcc-c++"
    DEPS_WAYLAND="$DEPS"
else
    echo -e "${RED}❌ Unsupported package manager${RESET}"
    echo "Please install manually: glew, glfw, mesa (OpenGL), g++"
    exit 1
fi

echo -e "${CYAN}Detected package manager: ${PKG_MANAGER}${RESET}"

# Check for Wayland
if [[ "$XDG_SESSION_TYPE" == "wayland" ]] && [[ "$PKG_MANAGER" == "pacman" ]]; then
    echo -e "${YELLOW}⚠ Wayland detected, using glfw-wayland${RESET}"
    DEPS="$DEPS_WAYLAND"
fi

# Install dependencies
echo -e "\n${CYAN}📦 Installing dependencies...${RESET}"
$PKG_INSTALL $DEPS

# Compile
echo -e "\n${CYAN}🔨 Compiling...${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

g++ -std=c++17 -O2 -Wall -o christmas_tree christmas_tree.cpp -lGL -lGLEW -lglfw -lm

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Compilation failed${RESET}"
    exit 1
fi

echo -e "${GREEN}✓ Compilation successful!${RESET}"

# Install
echo -e "\n${CYAN}📁 Installing to ~/.local/bin...${RESET}"

mkdir -p "$HOME/.local/bin"
cp christmas_tree "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/christmas_tree"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}⚠ ~/.local/bin is not in your PATH${RESET}"
    echo -e "  Add this to your .zshrc or .bashrc:"
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
fi

echo -e "\n${MAGENTA}═══════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}🎄 Installation complete!${RESET}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${RESET}"

echo -e "\n${CYAN}Usage:${RESET}"
echo "  christmas_tree &     # Run in background"
echo "  pkill christmas_tree # Stop"

echo -e "\n${CYAN}Auto-start (add to .zshrc):${RESET}"
echo '  # 🎄 Christmas tree overlay'
echo '  if [[ -o interactive ]] && [[ "$TERM" == *"kitty"* ]]; then'
echo '      pgrep -x christmas_tree >/dev/null || christmas_tree &>/dev/null &'
echo '  fi'

echo -e "\n${CYAN}Or create a systemd user service:${RESET}"
echo "  See: ~/.config/systemd/user/christmas_tree.service"

# Offer to create systemd service
echo ""
read -p "Create systemd user service for auto-start? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p "$HOME/.config/systemd/user"
    cat > "$HOME/.config/systemd/user/christmas_tree.service" << EOF
[Unit]
Description=Cyberpunk Christmas Tree Overlay
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/bin/christmas_tree
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF
    
    systemctl --user daemon-reload
    systemctl --user enable christmas_tree.service
    
    echo -e "${GREEN}✓ Systemd service created and enabled${RESET}"
    echo "  Start now with: systemctl --user start christmas_tree"
    echo "  Stop with: systemctl --user stop christmas_tree"
fi

echo -e "\n${GREEN}🎄 Crăciun Fericit! 🎄${RESET}\n"

# Ask if user wants to run it now
read -p "Run the Christmas tree now? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${GREEN}🎄 Starting Christmas tree...${RESET}"
    "$HOME/.local/bin/christmas_tree" &
    disown
fi