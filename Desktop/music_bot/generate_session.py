"""
Session String Generator for Assistant Account
Run this script ONCE to generate a session string for your assistant account
"""

from pyrogram import Client
import asyncio
import os

# Get these from my.telegram.org
API_ID = int(input("Enter API ID: "))
API_HASH = input("Enter API HASH: ")

async def generate_session():
    """Generate session string for assistant account"""
    
    print("\n🔐 Pyrogram Session String Generator\n")
    print("📱 Enter your phone number with country code (e.g., +1234567890)")
    
    async with Client(
        "assistant_session",
        api_id=API_ID,
        api_hash=API_HASH
    ) as app:
        # Get session string
        session_string = await app.export_session_string()
        
        print("\n✅ Session String Generated Successfully!\n")
        print("=" * 80)
        print(session_string)
        print("=" * 80)
        print("\n💾 Save this string in your .env file as ASSISTANT_SESSION_STRING")
        print("\n📝 Bot username:", (await app.get_me()).username)
        print("📝 Bot name:", (await app.get_me()).first_name)
        
        # Also save to file
        with open("assistant_session_string.txt", "w") as f:
            f.write(session_string)
        
        print("\n💡 Session string also saved to 'assistant_session_string.txt'")

if __name__ == "__main__":
    try:
        asyncio.run(generate_session())
    except KeyboardInterrupt:
        print("\n\n❌ Generation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
