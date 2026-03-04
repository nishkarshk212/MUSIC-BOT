import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.error import Conflict
from dotenv import load_dotenv
import atexit
import signal
import sys
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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
    )
    await message.reply_text(help_text)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    # Get bot's name
    bot_info = await context.bot.get_me()
    bot_name = bot_info.first_name
    
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
    
    await message.reply_text(start_text, reply_markup=reply_markup, parse_mode='HTML')

async def _delete_after_delay(context: ContextTypes.DEFAULT_TYPE):
    try:
        data = getattr(context.job, "data", {}) if hasattr(context, "job") else {}
        chat_id = data.get("chat_id")
        message_id = data.get("message_id")
        if chat_id and message_id:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
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
    
    lock_path = os.path.join(os.path.dirname(__file__), '.bot.lock')
    ensure_single_instance(lock_path)
    
    # Create application
    logger.info("Creating Telegram application...")
    try:
        application = Application.builder().token(bot_token).build()
        logger.info("Application created successfully")
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
    
    # Start the bot
    logger.info("Bot is starting...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Conflict:
        logger.error("Bot terminated: another getUpdates request is active. Ensure only one instance runs.")
        sys.exit(1)


if __name__ == '__main__':
    main()
