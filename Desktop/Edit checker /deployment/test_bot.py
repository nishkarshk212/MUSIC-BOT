import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bot_token():
    """Test if bot token is properly configured"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        logger.error("❌ BOT_TOKEN not found in environment variables")
        logger.error("Please set BOT_TOKEN in your .env file or environment variables")
        return False
    
    if bot_token.startswith('your_') or bot_token == 'your_bot_token_here':
        logger.error("❌ Invalid BOT_TOKEN - please replace with your actual bot token")
        return False
    
    logger.info("✅ BOT_TOKEN found and appears valid")
    return True

def test_dependencies():
    """Test if required dependencies are installed"""
    try:
        import telegram
        logger.info(f"✅ python-telegram-bot version: {telegram.__version__}")
    except ImportError:
        logger.error("❌ python-telegram-bot not installed")
        return False
    
    try:
        import dotenv
        logger.info("✅ python-dotenv installed")
    except ImportError:
        logger.error("❌ python-dotenv not installed")
        return False
    
    return True

if __name__ == '__main__':
    print("Testing bot configuration...\n")
    
    deps_ok = test_dependencies()
    token_ok = test_bot_token()
    
    if deps_ok and token_ok:
        print("\n✅ All tests passed! Your bot should work correctly.")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")