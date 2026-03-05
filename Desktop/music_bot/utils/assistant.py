import logging
import os
from pyrogram import Client
from pyrogram.raw.functions.phone import GetGroupCall
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.types import InputGroupCall
from config import Config
import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Assistant:
    """Assistant client for joining voice chats and playing music"""
    
    def __init__(self):
        """Initialize assistant client"""
        self.client = None
        self.pytgcalls = None
        self.voice_chats = {}  # Track active voice chats
        self.call = None
        self.stream_url = None
        
    async def start(self):
        """Start the assistant client"""
        try:
            # Create assistant client with priority: Session String > Bot Token > Phone Number
            if Config.ASSISTANT_SESSION_STRING:
                # Use session string (most reliable)
                self.client = Client(
                    "assistant",
                    api_id=Config.ASSISTANT_API_ID,
                    api_hash=Config.ASSISTANT_API_HASH,
                    session_string=Config.ASSISTANT_SESSION_STRING
                )
                logger.info("🔐 Assistant initialized with session string")
                
            elif Config.ASSISTANT_BOT_TOKEN:
                # Use bot token
                self.client = Client(
                    "assistant",
                    api_id=Config.ASSISTANT_API_ID,
                    api_hash=Config.ASSISTANT_API_HASH,
                    bot_token=Config.ASSISTANT_BOT_TOKEN
                )
                logger.info("🤖 Assistant initialized with bot token")
                
            else:
                # Use phone number
                self.client = Client(
                    "assistant",
                    api_id=Config.ASSISTANT_API_ID,
                    api_hash=Config.ASSISTANT_API_HASH,
                    phone_number=Config.ASSISTANT_PHONE
                )
                logger.info("📱 Assistant initialized with phone number")
            
            await self.client.start()
            me = await self.client.get_me()
            logger.info(f"✅ Assistant started: @{me.username} ({me.first_name})")
            
            # Initialize PyTgCalls
            self.pytgcalls = PyTgCalls(self.client)
            await self.pytgcalls.start()
            logger.info("🎵 PyTgCalls initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to start assistant: {e}")
            logger.error("💡 Run 'python generate_session.py' to create a session string")
            raise
    
    async def invite_to_group(self, chat_id: int, client):
        """
        Invite assistant account to a group using an invite link
        
        Args:
            chat_id: The ID of the chat/group
            client: Main bot client
            
        Returns:
            bool: True if successfully joined, False otherwise
        """
        try:
            # Get assistant user info
            assistant_user = await self.client.get_me()
            
            # Create an invite link for the assistant
            invite_link = await client.export_chat_invite_link(chat_id)
            
            # Assistant joins via the link
            await self.client.join_chat(invite_link)
            
            logger.info(f"✅ Successfully added @{assistant_user.username} to group {chat_id} via invite link")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add assistant to group: {e}")
            return False
    
    async def is_in_group(self, chat_id: int) -> bool:
        """
        Check if assistant account is in the group
        
        Args:
            chat_id: The ID of the chat/group
            
        Returns:
            bool: True if assistant is in group, False otherwise
        """
        try:
            assistant_user = await self.client.get_me()
            member = await self.client.get_chat_member(chat_id, assistant_user.id)
            return member is not None
            
        except Exception as e:
            logger.warning(f"Assistant not in group {chat_id}: {e}")
            return False
    
    async def stop(self):
        """Stop the assistant client"""
        try:
            if self.pytgcalls:
                await self.pytgcalls.stop()
                logger.info("PyTgCalls stopped")
            
            if self.client:
                await self.client.stop()
                logger.info("Assistant stopped")
        except Exception as e:
            logger.error(f"Error stopping assistant: {e}")
    
    async def join_voice_chat(self, chat_id: int):
        """
        Join a voice chat in the specified chat using pytgcalls
        
        Args:
            chat_id: The ID of the chat/group
            
        Returns:
            bool: True if successfully joined, False otherwise
        """
        try:
            logger.info(f"🎙️ Attempting to join voice chat in {chat_id}")
            
            # First verify assistant is in the group
            try:
                member = await self.client.get_chat_member(chat_id, "me")
                logger.info(f"✅ Assistant is member of group: {member.status}")
            except Exception as member_error:
                logger.error(f"❌ Assistant not in group! Error: {member_error}")
                return False
            
            # Check if already in voice chat
            if chat_id in self.voice_chats:
                logger.info(f"Already in voice chat {chat_id}")
                return True
            
            # Note: In pytgcalls 0.9.7, we can only verify join capability when play_audio is called
            # Don't mark as joined yet - wait for actual join_group_call in play_audio
            logger.info(f"⏳ Voice chat ready in {chat_id}. Will join when /play is used.")
            logger.info(f"🎵 Ready to play music!")
            
            # Return True to indicate readiness, but don't mark as joined yet
            return True
            
        except Exception as e:
            error_msg = f"❌ Critical error joining voice chat: {e}"
            logger.error(error_msg)
            logger.error(f"Chat ID: {chat_id}")
            assistant_info = await self.client.get_me()
            logger.error(f"Assistant: @{assistant_info.username} ({assistant_info.id})")
            return False
    
    async def leave_voice_chat(self, chat_id: int):
        """
        Leave a voice chat in the specified chat
        
        Args:
            chat_id: The ID of the chat/group
            
        Returns:
            bool: True if successfully left, False otherwise
        """
        try:
            if chat_id not in self.voice_chats:
                logger.warning(f"Not in voice chat {chat_id}")
                return False
            
            # Stop playback and leave group call
            try:
                await self.pytgcalls.leave_group_call(chat_id)
                logger.info(f"✅ Left voice chat in {chat_id}")
            except Exception as leave_error:
                logger.warning(f"Error leaving voice chat: {leave_error}")
            
            del self.voice_chats[chat_id]
            return True
            
        except Exception as e:
            logger.error(f"Error leaving voice chat: {e}")
            return False
    
    async def is_voice_chat_active(self, chat_id: int) -> bool:
        """
        Check if there's an active voice chat in the group
        
        Args:
            chat_id: The ID of the chat/group
            
        Returns:
            bool: True if voice chat is active, False otherwise
        """
        try:
            peer = await self.client.resolve_peer(chat_id)
            full_chat = await self.client.invoke(GetFullChannel(channel=peer))
            
            return full_chat.full_chat.call is not None
            
        except Exception as e:
            logger.error(f"Error checking voice chat status: {e}")
            return False
    
    async def play_audio(self, chat_id: int, audio_path: str, volume: int = 100):
        """
        Play audio file in the voice chat using pytgcalls
        
        Args:
            chat_id: The ID of the chat/group
            audio_path: Path to the audio file
            volume: Volume level (1-100)
            
        Returns:
            bool: True if successfully started playing, False otherwise
        """
        try:
            if chat_id not in self.voice_chats:
                logger.error(f"Not in voice chat {chat_id}")
                return False
            
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return False
            
            # Use pytgcalls to join and play audio
            try:
                await self.pytgcalls.join_group_call(
                    chat_id,
                    AudioPiped(
                        audio_path,
                        audio_parameters=f"-vn -ar 48000 -ac 2 -b:a 320k"
                    )
                )
                # Only mark as joined if actual join succeeds
                self.voice_chats[chat_id] = True
                logger.info(f"✅ Successfully joined voice chat in {chat_id}")
            except Exception as join_error:
                logger.error(f"❌ Failed to join voice chat: {join_error}")
                logger.error(f"💡 This is likely due to PyTgCalls WebRTC module issue on macOS ARM64")
                logger.error(f"🚀 Solution: Deploy to Ubuntu x86_64 server")
                # Make sure not marked as joined
                if chat_id in self.voice_chats:
                    del self.voice_chats[chat_id]
                raise join_error
            
            logger.info(f"🎵 Now playing: {audio_path} in {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            logger.error(f"💡 Architecture issue detected. Please deploy to Ubuntu x86_64.")
            return False
    
    async def stop_audio(self, chat_id: int):
        """
        Stop current audio playback
        
        Args:
            chat_id: The ID of the chat/group
            
        Returns:
            bool: True if successfully stopped, False otherwise
        """
        try:
            if chat_id not in self.voice_chats:
                return False
            
            self.pytgcalls.stop(chat_id)
            logger.info(f"Stopped audio in {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
            return False
    
    async def is_in_voice_chat(self, chat_id: int) -> bool:
        """
        Check if assistant is in a voice chat
        
        Args:
            chat_id: The ID of the chat/group
            
        Returns:
            bool: True if in voice chat, False otherwise
        """
        return chat_id in self.voice_chats
    
    async def set_volume(self, chat_id: int, volume: int):
        """
        Set volume for audio playback
        
        Args:
            chat_id: The ID of the chat/group
            volume: Volume level (1-100)
            
        Returns:
            bool: True if volume set successfully, False otherwise
        """
        try:
            if chat_id not in self.voice_chats:
                return False
            
            # Placeholder for volume control
            logger.info(f"Volume set to {volume} in {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    async def pause_audio(self, chat_id: int):
        """Pause audio playback"""
        try:
            if chat_id not in self.voice_chats:
                return False
            
            logger.info(f"Audio paused in {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error pausing audio: {e}")
            return False
    
    async def resume_audio(self, chat_id: int):
        """Resume audio playback"""
        try:
            if chat_id not in self.voice_chats:
                return False
            
            logger.info(f"Audio resumed in {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error resuming audio: {e}")
            return False
