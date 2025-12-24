#!/usr/bin/env bash
# =============================================================================
# Brad TUI Ultra - Uninstall Script
# =============================================================================
# This script uninstalls Brad TUI Ultra from your system
# Usage: bash uninstall_brad_ultra.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo "========================================="
echo "🎄 Brad TUI Ultra - Uninstaller"
echo "========================================="
echo ""

# Confirm uninstall
read -p "Are you sure you want to uninstall Brad TUI Ultra? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Uninstall cancelled"
    exit 0
fi

echo ""
log_info "Starting uninstallation..."
echo ""

# Remove executables
log_info "Removing executables..."
rm -f ~/bin/brad_tui_ultra.py
rm -f ~/bin/brad_tui.py
rm -f ~/bin/brad_tui_enhanced.py
rm -f ~/bin/brad_tui_config.py
rm -f ~/bin/brad_tui_plugins.py
rm -f ~/bin/brad_tui_effects.py
rm -f ~/bin/brad_tui_themes.py
rm -f ~/bin/brad_tui_utils.py
rm -f ~/bin/brad_tui_logging.py
rm -f ~/bin/brad_tui_components.py
rm -f ~/bin/install_brad_ultra.sh
rm -f ~/bin/uninstall_brad_ultra.sh
log_success "Executables removed"

# Remove configuration (ask user)
read -p "Remove configuration files? This will delete all your settings. (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Removing configuration..."
    rm -rf ~/.config/brad_tui
    log_success "Configuration removed"
else
    log_info "Configuration kept at ~/.config/brad_tui"
fi

# Remove cache (ask user)
read -p "Remove cache and logs? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Removing cache and logs..."
    rm -rf ~/.cache/brad_tui
    log_success "Cache and logs removed"
else
    log_info "Cache kept at ~/.cache/brad_tui"
fi

# Restore tmux config backup
if [ -f ~/.tmux.conf.backup ]; then
    read -p "Restore previous tmux configuration? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restoring tmux configuration..."
        mv ~/.tmux.conf.backup ~/.tmux.conf
        log_success "Tmux configuration restored"
    fi
fi

# Remove zsh integration
if [ -f ~/.zshrc_brad_ultra_integration ]; then
    log_info "Removing zsh integration..."
    rm -f ~/.zshrc_brad_ultra_integration
    log_success "Zsh integration removed"
fi

# Remove desktop entry
if [ -f ~/.local/share/applications/brad-tui-ultra.desktop ]; then
    log_info "Removing desktop entry..."
    rm -f ~/.local/share/applications/brad-tui-ultra.desktop
    log_success "Desktop entry removed"
fi

# Clean up shell config (optional)
read -p "Remove Brad TUI references from shell config files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Cleaning shell configuration..."
    
    # Create backup first
    if [ -f ~/.zshrc ]; then
        cp ~/.zshrc ~/.zshrc.backup_$(date +%Y%m%d_%H%M%S)
        
        # Remove Brad TUI lines
        sed -i.bak '/brad_tui/d' ~/.zshrc
        sed -i.bak '/BRAD_TUI/d' ~/.zshrc
        sed -i.bak '/brad-/d' ~/.zshrc
        rm ~/.zshrc.bak
        
        log_success "Cleaned ~/.zshrc"
    fi
    
    if [ -f ~/.bashrc ]; then
        cp ~/.bashrc ~/.bashrc.backup_$(date +%Y%m%d_%H%M%S)
        
        # Remove Brad TUI lines
        sed -i.bak '/brad_tui/d' ~/.bashrc
        sed -i.bak '/BRAD_TUI/d' ~/.bashrc
        sed -i.bak '/brad-/d' ~/.bashrc
        rm ~/.bashrc.bak
        
        log_success "Cleaned ~/.bashrc"
    fi
else
    log_info "Shell configuration kept unchanged"
fi

# Summary
echo ""
echo "========================================="
log_success "Brad TUI Ultra has been uninstalled"
echo "========================================="
echo ""
echo "Summary of changes:"
echo "  ✓ Executables removed from ~/bin"
echo "  ✓ Desktop entry removed"

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  ✓ Shell configuration cleaned"
fi

echo ""
echo "Note: You may need to restart your terminal or"
echo "run 'source ~/.zshrc' (or ~/.bashrc) for changes"
echo "to take effect."
echo ""
echo "Thank you for using Brad TUI Ultra! 🎄"
echo ""

# Ask if user wants to provide feedback
read -p "Would you like to tell us why you're uninstalling? (optional) (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please enter your feedback (press Ctrl+D when done):"
    feedback=$(cat)
    
    # Save feedback to a file (could be uploaded to analytics service)
    feedback_file=~/.cache/brad_tui_uninstall_feedback_$(date +%Y%m%d_%H%M%S).txt
    echo "$feedback" > "$feedback_file"
    
    log_success "Thank you for your feedback! Saved to $feedback_file"
fi

echo ""
log_info "Uninstallation complete!"
