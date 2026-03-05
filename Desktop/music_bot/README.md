# 🎵 Telegram Music VC Bot

A fully functional Telegram music bot that plays songs in voice chats using an assistant account. The bot can send messages to group chats while the assistant joins the voice chat to play music.

## ✨ Features

- 🎵 **Play Music** - Play songs from YouTube, Spotify links, or search by name
- 📋 **Queue System** - Add multiple songs to queue and manage playback
- 🎙️ **Voice Chat Integration** - Assistant account joins VC automatically
- 📢 **Group Messaging** - Bot sends now playing info and updates in group chat
- ⏯️ **Playback Controls** - Pause, resume, skip, and stop functionality
- 🔊 **Volume Control** - Adjust playback volume
- 👥 **Multi-User Support** - Anyone in group can request songs
- 🛡️ **Admin Commands** - Special commands for group admins
- 📊 **Queue Display** - View current queue with song details
- 🔄 **Auto Play Next** - Automatically plays next song when current ends
- ⚡ **Fast Response** - Optimized for quick processing

## 📁 Project Structure

```
music_bot/
├── bot.py                  # Main bot file with all commands
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── utils/
│   ├── __init__.py
│   ├── assistant.py       # Assistant client for voice chat operations
│   ├── music_player.py    # Music player and queue management
│   └── decorators.py      # Authorization and admin check decorators
└── README.md              # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Telegram account (for assistant)
- API ID and API Hash from [my.telegram.org](https://my.telegram.org/apps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install FFmpeg

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add to system PATH

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Step 3: Get Telegram Credentials

1. **Create a Bot:**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Save the `BOT_TOKEN`

2. **Get API Credentials:**
   - Go to https://my.telegram.org/apps
   - Log in with your phone number
   - Create a new application
   - Copy your `API_ID` and `API_HASH`

3. **Get Your User ID:**
   - Message [@userinfobot](https://t.me/userinfobot)
   - It will reply with your user ID

### Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your credentials:
```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
API_ID=12345678
API_HASH=your_api_hash_here

# Assistant Account (Your Personal Account)
ASSISTANT_API_ID=12345678
ASSISTANT_API_HASH=your_api_hash_here
ASSISTANT_PHONE=+1234567890

# Owner Configuration
OWNER_ID=your_telegram_user_id

# Optional
SUDO_USERS=123456789 987654321
MAX_DURATION_MINUTES=60
```

### Step 5: Run the Bot

```bash
python bot.py
```

## 📖 Usage

### Initial Setup in Group

1. **Add the bot to your group**
2. **Make the bot an admin** (required for sending messages)
3. **Start a voice chat** in your group
4. **Use /play command** to start playing music

The assistant account will automatically join the voice chat and play music!

### Bot Commands

#### Basic Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help and all available commands
- `/ping` - Check bot response time

#### Music Commands

- `/play [song name/url]` - Play a song (supports YouTube links, Spotify, or search query)
- `/pause` - Pause the current song (admin only)
- `/resume` - Resume paused song (admin only)
- `/skip` - Skip to the next song
- `/stop` - Stop playback and clear queue (admin only)
- `/queue` - Show the current song queue
- `/current` - Show currently playing song
- `/vc` - Check voice chat status

### Example Usage

```
/play Despacito
/play https://www.youtube.com/watch?v=kJQP7kiw5Fk
/pause
/resume
/skip
/queue
/stop
```

## ⚙️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Bot token from @BotFather | Required |
| `API_ID` | Telegram API ID | Required |
| `API_HASH` | Telegram API Hash | Required |
| `ASSISTANT_API_ID` | Assistant API ID | Required |
| `ASSISTANT_API_HASH` | Assistant API Hash | Required |
| `ASSISTANT_PHONE` | Assistant phone number | Required |
| `OWNER_ID` | Bot owner's Telegram ID | Required |
| `SUDO_USERS` | Authorized users (space-separated) | Optional |
| `MAX_DURATION_MINUTES` | Max song duration | 60 |
| `LOG_GROUP_ID` | Group ID for logs | Optional |

## 🔧 Troubleshooting

### Common Issues

**1. Assistant can't join voice chat:**
- Make sure there's an active voice chat in the group
- Ensure the assistant account is a member of the group
- Check if the assistant has permissions to join

**2. Music not playing:**
- Verify FFmpeg is installed correctly
- Check if the downloaded file exists and is accessible
- Ensure the assistant is in the voice chat

**3. Bot not responding:**
- Check if bot token is correct
- Verify the bot is added to the group
- Ensure bot has admin privileges

**4. "Song too long" error:**
- Increase `MAX_DURATION_MINUTES` in `.env`
- Try playing a shorter song

### Logs

Check the console output for detailed logs. The bot logs:
- Connection status
- Song downloads
- Playback events
- Errors and warnings

## 📝 Notes

- The assistant account must be a member of the group to join voice chats
- Voice chats must be started manually before the bot can join
- Maximum queue size is 100 songs by default
- Songs are downloaded temporarily and deleted after playback
- The bot works best in groups with proper admin permissions

## 🛡️ Security

- Keep your `.env` file private and never commit it to version control
- Don't share your API credentials or bot token
- Only trusted users should have sudo access
- Use appropriate privacy settings for your assistant account

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review the code comments
- Contact the maintainer

## 🎉 Credits

- Built with [Pyrogram](https://github.com/pyrogram/pyrogram)
- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for audio extraction
- Powered by [FFmpeg](https://ffmpeg.org/) for audio processing

---

**Made with ❤️ for music lovers**

Enjoy your music! 🎵
