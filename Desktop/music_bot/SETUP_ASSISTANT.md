# 🔐 Assistant Account Setup Guide

## Why You Need a Session String

The assistant account (@lilly_assistant) needs to join your groups to play music in voice chats. Using a **session string** is the most reliable method because:

✅ **No login required every time** - Generate once, use forever  
✅ **More stable than phone login** - No 2FA prompts  
✅ **Works in all environments** - Perfect for VPS/hosting  
✅ **Auto-invite to groups** - Bot can add assistant automatically  

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Login with your phone number (the one you want as assistant)
3. Click on **"API development tools"**
4. Create a new application (any name works)
5. Copy your **API ID** and **API HASH**

### Step 2: Generate Session String

```bash
# Run the session generator
python generate_session.py
```

**What happens:**
- Enter your API ID and API HASH
- Enter your phone number with country code (e.g., +1234567890)
- You'll receive a confirmation code from Telegram
- Enter the code
- If you have 2FA enabled, enter your password
- ✅ Session string generated!

**Example output:**
```
🔐 Pyrogram Session String Generator

📱 Enter your phone number with country code (e.g., +1234567890)

✅ Session String Generated Successfully!

================================================================================
1BVtsOKoBu... (long string) ...AAaBcDeFgHiJkLmNoPqRsTuVwXyZ
================================================================================

💾 Save this string in your .env file as ASSISTANT_SESSION_STRING
📝 Bot username: lilly_assistant
📝 Bot name: Lily x assistant

💡 Session string also saved to 'assistant_session_string.txt'
```

### Step 3: Configure Your .env File

Open `.env` and add the session string:

```env
# RECOMMENDED: Session String Method
ASSISTANT_SESSION_STRING=1BVtsOKoBu... (your full session string)

# Also add these (from my.telegram.org)
ASSISTANT_API_ID=12345678
ASSISTANT_API_HASH=your_api_hash_here
```

---

## 🎯 How It Works

### Before (Without Session String):
❌ Need to login with phone every time bot starts  
❌ 2FA code required on each restart  
❌ Can't auto-invite assistant to groups  
❌ Manual setup required  

### After (With Session String):
✅ One-time setup  
✅ Bot starts automatically  
✅ Auto-invites assistant to groups  
✅ Works on VPS/cloud hosting  

---

## 🤖 Auto-Invite Feature

Once configured with a session string, when you use `/play` in a new group:

1. Bot checks if @lilly_assistant is in the group
2. If not → **Bot automatically adds assistant**
3. Assistant joins voice chat
4. Music starts playing! 🎵

**Requirements for auto-invite:**
- Bot must be admin with "Add Members" permission
- Group must allow adding members
- Assistant account must be properly configured

---

## 🛠️ Troubleshooting

### "Peer id invalid" Error
**Cause:** Assistant account not in the group  
**Solution:** Use the session string method for auto-invite, or manually add @lilly_assistant

### "Session string expired" 
**Cause:** Session strings can expire if you logout from Telegram  
**Solution:** Regenerate with `python generate_session.py`

### "Can't invite assistant"
**Cause:** Bot doesn't have admin permissions  
**Solution:** Make bot an admin with "Add Members" permission

---

## 📝 Alternative Methods

### Method 2: Phone Number (Less Reliable)
```env
ASSISTANT_PHONE=+1234567890
ASSISTANT_API_ID=12345678
ASSISTANT_API_HASH=your_hash
# Leave ASSISTANT_SESSION_STRING empty
```
⚠️ Requires entering 2FA code every time bot starts

### Method 3: Bot Token (For Assistant Bot)
```env
ASSISTANT_BOT_TOKEN=bot_token_from_botfather
# Leave ASSISTANT_SESSION_STRING and ASSISTANT_PHONE empty
```
⚠️ Limited functionality (bots can't join some voice chats)

---

## 💡 Pro Tips

1. **Keep your session string private** - It's like a password
2. **Backup your .env file** - Contains all credentials
3. **Use the same API credentials** for both bot and assistant
4. **Test in a small group first** before deploying to production

---

## 🎉 Success Checklist

- [ ] Generated session string with `generate_session.py`
- [ ] Added `ASSISTANT_SESSION_STRING` to `.env`
- [ ] Set `ASSISTANT_API_ID` and `ASSISTANT_API_HASH`
- [ ] Restarted bot successfully
- [ ] Tested `/play` in a group
- [ ] Assistant joined voice chat automatically

**All done!** 🎵 Your music bot is now fully automated!

---

## 📞 Support

If you need help:
- Check the logs: Look for errors starting with ❌
- Read error messages carefully
- Make sure all environment variables are set correctly
- Test with `python generate_session.py` first

**Happy listening!** 🎶
