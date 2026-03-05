from functools import wraps
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authorization_check(func):
    """
    Decorator to check if user is authorized to use bot commands
    In groups, anyone can use commands. In private, only sudo users and owner.
    """
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # If in group/supergroup, allow all users
            if message.chat.type.name in ['GROUP', 'SUPERGROUP']:
                return await func(client, message, *args, **kwargs)
            
            # If in private chat, check if user is owner or sudo user
            if message.chat.type.name == 'PRIVATE':
                if message.from_user.id == Config.OWNER_ID:
                    return await func(client, message, *args, **kwargs)
                
                if Config.SUDO_USERS and message.from_user.id in Config.SUDO_USERS:
                    return await func(client, message, *args, **kwargs)
                
                await message.reply_text(
                    "❌ This command only works in groups or for authorized users!"
                )
                return
            
            # For other chat types, allow
            return await func(client, message, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authorization error: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    return wrapper


def admin_check(func):
    """
    Decorator to check if user is admin in the chat
    Only for group commands
    """
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            # Skip admin check for private chats
            if message.chat.type.name == 'PRIVATE':
                return await func(client, message, *args, **kwargs)
            
            # Check if in group
            if message.chat.type.name not in ['GROUP', 'SUPERGROUP']:
                return await func(client, message, *args, **kwargs)
            
            user_id = message.from_user.id
            
            # Owner can always use commands
            if user_id == Config.OWNER_ID:
                return await func(client, message, *args, **kwargs)
            
            # Sudo users can always use commands
            if Config.SUDO_USERS and user_id in Config.SUDO_USERS:
                return await func(client, message, *args, **kwargs)
            
            # Check if user is admin
            try:
                member = await client.get_chat_member(message.chat.id, user_id)
                
                if member.status in ['administrator', 'creator']:
                    return await func(client, message, *args, **kwargs)
                
                await message.reply_text(
                    "❌ This command requires administrator privileges!"
                )
                return
                
            except UserNotParticipant:
                await message.reply_text("❌ You are not a member of this chat!")
                return
            
        except ChatAdminRequired:
            await message.reply_text(
                "❌ I need to be an admin to perform this action!\n\n"
                "Please make me an admin first."
            )
            return
            
        except Exception as e:
            logger.error(f"Admin check error: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    return wrapper


def bot_admin_check(func):
    """
    Decorator to check if bot is admin in the chat
    """
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            if message.chat.type.name not in ['GROUP', 'SUPERGROUP']:
                return await func(client, message, *args, **kwargs)
            
            bot_me = await client.get_chat_member(
                message.chat.id,
                (await client.get_me()).id
            )
            
            if bot_me.status != 'administrator':
                await message.reply_text(
                    "❌ I need to be an admin to work in this chat!\n\n"
                    "Please add me as an admin."
                )
                return
            
            return await func(client, message, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Bot admin check error: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    return wrapper
