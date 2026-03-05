import logging
import asyncio
import os
import yt_dlp
from typing import Dict, List, Optional, Any
from config import Config
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicPlayer:
    """Music player for managing queues and playback"""
    
    def __init__(self):
        """Initialize music player"""
        self.queues: Dict[int, List[Dict]] = {}  # chat_id -> queue list
        self.current: Dict[int, Dict] = {}  # chat_id -> current song
        self.is_playing_dict: Dict[int, bool] = {}  # chat_id -> playing status
        self.download_path = tempfile.gettempdir() + "/music_bot/"
        
        # Create download directory
        os.makedirs(self.download_path, exist_ok=True)
        
    async def download_audio(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download audio from URL using yt-dlp
        
        Args:
            url: YouTube or other supported URL
            
        Returns:
            dict with file_path, title, duration, thumbnail or None if failed
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.download_path}%(id)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    return None
                
                # Get the file path after conversion
                file_path = f"{self.download_path}{info['id']}.mp3"
                
                return {
                    'file_path': file_path,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'url': url
                }
                
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None
    
    async def search_youtube(self, query: str) -> Optional[str]:
        """
        Search YouTube and return the first result URL
        
        Args:
            query: Search query
            
        Returns:
            YouTube URL or None if not found
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch1',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)
                
                if result and 'entries' in result and len(result['entries']) > 0:
                    video = result['entries'][0]
                    return f"https://www.youtube.com/watch?v={video['id']}"
                    
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
        
        return None
    
    async def add_to_queue(
        self,
        chat_id: int,
        query: str,
        requested_by: int,
        message=None
    ) -> Optional[Dict]:
        """
        Add a song to the queue
        
        Args:
            chat_id: The ID of the chat
            query: Song name or URL
            requested_by: User ID who requested the song
            message: Original message object
            
        Returns:
            Song info dict or None if failed
        """
        try:
            # Check if URL or search query
            is_url = query.startswith(('http://', 'https://'))
            
            if not is_url:
                # Search YouTube
                logger.info(f"Searching for: {query}")
                youtube_url = await self.search_youtube(query)
                
                if not youtube_url:
                    return None
                
                query = youtube_url
            
            # Download the audio
            logger.info(f"Downloading: {query}")
            song_info = await self.download_audio(query)
            
            if not song_info:
                return None
            
            # Format duration
            duration_seconds = song_info['duration']
            duration_str = self.format_duration(duration_seconds)
            
            # Check max duration
            if duration_seconds > Config.MAX_DURATION:
                logger.warning(f"Song too long: {duration_seconds}s")
                # Clean up downloaded file
                if os.path.exists(song_info['file_path']):
                    os.remove(song_info['file_path'])
                return None
            
            # Get requester name
            requester_name = "Unknown"
            if message and hasattr(message, 'from_user'):
                requester_name = message.from_user.first_name
            
            # Create song entry
            song_entry = {
                'title': song_info['title'],
                'file_path': song_info['file_path'],
                'duration': duration_str,
                'duration_seconds': duration_seconds,
                'requested_by': requested_by,
                'requester_name': requester_name,
                'thumbnail': song_info.get('thumbnail', ''),
                'uploader': song_info.get('uploader', 'Unknown')
            }
            
            # Initialize queue if not exists
            if chat_id not in self.queues:
                self.queues[chat_id] = []
            
            # Add to queue
            self.queues[chat_id].append(song_entry)
            position = len(self.queues[chat_id])
            
            logger.info(f"Added to queue: {song_info['title']} at position {position}")
            
            song_entry['position'] = position
            return song_entry
            
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            return None
    
    async def play_next(
        self,
        chat_id: int,
        assistant,
        client
    ):
        """
        Play the next song in the queue
        
        Args:
            chat_id: The ID of the chat
            assistant: Assistant instance
            client: Bot client instance
        """
        try:
            # Check if there's a queue
            if chat_id not in self.queues or len(self.queues[chat_id]) == 0:
                logger.info(f"No songs in queue for {chat_id}")
                self.is_playing_dict[chat_id] = False
                return
            
            # Get next song
            song = self.queues[chat_id].pop(0)
            
            # Set as current
            self.current[chat_id] = song
            self.is_playing_dict[chat_id] = True
            
            logger.info(f"Playing: {song['title']} in {chat_id}")
            
            # Check if assistant is in the group
            assistant_in_group = await assistant.is_in_group(chat_id)
            if not assistant_in_group:
                logger.warning(f"⚠️ Assistant not in group {chat_id}, attempting to invite...")
                
                # Get bot and assistant info first
                bot_info = await client.get_me()
                assistant_info = await assistant.client.get_me()
                
                # Try to invite assistant
                invited = await assistant.invite_to_group(chat_id, client)
                
                if not invited:
                    await client.send_message(
                        chat_id,
                        f"❌ **Assistant Not In Group!**\n\n"
                        f"**Problem:** @{assistant_info.username} is not a member of this group.\n\n"
                        f"**Quick Fix (Choose One):**\n\n"
                        f"**Option 1 - Manual Add (Fastest):**\n"
                        f"1. Go to group info\n"
                        f"2. Tap 'Add Members'\n"
                        f"3. Search: @{assistant_info.username}\n"
                        f"4. Add to group\n"
                        f"5. Promote as admin with 'Manage Voice Chats' permission\n"
                        f"6. Start a voice chat\n"
                        f"7. Use /play again\n\n"
                        f"**Option 2 - Use Invite Link:**\n"
                        f"• Make sure bot (@{bot_info.username}) is admin with 'Add Members' permission\n"
                        f"• Bot will try to generate invite link automatically\n\n"
                        f"**Option 3 - Generate Session String:**\n"
                        f"• Run: `python generate_session.py`\n"
                        f"• Add ASSISTANT_SESSION_STRING to .env\n"
                        f"• Restart bot for auto-invite feature\n\n"
                        f"**Current Status:**\n"
                        f"🤖 Bot: @{bot_info.username}\n"
                        f"👤 Assistant: @{assistant_info.username}\n"
                        f"🆔 Chat ID: `{chat_id}`"
                    )
                    return
                
                await client.send_message(
                    chat_id,
                    f"✅ **Assistant Added Successfully!**\n\n"
                    f"@{assistant_info.username} has joined the group via invite link.\n"
                    f"Now joining voice chat..."
                )
            
            # Check if voice chat is active in the group
            is_vc_active = await assistant.is_voice_chat_active(chat_id)
            if not is_vc_active:
                logger.warning(f"No active voice chat in {chat_id}")
                await client.send_message(
                    chat_id,
                    "❌ **No Active Voice Chat!**\n\n"
                    "Please start a voice chat in your group first, then try again.\n\n"
                    "**How to start:**\n"
                    "1. Tap on the phone/video icon in your group\n"
                    "2. Start a voice chat\n"
                    "3. Use /play again to make me join"
                )
                return
            
            # Join voice chat if not already in
            if not await assistant.is_in_voice_chat(chat_id):
                joined = await assistant.join_voice_chat(chat_id)
                if not joined:
                    logger.error("Failed to join voice chat")
                    bot_info = await client.get_me()
                    await client.send_message(
                        chat_id,
                        f"❌ **Failed to Join Voice Chat!**\n\n"
                        f"**Possible Reasons:**\n"
                        f"1. No active voice chat in this group\n"
                        f"2. Assistant (@lilly_assistant) is not an admin\n"
                        f"3. Assistant doesn't have voice chat permissions\n\n"
                        f"**Solution:**\n"
                        f"• Make @{bot_info.username} and @lilly_assistant both admins\n"
                        f"• Grant 'Manage Voice Chats' permission\n"
                        f"• Start a voice chat first\n"
                        f"• Try /play again"
                    )
                    return
            
            # Play the audio
            play_success = await assistant.play_audio(chat_id, song['file_path'])
            
            if not play_success:
                # Failed to join voice chat - likely macOS ARM64 issue
                bot_info = await client.get_me()
                assistant_info = await assistant.client.get_me()
                await client.send_message(
                    chat_id,
                    f"❌ **Failed to Join Voice Chat!**\n\n"
                    f"**Issue:** Assistant (@{assistant_info.username}) cannot connect to voice chat.\n\n"
                    f"**Reason:** This is a known compatibility issue with PyTgCalls on macOS ARM64 (Apple Silicon).\n\n"
                    f"**✅ Solution:** The bot needs to be deployed on an Ubuntu x86_64 server for voice chat functionality.\n\n"
                    f"**Current Status**:\\n"
                    f"🤖 Bot: @{bot_info.username}\n"
                    f"👤 Assistant: @{assistant_info.username}\n"
                    f"💻 Platform: macOS (ARM64) - Not compatible with voice chats\n\n"
                    f"📚 See `UBUNTU_SUMMARY.md` for deployment guide."
                )
                return
            
            # Send notification
            await client.send_message(
                chat_id,
                f"🎵 **Now Playing:**\n\n"
                f"**Title:** {song['title']}\n"
                f"**Duration:** {song['duration']}\n"
                f"**Requested by:** {song['requester_name']}"
            )
            
            # Monitor playback
            asyncio.create_task(self.monitor_playback(chat_id, assistant, client, song))
            
        except Exception as e:
            logger.error(f"Error playing next song: {e}")
            self.is_playing_dict[chat_id] = False
    
    async def monitor_playback(
        self,
        chat_id: int,
        assistant,
        client,
        song: Dict
    ):
        """
        Monitor playback and play next song when finished
        
        Args:
            chat_id: The ID of the chat
            assistant: Assistant instance
            client: Bot client instance
            song: Current song info
        """
        try:
            # Wait for song duration
            await asyncio.sleep(song['duration_seconds'])
            
            # Clean up file
            if os.path.exists(song['file_path']):
                os.remove(song['file_path'])
            
            # Play next song
            await self.play_next(chat_id, assistant, client)
            
        except Exception as e:
            logger.error(f"Error monitoring playback: {e}")
    
    def pause(self, chat_id: int) -> bool:
        """Pause current playback"""
        if chat_id not in self.is_playing_dict or not self.is_playing_dict[chat_id]:
            return False
        
        self.is_playing_dict[chat_id] = False
        logger.info(f"Paused playback in {chat_id}")
        return True
    
    def resume(self, chat_id: int) -> bool:
        """Resume paused playback"""
        if chat_id not in self.is_playing_dict:
            return False
        
        self.is_playing_dict[chat_id] = True
        logger.info(f"Resumed playback in {chat_id}")
        return True
    
    async def skip_current(self, chat_id: int) -> bool:
        """Skip current song"""
        if chat_id not in self.queues or len(self.queues[chat_id]) == 0:
            return False
        
        # Remove current song file
        if chat_id in self.current and self.current[chat_id]:
            file_path = self.current[chat_id].get('file_path')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        
        self.current[chat_id] = None
        logger.info(f"Skipped song in {chat_id}")
        return True
    
    async def stop(self, chat_id: int, assistant) -> bool:
        """
        Stop playback and clear queue
        
        Args:
            chat_id: The ID of the chat
            assistant: Assistant instance
        """
        try:
            # Clear queue
            if chat_id in self.queues:
                # Delete all downloaded files
                for song in self.queues[chat_id]:
                    if 'file_path' in song and os.path.exists(song['file_path']):
                        os.remove(song['file_path'])
                del self.queues[chat_id]
            
            # Clear current
            if chat_id in self.current:
                if self.current[chat_id] and 'file_path' in self.current[chat_id]:
                    if os.path.exists(self.current[chat_id]['file_path']):
                        os.remove(self.current[chat_id]['file_path'])
                del self.current[chat_id]
            
            # Stop assistant audio
            await assistant.stop_audio(chat_id)
            
            # Leave voice chat
            await assistant.leave_voice_chat(chat_id)
            
            self.is_playing_dict[chat_id] = False
            
            logger.info(f"Stopped playback in {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
            return False
    
    def get_queue(self, chat_id: int) -> List[Dict]:
        """Get current queue for a chat"""
        return self.queues.get(chat_id, [])
    
    def get_current(self, chat_id: int) -> Optional[Dict]:
        """Get current playing song"""
        return self.current.get(chat_id)
    
    def is_playing(self, chat_id: int) -> bool:
        """Check if currently playing"""
        return self.is_playing_dict.get(chat_id, False)
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
