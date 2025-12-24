#!/bin/bash
# Script de instalare pentru Brad TUI Ultimate

set -e

echo "🎄 Instalare Brad TUI Ultimate..."
echo ""

# Verifică dacă există Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nu este instalat. Te rog instalează Python 3 mai întâi."
    exit 1
fi

echo "✓ Python 3 găsit: $(python3 --version)"

# Verifică/instalează prompt_toolkit
echo ""
echo "📦 Verificare dependențe..."
if ! python3 -c "import prompt_toolkit" &> /dev/null; then
    echo "  Instalare prompt_toolkit..."
    pip3 install --user prompt_toolkit || {
        echo "❌ Nu s-a putut instala prompt_toolkit"
        echo "   Încearcă manual: pip3 install --user prompt_toolkit"
        exit 1
    }
fi

echo "✓ prompt_toolkit instalat"

# Creează director bin în home dacă nu există
mkdir -p ~/bin

# Copiază scriptul
echo ""
echo "📋 Copiere fișiere..."
cp -f brad_tui_ultimate.py ~/bin/brad_tui
chmod +x ~/bin/brad_tui

echo "✓ Brad TUI instalat în ~/bin/brad_tui"

# Actualizare tmux config
echo ""
echo "🔧 Configurare tmux..."
cp -f .tmux.conf ~/.tmux.conf
echo "✓ Configurare tmux actualizată"

# Verifică dacă ~/bin e în PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo ""
    echo "⚠️  IMPORTANT: Adaugă ~/bin în PATH!"
    echo "   Adaugă în ~/.bashrc sau ~/.zshrc:"
    echo "   export PATH=\"\$HOME/bin:\$PATH\""
fi

echo ""
echo "✨ Instalare completă!"
echo ""
echo "Pentru a rula Brad TUI:"
echo "  1. În tmux: Apasă Prefix+B (de obicei Ctrl+B apoi B)"
echo "  2. Direct: ~/bin/brad_tui"
echo ""
echo "🎄 Sărbători fericite!"
