#!/bin/bash

echo "========================================"
echo "  Installing Nom Viet for RIME"
echo "========================================"
echo

# Detect RIME directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    RIME_DIR="$HOME/Library/Rime"
elif [[ -d "$HOME/.config/ibus/rime" ]]; then
    RIME_DIR="$HOME/.config/ibus/rime"
elif [[ -d "$HOME/.local/share/fcitx5/rime" ]]; then
    RIME_DIR="$HOME/.local/share/fcitx5/rime"
else
    echo "ERROR: Could not find RIME directory"
    echo "Please install Squirrel (macOS), ibus-rime, or fcitx5-rime first"
    exit 1
fi

echo "RIME directory: $RIME_DIR"
echo

cd "$RIME_DIR"

echo "Downloading nom_viet.schema.yaml..."
curl -LO https://github.com/nhatvu148/rime-nom-viet/raw/main/nom_viet.schema.yaml

echo "Downloading nom_viet.dict.yaml..."
curl -LO https://github.com/nhatvu148/rime-nom-viet/raw/main/nom_viet.dict.yaml

echo
echo "Creating default.custom.yaml..."
cat > default.custom.yaml << 'EOF'
patch:
  schema_list:
    - schema: nom_viet
    - schema: luna_pinyin
EOF

echo
echo "========================================"
echo "  Installation complete!"
echo "========================================"
echo
echo "Files installed to: $RIME_DIR"
echo
echo "NEXT STEPS:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  1. Click Squirrel icon → Deploy (重新部署)"
    echo "  2. Press Ctrl+\` or F4 to select 'Nom Viet'"
else
    echo "  1. Right-click RIME icon → Deploy"
    echo "  2. Press Ctrl+\` or F4 to select 'Nom Viet'"
fi
echo
