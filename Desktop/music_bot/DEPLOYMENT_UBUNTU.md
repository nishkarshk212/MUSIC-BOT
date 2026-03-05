# Ubuntu Server Deployment Guide for Music Bot

## 🎯 Why Ubuntu Fixes the Issue

Your Mac has an **ARM64 (Apple Silicon)** processor, but PyTgCalls 0.9.7's Node.js module (`wrtc.node`) is compiled for **x86_64** architecture. 

**Ubuntu servers typically use x86_64 architecture**, which is fully compatible with PyTgCalls 0.9.7's pre-built binaries!

---

## 📋 Step-by-Step Deployment on Ubuntu

### Method 1: Manual Installation (Recommended)

#### 1. Connect to Your Ubuntu Server

```bash
ssh user@your-server-ip
```

#### 2. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

#### 3. Install Python and Dependencies

```bash
# Install Python 3.11 and required packages
sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg git curl

# Verify installations
python3 --version
pip3 --version
ffmpeg -version
```

#### 4. Clone or Upload Your Bot Code

**Option A: If using Git**
```bash
cd ~
git clone <your-repo-url> music_bot
cd music_bot
```

**Option B: Upload via SCP from your Mac**
```bash
# On your Mac, run this command:
scp -r /Users/nishkarshkr/Desktop/music_bot/* user@your-server-ip:~/music_bot/
```

#### 5. Create Virtual Environment

```bash
cd ~/music_bot
python3 -m venv .venv
source .venv/bin/activate
```

#### 6. Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### 7. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env
```

Fill in your credentials:
```env
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id
API_HASH=your_api_hash

# RECOMMENDED: Use session string
ASSISTANT_SESSION_STRING=your_session_string

# OR use phone number (less reliable)
ASSISTANT_API_ID=your_assistant_api_id
ASSISTANT_API_HASH=your_assistant_api_hash
ASSISTANT_PHONE=+1234567890

OWNER_ID=your_telegram_user_id
```

#### 8. Generate Session String (If Using Assistant Account)

```bash
# Run the session generator
python generate_session.py
```

Follow the prompts to log in with your assistant account, then copy the generated session string to your `.env` file.

#### 9. Test the Bot

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Run the bot
python bot.py
```

You should see output like:
```
INFO:__main__:Bot logged in as: @YourBotName
INFO:__main__:Bot is now running!
```

✅ **No more Node.js architecture errors!** The x86_64 server will use the correct binary.

---

### Method 2: Using Docker (Alternative)

If you prefer containerization:

#### 1. Install Docker on Ubuntu

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. Create Dockerfile

Create a file named `Dockerfile` in your bot directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
```

#### 3. Build and Run

```bash
# Build the image
docker build -t music-bot .

# Run the container
docker run -d \
  --name music-bot \
  --restart unless-stopped \
  -e BOT_TOKEN=your_token \
  -e API_ID=your_id \
  -e API_HASH=your_hash \
  -e ASSISTANT_SESSION_STRING=your_session \
  music-bot
```

---

## 🔧 Troubleshooting on Ubuntu

### Issue 1: Permission Denied

```bash
# Fix: Give execute permissions
chmod +x bot.py

# Or run with python directly
python bot.py
```

### Issue 2: Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :8080

# Kill the process if needed
sudo kill -9 <PID>
```

### Issue 3: Bot Keeps Stopping

Use a process manager like `screen` or `systemd`:

**Using Screen:**
```bash
# Install screen
sudo apt install screen

# Start a screen session
screen -S musicbot

# Run your bot
python bot.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r musicbot
```

**Using Systemd (Better for Production):**

Create `/etc/systemd/system/music-bot.service`:

```ini
[Unit]
Description=Telegram Music Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/music_bot
Environment="PATH=/home/ubuntu/music_bot/.venv/bin"
ExecStart=/home/ubuntu/music_bot/.venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl start music-bot
sudo systemctl enable music-bot
sudo systemctl status music-bot
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Python 3.11+ is installed
- [ ] FFmpeg is installed: `ffmpeg -version`
- [ ] Virtual environment is active: `(venv)` prefix in terminal
- [ ] All packages installed: `pip list`
- [ ] `.env` file exists with correct values
- [ ] Bot starts without errors
- [ ] Assistant can join voice chats
- [ ] Music plays correctly

---

## 🎉 Success Indicators

When everything works, you should see:

```bash
✅ Assistant started: @your_assistant
✅ PyTgCalls initialized
✅ Bot logged in as: @YourMusicBot
✅ Bot is now running!
```

And when playing music:

```bash
🎙️ Attempting to join voice chat in -1003843911730
✅ Assistant is member of group
✅ Voice chat marked as active
🎵 Now Playing: Song Title
```

**NO MORE:** `Error: dlopen(...wrtc.node...) incompatible architecture`

---

## 📝 Quick Reference Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Check Python version
python --version

# Check installed packages
pip list

# View bot logs (if using systemd)
sudo journalctl -u music-bot -f

# Restart bot (if using systemd)
sudo systemctl restart music-bot

# Stop bot
sudo systemctl stop music-bot
```

---

## 🔐 Security Tips

1. **Never commit `.env` to Git** - it's already in `.gitignore`
2. **Use environment variables** for sensitive data
3. **Set up firewall rules**: `sudo ufw enable`
4. **Regular updates**: `sudo apt update && sudo apt upgrade -y`
5. **Monitor logs** for suspicious activity

---

## 🚀 Performance Optimization

For better performance on Ubuntu:

```bash
# Install additional optimizations
sudo apt install -y libopus-dev opus-tools

# Set optimal FFmpeg flags (already configured in code)
# Audio parameters: -vn -ar 48000 -ac 2 -b:a 320k
```

---

**Congratulations!** Your music bot should now work perfectly on Ubuntu with full voice chat support! 🎵
