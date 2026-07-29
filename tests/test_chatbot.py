"""Tests for simplechatbot.chatbot module."""

from unittest.mock import MagicMock, patch

import pytest

from simplechatbot.chatbot import SimpleChatbot
from simplechatbot.config import AVAILABLE_MODELS, AgentCoreSettings, ChatbotSettings


class TestSimpleChatbotInit:
    """Tests for SimpleChatbot initialization."""

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_init_default_model(self, mock_client):
        """Should initialize with default model (Claude Sonnet 4.6)."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        assert chatbot.model_key == "claude-sonnet-4.6"
        assert chatbot.model_id == "us.anthropic.claude-sonnet-4-6"
        assert chatbot._mode == "direct"

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_init_custom_model(self, mock_client):
        """Should initialize with a specified model."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot(model_key="claude-haiku-4.5")
        assert chatbot.model_key == "claude-haiku-4.5"
        assert chatbot.model_id == "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    def test_init_invalid_model_raises(self):
        """Should raise ValueError for unknown model key."""
        with pytest.raises(ValueError, match="Unknown model key"):
            SimpleChatbot(model_key="invalid-model")

    @patch("simplechatbot.chatbot.SimpleChatbot._create_agentcore_client")
    def test_init_agentcore_mode(self, mock_client):
        """Should initialize in AgentCore mode when enabled."""
        mock_client.return_value = MagicMock()
        settings = AgentCoreSettings(
            enabled=True,
            agent_runtime_arn="arn:aws:bedrock-agentcore:us-east-1:123:runtime/test",
        )
        chatbot = SimpleChatbot(agentcore_settings=settings)
        assert chatbot._mode == "agentcore"
        assert chatbot._agentcore_client is not None
        assert chatbot._client is None

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_init_agentcore_disabled(self, mock_client):
        """Should use direct mode when AgentCore is disabled."""
        mock_client.return_value = MagicMock()
        settings = AgentCoreSettings(enabled=False)
        chatbot = SimpleChatbot(agentcore_settings=settings)
        assert chatbot._mode == "direct"


class TestSimpleChatbotSetModel:
    """Tests for model switching."""

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_switch_to_valid_model(self, mock_client):
        """Should switch to a valid model and return its name."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        name = chatbot.set_model("claude-opus-4.5")
        assert name == "Claude Opus 4.5"
        assert chatbot.model_key == "claude-opus-4.5"

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_switch_to_invalid_model(self, mock_client):
        """Should raise ValueError for invalid model key."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        with pytest.raises(ValueError, match="Unknown model key"):
            chatbot.set_model("nonexistent")


class TestSimpleChatbotGetResponse:
    """Tests for get_response method."""

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_empty_message_returns_prompt(self, mock_client):
        """Empty message should return a prompt to enter something."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        result = chatbot.get_response("   ")
        assert "Please enter a message" in result

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_successful_response(self, mock_client):
        """Should return model response and update history."""
        mock_bedrock = MagicMock()
        mock_bedrock.converse.return_value = {
            "output": {
                "message": {
                    "content": [{"text": "Hello! How can I help?"}]
                }
            },
            "usage": {"inputTokens": 50, "outputTokens": 10},
        }
        mock_client.return_value = mock_bedrock

        chatbot = SimpleChatbot()
        response = chatbot.get_response("Hi there")

        assert response == "Hello! How can I help?"
        assert len(chatbot.conversation_history) == 2
        assert chatbot.conversation_history[0]["role"] == "user"
        assert chatbot.conversation_history[1]["role"] == "assistant"

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_api_error_removes_message_from_history(self, mock_client):
        """On API error, the failed user message should be removed from history."""
        from botocore.exceptions import ClientError

        mock_bedrock = MagicMock()
        mock_bedrock.converse.side_effect = ClientError(
            {"Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}},
            "Converse",
        )
        mock_client.return_value = mock_bedrock

        chatbot = SimpleChatbot()
        with pytest.raises(RuntimeError, match="throttled"):
            chatbot.get_response("test message")

        assert len(chatbot.conversation_history) == 0


class TestSimpleChatbotHistory:
    """Tests for conversation history management."""

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_clear_history(self, mock_client):
        """clear_history should empty the conversation history."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        chatbot.conversation_history = [
            {"role": "user", "content": [{"text": "test"}]},
            {"role": "assistant", "content": [{"text": "response"}]},
        ]
        chatbot.clear_history()
        assert len(chatbot.conversation_history) == 0

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_get_history_length(self, mock_client):
        """get_history_length should return correct count."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        assert chatbot.get_history_length() == 0
        chatbot.conversation_history.append({"role": "user", "content": [{"text": "hi"}]})
        assert chatbot.get_history_length() == 1

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_trim_history(self, mock_client):
        """History should be trimmed when exceeding limit."""
        mock_client.return_value = MagicMock()
        settings = ChatbotSettings(conversation_history_limit=2)
        chatbot = SimpleChatbot(settings=settings)

        # Add 6 messages (3 pairs), limit is 2 pairs (4 messages)
        for i in range(6):
            role = "user" if i % 2 == 0 else "assistant"
            chatbot.conversation_history.append(
                {"role": role, "content": [{"text": f"msg {i}"}]}
            )

        chatbot._trim_history()
        # Should keep only 4 messages (2 pairs)
        assert len(chatbot.conversation_history) == 4
        # Should keep the most recent messages
        assert chatbot.conversation_history[0]["content"][0]["text"] == "msg 2"


class TestSimpleChatbotModelInfo:
    """Tests for model info retrieval."""

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_get_current_model_info(self, mock_client):
        """Should return complete model info including mode."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        info = chatbot.get_current_model_info()
        assert info["model_key"] == "claude-sonnet-4.6"
        assert info["name"] == "Claude Sonnet 4.6"
        assert info["model_id"] == "us.anthropic.claude-sonnet-4-6"
        assert info["mode"] == "direct"
        assert "description" in info

    @patch("simplechatbot.chatbot.SimpleChatbot._create_bedrock_client")
    def test_get_mode_direct(self, mock_client):
        """get_mode should return 'direct' in direct mode."""
        mock_client.return_value = MagicMock()
        chatbot = SimpleChatbot()
        assert chatbot.get_mode() == "direct"
