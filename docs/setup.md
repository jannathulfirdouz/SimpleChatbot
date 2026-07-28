# Setup Instructions

## Prerequisites

- **Python 3.10+** - Download from [python.org](https://www.python.org/downloads/)
- **AWS Account** - With Amazon Bedrock access enabled
- **AWS CLI** (optional) - For credential configuration

## AWS Configuration

### 1. Enable Bedrock Model Access

1. Sign in to the [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **Amazon Bedrock** > **Model access**
3. Request access to the Anthropic Claude models you want to use:
   - Claude Sonnet 4.6
   - Claude Sonnet 4.5
   - Claude Haiku 4.5
   - Claude Opus 4.5
4. Wait for access to be granted (usually instant for most models)

### 2. Configure AWS Credentials

The chatbot uses the default AWS profile. Configure it using one of these methods:

**Option A: AWS CLI (Recommended)**

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

**Option B: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

**Option C: AWS Credentials File**

Edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

And `~/.aws/config`:

```ini
[default]
region = us-east-1
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SimpleChatbot
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Standard installation
pip install -e .

# With development tools
pip install -e ".[dev]"
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## Running the Application

### CLI Interface

```bash
# Using convenience script (Windows)
scripts\run.bat

# Using convenience script (macOS/Linux)
chmod +x scripts/run.sh
./scripts/run.sh

# Direct execution
python -m simplechatbot.cli
```

### Web Interface

```bash
# Using convenience script (Windows)
scripts\run_web.bat

# Using convenience script (macOS/Linux)
chmod +x scripts/run_web.sh
./scripts/run_web.sh

# Direct execution
python -m simplechatbot.web.app
```

The web interface will be available at `http://127.0.0.1:5000`.

## Troubleshooting

### Common Issues

**"AWS credentials not found"**
- Verify your credentials are configured: `aws sts get-caller-identity`
- Check that the profile name in `.env` matches your configured profile

**"Access denied to model"**
- Ensure you've enabled model access in the Bedrock console
- Verify your IAM user/role has `bedrock:InvokeModel` permissions

**"Module not found"**
- Make sure you've activated the virtual environment
- Reinstall with `pip install -e .`

**Web interface not loading**
- Check that port 5000 is not in use by another application
- Try changing `FLASK_PORT` in your `.env` file
