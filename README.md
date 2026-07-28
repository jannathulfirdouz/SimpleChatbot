# SimpleChatbot

A production-ready Python chatbot powered by Amazon Bedrock Anthropic Claude models. Features both a CLI interface for quick testing and a Flask-based web GUI with a modern, responsive design.

## Features

- **Multiple Anthropic Models**: Support for Claude Sonnet 4.6, Sonnet 4.5, Haiku 4.5, and Opus 4.5
- **AWS Bedrock Integration**: Uses the Converse API for consistent multi-turn conversations
- **CLI Interface**: Beautiful terminal UI with Rich for quick testing
- **Web GUI**: Modern Flask-based chat interface with Amazon color scheme
- **Model Selector**: Switch between models on the fly
- **Conversation History**: Maintains context across messages
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Production Ready**: Follows Python best practices with type hints, docstrings, and PEP 8

## Quick Start

### Prerequisites

- Python 3.10+
- AWS account with Bedrock access enabled
- AWS credentials configured (default profile)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd SimpleChatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install the package
pip install -e .
```

### Running the CLI

```bash
# Windows
scripts\run.bat

# macOS/Linux
chmod +x scripts/run.sh
./scripts/run.sh
```

### Running the Web GUI

```bash
# Windows
scripts\run_web.bat

# macOS/Linux
chmod +x scripts/run_web.sh
./scripts/run_web.sh
```

The web interface will open automatically at `http://127.0.0.1:5000`.

## Configuration

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | `us-east-1` | AWS region for Bedrock |
| `AWS_PROFILE` | `default` | AWS credentials profile |
| `BEDROCK_MODEL_ID` | `us.anthropic.claude-sonnet-4-6` | Default model ID |
| `MAX_TOKENS` | `4096` | Maximum response tokens |
| `CONVERSATION_HISTORY_LIMIT` | `20` | Max conversation turns to maintain |

## Supported Models

| Model | ID | Description |
|-------|----|----|
| Claude Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` | Latest mid-tier model with 1M context |
| Claude Sonnet 4.5 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Optimized for agents and coding |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | Fast and efficient |
| Claude Opus 4.5 | `us.anthropic.claude-opus-4-5-20251101-v1:0` | Most capable model |

## Project Structure

```
SimpleChatbot/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
├── MANIFEST.in
├── scripts/
│   ├── run.sh
│   ├── run.bat
│   ├── run_web.sh
│   └── run_web.bat
├── src/
│   └── simplechatbot/
│       ├── __init__.py
│       ├── chatbot.py
│       ├── config.py
│       ├── cli.py
│       └── web/
│           ├── __init__.py
│           ├── app.py
│           ├── static/
│           │   ├── css/style.css
│           │   ├── js/chat.js
│           │   └── images/logo.svg
│           └── templates/
│               ├── base.html
│               └── index.html
└── docs/
    ├── setup.md
    ├── api.md
    └── deployment.md
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Build the Builder Workshop

This project was created as part of the **Build the Builder** workshop, demonstrating how to build production-ready AI applications using Amazon Bedrock and Python.
