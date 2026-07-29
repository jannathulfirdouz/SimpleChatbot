"""Tests for simplechatbot.web.app module."""

from unittest.mock import MagicMock, patch

import pytest

from simplechatbot.web.app import app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check(self, client):
        """Health check should return 200 with status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["application"] == "SimpleChatbot"


class TestModelsEndpoint:
    """Tests for the /api/models endpoint."""

    @patch("simplechatbot.web.app.get_chatbot")
    def test_list_models(self, mock_get_chatbot, client):
        """Should return list of available models."""
        mock_chatbot = MagicMock()
        mock_chatbot.model_key = "claude-sonnet-4.6"
        mock_get_chatbot.return_value = mock_chatbot

        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.get_json()
        assert "models" in data
        assert "current" in data
        assert len(data["models"]) == 4


class TestChatEndpoint:
    """Tests for the /api/chat endpoint."""

    @patch("simplechatbot.web.app.get_chatbot")
    def test_chat_missing_message(self, mock_get_chatbot, client):
        """Should return 400 if message field is missing."""
        response = client.post("/api/chat", json={})
        assert response.status_code == 400

    @patch("simplechatbot.web.app.get_chatbot")
    def test_chat_empty_message(self, mock_get_chatbot, client):
        """Should return 400 if message is empty."""
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 400

    @patch("simplechatbot.web.app.get_chatbot")
    def test_chat_successful(self, mock_get_chatbot, client):
        """Should return 200 with response on success."""
        mock_chatbot = MagicMock()
        mock_chatbot.get_response.return_value = "Hello! How can I help?"
        mock_chatbot.get_current_model_info.return_value = {"name": "Claude Sonnet 4.6"}
        mock_chatbot.get_history_length.return_value = 2
        mock_get_chatbot.return_value = mock_chatbot

        response = client.post("/api/chat", json={"message": "Hi there"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["response"] == "Hello! How can I help?"

    @patch("simplechatbot.web.app.get_chatbot")
    def test_chat_runtime_error(self, mock_get_chatbot, client):
        """Should return 500 on RuntimeError."""
        mock_chatbot = MagicMock()
        mock_chatbot.get_response.side_effect = RuntimeError("Model unavailable")
        mock_get_chatbot.return_value = mock_chatbot

        response = client.post("/api/chat", json={"message": "Hi"})
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data


class TestModelSwitchEndpoint:
    """Tests for POST /api/model endpoint."""

    @patch("simplechatbot.web.app.get_chatbot")
    def test_switch_model_missing_key(self, mock_get_chatbot, client):
        """Should return 400 if model_key is missing."""
        response = client.post("/api/model", json={})
        assert response.status_code == 400

    @patch("simplechatbot.web.app.get_chatbot")
    def test_switch_model_success(self, mock_get_chatbot, client):
        """Should return 200 on successful model switch."""
        mock_chatbot = MagicMock()
        mock_chatbot.set_model.return_value = "Claude Haiku 4.5"
        mock_chatbot.get_current_model_info.return_value = {
            "model_key": "claude-haiku-4.5",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "name": "Claude Haiku 4.5",
            "description": "Fast and efficient",
            "mode": "direct",
        }
        mock_get_chatbot.return_value = mock_chatbot

        response = client.post("/api/model", json={"model_key": "claude-haiku-4.5"})
        assert response.status_code == 200
        data = response.get_json()
        assert "Switched to" in data["message"]


class TestClearHistoryEndpoint:
    """Tests for DELETE /api/history endpoint."""

    @patch("simplechatbot.web.app.get_chatbot")
    def test_clear_history(self, mock_get_chatbot, client):
        """Should return 200 and clear history."""
        mock_chatbot = MagicMock()
        mock_get_chatbot.return_value = mock_chatbot

        response = client.delete("/api/history")
        assert response.status_code == 200
        data = response.get_json()
        assert "cleared" in data["message"].lower()
        mock_chatbot.clear_history.assert_called_once()
