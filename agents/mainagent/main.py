"""SimpleChatbot Main Agent - Amazon Bedrock AgentCore Runtime Entry Point.

This module implements the main agent for SimpleChatbot using Strands Agents
with BedrockModel, deployed to Amazon Bedrock AgentCore Runtime via the
@app.entrypoint decorator from the bedrock-agentcore SDK.

Endpoints (auto-managed by SDK):
    POST /invocations - Main agent endpoint (AgentCore standard)
    GET /ping - Health check endpoint (AgentCore standard)

Usage:
    Local testing:
        python main.py
        curl -X POST http://localhost:8080/invocations \\
            -H "Content-Type: application/json" \\
            -d '{"prompt": "Hello!"}'

    Deploy to AgentCore:
        agentcore deploy
"""

import logging
import sys
from typing import Any, Dict

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("mainagent")

# ---------------------------------------------------------------------------
# Agent Configuration
# ---------------------------------------------------------------------------

MODEL_ID = "us.anthropic.claude-sonnet-4-6"
AWS_REGION = "us-east-1"

SYSTEM_PROMPT = (
    "You are a helpful, knowledgeable, and friendly AI assistant powered by Amazon Bedrock. "
    "You provide clear, accurate, and concise answers to user questions. "
    "When you don't know something, you say so honestly rather than guessing. "
    "You format your responses with appropriate structure when helpful, "
    "using bullet points, numbered lists, or code blocks as needed. "
    "You maintain a professional yet approachable tone throughout the conversation."
)

# ---------------------------------------------------------------------------
# Initialize Application and Agent
# ---------------------------------------------------------------------------

app = BedrockAgentCoreApp()

model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
)

logger.info("Main agent initialized (model=%s, region=%s)", MODEL_ID, AWS_REGION)

# ---------------------------------------------------------------------------
# Agent Entry Point
# ---------------------------------------------------------------------------


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process user input and return a response from the agent.

    This function is decorated with @app.entrypoint which registers it
    as the handler for POST /invocations requests on AgentCore Runtime.

    Args:
        payload: JSON request body containing:
            - prompt (str): The user's message text.

    Returns:
        Dictionary with the agent's response:
            - result (str): The agent's response message.

    Raises:
        Returns error response dict on failure (does not raise).
    """
    logger.info("Received invocation request")

    # Extract prompt from payload
    prompt = payload.get("prompt", "")

    if not prompt or not prompt.strip():
        logger.warning("Empty or missing prompt in request")
        return {
            "error": "No prompt found in input. Please provide a JSON payload with a 'prompt' key.",
            "status": "error",
        }

    try:
        logger.info("Processing prompt (length=%d chars)", len(prompt))

        # Invoke the Strands agent
        result = agent(prompt)

        logger.info("Response generated successfully")

        return {
            "result": result.message,
            "model": MODEL_ID,
            "status": "success",
        }

    except Exception as e:
        logger.error("Agent processing failed: %s", str(e), exc_info=True)
        return {
            "error": f"Agent processing failed: {str(e)}",
            "status": "error",
        }


# ---------------------------------------------------------------------------
# Local Execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting main agent locally on port 8080...")
    app.run()
