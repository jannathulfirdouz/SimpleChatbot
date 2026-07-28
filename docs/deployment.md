# Deployment Guide

## Overview

This guide covers deploying SimpleChatbot to various environments. The application consists of a Flask web server that communicates with Amazon Bedrock.

## Production Considerations

### Security

- **Never commit `.env` files** or AWS credentials to version control
- Use IAM roles instead of access keys in production environments
- Enable HTTPS with a reverse proxy (Nginx, ALB)
- Set `FLASK_DEBUG=false` in production
- Consider adding rate limiting and authentication

### IAM Permissions

The application requires the following IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-*"
            ]
        }
    ]
}
```

---

## Deployment Options

### Option 1: EC2 Instance

1. **Launch an EC2 instance** (Amazon Linux 2023 or Ubuntu)

2. **Install dependencies:**
   ```bash
   sudo yum install python3.11 python3.11-pip git -y  # Amazon Linux
   # or
   sudo apt install python3.11 python3.11-venv git -y  # Ubuntu
   ```

3. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd SimpleChatbot
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -e .
   pip install gunicorn
   ```

4. **Configure IAM role** on the EC2 instance (preferred over access keys)

5. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 "simplechatbot.web.app:app"
   ```

6. **Setup systemd service** (`/etc/systemd/system/simplechatbot.service`):
   ```ini
   [Unit]
   Description=SimpleChatbot Web Application
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/SimpleChatbot
   Environment="PATH=/home/ec2-user/SimpleChatbot/venv/bin"
   ExecStart=/home/ec2-user/SimpleChatbot/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 "simplechatbot.web.app:app"
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable simplechatbot
   sudo systemctl start simplechatbot
   ```

### Option 2: AWS App Runner

1. **Create a `Procfile`:**
   ```
   web: gunicorn -w 4 -b 0.0.0.0:8080 "simplechatbot.web.app:app"
   ```

2. **Deploy via AWS Console** or CLI:
   - Source: GitHub repository
   - Runtime: Python 3.11
   - Build command: `pip install -e . && pip install gunicorn`
   - Start command: `gunicorn -w 4 -b 0.0.0.0:8080 "simplechatbot.web.app:app"`

3. **Configure IAM access role** with Bedrock permissions

### Option 3: Docker Container

1. **Create `Dockerfile`:**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY . .

   RUN pip install --no-cache-dir -e . gunicorn

   EXPOSE 8000

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "simplechatbot.web.app:app"]
   ```

2. **Build and run:**
   ```bash
   docker build -t simplechatbot .
   docker run -p 8000:8000 \
     -e AWS_ACCESS_KEY_ID=... \
     -e AWS_SECRET_ACCESS_KEY=... \
     -e AWS_REGION=us-east-1 \
     simplechatbot
   ```

3. **Push to ECR and deploy to ECS/Fargate** for production use.

### Option 4: AWS Lambda with API Gateway

For serverless deployment, wrap the Flask app with a Lambda adapter:

1. **Install adapter:**
   ```bash
   pip install mangum
   ```

2. **Create `lambda_handler.py`:**
   ```python
   from mangum import Mangum
   from simplechatbot.web.app import app

   handler = Mangum(app)
   ```

3. **Deploy with AWS SAM or CDK**

---

## Nginx Reverse Proxy

For production, place Nginx in front of Gunicorn:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

## Monitoring

- Use the `/health` endpoint for load balancer health checks
- Configure CloudWatch alarms for Bedrock API errors
- Monitor application logs for RuntimeError entries
- Track response times and token usage via CloudWatch metrics

## Scaling

- **Horizontal**: Add more Gunicorn workers or ECS tasks
- **Session state**: Current implementation uses in-memory conversation history; for multi-instance deployments, consider using DynamoDB or ElastiCache for session state
- **Rate limiting**: Implement per-user rate limiting to control Bedrock API costs

---

## Option 5: Amazon Bedrock AgentCore Runtime (Recommended)

Deploy the chatbot as a managed agent on AgentCore Runtime using the Strands Agents framework and the AgentCore CLI.

### Architecture

```
Web GUI / CLI → chatbot.py → AgentCore Runtime → mainagent (Strands) → Bedrock API
```

### Prerequisites

- Node.js 20+ (for AgentCore CLI)
- Python 3.10+
- AWS CLI with valid credentials
- Claude Sonnet 4.6 model access enabled in Bedrock console

### Quick Deploy

```bash
# Install AgentCore CLI
npm install -g @aws/agentcore

# Navigate to the agent directory
cd agents/mainagent

# Test locally first
agentcore dev --no-browser

# Deploy to AWS
agentcore deploy

# Invoke your deployed agent
agentcore invoke '{"prompt": "Hello from SimpleChatbot!"}'
```

### Or use the setup script:

```bash
# macOS/Linux
chmod +x scripts/setup_main_agents.sh
./scripts/setup_main_agents.sh

# Windows
scripts\setup_main_agents.bat
```

### Monitoring and Logs

```bash
# Check deployment status
agentcore status

# Stream live logs
agentcore logs

# Search logs for errors
agentcore logs --filter "ERROR"
```

### Key Endpoints (Auto-managed by SDK)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/invocations` | POST | Main agent endpoint |
| `/ping` | GET | Health check |

### Request Format

```json
{
    "prompt": "What is Amazon Bedrock?"
}
```

### Response Format

```json
{
    "result": "Amazon Bedrock is a fully managed service...",
    "model": "us.anthropic.claude-sonnet-4-6",
    "status": "success"
}
```

### Cleanup

```bash
agentcore remove all
agentcore deploy  # Tears down removed resources
```

For full deployment documentation, see [scripts/README.md](../scripts/README.md).
