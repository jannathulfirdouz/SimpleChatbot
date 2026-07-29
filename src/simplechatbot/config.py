"""Configuration and settings for SimpleChatbot.

This module defines all configuration constants, model mappings,
and settings used throughout the application. Values can be
overridden via environment variables or a .env file.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ---------------------------------------------------------------------------
# AWS Configuration
# ---------------------------------------------------------------------------

AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE: str = os.getenv("AWS_PROFILE", "default")


# ---------------------------------------------------------------------------
# Anthropic Model Configuration
# ---------------------------------------------------------------------------

# Available Anthropic Claude models on Amazon Bedrock
AVAILABLE_MODELS: Dict[str, Dict[str, str]] = {
    "claude-sonnet-4.6": {
        "model_id": "us.anthropic.claude-sonnet-4-6",
        "name": "Claude Sonnet 4.6",
        "description": "Latest mid-tier model with 1M context window, improved coding and reasoning",
    },
    "claude-sonnet-4.5": {
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "name": "Claude Sonnet 4.5",
        "description": "Optimized for agents, coding, and computer use",
    },
    "claude-haiku-4.5": {
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "name": "Claude Haiku 4.5",
        "description": "Lightweight model optimized for speed and efficiency",
    },
    "claude-opus-4.5": {
        "model_id": "us.anthropic.claude-opus-4-5-20251101-v1:0",
        "name": "Claude Opus 4.5",
        "description": "Most capable model for complex tasks and reasoning",
    },
}

# Default model selection
DEFAULT_MODEL_KEY: str = "claude-sonnet-4.6"
DEFAULT_MODEL_ID: str = os.getenv(
    "BEDROCK_MODEL_ID", AVAILABLE_MODELS[DEFAULT_MODEL_KEY]["model_id"]
)


# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT: str = (
    "You are a helpful, knowledgeable, and friendly AI assistant powered by Amazon Bedrock. "
    "You provide clear, accurate, and concise answers to user questions. "
    "When you don't know something, you say so honestly rather than guessing. "
    "You format your responses with appropriate structure when helpful, "
    "using bullet points, numbered lists, or code blocks as needed. "
    "You maintain a professional yet approachable tone throughout the conversation."
)


# ---------------------------------------------------------------------------
# Chatbot Settings
# ---------------------------------------------------------------------------

@dataclass
class ChatbotSettings:
    """Configuration settings for the chatbot behavior.

    Attributes:
        max_tokens: Maximum number of tokens in the model response.
        temperature: Controls randomness in responses (0.0 = deterministic, 1.0 = creative).
        top_p: Nucleus sampling parameter for response diversity. Set to None for Claude models.
        conversation_history_limit: Maximum number of message pairs to retain in history.
    """

    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    top_p: Optional[float] = None  # Changed to None for Claude models
    conversation_history_limit: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "20"))


# ---------------------------------------------------------------------------
# Flask Web Application Settings
# ---------------------------------------------------------------------------

@dataclass
class FlaskSettings:
    """Configuration settings for the Flask web application.

    Attributes:
        host: Host address to bind the Flask server.
        port: Port number for the Flask server.
        debug: Whether to run Flask in debug mode.
    """

    host: str = os.getenv("FLASK_HOST", "127.0.0.1")
    port: int = int(os.getenv("FLASK_PORT", "5000"))
    debug: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"


# ---------------------------------------------------------------------------
# AgentCore Runtime Settings
# ---------------------------------------------------------------------------

@dataclass
class AgentCoreSettings:
    """Configuration settings for AgentCore Runtime integration.

    Attributes:
        enabled: Whether to route requests through AgentCore Runtime.
        agent_runtime_arn: The ARN of the deployed AgentCore agent runtime.
        region: AWS region where the agent is deployed.
    """

    enabled: bool = os.getenv("AGENTCORE_ENABLED", "false").lower() == "true"
    agent_runtime_arn: str = os.getenv("AGENTCORE_AGENT_ARN", "")
    region: str = os.getenv("AGENTCORE_REGION", AWS_REGION)


def get_model_id(model_key: str) -> str:
    """Get the Bedrock model ID for a given model key.

    Args:
        model_key: The short key identifying the model (e.g., 'claude-sonnet-4.6').

    Returns:
        The full model ID string for use with the Bedrock API.

    Raises:
        ValueError: If the model_key is not found in AVAILABLE_MODELS.
    """
    if model_key not in AVAILABLE_MODELS:
        valid_keys = ", ".join(AVAILABLE_MODELS.keys())
        raise ValueError(
            f"Unknown model key '{model_key}'. Valid options: {valid_keys}"
        )
    return AVAILABLE_MODELS[model_key]["model_id"]


def get_model_name(model_key: str) -> str:
    """Get the display name for a given model key.

    Args:
        model_key: The short key identifying the model.

    Returns:
        The human-readable model name.

    Raises:
        ValueError: If the model_key is not found in AVAILABLE_MODELS.
    """
    if model_key not in AVAILABLE_MODELS:
        valid_keys = ", ".join(AVAILABLE_MODELS.keys())
        raise ValueError(
            f"Unknown model key '{model_key}'. Valid options: {valid_keys}"
        )
    return AVAILABLE_MODELS[model_key]["name"]
