# Edit Checker Bot - Deployment Instructions

## Overview
This is a Telegram bot that automatically monitors and deletes edited messages in groups to maintain transparency and prevent misuse.

## Features
- Automatically detects and deletes edited messages in groups
- Sends warnings to the group (with user ID only)
- Sends detailed alerts to group administrators (with user mentions)
- Includes "Add to Group" button in start command with umbrella symbol (☂︎)

## Deployment Files
- `bot.py` - Main bot application
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (contains bot token)
- `Procfile` - Process configuration for cloud platforms
- `runtime.txt` - Python runtime version
- `deploy.sh` - Automated deployment script
- `render.yaml` - Configuration for Render.com deployment

## Deployment Options

### Option 1: Manual Deployment (Linux/Ubuntu)
1. Upload all files to your server
2. Make the deploy script executable: `chmod +x deploy.sh`
3. Run the deployment script: `./deploy.sh`

### Option 2: Heroku/Render Deployment
1. Create a new app on your preferred platform
2. Connect your GitHub repository or upload the files
3. Set the environment variable `BOT_TOKEN` with your bot token
4. Deploy the application

### Option 3: Docker Deployment
Create a Dockerfile with:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## Environment Variables
- `BOT_TOKEN` - Your Telegram bot token (already configured in .env)

## Requirements
- Python 3.11+
- python-telegram-bot >= 21.0
- python-dotenv == 1.0.0
- psutil >= 5.9.0

## Bot Commands
- `/start` - Welcome message with add to group button
- `/help` - Help information
- `/healthcheck` - Bot status (admin only)

## Important Notes
- The bot must be added as an administrator in groups to delete messages
- Requires "Delete messages" permission
- Works only in groups and supergroups, not private chats
- The .env file contains your bot token - keep it secure!

## Support
For issues or questions, please check the bot's functionality in a test group first.