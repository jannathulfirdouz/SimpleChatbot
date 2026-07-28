# Main Agent Deployment Guide

Complete guide for deploying SimpleChatbot's main agent to Amazon Bedrock AgentCore Runtime using the AgentCore CLI.

## Architecture

```
Web GUI / CLI → chatbot.py → AgentCore Runtime → mainagent (Strands) → Bedrock API
```

The main agent runs as a managed service on AgentCore Runtime, providing:
- Automatic scaling and session management
- IAM-based authentication (SigV4)
- CloudWatch logging and observability
- Health checks via `/ping` endpoint

## Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| AWS CLI | 2.x | [AWS CLI Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| AWS CDK | 2.x | `npm install -g aws-cdk` |
| uv (optional) | latest | `pip install uv` |

### AWS Credentials

Ensure your credentials are configured and valid:

```bash
aws configure
aws sts get-caller-identity
```

### Developer IAM Permissions

The developer running the AgentCore CLI needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:*",
                "bedrock:InvokeModel",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:GetRole",
                "cloudformation:*",
                "ecr:*",
                "logs:*",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

> **Note**: For production, scope these permissions down to specific resources.

## Setup & Deployment

### Full Setup (Recommended for first time)

```bash
# macOS/Linux
chmod +x scripts/setup_main_agents.sh
./scripts/setup_main_agents.sh

# Windows
scripts\setup_main_agents.bat
```

This will:
1. Validate all prerequisites
2. Install the AgentCore CLI (`@aws/agentcore`)
3. Scaffold the agent project with `agentcore create`
4. Verify agent code and dependencies
5. Prompt for deployment

### Local Development Only

```bash
# macOS/Linux
./scripts/setup_main_agents.sh dev

# Windows
scripts\setup_main_agents.bat dev
```

Starts the agent locally on port 8080 with hot-reload.

### Deploy Only (Skip scaffold)

```bash
# macOS/Linux
./scripts/setup_main_agents.sh deploy

# Windows
scripts\setup_main_agents.bat deploy
```

## AgentCore CLI Commands

| Command | Description |
|---------|-------------|
| `agentcore create` | Scaffold a new agent project (interactive wizard) |
| `agentcore dev` | Start local dev server with hot-reload and inspector |
| `agentcore deploy` | Deploy agent to AWS via CDK |
| `agentcore invoke '{"prompt": "Hello!"}'` | Test agent invocation |
| `agentcore status` | Show deployed resource details |
| `agentcore logs` | Stream or search agent runtime logs |
| `agentcore remove all` | Remove resources (follow with `deploy` to tear down) |

## Testing Locally

1. Start the local dev server:
   ```bash
   cd agents/mainagent
   agentcore dev --no-browser
   ```

2. In another terminal, test the agent:
   ```bash
   # Health check
   curl http://localhost:8080/ping

   # Send a message
   curl -X POST http://localhost:8080/invocations \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What is Amazon Bedrock?"}'
   ```

3. Expected response:
   ```json
   {
     "result": "Amazon Bedrock is a fully managed service...",
     "model": "us.anthropic.claude-sonnet-4-6",
     "status": "success"
   }
   ```

## Invoking the Deployed Agent

After deployment, invoke your agent:

```bash
# Using AgentCore CLI
agentcore invoke '{"prompt": "Hello from SimpleChatbot!"}'

# Using curl with IAM auth (via AWS SigV4)
# The agentcore CLI handles auth automatically
```

## Monitoring

```bash
# Check deployment status
agentcore status

# Stream live logs
agentcore logs

# Search logs for errors
agentcore logs --filter "ERROR"
```

## Configuration Options

### Memory Modes

When creating with `agentcore create`, you can choose:
- `none` - No persistent memory (default for SimpleChatbot)
- `short-term` - Session-based memory
- `long-term` - Persistent summarized memory

### Network Configuration

- `PUBLIC` - Internet-accessible (default for development)
- `VPC` - Private VPC deployment (production)

### Lifecycle Settings

Configure in `agentcore/agentcore.json`:
- Idle timeout
- Max concurrent sessions
- Auto-scaling parameters

## Troubleshooting

### "AgentCore CLI not found"

```bash
npm install -g @aws/agentcore
```

### "Access Denied" during deploy

- Verify your IAM permissions include `bedrock-agentcore:*`
- Check that CDK has been bootstrapped: `cdk bootstrap`
- Ensure the model is enabled in the Bedrock console

### "Port 8080 already in use" (local dev)

```bash
# Find and kill the process using port 8080
# macOS/Linux:
lsof -ti:8080 | xargs kill -9

# Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### "Model access denied"

1. Go to the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/)
2. Navigate to Model access
3. Enable Claude Sonnet 4.6

### "CDK bootstrap required"

```bash
cdk bootstrap aws://ACCOUNT_ID/REGION
```

### Agent returns empty response

- Check CloudWatch logs: `agentcore logs`
- Verify the prompt is non-empty in your request
- Test locally first with `agentcore dev`

## Security Best Practices

- Use IAM roles with least-privilege permissions
- Never hardcode credentials in agent code
- Use VPC mode for production deployments
- Enable CloudWatch logging for audit trails
- Rotate credentials regularly
- Use AWS Secrets Manager for any API keys

## Cleanup

To remove deployed resources:

```bash
agentcore remove all
agentcore deploy  # This tears down the removed resources
```
