#!/usr/bin/env python3
"""
Test script to verify bot configuration and dependencies
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import telegram
        print("✅ python-telegram-bot installed")
    except ImportError:
        print("❌ python-telegram-bot not installed")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    try:
        import config
        print("✅ Config module loaded")
        
        if not config.BOT_TOKEN or config.BOT_TOKEN == 'your_bot_token_here':
            print("⚠️  Bot token not configured in .env file")
            return False
        else:
            print("✅ Bot token configured")
            
        print(f"✅ Default time setting: {config.DEFAULT_TIME} seconds")
        print(f"✅ Available time options: {list(config.TIME_OPTIONS.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def main():
    print("🤖 Telegram Self-Destruct Bot - Test Script")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration tests failed.")
        print("Please check your .env file and make sure BOT_TOKEN is set.")
        sys.exit(1)
    
    print("\n✅ All tests passed! You're ready to run the bot.")
    print("\nTo start the bot, run: python bot.py")

if __name__ == "__main__":
    main()