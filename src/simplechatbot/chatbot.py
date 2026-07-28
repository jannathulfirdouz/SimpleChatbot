"""Core chatbot logic and SimpleChatbot class.

This module implements the SimpleChatbot class that interfaces with
Amazon Bedrock's Converse API to generate responses using Anthropic
Claude models. It manages conversation history and provides methods
for both single responses and interactive chat loops.
"""

import logging
import os
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

from simplechatbot.config import (
    AVAILABLE_MODELS,
    AWS_PROFILE,
    AWS_REGION,
    DEFAULT_MODEL_ID,
    DEFAULT_MODEL_KEY,
    SYSTEM_PROMPT,
    ChatbotSettings,
)

logger = logging.getLogger(__name__)


class SimpleChatbot:
    """A chatbot powered by Amazon Bedrock Anthropic Claude models.

    This class manages the interaction with Amazon Bedrock's Converse API,
    maintaining conversation history and supporting multiple Anthropic models.

    Attributes:
        model_id: The Bedrock model ID currently in use.
        model_key: The short key for the current model.
        settings: ChatbotSettings instance with configuration values.
        conversation_history: List of message dictionaries for context.
    """

    def __init__(
        self,
        model_key: str = DEFAULT_MODEL_KEY,
        settings: Optional[ChatbotSettings] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Initialize the SimpleChatbot.

        Args:
            model_key: Key identifying which Anthropic model to use.
                       Defaults to Claude Sonnet 4.6.
            settings: Optional ChatbotSettings instance. Uses defaults if None.
            system_prompt: Optional custom system prompt. Uses default if None.

        Raises:
            ValueError: If the model_key is not recognized.
            ConnectionError: If AWS credentials cannot be resolved.
        """
        if model_key not in AVAILABLE_MODELS:
            valid_keys = ", ".join(AVAILABLE_MODELS.keys())
            raise ValueError(
                f"Unknown model key '{model_key}'. Valid options: {valid_keys}"
            )

        self.model_key: str = model_key
        self.model_id: str = AVAILABLE_MODELS[model_key]["model_id"]
        self.settings: ChatbotSettings = settings or ChatbotSettings()
        self.system_prompt: str = system_prompt or SYSTEM_PROMPT
        self.conversation_history: List[Dict] = []

        # Initialize the Bedrock Runtime client
        self._client = self._create_bedrock_client()

    def _create_bedrock_client(self):
        """Create and return a boto3 Bedrock Runtime client.

        Returns:
            A boto3 client for the bedrock-runtime service.

        Raises:
            ConnectionError: If credentials cannot be found or profile is invalid.
        """
        try:
            # First try to use environment variables directly
            access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            session_token = os.environ.get('AWS_SESSION_TOKEN')
            region = os.environ.get('AWS_DEFAULT_REGION', AWS_REGION)
            
            # If we have explicit credentials, use them directly
            if access_key and secret_key:
                logger.info("Using AWS credentials from environment variables")
                client = boto3.client(
                    'bedrock-runtime',
                    region_name=region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token if session_token else None
                )
            else:
                # Fallback to profile-based approach
                logger.info("Using AWS profile: %s", AWS_PROFILE)
                session = boto3.Session(
                    profile_name=AWS_PROFILE,
                    region_name=AWS_REGION,
                )
                client = session.client("bedrock-runtime")
            
            logger.info(
                "Bedrock client initialized (region=%s, model=%s)",
                region,
                self.model_id,
            )
            return client
            
        except ProfileNotFound as e:
            raise ConnectionError(
                f"AWS profile '{AWS_PROFILE}' not found. "
                f"Please configure your AWS credentials. Error: {e}"
            ) from e
        except NoCredentialsError as e:
            raise ConnectionError(
                "AWS credentials not found. Please configure your credentials "
                "using 'aws configure' or set appropriate environment variables. "
                f"Error: {e}"
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Failed to initialize Bedrock client: {e}"
            ) from e

    def set_model(self, model_key: str) -> str:
        """Switch to a different Anthropic model.

        Args:
            model_key: The key of the model to switch to.

        Returns:
            The display name of the newly selected model.

        Raises:
            ValueError: If the model_key is not recognized.
        """
        if model_key not in AVAILABLE_MODELS:
            valid_keys = ", ".join(AVAILABLE_MODELS.keys())
            raise ValueError(
                f"Unknown model key '{model_key}'. Valid options: {valid_keys}"
            )

        self.model_key = model_key
        self.model_id = AVAILABLE_MODELS[model_key]["model_id"]
        logger.info("Model switched to: %s (%s)", model_key, self.model_id)
        return AVAILABLE_MODELS[model_key]["name"]

    def get_response(self, user_message: str) -> str:
        """Send a message to the model and get a response.

        This method adds the user message to conversation history,
        calls the Bedrock Converse API, and returns the assistant's response.

        Args:
            user_message: The user's input message.

        Returns:
            The model's response text.

        Raises:
            RuntimeError: If the API call fails or response is malformed.
        """
        if not user_message.strip():
            return "Please enter a message."

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": [{"text": user_message}],
        })

        # Trim history if it exceeds the limit
        self._trim_history()

        try:
            # Build inference config - ONLY include topP if it has a valid value
            inference_config = {
                "maxTokens": self.settings.max_tokens,
                "temperature": self.settings.temperature,
            }
            # Only add topP if it's not None and is a valid number
            if self.settings.top_p is not None and isinstance(self.settings.top_p, (int, float)):
                inference_config["topP"] = float(self.settings.top_p)

            # Call the Bedrock Converse API
            response = self._client.converse(
                modelId=self.model_id,
                messages=self.conversation_history,
                system=[{"text": self.system_prompt}],
                inferenceConfig=inference_config,
            )

            # Extract the assistant's response
            assistant_message = response["output"]["message"]["content"][0]["text"]

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": [{"text": assistant_message}],
            })

            logger.debug(
                "Response received (tokens_in=%s, tokens_out=%s)",
                response.get("usage", {}).get("inputTokens", "N/A"),
                response.get("usage", {}).get("outputTokens", "N/A"),
            )

            return assistant_message

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            # Remove the failed user message from history
            self.conversation_history.pop()

            if error_code == "AccessDeniedException":
                raise RuntimeError(
                    f"Access denied to model '{self.model_id}'. "
                    "Please ensure you have enabled this model in the Amazon Bedrock console. "
                    f"Details: {error_message}"
                ) from e
            elif error_code == "ValidationException":
                raise RuntimeError(
                    f"Invalid request to Bedrock API: {error_message}"
                ) from e
            elif error_code == "ThrottlingException":
                raise RuntimeError(
                    "Request was throttled. Please wait a moment and try again."
                ) from e
            elif error_code == "ModelTimeoutException":
                raise RuntimeError(
                    "The model took too long to respond. Please try again with a shorter message."
                ) from e
            else:
                raise RuntimeError(
                    f"Bedrock API error ({error_code}): {error_message}"
                ) from e

        except Exception as e:
            # Remove the failed user message from history
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()

            raise RuntimeError(
                f"Unexpected error communicating with Bedrock: {e}"
            ) from e

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared.")

    def get_history_length(self) -> int:
        """Get the number of messages in conversation history.

        Returns:
            The number of messages currently stored.
        """
        return len(self.conversation_history)

    def _trim_history(self) -> None:
        """Trim conversation history to stay within the configured limit.

        Removes the oldest message pairs (user + assistant) when the
        history exceeds the conversation_history_limit setting.
        The limit is applied to message pairs (each pair = 2 messages).
        """
        max_messages = self.settings.conversation_history_limit * 2
        if len(self.conversation_history) > max_messages:
            # Remove oldest messages, keeping the most recent ones
            excess = len(self.conversation_history) - max_messages
            self.conversation_history = self.conversation_history[excess:]
            logger.debug(
                "Trimmed %d messages from history. Current length: %d",
                excess,
                len(self.conversation_history),
            )

    def get_current_model_info(self) -> Dict[str, str]:
        """Get information about the currently selected model.

        Returns:
            Dictionary with model_key, model_id, name, and description.
        """
        model_info = AVAILABLE_MODELS[self.model_key].copy()
        model_info["model_key"] = self.model_key
        return model_info


def chat_loop() -> None:
    """Run an interactive chat loop in the terminal.

    This function provides a simple command-line interface for testing
    the chatbot. It handles user input, displays responses, and supports
    commands for switching models, clearing history, and quitting.
    """
    print("\n" + "=" * 60)
    print("  SimpleChatbot - Amazon Bedrock Claude")
    print("=" * 60)
    print("\nCommands:")
    print("  /quit    - Exit the chatbot")
    print("  /clear   - Clear conversation history")
    print("  /model   - Show current model")
    print("  /models  - List available models")
    print("  /switch <key> - Switch to a different model")
    print("-" * 60 + "\n")

    try:
        chatbot = SimpleChatbot()
    except (ConnectionError, ValueError) as e:
        print(f"\nError initializing chatbot: {e}")
        return

    model_info = chatbot.get_current_model_info()
    print(f"Using model: {model_info['name']}")
    print(f"Model ID: {model_info['model_id']}")
    print(f"Type your message or use a command.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower().split()

                if command[0] == "/quit":
                    print("\nGoodbye!")
                    break
                elif command[0] == "/clear":
                    chatbot.clear_history()
                    print("Conversation history cleared.\n")
                    continue
                elif command[0] == "/model":
                    info = chatbot.get_current_model_info()
                    print(f"Current model: {info['name']} ({info['model_id']})\n")
                    continue
                elif command[0] == "/models":
                    print("\nAvailable models:")
                    for key, model in AVAILABLE_MODELS.items():
                        marker = " *" if key == chatbot.model_key else ""
                        print(f"  {key}: {model['name']}{marker}")
                        print(f"    {model['description']}")
                    print()
                    continue
                elif command[0] == "/switch" and len(command) > 1:
                    try:
                        name = chatbot.set_model(command[1])
                        print(f"Switched to: {name}\n")
                    except ValueError as e:
                        print(f"Error: {e}\n")
                    continue
                else:
                    print("Unknown command. Type /quit to exit.\n")
                    continue

            # Get response from the model
            response = chatbot.get_response(user_input)
            print(f"\nAssistant: {response}\n")

        except RuntimeError as e:
            print(f"\nError: {e}\n")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    chat_loop()