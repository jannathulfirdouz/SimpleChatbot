#!/bin/bash
# =============================================================================
# SimpleChatbot - Web GUI Runner (macOS/Linux)
# =============================================================================
# This script activates the virtual environment, installs dependencies,
# and launches the Flask web GUI. The browser opens automatically.
# =============================================================================

set -e

# Navigate to the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "============================================="
echo "  SimpleChatbot - Web Interface"
echo "  Build the Builder Workshop"
echo "============================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    echo "Please install Python 3.10 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade the package in editable mode
echo "Installing dependencies..."
pip install -e . --quiet
echo "Dependencies installed."
echo ""

# Get host and port from environment or use defaults
HOST="${FLASK_HOST:-127.0.0.1}"
PORT="${FLASK_PORT:-5000}"
URL="http://${HOST}:${PORT}"

echo "Starting SimpleChatbot Web GUI..."
echo "URL: ${URL}"
echo ""

# Open browser after a short delay (background process)
(sleep 2 && open "${URL}" 2>/dev/null || xdg-open "${URL}" 2>/dev/null || true) &

# Run the Flask web application
python -m simplechatbot.web.app
