# Edit_checker

# Telegram Edit Checker Bot

A Telegram bot that monitors group messages and automatically deletes any edited messages, while warning the user who edited them.

## Features

- 🚫 Automatically deletes edited messages in groups
- ⚠️ Sends a warning to users who edit messages
- 👥 Works for all users (members, admins, etc.)
- 🔄 Auto-deletes warning messages after 10 seconds

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token:
   ```
   BOT_TOKEN=your_actual_bot_token_here
   ```

### 4. Add Bot to Your Group

1. Add the bot to your Telegram group
2. Make sure to give the bot **admin privileges** with permission to:
   - Delete messages
   - Send messages

### 5. Run the Bot Locally

```bash
python bot.py
```

## Deployment

### Deploy to Render

1. Fork this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Worker" (**Important**: Must be Worker, not Web Service)
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: telegram-edit-checker-bot
   - **Runtime**: Python 3
   - **Region**: Choose your preferred region
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Auto Deploy**: Disable (set to false)
6. Add environment variable:
   - **Key**: `BOT_TOKEN`
   - **Value**: Your Telegram bot token
7. Click "Create Worker"

**Important**: Workers don't need open ports, so ignore any port scanning messages.
The bot will automatically start and stay online 24/7.

## How It Works

- The bot monitors all messages in groups where it's added
- When any user (member or admin) edits a message, the bot:
  1. Immediately deletes the edited message
  2. Sends a warning message to the group
  3. Automatically deletes the warning after 10 seconds

## Requirements

- Python 3.8 or higher
- A Telegram bot token from BotFather
- Admin permissions in the group (to delete messages)

## Notes

- The bot only works in groups and supergroups
- The bot needs admin permissions to delete messages
- Warning messages are automatically deleted after 10 seconds to keep the chat clean

## Troubleshooting

- **Bot not deleting messages**: Make sure the bot has admin permissions with "Delete messages" enabled
- **Bot not responding**: Check that your BOT_TOKEN is correct in the `.env` file
- **Import errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`
