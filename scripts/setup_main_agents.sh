#!/bin/bash
# =============================================================================
# SimpleChatbot - Main Agent Setup & Deployment (macOS/Linux)
# =============================================================================
# This script validates prerequisites, installs the AgentCore CLI,
# scaffolds the agent project, and deploys to Amazon Bedrock AgentCore Runtime.
#
# Usage:
#   chmod +x scripts/setup_main_agents.sh
#   ./scripts/setup_main_agents.sh
#
# Commands:
#   ./scripts/setup_main_agents.sh          # Full setup and deploy
#   ./scripts/setup_main_agents.sh dev      # Local development only
#   ./scripts/setup_main_agents.sh deploy   # Deploy only (skip scaffold)
# =============================================================================

set -e

# Navigate to the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AGENT_DIR="$PROJECT_DIR/agents/mainagent"

echo "============================================="
echo "  SimpleChatbot - Main Agent Setup"
echo "  Amazon Bedrock AgentCore Runtime"
echo "============================================="
echo ""

# ---------------------------------------------------------------------------
# Step 1: Validate Prerequisites
# ---------------------------------------------------------------------------

echo "[1/7] Validating prerequisites..."

# Check Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed. Please install Python 3.10+."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10+ required. Found: Python $PYTHON_VERSION"
    exit 1
fi
echo "  Python $PYTHON_VERSION"

# Check Node.js 20+
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Please install Node.js 20+."
    echo "  Install: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "ERROR: Node.js 20+ required. Found: v$(node -v)"
    exit 1
fi
echo "  Node.js $(node -v)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed."
    exit 1
fi
echo "  npm $(npm -v)"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI is not installed."
    echo "  Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi
echo "  AWS CLI $(aws --version | cut -d' ' -f1)"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "ERROR: AWS credentials not configured or expired."
    echo "  Run: aws configure"
    exit 1
fi
echo "  AWS credentials: valid"

# Check uv (optional but recommended)
if command -v uv &> /dev/null; then
    echo "  uv $(uv --version)"
else
    echo "  uv: not found (will use pip instead)"
fi

echo ""
echo "  All prerequisites validated."
echo ""

# ---------------------------------------------------------------------------
# Step 2: Install AgentCore CLI
# ---------------------------------------------------------------------------

echo "[2/7] Checking AgentCore CLI..."

if command -v agentcore &> /dev/null; then
    echo "  AgentCore CLI already installed: $(agentcore --version 2>/dev/null || echo 'installed')"
else
    echo "  Installing @aws/agentcore CLI..."
    npm install -g @aws/agentcore
    echo "  AgentCore CLI installed successfully."
fi
echo ""

# ---------------------------------------------------------------------------
# Step 3: Handle command argument
# ---------------------------------------------------------------------------

COMMAND="${1:-full}"

if [ "$COMMAND" = "dev" ]; then
    echo "[3/7] Skipping scaffold (dev mode)..."
    echo ""
    echo "[4/7] Skipping copy (dev mode)..."
    echo ""
    echo "[5/7] Starting local development server..."
    echo ""
    echo "  Starting agentcore dev on port 8080..."
    echo "  Test with: curl -X POST http://localhost:8080/invocations -H 'Content-Type: application/json' -d '{\"prompt\": \"Hello!\"}'"
    echo ""
    cd "$AGENT_DIR"
    agentcore dev --no-browser
    exit 0
fi

if [ "$COMMAND" = "deploy" ]; then
    echo "[3/7] Skipping scaffold (deploy mode)..."
    echo ""
    echo "[4/7] Skipping copy (deploy mode)..."
    echo ""
    echo "[5/7] Skipping dev (deploy mode)..."
    echo ""
    echo "[6/7] Deploying to AgentCore Runtime..."
    cd "$AGENT_DIR"
    agentcore deploy
    echo ""
    echo "[7/7] Deployment complete!"
    echo ""
    echo "  Next steps:"
    echo "    agentcore invoke '{\"prompt\": \"Hello from SimpleChatbot!\"}'"
    echo "    agentcore status"
    echo "    agentcore logs"
    exit 0
fi

# ---------------------------------------------------------------------------
# Step 4: Scaffold Agent Project (if not already done)
# ---------------------------------------------------------------------------

echo "[3/7] Scaffolding agent project..."

if [ -d "$AGENT_DIR/agentcore" ]; then
    echo "  Agent project already scaffolded. Skipping."
else
    cd "$AGENT_DIR"
    agentcore create --name mainagent --framework Strands --protocol HTTP --model-provider Bedrock --memory none
    echo "  Agent project scaffolded."
fi
echo ""

# ---------------------------------------------------------------------------
# Step 5: Ensure agent code is in place
# ---------------------------------------------------------------------------

echo "[4/7] Verifying agent code..."

if [ -f "$AGENT_DIR/main.py" ]; then
    echo "  main.py found in agents/mainagent/"
else
    echo "ERROR: main.py not found in agents/mainagent/"
    echo "  Please ensure the agent code exists at: $AGENT_DIR/main.py"
    exit 1
fi

if [ -f "$AGENT_DIR/pyproject.toml" ]; then
    echo "  pyproject.toml found in agents/mainagent/"
else
    echo "ERROR: pyproject.toml not found in agents/mainagent/"
    exit 1
fi
echo ""

# ---------------------------------------------------------------------------
# Step 6: Install dependencies
# ---------------------------------------------------------------------------

echo "[5/7] Installing dependencies..."

cd "$AGENT_DIR"

if command -v uv &> /dev/null; then
    uv sync
    echo "  Dependencies installed with uv."
else
    python3 -m pip install -e . --quiet
    echo "  Dependencies installed with pip."
fi
echo ""

# ---------------------------------------------------------------------------
# Step 7: Local testing prompt
# ---------------------------------------------------------------------------

echo "[6/7] Ready for local testing..."
echo ""
echo "  To test locally, run:"
echo "    cd $AGENT_DIR"
echo "    agentcore dev --no-browser"
echo ""
echo "  Then in another terminal:"
echo "    curl -X POST http://localhost:8080/invocations \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"prompt\": \"Hello from SimpleChatbot!\"}'"
echo ""

# ---------------------------------------------------------------------------
# Step 8: Deploy
# ---------------------------------------------------------------------------

echo "[7/7] Deploying to AgentCore Runtime..."
echo ""

read -p "  Deploy to AWS now? (y/N): " DEPLOY_CONFIRM

if [[ "$DEPLOY_CONFIRM" =~ ^[Yy]$ ]]; then
    agentcore deploy
    echo ""
    echo "============================================="
    echo "  Deployment Complete!"
    echo "============================================="
    echo ""
    echo "  Next steps:"
    echo "    agentcore invoke '{\"prompt\": \"Hello from SimpleChatbot!\"}'"
    echo "    agentcore status"
    echo "    agentcore logs"
else
    echo ""
    echo "  Deployment skipped. To deploy later, run:"
    echo "    cd $AGENT_DIR"
    echo "    agentcore deploy"
fi

echo ""
echo "  Done!"
