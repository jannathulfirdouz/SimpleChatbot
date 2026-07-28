"""Flask application and routes for SimpleChatbot web interface.

This module provides the web-based chat interface with API endpoints
for sending messages, switching models, and managing conversation history.
"""

import logging
import webbrowser
from threading import Timer
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from simplechatbot.chatbot import SimpleChatbot
from simplechatbot.config import AVAILABLE_MODELS, FlaskSettings

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)

# Global chatbot instance (created on first request)
_chatbot: SimpleChatbot | None = None


def get_chatbot() -> SimpleChatbot:
    """Get or create the global chatbot instance.

    Returns:
        The SimpleChatbot instance.

    Raises:
        RuntimeError: If the chatbot cannot be initialized.
    """
    global _chatbot
    if _chatbot is None:
        try:
            _chatbot = SimpleChatbot()
            logger.info("Chatbot instance created successfully.")
        except (ConnectionError, ValueError) as e:
            logger.error("Failed to initialize chatbot: %s", e)
            raise RuntimeError(f"Failed to initialize chatbot: {e}") from e
    return _chatbot


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Render the main chat interface."""
    models = [
        {"key": key, "name": model["name"], "description": model["description"]}
        for key, model in AVAILABLE_MODELS.items()
    ]
    return render_template("index.html", models=models)


@app.route("/api/chat", methods=["POST"])
def chat() -> tuple[Dict[str, Any], int]:
    """Handle chat message and return model response.

    Request JSON:
        message (str): The user's message text.

    Returns:
        JSON response with the assistant's reply or error message.
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field in request body."}), 400

    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        chatbot = get_chatbot()
        response = chatbot.get_response(message)
        return jsonify({
            "response": response,
            "model": chatbot.get_current_model_info()["name"],
            "history_length": chatbot.get_history_length(),
        }), 200
    except RuntimeError as e:
        logger.error("Chat error: %s", e)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/api/model", methods=["GET"])
def get_model() -> tuple[Dict[str, Any], int]:
    """Get the current model information.

    Returns:
        JSON with current model details.
    """
    try:
        chatbot = get_chatbot()
        info = chatbot.get_current_model_info()
        return jsonify({"model": info}), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/model", methods=["POST"])
def switch_model() -> tuple[Dict[str, Any], int]:
    """Switch to a different Anthropic model.

    Request JSON:
        model_key (str): The key of the model to switch to.

    Returns:
        JSON confirming the model switch or error message.
    """
    data = request.get_json()

    if not data or "model_key" not in data:
        return jsonify({"error": "Missing 'model_key' field in request body."}), 400

    model_key = data["model_key"].strip()

    try:
        chatbot = get_chatbot()
        name = chatbot.set_model(model_key)
        return jsonify({
            "message": f"Switched to {name}",
            "model": chatbot.get_current_model_info(),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["DELETE"])
def clear_history() -> tuple[Dict[str, Any], int]:
    """Clear the conversation history.

    Returns:
        JSON confirming the history was cleared.
    """
    try:
        chatbot = get_chatbot()
        chatbot.clear_history()
        return jsonify({"message": "Conversation history cleared."}), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models", methods=["GET"])
def list_models() -> tuple[Dict[str, Any], int]:
    """List all available models.

    Returns:
        JSON with list of available models and the current model key.
    """
    try:
        chatbot = get_chatbot()
        models = [
            {
                "key": key,
                "name": model["name"],
                "model_id": model["model_id"],
                "description": model["description"],
                "active": key == chatbot.model_key,
            }
            for key, model in AVAILABLE_MODELS.items()
        ]
        return jsonify({"models": models, "current": chatbot.model_key}), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check() -> tuple[Dict[str, Any], int]:
    """Health check endpoint.

    Returns:
        JSON with application health status.
    """
    return jsonify({"status": "healthy", "application": "SimpleChatbot"}), 200


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------


def open_browser(host: str, port: int) -> None:
    """Open the default web browser to the application URL.

    Args:
        host: The host address.
        port: The port number.
    """
    url = f"http://{host}:{port}"
    webbrowser.open(url)


def main() -> None:
    """Main entry point for the web application.

    Starts the Flask development server and opens the browser.
    """
    settings = FlaskSettings()

    print("\n" + "=" * 50)
    print("  SimpleChatbot Web Interface")
    print("  Build the Builder Workshop")
    print("=" * 50)
    print(f"\n  Starting server at http://{settings.host}:{settings.port}")
    print("  Press Ctrl+C to stop the server.\n")

    # Open browser after a short delay to allow server to start
    if not settings.debug:
        Timer(1.5, open_browser, args=[settings.host, settings.port]).start()

    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
    )


if __name__ == "__main__":
    main()
