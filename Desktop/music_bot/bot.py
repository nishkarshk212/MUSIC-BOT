import logging
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from config import Config
from utils.assistant import Assistant
from utils.music_player import MusicPlayer
from utils.decorators import admin_check, authorization_check
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize bot
app = Client(
    "music_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Global instances
assistant = None
music_player = None


@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    """Handle /start command"""
    
    boot = await message.reply_text("⚡ Booting Ultra Pro Max Engine...")
    await asyncio.sleep(1)
    await boot.edit("🎶 Syncing Voice Modules...")
    await asyncio.sleep(1)
    await boot.edit("🚀 Loading Premium Interface...")
    await asyncio.sleep(1)

    # PRIVATE UI
    if message.chat.type.name == "PRIVATE":
        # Get bot's profile photo and send as spoiler
        try:
            async for photo in client.get_chat_photos(Config.BOT_USERNAME):
                photo_id = photo.file_id
                await message.reply_photo(
                    photo=photo_id,
                    caption=f"💖 **Here's My Profile Picture!**\n\nTap to reveal ✨",
                    has_spoiler=True
                )
                break  # Only get the first photo
        except Exception as e:
            logger.warning(f"Could not send profile photo: {e}")

        text = f"""
**🎧 {Config.BOT_NAME} 🎧**

✨ Hello **{message.from_user.first_name}**

🎶 High Quality VC Streaming  
⚡ Fast • Stable • 24/7 Online  
📻 YouTube • Live • Files  

**➕ Add Me To Group  
👑 Promote Me Admin  
▶️ Use /play in Group**

💎 Multi-Group Global System Enabled
"""

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣 ➕",
             url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("🎛 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦", callback_data="commands"),
                InlineKeyboardButton("📊 𝗦𝗧𝗔𝗧𝗦", callback_data="stats")
            ],
            [
                InlineKeyboardButton("💁 𝗛𝗘𝗟𝗣", callback_data="help_private"),
                InlineKeyboardButton("📢 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url="https://t.me/YOUR_SUPPORT")
            ],
            [
                InlineKeyboardButton("👑 𝗢𝗪𝗡𝗘𝗥", url="https://t.me/YOUR_USERNAME")
            ]
        ])

        await boot.edit(text, reply_markup=keyboard, disable_web_page_preview=True)


    # GROUP UI
    else:
        # Admin Check
        try:
            bot_member = await client.get_chat_member(message.chat.id, "me")
            
            # Check if bot is admin and has voice chat permissions
            is_admin = bot_member.status in ['administrator', 'creator']
            has_voice_permission = False
            
            if is_admin and bot_member.privileges:
                # Check various voice chat related privileges
                has_voice_permission = (
                    bot_member.privileges.can_manage_video_chats or
                    bot_member.privileges.can_manage_chat or
                    bot_member.privileges.can_delete_messages or
                    bot_member.privileges.can_restrict_members
                )
            
            if not is_admin or not has_voice_permission:
                warn_text = """
🚨 **I Need Voice Chat Permission!**

👑 Promote Me As Admin  
🎙 Enable Voice Chat Permissions  
Then Use /play
"""
                return await boot.edit(warn_text)
                
        except Exception as e:
            logger.warning(f"Error checking bot permissions: {e}")
            # If we can't check, show warning anyway
            warn_text = """
🚨 **Permission Check Failed!**

👑 Please Make Me An Admin  
🎙 Enable Voice Chat Permissions  
Then Use /play
"""
            return await boot.edit(warn_text)

        group_text = f"""
🎧 **{Config.BOT_NAME} Activated**

👥 **{message.chat.title}**

🎶 Use /play song name  
⏹ /stop | ⏸ /pause | ⏭ /skip  
📜 /queue to see playlist

⚡ Inline Controls Enabled
"""

        controls = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("▶ Resume", callback_data="resume")
            ],
            [
                InlineKeyboardButton("⏭ Skip", callback_data="skip"),
                InlineKeyboardButton("⏹ Stop", callback_data="stop")
            ]
        ])

        await boot.edit(group_text, reply_markup=controls)


# ================= CALLBACK CONTROLS =================

@app.on_callback_query()
async def callbacks(client, query):
    """Handle callback queries from inline buttons"""
    data = query.data

    if data == "commands":
        await query.message.edit("""
**🎛 MUSIC COMMANDS**

▶ /play - Play Song  
⏸ /pause - Pause  
▶ /resume - Resume  
⏭ /skip - Skip  
⏹ /stop - Stop  
📜 /queue - Show Queue
""")

    elif data == "stats":
        await query.answer("📊 Stats Feature Coming Soon!", show_alert=True)

    elif data == "help_private":
        await query.message.edit("""
**💁 HELP & SUPPORT**

🎵 **How to use me:**

1️⃣ Add me to your group
2️⃣ Make me an admin
3️⃣ Use /play in group

**Commands:**
/play [song] - Play music
/pause - Pause song
/resume - Resume
/skip - Skip to next
/stop - Stop playback
/queue - See playlist

**Need Help?**
Contact: @YOUR_USERNAME
""", disable_web_page_preview=True)
        
        # Add back button
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝗕𝗔𝗖𝗞", callback_data="back_start")]
        ])
        await query.message.edit_reply_markup(reply_markup=back_keyboard)

    elif data == "queue":
        global music_player
        if not music_player:
            return await query.answer("Bot not initialized!", show_alert=True)
        
        chat_id = query.message.chat.id
        queue = music_player.get_queue(chat_id)
        
        if not queue:
            return await query.answer("📭 Queue is empty!", show_alert=True)
        
        queue_text = "**📜 Current Queue:**\n\n"
        for i, song in enumerate(queue[:5], 1):
            queue_text += f"{i}. 🎵 {song['title']} - {song['duration']}\n"
            queue_text += f"   Requested by: {song['requester_name']}\n\n"
        
        if len(queue) > 5:
            queue_text += f"...and {len(queue) - 5} more songs"
        
        await query.message.edit(queue_text, disable_web_page_preview=True)
        
        # Add back button
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝗕𝗔𝗖𝗞", callback_data="back_start")]
        ])
        await query.message.edit_reply_markup(reply_markup=back_keyboard)

    elif data == "back_start":
        # Go back to start message
        text = f"""
**🎧 {Config.BOT_NAME} 🎧**

✨ Hello **{query.from_user.first_name}**

🎶 High Quality VC Streaming  
⚡ Fast • Stable • 24/7 Online  
📻 YouTube • Live • Files  

**➕ Add Me To Group  
👑 Promote Me Admin  
▶️ Use /play in Group**

💎 Multi-Group Global System Enabled
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣 ➕",
             url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("🎛 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦", callback_data="commands"),
                InlineKeyboardButton("📊 𝗦𝗧𝗔𝗧𝗦", callback_data="stats")
            ],
            [
                InlineKeyboardButton("💁 𝗛𝗘𝗟𝗣", callback_data="help_private"),
                InlineKeyboardButton("📢 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url="https://t.me/YOUR_SUPPORT")
            ],
            [
                InlineKeyboardButton("👑 𝗢𝗪𝗡𝗘𝗥", url="https://t.me/YOUR_USERNAME")
            ]
        ])
        await query.message.edit(text, reply_markup=keyboard, disable_web_page_preview=True)

    elif data in ["pause", "resume", "skip", "stop"]:
        await query.answer(f"🎶 {data.capitalize()} command received!")


@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message: Message):
    """Handle /help command"""
    await message.reply_text(
        "**📚 Help & Commands**\n\n"
        "**Bot Commands:**\n\n"
        "/start - Start the bot\n"
        "/play [query] - Play a song (supports YouTube links, Spotify, or search)\n"
        "/pause - Pause the current song\n"
        "/resume - Resume the paused song\n"
        "/skip - Skip to the next song\n"
        "/stop - Stop playback and clear queue\n"
        "/queue - View the song queue\n"
        "/current - Show currently playing song\n"
        "/volume [1-100] - Adjust volume\n"
        "/vc - Voice chat status and controls\n\n"
        "**Admin Commands:**\n"
        "/skipforce - Force skip (admins only)\n"
        "/stopforce - Force stop (admins only)\n\n"
        "**Note:** The assistant account will join your VC to play music."
    )


# Cooldown dictionary for anti-spam
cooldowns = {}

# Format Duration Function
def format_duration(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

# Fake Progress Bar
def progress_bar(percent):
    filled = int(percent / 10)
    return "▰" * filled + "▱" * (10 - filled)

@app.on_message(filters.command("play") & filters.group)
@authorization_check
async def play_command(client, message: Message):
    """Handle /play command with premium UI"""
    global assistant, music_player
    
    user_id = message.from_user.id
    now = time.time()
    
    # Anti Spam Cooldown (5 sec)
    if user_id in cooldowns and now - cooldowns[user_id] < 5:
        return await message.reply_text("⏳ Please Wait Before Using /play Again.")
    
    cooldowns[user_id] = now
    
    if not assistant or not music_player:
        await message.reply_text("❌ Bot is not properly initialized. Please contact the owner.")
        return
    
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Give Song Name**\n\nExample:\n`/play Believer`"
        )
    
    query = " ".join(message.command[1:])
    requester = message.from_user.mention
    chat_id = message.chat.id
    
    searching = await message.reply_text(
        f"🔎 Searching: **{query}**..."
    )
    
    await asyncio.sleep(1.5)
    await searching.edit("🎶 Fetching Audio From Server...")
    await asyncio.sleep(1.5)
    await searching.edit("🚀 Joining Voice Chat...")
    await asyncio.sleep(1)
    
    try:
        # Add to queue and get info
        result = await music_player.add_to_queue(
            chat_id=chat_id,
            query=query,
            requested_by=message.from_user.id,
            message=message
        )
        
        if result:
            title = result['title']
            duration_seconds = result.get('duration_seconds', 225)
            duration = format_duration(duration_seconds)
            bar = progress_bar(20)
            
            now_playing = f"""
**🎧 NOW PLAYING**

🎵 **{title}**  
⏱ {duration}  
🙋 {requester}

{bar} 20%

⚡ Streaming In Voice Chat...
"""
            
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                    InlineKeyboardButton("▶ Resume", callback_data="resume"),
                    InlineKeyboardButton("⏭ Skip", callback_data="skip"),
                    InlineKeyboardButton("⏹ Stop", callback_data="stop"),
                ],
                [
                    InlineKeyboardButton("📜 Queue", callback_data="queue")
                ]
            ])
            
            await searching.edit(now_playing, reply_markup=buttons, disable_web_page_preview=True)
            
            # Try to start playing if not already playing
            if not music_player.is_playing(chat_id):
                await music_player.play_next(chat_id, assistant, client)
        else:
            await searching.edit("❌ Failed to process the song. Please try again.")
    
    except Exception as e:
        logger.error(f"Error in play_command: {e}")
        await searching.edit(f"❌ Error: {str(e)}")


@app.on_message(filters.command("pause"))
@authorization_check
@admin_check
async def pause_command(client, message: Message):
    """Handle /pause command"""
    global music_player
    
    if not music_player:
        await message.reply_text("❌ Bot is not properly initialized.")
        return
    
    chat_id = message.chat.id
    
    if music_player.pause(chat_id):
        await message.reply_text("⏸️ **Playback Paused**")
    else:
        await message.reply_text("❌ No active playback to pause!")


@app.on_message(filters.command("resume"))
@authorization_check
@admin_check
async def resume_command(client, message: Message):
    """Handle /resume command"""
    global music_player
    
    if not music_player:
        await message.reply_text("❌ Bot is not properly initialized.")
        return
    
    chat_id = message.chat.id
    
    if music_player.resume(chat_id):
        await message.reply_text("▶️ **Playback Resumed**")
    else:
        await message.reply_text("❌ Nothing is paused!")


@app.on_message(filters.command("skip"))
@authorization_check
async def skip_command(client, message: Message):
    """Handle /skip command"""
    global music_player, assistant
    
    if not music_player or not assistant:
        await message.reply_text("❌ Bot is not properly initialized.")
        return
    
    chat_id = message.chat.id
    
    skipped = await music_player.skip_current(chat_id)
    
    if skipped:
        await message.reply_text("⏭️ **Skipped to next song**")
        # Play next song
        await music_player.play_next(chat_id, assistant, client)
    else:
        await message.reply_text("❌ No songs in queue to skip!")


@app.on_message(filters.command("stop"))
@authorization_check
@admin_check
async def stop_command(client, message: Message):
    """Handle /stop command"""
    global music_player, assistant
    
    if not music_player or not assistant:
        await message.reply_text("❌ Bot is not properly initialized.")
        return
    
    chat_id = message.chat.id
    
    stopped = await music_player.stop(chat_id, assistant)
    
    if stopped:
        await message.reply_text("⏹️ **Playback Stopped**")
    else:
        await message.reply_text("❌ No active playback!")


@app.on_message(filters.command("queue"))
@authorization_check
async def queue_command(client, message: Message):
    """Handle /queue command"""
    global music_player
    
    if not music_player:
        await message.reply_text("❌ Bot is not properly initialized.")
        return
    
    chat_id = message.chat.id
    queue = music_player.get_queue(chat_id)
    
    if not queue:
        await message.reply_text("📭 **Queue is empty!**\n\nAdd songs with /play")
        return
    
    queue_text = "📋 **Current Queue:**\n\n"
    for i, song in enumerate(queue[:10], 1):  # Show first 10 songs
        queue_text += f"{i}. 🎵 {song['title']} - {song['duration']}\n"
        queue_text += f"   Requested by: {song['requested_by']}\n\n"
    
    if len(queue) > 10:
        queue_text += f"...and {len(queue) - 10} more songs"
    
    await message.reply_text(queue_text)


@app.on_message(filters.command("current"))
@authorization_check
async def current_command(client, message: Message):
    """Handle /current command"""
    global music_player
    
    if not music_player:
        await message.reply_text("❌ Bot is not properly initialized.")
        return
    
    chat_id = message.chat.id
    current = music_player.get_current(chat_id)
    
    if current:
        await message.reply_text(
            f"🎵 **Now Playing:**\n\n"
            f"**Title:** {current['title']}\n"
            f"**Duration:** {current['duration']}\n"
            f"**Requested by:** {current['requested_by']}"
        )
    else:
        await message.reply_text("❌ Nothing is playing right now!")


@app.on_message(filters.command("vc"))
@authorization_check
async def vc_command(client, message: Message):
    """Handle /vc command - Voice chat status"""
    global assistant
    
    if not assistant:
        await message.reply_text("❌ Assistant not available.")
        return
    
    chat_id = message.chat.id
    
    # Check if assistant is in VC
    is_in_vc = await assistant.is_in_voice_chat(chat_id)
    
    if is_in_vc:
        await message.reply_text(
            "🎙️ **Voice Chat Status:**\n\n"
            "✅ Assistant is in the voice chat\n"
            "🎵 Currently playing music"
        )
    else:
        await message.reply_text(
            "🎙️ **Voice Chat Status:**\n\n"
            "❌ Assistant is not in the voice chat\n"
            "Use /play to make me join and play music"
        )


@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    """Handle /ping command"""
    start_time = asyncio.get_event_loop().time()
    msg = await message.reply_text("🏓 Pinging...")
    end_time = asyncio.get_event_loop().time()
    
    ping_time = round((end_time - start_time) * 1000, 2)
    
    await msg.edit_text(f"🏓 **Pong!**\n\nResponse time: `{ping_time}ms`")


@app.on_message(filters.command("checkvc"))
@authorization_check
async def checkvc_command(client, message: Message):
    """Check voice chat status and assistant membership"""
    global assistant, music_player
    
    if not assistant or not music_player:
        await message.reply_text("❌ Bot not initialized!")
        return
    
    chat_id = message.chat.id
    
    # Check if in group
    if message.chat.type.name not in ['GROUP', 'SUPERGROUP']:
        await message.reply_text("❌ This command only works in groups!")
        return
    
    checking = await message.reply_text("🔍 Checking voice chat status...")
    
    try:
        # Check 1: Is assistant in group?
        try:
            member = await assistant.client.get_chat_member(chat_id, "me")
            assistant_status = f"✅ In group (Status: {member.status})"
        except Exception as e:
            assistant_status = f"❌ NOT in group! Error: {e}"
        
        # Check 2: Is there an active voice chat?
        try:
            is_vc_active = await assistant.is_voice_chat_active(chat_id)
            vc_status = "✅ Active" if is_vc_active else "❌ No active voice chat"
        except Exception as e:
            vc_status = f"❌ Error checking: {e}"
        
        # Check 3: Is assistant in voice chat?
        in_vc = await assistant.is_in_voice_chat(chat_id)
        in_vc_status = "✅ Joined VC" if in_vc else "❌ Not in VC"
        
        # Get bot info
        bot_info = await client.get_me()
        assistant_info = await assistant.client.get_me()
        
        report = f"""
**🔍 Voice Chat Status Report**

**Group:** {message.chat.title}
**Chat ID:** `{chat_id}`

**Assistant Account:** @{assistant_info.username}
{assistant_status}

**Voice Chat:** {vc_status}
**Assistant in VC:** {in_vc_status}

**Bot Admin:** @{bot_info.username}

**Solutions:**
• If assistant not in group: Add @{assistant_info.username} manually
• If no VC: Start a voice chat first
• Then use /play to test
"""
        
        await checking.edit(report)
        
    except Exception as e:
        await checking.edit(f"❌ Error: {e}")


async def initialize():
    """Initialize bot components"""
    global assistant, music_player
    
    logger.info("Initializing bot...")
    
    # Start the main bot client first
    await app.start()
    logger.info("Main bot started!")
    
    # Initialize assistant
    assistant = Assistant()
    await assistant.start()
    logger.info("Assistant started!")
    
    # Initialize music player
    music_player = MusicPlayer()
    logger.info("Music player initialized!")
    
    # Get bot info
    bot_info = await app.get_me()
    Config.BOT_USERNAME = bot_info.username
    Config.BOT_NAME = bot_info.first_name
    
    logger.info(f"Bot logged in as: @{Config.BOT_USERNAME}")


async def main():
    """Main function"""
    await initialize()
    
    logger.info("Bot is now running!")
    
    # Keep the bot running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopping...")
        if assistant:
            await assistant.stop()
        await app.stop()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
