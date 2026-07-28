# API Documentation

## Web API Endpoints

The SimpleChatbot web application exposes the following REST API endpoints.

### Base URL

```
http://127.0.0.1:5000
```

---

### POST /api/chat

Send a message and receive a response from the AI model.

**Request:**

```json
{
    "message": "Hello, how are you?"
}
```

**Response (200):**

```json
{
    "response": "Hello! I'm doing well, thank you for asking...",
    "model": "Claude Sonnet 4.6",
    "history_length": 2
}
```

**Error Response (400):**

```json
{
    "error": "Missing 'message' field in request body."
}
```

**Error Response (500):**

```json
{
    "error": "Access denied to model 'us.anthropic.claude-sonnet-4-6'. Please ensure you have enabled this model in the Amazon Bedrock console."
}
```

---

### GET /api/model

Get information about the currently selected model.

**Response (200):**

```json
{
    "model": {
        "model_key": "claude-sonnet-4.6",
        "model_id": "us.anthropic.claude-sonnet-4-6",
        "name": "Claude Sonnet 4.6",
        "description": "Latest mid-tier model with 1M context window, improved coding and reasoning"
    }
}
```

---

### POST /api/model

Switch to a different Anthropic model.

**Request:**

```json
{
    "model_key": "claude-haiku-4.5"
}
```

**Response (200):**

```json
{
    "message": "Switched to Claude Haiku 4.5",
    "model": {
        "model_key": "claude-haiku-4.5",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "name": "Claude Haiku 4.5",
        "description": "Lightweight model optimized for speed and efficiency"
    }
}
```

**Valid model keys:**

| Key | Model |
|-----|-------|
| `claude-sonnet-4.6` | Claude Sonnet 4.6 |
| `claude-sonnet-4.5` | Claude Sonnet 4.5 |
| `claude-haiku-4.5` | Claude Haiku 4.5 |
| `claude-opus-4.5` | Claude Opus 4.5 |

---

### GET /api/models

List all available models with their status.

**Response (200):**

```json
{
    "models": [
        {
            "key": "claude-sonnet-4.6",
            "name": "Claude Sonnet 4.6",
            "model_id": "us.anthropic.claude-sonnet-4-6",
            "description": "Latest mid-tier model with 1M context window, improved coding and reasoning",
            "active": true
        },
        {
            "key": "claude-sonnet-4.5",
            "name": "Claude Sonnet 4.5",
            "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "description": "Optimized for agents, coding, and computer use",
            "active": false
        }
    ],
    "current": "claude-sonnet-4.6"
}
```

---

### DELETE /api/history

Clear the conversation history.

**Response (200):**

```json
{
    "message": "Conversation history cleared."
}
```

---

### GET /health

Health check endpoint for monitoring.

**Response (200):**

```json
{
    "status": "healthy",
    "application": "SimpleChatbot"
}
```

---

## Python API

### SimpleChatbot Class

```python
from simplechatbot.chatbot import SimpleChatbot
from simplechatbot.config import ChatbotSettings

# Initialize with defaults
chatbot = SimpleChatbot()

# Initialize with custom settings
settings = ChatbotSettings(
    max_tokens=2048,
    temperature=0.5,
    conversation_history_limit=10,
)
chatbot = SimpleChatbot(
    model_key="claude-haiku-4.5",
    settings=settings,
    system_prompt="You are a coding assistant.",
)

# Send a message
response = chatbot.get_response("What is Python?")
print(response)

# Switch models
chatbot.set_model("claude-opus-4.5")

# Clear history
chatbot.clear_history()

# Get model info
info = chatbot.get_current_model_info()
print(info["name"])  # "Claude Sonnet 4.6"
```

### Configuration

```python
from simplechatbot.config import (
    AVAILABLE_MODELS,
    get_model_id,
    get_model_name,
    ChatbotSettings,
    FlaskSettings,
)

# Get a model ID
model_id = get_model_id("claude-sonnet-4.6")
# "us.anthropic.claude-sonnet-4-6"

# List all models
for key, model in AVAILABLE_MODELS.items():
    print(f"{key}: {model['name']}")
```
