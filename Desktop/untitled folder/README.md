# Message-SelfDestructur

A Telegram bot that automatically deletes messages in groups after a customizable time period.

## Features

- 🗑️ Auto-delete messages after set time intervals
- ⏱️ Customizable timer with button interface (10s to 1h)
- 🤖 Easy-to-use commands
- 📊 Status checking
- 🔧 Configurable time options

## Setup

1. **Create a Telegram Bot:**
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram
   - Use `/newbot` command to create a new bot
   - Copy the bot token

2. **Install Dependencies:**
   ```bash
   # Using the setup script (recommended)
   ./setup.sh
   
   # Or manually:
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the Bot:**
   - Edit `.env` file
   - Replace `your_bot_token_here` with your actual bot token

4. **Run the Bot:**
   ```bash
   # Make sure virtual environment is activated
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python bot.py
   ```

## Usage

### Commands:
- `/start` - Start the bot and show welcome message with "Add to Group" button
- `/timer` - Open timer selection menu
- `/status` - Check current timer settings
- `/help` - Show help information

### Welcome Message Features:
- 🆕 **Add to Group button** - Direct link to add bot to any group
- 💬 **Join Our Chat button** - Direct link to https://t.me/last_promise_chatting_212
- 🕐 **Set Timer button** - Quick access to timer settings

### Timer Selection Features:
- ⚙️ **Custom Timer** - Set precise time with +/- buttons for hours, minutes, seconds
- 🎯 **Preset Options** - Quick select from 10s, 30s, 1m, 5m, 10m, 30m, 1h, off

### Timer Options:
- `10s` - 10 seconds
- `30s` - 30 seconds
- `1m` - 1 minute
- `5m` - 5 minutes
- `10m` - 10 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `off` - Disable auto-deletion

## Group Setup

1. Add the bot to your Telegram group
2. Make the bot an **admin** with "Delete messages" permission
3. The bot will automatically start monitoring and deleting messages

## Configuration

Edit `config.py` to customize:
- Default deletion time
- Available time options
- Logging settings

## How It Works

1. The bot monitors all messages in the group
2. When a message is sent, it schedules deletion based on current timer setting
3. Messages are deleted automatically after the specified time
4. Users can change the timer using the `/timer` command

## Requirements

- Python 3.7+
- python-telegram-bot 20.7+
- python-dotenv 1.0.0+

## Note

- The bot needs admin permissions to delete messages
- For production use, consider using a database instead of in-memory storage
- Bot will only work in groups where it has proper permissions
- Make sure only one instance of the bot is running to avoid conflicts