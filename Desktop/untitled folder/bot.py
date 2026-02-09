import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import config
import urllib.parse

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with instructions and add to group button"""
    # Get bot username for the add to group link
    bot_username = context.bot.username
    if not bot_username:
        # Fallback if we can't get username
        add_group_url = "https://t.me/"
    else:
        add_group_url = f"https://t.me/{bot_username}?startgroup=botstart"
    
    # Direct group link
    direct_group_url = "https://t.me/last_promise_chatting_212"
    
    welcome_text = (
        "🎯 *Message Self-Destruct Bot*\n\n"
        "I automatically delete messages after a set time!\n\n"
        "📋 *Commands:*\n"
        "• /timer - Set deletion timer\n"
        "• /status - Check current timer setting\n"
        "• /help - Show this help message\n\n"
        "⚠️ *Note:* Add me as admin with delete message permissions for full functionality!"
    )
    
    # Create inline keyboard with both Add to Group buttons
    keyboard = [
        [InlineKeyboardButton("➕ Add to Group", url=add_group_url)],
        [InlineKeyboardButton("💬 Join Our Chat", url=direct_group_url)],
        [InlineKeyboardButton("⏱️ Set Timer", callback_data="show_timer")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "🤖 *Message Self-Destruct Bot Help*\n\n"
        "*How it works:*\n"
        "1. I monitor all messages in the group\n"
        "2. Delete them after the set time period\n"
        "3. You can customize the timer with /timer\n\n"
        "*Available Commands:*\n"
        "/start - Start the bot\n"
        "/timer - Set deletion timer\n"
        "/status - Check current settings\n"
        "/help - Show this help\n\n"
        "*Timer Options:*\n"
        "• 10s, 30s, 1m, 5m, 10m, 30m, 1h\n"
        "• 'off' to disable auto-deletion"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def show_timer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show timer selection menu"""
    # Check if this is a custom timer request
    if update.callback_query and update.callback_query.data == "custom_timer":
        await show_custom_timer(update, context)
        return
    
    keyboard = []
    row = []
    
    # Create buttons in rows of 3
    for i, (label, seconds) in enumerate(config.TIME_OPTIONS.items()):
        button = InlineKeyboardButton(
            f"{label} ({seconds}s)" if seconds > 0 else label,
            callback_data=f"set_timer_{label}"
        )
        row.append(button)
        
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Add custom timer button
    keyboard.append([InlineKeyboardButton("⚙️ Custom Timer", callback_data="custom_timer")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_time = config.DEFAULT_TIME
    for label, seconds in config.TIME_OPTIONS.items():
        if seconds == config.DEFAULT_TIME:
            current_time = label
            break
    
    message = f"⏱️ *Select Auto-Delete Timer*\n\nCurrent setting: {current_time}"
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle timer setting from callback"""
    query = update.callback_query
    await query.answer()
    
    # Extract timer value from callback data
    timer_label = query.data.replace('set_timer_', '')
    seconds = config.TIME_OPTIONS.get(timer_label, config.DEFAULT_TIME)
    
    # Update default time
    config.DEFAULT_TIME = seconds
    
    # Update message
    status = f"✅ Timer set to {timer_label}" if seconds > 0 else "✅ Auto-deletion disabled"
    await query.edit_message_text(f"⏱️ *Timer Settings*\n\n{status}")
    
    logger.info(f"Timer set to {timer_label} ({seconds}s) by user {update.effective_user.id}")

async def show_custom_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show custom timer interface with +/- buttons"""
    user_id = update.effective_user.id
    
    # Initialize custom timer for user if not exists
    if user_id not in config.user_custom_timers:
        config.user_custom_timers[user_id] = {'hours': 0, 'minutes': 0, 'seconds': 30}
    
    timer_data = config.user_custom_timers[user_id]
    
    # Create keyboard with +/- buttons
    keyboard = [
        # Hours row
        [
            InlineKeyboardButton("H-1", callback_data="custom_h_dec"),
            InlineKeyboardButton(f"Hours: {timer_data['hours']}", callback_data="custom_dummy"),
            InlineKeyboardButton("H+1", callback_data="custom_h_inc")
        ],
        # Minutes row
        [
            InlineKeyboardButton("M-1", callback_data="custom_m_dec"),
            InlineKeyboardButton(f"Minutes: {timer_data['minutes']}", callback_data="custom_dummy"),
            InlineKeyboardButton("M+1", callback_data="custom_m_inc")
        ],
        # Seconds row
        [
            InlineKeyboardButton("S-1", callback_data="custom_s_dec"),
            InlineKeyboardButton(f"Seconds: {timer_data['seconds']}", callback_data="custom_dummy"),
            InlineKeyboardButton("S+1", callback_data="custom_s_inc")
        ],
        # Action buttons
        [
            InlineKeyboardButton("✅ Set Timer", callback_data="custom_set"),
            InlineKeyboardButton("↩️ Back", callback_data="show_timer")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    total_seconds = timer_data['hours'] * 3600 + timer_data['minutes'] * 60 + timer_data['seconds']
    
    message = (
        f"⚙️ *Custom Timer Settings*\n\n"
        f"Current setting: {timer_data['hours']:02d}:{timer_data['minutes']:02d}:{timer_data['seconds']:02d} ({total_seconds}s)\n\n"
        f"Use +/- buttons to adjust time\n"
        f"Press ✅ Set Timer when done"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_custom_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle custom timer button presses"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in config.user_custom_timers:
        config.user_custom_timers[user_id] = {'hours': 0, 'minutes': 0, 'seconds': 30}
    
    timer_data = config.user_custom_timers[user_id]
    action = query.data
    
    # Handle increment/decrement
    if action == "custom_h_inc":
        timer_data['hours'] = min(timer_data['hours'] + 1, 23)
    elif action == "custom_h_dec":
        timer_data['hours'] = max(timer_data['hours'] - 1, 0)
    elif action == "custom_m_inc":
        timer_data['minutes'] = min(timer_data['minutes'] + 1, 59)
    elif action == "custom_m_dec":
        timer_data['minutes'] = max(timer_data['minutes'] - 1, 0)
    elif action == "custom_s_inc":
        timer_data['seconds'] = min(timer_data['seconds'] + 1, 59)
    elif action == "custom_s_dec":
        timer_data['seconds'] = max(timer_data['seconds'] - 1, 0)
    elif action == "custom_set":
        # Calculate total seconds and set as default
        total_seconds = timer_data['hours'] * 3600 + timer_data['minutes'] * 60 + timer_data['seconds']
        if total_seconds > 0:
            config.DEFAULT_TIME = total_seconds
            await query.edit_message_text(
                f"✅ *Custom Timer Set*\n\n"
                f"Timer: {timer_data['hours']:02d}:{timer_data['minutes']:02d}:{timer_data['seconds']:02d} ({total_seconds}s)",
                parse_mode='Markdown'
            )
            logger.info(f"Custom timer set to {total_seconds}s by user {user_id}")
        else:
            await query.answer("⚠️ Timer must be greater than 0 seconds", show_alert=True)
        return
    elif action == "custom_dummy":
        # Dummy button, just acknowledge
        await query.answer()
        return
    
    # Update the custom timer display
    await show_custom_timer(update, context)

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current bot status"""
    current_time = config.DEFAULT_TIME
    current_label = "off"
    
    for label, seconds in config.TIME_OPTIONS.items():
        if seconds == current_time:
            current_label = label
            break
    
    status_text = (
        f"📊 *Bot Status*\n\n"
        f"⏱️ Current timer: {current_label}\n"
        f"👥 Monitoring: This group\n"
        f"🗑️ Auto-delete: {'Enabled' if current_time > 0 else 'Disabled'}"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def delete_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a message"""
    try:
        # Extract chat_id and message_id from job data
        job = context.job
        chat_id = job.data['chat_id']
        message_id = job.data['message_id']
        
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted message {message_id} from chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and schedule deletion"""
    # Skip if it's a service message or from the bot itself
    if update.message is None or update.message.from_user is None:
        return
    
    if update.message.from_user.id == context.bot.id:
        return
    
    # Skip command messages
    if update.message.text and update.message.text.startswith('/'):
        return
    
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    delete_time = config.DEFAULT_TIME
    
    # Don't delete if timer is off
    if delete_time == 0:
        return
    
    # Schedule message deletion
    logger.info(f"Scheduling deletion of message {message_id} in {delete_time} seconds")
    
    # Store message info for potential cancellation
    config.message_timers[message_id] = (chat_id, delete_time)
    
    # Schedule deletion job
    context.job_queue.run_once(
        delete_message,
        delete_time,
        data={'chat_id': chat_id, 'message_id': message_id}
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors"""
    logger.error(f"Exception while handling update: {context.error}")

def main() -> None:
    """Start the bot"""
    # Check if bot token is set
    if not config.BOT_TOKEN or config.BOT_TOKEN == 'your_bot_token_here':
        logger.error("Please set your BOT_TOKEN in the .env file")
        return
    
    # Create application (job queue is enabled by default with [job-queue] extra)
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Ensure job queue is available
    if application.job_queue is None:
        logger.error("Failed to initialize job queue. Message auto-deletion will not work.")
        return
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("timer", show_timer_menu))
    application.add_handler(CommandHandler("status", show_status))
    application.add_handler(CallbackQueryHandler(set_timer, pattern=r'^set_timer_'))
    application.add_handler(CallbackQueryHandler(show_timer_menu, pattern=r'^show_timer$'))
    application.add_handler(CallbackQueryHandler(handle_custom_timer, pattern=r'^custom_'))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("Bot started successfully!")
    logger.info("Make sure to add the bot to your group and make it admin with delete permissions")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()