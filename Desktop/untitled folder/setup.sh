#!/bin/bash

# Telegram Self-Destruct Bot Setup Script

echo "🤖 Setting up Telegram Self-Destruct Bot..."
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python version: $PYTHON_VERSION"

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your BOT_TOKEN:"
    echo "BOT_TOKEN=your_telegram_bot_token_here"
    exit 1
fi

# Check if bot token is set
BOT_TOKEN=$(grep "BOT_TOKEN=" .env | cut -d'=' -f2)

if [ "$BOT_TOKEN" = "your_bot_token_here" ] || [ -z "$BOT_TOKEN" ]; then
    echo "❌ Bot token not configured!"
    echo "Please edit .env file and add your Telegram bot token."
    echo "Get your token from @BotFather on Telegram."
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the bot:"
echo "   python bot.py"
echo ""
echo "📝 Bot Commands:"
echo "   /start  - Start the bot"
echo "   /timer  - Set deletion timer"
echo "   /status - Check current settings"
echo "   /help   - Show help"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Add the bot to your Telegram group"
echo "   2. Make it admin with 'Delete messages' permission"