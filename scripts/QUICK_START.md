# Quick Start - Main Agent Deployment

Deploy SimpleChatbot's main agent to Amazon Bedrock AgentCore in under 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.10+
- [ ] Node.js 20+
- [ ] AWS CLI configured with valid credentials
- [ ] Bedrock model access enabled (Claude Sonnet 4.6)

## One-Command Setup

```bash
# macOS/Linux
chmod +x scripts/setup_main_agents.sh && ./scripts/setup_main_agents.sh

# Windows
scripts\setup_main_agents.bat
```

## Manual Quick Start

```bash
# 1. Install AgentCore CLI
npm install -g @aws/agentcore

# 2. Navigate to agent directory
cd agents/mainagent

# 3. Test locally
agentcore dev --no-browser

# 4. (In another terminal) Test it works
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'

# 5. Deploy to AWS
agentcore deploy

# 6. Invoke your deployed agent
agentcore invoke '{"prompt": "Hello from SimpleChatbot!"}'
```

## Verify Deployment

```bash
agentcore status
agentcore logs
```

## Cleanup

```bash
agentcore remove all
agentcore deploy
```

For full documentation, see [README.md](README.md).
