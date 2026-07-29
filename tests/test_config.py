"""Tests for simplechatbot.config module."""

import pytest

from simplechatbot.config import (
    AVAILABLE_MODELS,
    AWS_REGION,
    DEFAULT_MODEL_KEY,
    SYSTEM_PROMPT,
    AgentCoreSettings,
    ChatbotSettings,
    FlaskSettings,
    get_model_id,
    get_model_name,
)


class TestAvailableModels:
    """Tests for the AVAILABLE_MODELS configuration."""

    def test_all_models_present(self):
        """Verify all expected models are defined."""
        expected_keys = [
            "claude-sonnet-4.6",
            "claude-sonnet-4.5",
            "claude-haiku-4.5",
            "claude-opus-4.5",
        ]
        for key in expected_keys:
            assert key in AVAILABLE_MODELS

    def test_models_have_required_fields(self):
        """Each model must have model_id, name, and description."""
        for key, model in AVAILABLE_MODELS.items():
            assert "model_id" in model, f"{key} missing model_id"
            assert "name" in model, f"{key} missing name"
            assert "description" in model, f"{key} missing description"

    def test_default_model_exists(self):
        """Default model key must exist in available models."""
        assert DEFAULT_MODEL_KEY in AVAILABLE_MODELS

    def test_model_ids_use_cross_region_prefix(self):
        """All model IDs should use cross-region inference (us. prefix)."""
        for key, model in AVAILABLE_MODELS.items():
            assert model["model_id"].startswith("us."), (
                f"{key} model_id should start with 'us.' for cross-region inference"
            )


class TestGetModelId:
    """Tests for get_model_id function."""

    def test_valid_key_returns_model_id(self):
        """Valid key returns the correct model ID."""
        result = get_model_id("claude-sonnet-4.6")
        assert result == "us.anthropic.claude-sonnet-4-6"

    def test_invalid_key_raises_value_error(self):
        """Invalid key raises ValueError."""
        with pytest.raises(ValueError, match="Unknown model key"):
            get_model_id("invalid-model")


class TestGetModelName:
    """Tests for get_model_name function."""

    def test_valid_key_returns_name(self):
        """Valid key returns the human-readable name."""
        result = get_model_name("claude-haiku-4.5")
        assert result == "Claude Haiku 4.5"

    def test_invalid_key_raises_value_error(self):
        """Invalid key raises ValueError."""
        with pytest.raises(ValueError, match="Unknown model key"):
            get_model_name("nonexistent")


class TestChatbotSettings:
    """Tests for ChatbotSettings dataclass."""

    def test_default_values(self):
        """Settings should have sensible defaults."""
        settings = ChatbotSettings()
        assert settings.max_tokens == 4096
        assert settings.temperature == 0.7
        assert settings.top_p is None
        assert settings.conversation_history_limit == 20

    def test_custom_values(self):
        """Settings should accept custom values."""
        settings = ChatbotSettings(
            max_tokens=2048,
            temperature=0.5,
            conversation_history_limit=10,
        )
        assert settings.max_tokens == 2048
        assert settings.temperature == 0.5
        assert settings.conversation_history_limit == 10


class TestFlaskSettings:
    """Tests for FlaskSettings dataclass."""

    def test_default_values(self):
        """Flask settings should have sensible defaults."""
        settings = FlaskSettings()
        assert settings.host == "127.0.0.1"
        assert settings.port == 5000
        assert settings.debug is False


class TestAgentCoreSettings:
    """Tests for AgentCoreSettings dataclass."""

    def test_default_values(self):
        """AgentCore settings should default to disabled."""
        settings = AgentCoreSettings()
        assert settings.enabled is False
        assert settings.agent_runtime_arn == ""
        assert settings.region == AWS_REGION

    def test_custom_values(self):
        """AgentCore settings should accept custom values."""
        settings = AgentCoreSettings(
            enabled=True,
            agent_runtime_arn="arn:aws:bedrock-agentcore:us-east-1:123456:runtime/test",
            region="us-west-2",
        )
        assert settings.enabled is True
        assert "test" in settings.agent_runtime_arn
        assert settings.region == "us-west-2"


class TestSystemPrompt:
    """Tests for system prompt configuration."""

    def test_system_prompt_not_empty(self):
        """System prompt should not be empty."""
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_mentions_bedrock(self):
        """System prompt should reference Amazon Bedrock."""
        assert "Amazon Bedrock" in SYSTEM_PROMPT
