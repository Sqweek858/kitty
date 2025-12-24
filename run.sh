#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Cyberpunk Terminal - Launch Script
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       CYBERPUNK TERMINAL - Christmas Edition                 ║"
echo "║              Starting Enhanced Terminal UI...                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed!${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python version: ${PYTHON_VERSION}"

# Check if we're in the right directory
if [ ! -f "cyberpunk_terminal.py" ]; then
    echo -e "${RED}Error: cyberpunk_terminal.py not found!${NC}"
    echo "Please run this script from the workspace directory."
    exit 1
fi

# Check terminal capabilities
if [ -z "$TERM" ]; then
    echo -e "${YELLOW}Warning: TERM variable not set. Some features may not work.${NC}"
fi

echo -e "${GREEN}✓${NC} Terminal: ${TERM}"

# Get terminal size
if command -v tput &> /dev/null; then
    COLS=$(tput cols)
    ROWS=$(tput lines)
    echo -e "${GREEN}✓${NC} Terminal size: ${COLS}x${ROWS}"
    
    if [ "$COLS" -lt 80 ] || [ "$ROWS" -lt 24 ]; then
        echo -e "${YELLOW}Warning: Terminal size is small. Recommended: 80x24 or larger.${NC}"
    fi
fi

# Check for tmux/screen
if [ -n "$TMUX" ]; then
    echo -e "${GREEN}✓${NC} Running in tmux"
elif [ -n "$STY" ]; then
    echo -e "${GREEN}✓${NC} Running in screen"
fi

echo ""
echo -e "${CYAN}Starting Cyberpunk Terminal...${NC}"
echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
echo ""

# Run the terminal
python3 cyberpunk_terminal.py "$@"

# Exit message
echo ""
echo -e "${GREEN}Thank you for using Cyberpunk Terminal!${NC}"
