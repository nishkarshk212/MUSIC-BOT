import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.error import Conflict
from dotenv import load_dotenv
import atexit
import signal
import sys

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram channel for logs
LOG_CHANNEL = "@log_x_bott"

async def send_to_log_channel(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Send log messages to the Telegram channel"""
    try:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"Log sent to channel {LOG_CHANNEL}: {message[:50]}...")
    except Exception as e:
        logger.error(f"Failed to send log to channel {LOG_CHANNEL}: {e}")




async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edited messages - delete them and warn the user"""
    edited_message = update.edited_message
    
    if not edited_message:
        return
    
    chat = edited_message.chat
    user = edited_message.from_user
    
    # Only work in groups/supergroups
    if chat.type not in ['group', 'supergroup']:
        return
    
    # Check if this is an actual content edit or just a media view/other update
    # For reactions, Telegram doesn't actually send edited_message updates
    # But we'll ensure we're only processing actual content changes
    
    # Only process if the message has actual content (text or caption)
    # If there's no text or caption, it might be just a media view or other metadata change
    has_text = hasattr(edited_message, 'text') and edited_message.text is not None
    has_caption = hasattr(edited_message, 'caption') and edited_message.caption is not None
    
    if not (has_text or has_caption):
        # If there's no text or caption content, it's not a content edit we need to handle
        # This might be a media-only message update or other non-content change
        return
    
    # Log that we're processing an actual content edit
    logger.info(f"Processing actual content edit from user {user.id} in chat {chat.id}")
    
    # Send log to Telegram channel
    await send_to_log_channel(
        context,
        f"🔴 <b>Edited Message Detected</b>\n\n"
        f"👤 User: {user.mention_html()} (ID: <code>{user.id}</code>)\n"
        f"💬 Group: {chat.title} (<code>{chat.id}</code>)\n"
        f"📝 Original Text: {edited_message.text or '[Has caption]'}\n"
        f"⏰ Time: {edited_message.edit_date.strftime('%Y-%m-%d %H:%M:%S') if edited_message.edit_date else 'N/A'}"
    )
    
    # Log group activity for usage tracking
    log_group_add(chat.id, chat.title or "Unknown Group", chat.type)
    update_group_activity(chat.id)
    
    try:
        # Delete the edited message
        await context.bot.delete_message(
            chat_id=chat.id,
            message_id=edited_message.message_id
        )
        logger.info(f"Deleted edited message {edited_message.message_id} from user {user.id} in chat {chat.id}")
        
        # Send general warning to the group (with user ID only)
        warning_text = (
            f"⚠️ Warning: User ID {user.id} edited a message which is not allowed in this group!\n"
            f"The edited message has been deleted."
        )
        
        warning_message = await context.bot.send_message(
            chat_id=chat.id,
            text=warning_text,
            parse_mode='HTML'
        )
        
        # Schedule deletion of the warning message after 2 minutes
        logger.info(f"Scheduling deletion for message {warning_message.message_id} in chat {chat.id} after 120 seconds")
        job = context.job_queue.run_once(
            _delete_after_delay,
            when=120,
            data={"chat_id": chat.id, "message_id": warning_message.message_id}
        )
        logger.info(f"Job scheduled successfully: {job is not None}")
        
        # Get administrators of the group and send detailed warning mentioning the user
        try:
            administrators = await context.bot.get_chat_administrators(chat.id)
            
            # Send detailed warning to administrators mentioning the user
            for admin in administrators:
                # Skip sending to the user who edited if they are also an admin
                if admin.user.id != user.id:
                    detailed_warning = (
                        f"⚠️ Admin Alert: User {user.mention_html()} "
                        f"(ID: {user.id}) edited a message in group '{chat.title}'. "
                        f"The message has been deleted."
                    )
                    try:
                        await context.bot.send_message(
                            chat_id=admin.user.id,
                            text=detailed_warning,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Failed to send admin warning to {admin.user.id}: {e}")
        except Exception as e:
            logger.error(f"Failed to get administrators: {e}")
        
        delete_after = 120
        
        context.job_queue.run_once(
            _delete_after_delay,
            when=delete_after,
            data={"chat_id": chat.id, "message_id": warning_message.message_id}
        )
        
    except Exception as e:
        logger.error(f"Error handling edited message: {e}")

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check regular messages for links and delete them with a warning"""
    if not update.message:
        return
        
    user = update.effective_user
    chat = update.effective_chat
    
    # Only work in groups/supergroups
    if chat.type not in ['group', 'supergroup']:
        return
    
    # Check if the message contains links
    message_text = update.message.text or ""
    if "http" in message_text.lower() or "www." in message_text.lower() or ".com" in message_text.lower():
        # Send log to Telegram channel first
        await send_to_log_channel(
            context,
            f"🚫 <b>Link Detection Alert</b>\n\n"
            f"👤 User: {user.mention_html()} (ID: <code>{user.id}</code>)\n"
            f"💬 Group: {chat.title} (<code>{chat.id}</code>)\n"
            f"🔗 Link Message: {message_text[:100]}{'...' if len(message_text) > 100 else ''}\n"
            f"⏰ Time: {update.message.date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Send warning message
        warning = await update.message.reply_text(
            f"⚠️ Warning {user.mention_html()}!\nLinks are not allowed.",
            parse_mode="HTML"
        )

        # Delete user message
        await update.message.delete()

        # Wait 5 seconds then delete bot warning
        await asyncio.sleep(5)
        try:
            await warning.delete()
        except Exception as e:
            logger.error(f"Error deleting warning message: {e}")

 

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    help_text = (
        "ℹ️ Help\n\n"
        "ᴛʜɪꜱ ɪꜱ ᴀɴ ᴏꜰꜰɪᴄɪᴀʟ ʙᴏᴛ ᴄʀᴇᴀᴛᴇᴅ ʙʏ @Titanic_bots ᴡʜɪᴄʜ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴇᴅɪᴛᴇᴅ ᴍꜱɢ\n\n"
        "• Automatically deletes edited messages in groups\n"
        
        "• Commands:\n"
        "  • /help — Show this help\n"
        "  • /healthcheck — Check bot health status (private chat only)\n"
        "  • /botusage — Show bot usage information (authorized users only)\n"
    )
    await message.reply_text(help_text)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    # Get bot's name and profile photo
    bot_info = await context.bot.get_me()
    bot_name = bot_info.first_name
    
    # Log group activity if this is a group chat
    if chat.type in ['group', 'supergroup']:
        log_group_add(chat.id, chat.title or "Unknown Group", chat.type)
        update_group_activity(chat.id)
    
    start_text = (
        f"HEY {user.mention_html()}\n"
        f"This {bot_name} bot automatically monitors edited messages in the group and instantly deletes edited messages to maintain transparency and prevent misuse. It helps stop scams, fake edits, and rule-breaking by ensuring members cannot change messages after sending them."
    )
    
    # Get bot's username to create the Add to Group URL
    bot_username = (await context.bot.get_me()).username
    # Create inline keyboard with Add to Group button
    keyboard = [
        [
            InlineKeyboardButton("☂︎ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get bot's profile photo and send it with spoiler effect
    try:
        photos = await context.bot.get_user_profile_photos(bot_info.id, limit=1)
        if photos.total_count > 0 and photos.photos:
            photo = photos.photos[0][-1]  # Get the largest size
            sent_message = await context.bot.send_photo(
                chat_id=chat.id,
                photo=photo.file_id,
                caption=start_text,
                reply_markup=reply_markup,
                has_spoiler=True,  # This adds the spoiler effect
                parse_mode='HTML'
            )
            # If sent in a group, schedule deletion after 2 minutes
            if chat.type in ['group', 'supergroup']:
                logger.info(f"Scheduling deletion for start message {sent_message.message_id} in chat {chat.id} after 120 seconds")
                job = context.job_queue.run_once(
                    _delete_after_delay,
                    when=120,
                    data={"chat_id": chat.id, "message_id": sent_message.message_id}
                )
                logger.info(f"Start message job scheduled successfully: {job is not None}")
        else:
            # Fallback if no profile photo is set
            sent_message = await message.reply_text(start_text, reply_markup=reply_markup, parse_mode='HTML')
            # If sent in a group, schedule deletion after 2 minutes
            if chat.type in ['group', 'supergroup']:
                context.job_queue.run_once(
                    _delete_after_delay,
                    when=120,
                    data={"chat_id": chat.id, "message_id": sent_message.message_id}
                )
    except Exception:
        # Fallback if there's an error getting the photo
        sent_message = await message.reply_text(start_text, reply_markup=reply_markup, parse_mode='HTML')
        # If sent in a group, schedule deletion after 2 minutes
        if chat.type in ['group', 'supergroup']:
            context.job_queue.run_once(
                _delete_after_delay,
                when=120,
                data={"chat_id": chat.id, "message_id": sent_message.message_id}
            )

async def _delete_after_delay(context: ContextTypes.DEFAULT_TYPE):
    try:
        # Access the job data correctly
        if hasattr(context, 'job') and context.job and hasattr(context.job, 'data'):
            data = context.job.data
        elif hasattr(context, 'data'):
            data = context.data
        else:
            logger.error("No job data found for deletion")
            return
        
        chat_id = data.get("chat_id")
        message_id = data.get("message_id")
        
        if chat_id and message_id:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"Successfully deleted message {message_id} in chat {chat_id}")
        else:
            logger.error(f"Missing chat_id or message_id for deletion: chat_id={chat_id}, message_id={message_id}")
    except Exception as e:
        logger.error(f"Error deleting warning message: {e}")

async def show_warning_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    if chat.type not in ['group', 'supergroup']:
        await message.reply_text("This command can only be used in groups.")
        return
    seconds = 120
    await message.reply_text(f"Warning auto-delete timer is set to {seconds} seconds for this group.")

async def health_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Health check command to verify bot status"""
    import time
    import psutil
    
    message = update.effective_message
    chat = update.effective_chat
    
    # Only allow in private chats or by bot owner
    if chat.type != 'private':
        # Check if user is admin/owner (basic check)
        user = update.effective_user
        if user.username != 'Titanic_bots':  # Adjust this to your username
            await message.reply_text("/healthcheck command can only be used in private chat or by authorized users.")
            return
    
    try:
        # Get system info
        process = psutil.Process()
        uptime = time.time() - process.create_time()
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        # Get bot info
        bot_user = await context.bot.get_me()
        
        health_text = (
            "✅ Bot Health Status\n\n"
            f"🤖 Bot Username: @{bot_user.username}\n"
            f"🟢 Status: Online and Running\n"
            f"⏱️ Uptime: {uptime/3600:.1f} hours ({uptime/60:.1f} minutes)\n"
            f"💾 Memory Usage: {memory_info.rss / 1024 / 1024:.1f} MB\n"
            f"⚡ CPU Usage: {cpu_percent:.1f}%\n"
            f"📊 Active Handlers: {len(context.application.handlers.get(0, []))} registered handlers\n"
            f"🕒 Current Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"🐍 Python Version: {sys.version.split()[0]}\n"
            f"📡 Library: python-telegram-bot {getattr(context.bot, '__version__', 'unknown')}\n"
        )
        
        await message.reply_text(health_text)
        
    except Exception as e:
        error_text = f"❌ Health check failed: {str(e)}"
        await message.reply_text(error_text)

import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize the SQLite database for tracking bot usage"""
    db_path = os.path.join(os.path.dirname(__file__), 'bot_usage.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table for group tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            group_id INTEGER UNIQUE,
            title TEXT,
            type TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0
        )
    ''')
    
    # Create table for message tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            group_id INTEGER,
            user_id INTEGER,
            message_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (group_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path

def log_group_add(group_id, title, group_type):
    """Log when bot is added to a new group"""
    db_path = os.path.join(os.path.dirname(__file__), 'bot_usage.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO groups (group_id, title, type)
            VALUES (?, ?, ?)
        ''', (group_id, title, group_type))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log group add: {e}")
    finally:
        conn.close()

def update_group_activity(group_id):
    """Update last activity timestamp and increment message count"""
    db_path = os.path.join(os.path.dirname(__file__), 'bot_usage.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE groups 
            SET last_activity = CURRENT_TIMESTAMP, message_count = message_count + 1
            WHERE group_id = ?
        ''', (group_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to update group activity: {e}")
    finally:
        conn.close()

def get_bot_usage_stats():
    """Get comprehensive bot usage statistics"""
    db_path = os.path.join(os.path.dirname(__file__), 'bot_usage.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get total groups
        cursor.execute("SELECT COUNT(*) FROM groups")
        total_groups = cursor.fetchone()[0]
        
        # Get active groups (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM groups 
            WHERE last_activity > datetime('now', '-1 day')
        ''')
        active_groups = cursor.fetchone()[0]
        
        # Get total messages processed
        cursor.execute("SELECT SUM(message_count) FROM groups")
        total_messages = cursor.fetchone()[0] or 0
        
        # Get top 5 groups by activity
        cursor.execute('''
            SELECT title, message_count, last_activity 
            FROM groups 
            ORDER BY message_count DESC 
            LIMIT 5
        ''')
        top_groups = cursor.fetchall()
        
        # Get recent activity
        cursor.execute('''
            SELECT title, last_activity 
            FROM groups 
            ORDER BY last_activity DESC 
            LIMIT 5
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'total_groups': total_groups,
            'active_groups': active_groups,
            'total_messages': total_messages,
            'top_groups': top_groups,
            'recent_activity': recent_activity
        }
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        return None
    finally:
        conn.close()

async def bot_usage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show where the bot is being used - only for @Jayden_212"""
    message = update.effective_message
    user = update.effective_user
    
    # Only allow @Jayden_212 to use this command
    if user.username != 'Jayden_212':
        await message.reply_text("❌ This command is only available to @Jayden_212")
        return
    
    try:
        # Get usage statistics
        stats = get_bot_usage_stats()
        
        if not stats:
            await message.reply_text("❌ Failed to retrieve usage statistics")
            return
        
        # Format the response
        usage_text = (
            "📊 Bot Usage Statistics\n\n"
            f"📈 **Total Groups:** {stats['total_groups']}\n"
            f"⚡ **Active Groups (24h):** {stats['active_groups']}\n"
            f"💬 **Total Messages Processed:** {stats['total_messages']}\n\n"
        )
        
        # Top active groups
        if stats['top_groups']:
            usage_text += "**🏆 Most Active Groups:**\n"
            for i, (title, count, last_active) in enumerate(stats['top_groups'], 1):
                usage_text += f"{i}. {title} - {count} messages\n"
            usage_text += "\n"
        
        # Recent activity
        if stats['recent_activity']:
            usage_text += "**🕒 Recent Activity:**\n"
            for title, last_active in stats['recent_activity']:
                # Parse timestamp and format nicely
                try:
                    dt = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                    usage_text += f"• {title} - {dt.strftime('%Y-%m-%d %H:%M')}\n"
                except:
                    usage_text += f"• {title} - {last_active}\n"
        
        await message.reply_text(usage_text, parse_mode='Markdown')
        
    except Exception as e:
        error_text = f"❌ Failed to retrieve usage information: {str(e)}"
        await message.reply_text(error_text)

def ensure_single_instance(lock_path: str):
    pid = os.getpid()
    if os.path.exists(lock_path):
        try:
            with open(lock_path, 'r') as f:
                existing_pid_str = f.read().strip()
            existing_pid = int(existing_pid_str) if existing_pid_str.isdigit() else None
        except Exception:
            existing_pid = None
        if existing_pid:
            try:
                os.kill(existing_pid, 0)
                logger.error("Another bot instance is already running.")
                sys.exit(1)
            except OSError:
                pass
        try:
            os.remove(lock_path)
        except Exception:
            pass
    try:
        with open(lock_path, 'w') as f:
            f.write(str(pid))
    except Exception:
        logger.error("Could not create lock file.")
        sys.exit(1)
    def _cleanup():
        try:
            if os.path.exists(lock_path):
                with open(lock_path, 'r') as f:
                    content = f.read().strip()
                if content == str(pid):
                    os.remove(lock_path)
        except Exception:
            pass
    atexit.register(_cleanup)
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: sys.exit(0))

def main():
    """Start the bot"""
    logger.info("Starting bot initialization...")
    
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables.")
        logger.error("Please create a .env file with: BOT_TOKEN=your_bot_token_here")
        logger.error("Or set it as an environment variable.")
        raise ValueError("BOT_TOKEN not found. Please set it in .env file or as an environment variable.")
    
    # Validate bot token format
    if bot_token.startswith('your_') or len(bot_token) < 20:
        logger.error("Invalid BOT_TOKEN format detected")
        raise ValueError("Please provide a valid Telegram bot token")
    
    logger.info("Bot token validated successfully")
    
    # Initialize database for usage tracking
    db_path = init_database()
    logger.info(f"Database initialized at: {db_path}")
    
    lock_path = os.path.join(os.path.dirname(__file__), '.bot.lock')
    ensure_single_instance(lock_path)
    
    # Create application with job queue enabled
    logger.info("Creating Telegram application...")
    try:
        application = Application.builder().token(bot_token).build()
        logger.info("Application created successfully")
        logger.info(f"Job queue available: {application.job_queue is not None}")
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        logger.error("This might be due to an incompatible python-telegram-bot version")
        raise
    
    # Add handler for edited messages
    application.add_handler(
        MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message)
    )
    # Add handler for regular text messages containing links
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, check_message)
    )
    application.add_handler(
        CommandHandler("help", help_command)
    )
    application.add_handler(
        CommandHandler("start", start_command)
    )
    application.add_handler(
        CommandHandler("warning_timer", show_warning_timer)
    )
    application.add_handler(
        CommandHandler("healthcheck", health_check_command)
    )
    application.add_handler(
        CommandHandler("botusage", bot_usage_command)
    )
    
    # Start the bot
    logger.info("Bot is starting...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Conflict:
        logger.error("Bot terminated: another getUpdates request is active. Ensure only one instance runs.")
        sys.exit(1)


if __name__ == '__main__':
    main()
