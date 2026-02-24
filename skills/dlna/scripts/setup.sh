#!/bin/bash
# Setup script for dlna skill
# Creates virtual environment in the skill directory

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

echo "Setting up dlna skill..."
echo "Skill directory: $SKILL_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    uv venv "$VENV_DIR"
fi

# Install dependencies using uv
echo "Installing dependencies..."
cd "$SKILL_DIR"
uv sync

echo ""
echo "Setup complete!"
echo ""
echo "To use the dlna command:"
echo "  cd $SKILL_DIR"
echo "  uv run dlna discover"
echo ""
echo "Or activate the venv directly:"
echo "  source $VENV_DIR/bin/activate"
echo "  dlna discover"
