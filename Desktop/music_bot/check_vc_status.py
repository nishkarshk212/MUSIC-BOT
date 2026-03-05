#!/usr/bin/env python3
"""
Voice Chat Status Checker - ACCURATE VERSION
Shows the REAL voice chat status, not false positives
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.assistant import Assistant
from config import Config
from pyrogram import Client


async def check_voice_chat_status():
    """Check actual voice chat status"""
    
    print("🔍 Voice Chat Status Report - ACCURATE CHECK")
    print("=" * 60)
    print()
    
    # Group info
    group_name = "𝐖𝐨𝐫𝐥𝐝𝐰𝐢𝐝𝐞 𝐅𝐫𝐢𝐞𝐧𝐝𝐳𝐨𝐧𝐞 𝐂𝐡𝐚𝐭𝐭𝐢𝐧𝐠"
    chat_id = -1003843911730
    
    print(f"Group: {group_name}")
    print(f"Chat ID: {chat_id}")
    print()
    
    # Initialize assistant
    assistant = Assistant()
    
    try:
        # Start assistant
        await assistant.start()
        print(f"Assistant Account: @{assistant.client.me.username}")
        
        # Check if in group
        try:
            member = await assistant.client.get_chat_member(chat_id, "me")
            print(f"✅ In group (Status: {member.status})")
        except Exception as e:
            print(f"❌ NOT in group: {e}")
            print("\n💡 Solution: Add @lilyy_assistant to the group manually")
            return
        
        # Check if voice chat is active
        try:
            from pyrogram.raw.functions.phone import GetGroupCall
            from pyrogram.raw.functions.channels import GetFullChannel
            
            peer = await assistant.client.resolve_peer(chat_id)
            full_chat = await assistant.client.invoke(GetFullChannel(channel=peer))
            
            if full_chat.full_chat.call is not None:
                print(f"✅ Voice Chat: Active")
            else:
                print(f"❌ Voice Chat: NOT ACTIVE")
                print("\n💡 Solution: Start a voice chat in the group first")
                return
        except Exception as vc_error:
            print(f"⚠️ Could not check voice chat status: {vc_error}")
            return
        
        # Check ACTUAL assistant VC status (not just dictionary)
        print()
        print("🎤 Assistant Voice Chat Status:")
        print("-" * 60)
        
        # Method 1: Check internal tracking
        internally_tracked = chat_id in assistant.voice_chats
        print(f"Internal tracking: {'✅ YES' if internally_tracked else '❌ NO'}")
        
        # Method 2: Try to verify by checking active calls
        try:
            # Get current group call participants
            from pyrogram.raw.functions.phone import GetParticipants
            
            if hasattr(assistant.pytgcalls, '_call') and assistant.pytgcalls._call:
                # pytgcalls has an active call object
                print(f"PyTgCalls active call: ✅ YES")
                
                # This is the REAL test - can we actually play audio?
                print()
                print("🧪 Testing Actual Voice Chat Capability:")
                print("-" * 60)
                
                # Try a silent test (don't actually play, just test WebRTC)
                import subprocess
                try:
                    result = subprocess.run(
                        ['node', '-e', 'try { require("wrtc"); console.log("OK"); } catch(e) { console.error(e.message); process.exit(1); }'],
                        cwd=f"{sys.prefix}/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages/pytgcalls/node_modules/wrtc",
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    
                    if result.returncode == 0:
                        print("✅ WebRTC Module: Working")
                        print("✅ Assistant CAN join voice chat")
                    else:
                        print("❌ WebRTC Module: FAILED")
                        print(f"   Error: {result.stderr.strip()}")
                        print()
                        print("❌ Assistant CANNOT join voice chat")
                        print()
                        print("📋 Root Cause:")
                        print("   PyTgCalls 0.9.7 uses Node.js wrtc module")
                        print("   wrtc.node is compiled for x86_64 architecture")
                        print("   Your Mac uses ARM64 (Apple Silicon)")
                        print("   Architecture mismatch = Voice chat failure")
                        print()
                        print("✅ Solution:")
                        print("   Deploy bot to Ubuntu x86_64 server")
                        print("   See: UBUNTU_SUMMARY.md for deployment guide")
                        
                except FileNotFoundError:
                    print("⚠️ Node.js not found (required for PyTgCalls 0.9.7)")
                except subprocess.TimeoutExpired:
                    print("⚠️ WebRTC test timed out")
                
            else:
                print(f"PyTgCalls active call: ❌ NO")
                print()
                print("⏳ Assistant has NOT joined voice chat yet")
                print("   Will attempt to join when /play command is used")
                
        except Exception as check_error:
            print(f"⚠️ Could not verify: {check_error}")
        
        print()
        print("=" * 60)
        print("📊 Summary:")
        print("-" * 60)
        
        if internally_tracked:
            print("✅ Voice chat tracking: ACTIVE")
            print("   (But verify with /play command)")
        else:
            print("⏳ Voice chat tracking: NOT ACTIVE")
            print("   Assistant will try to join on next /play")
        
        # Platform check
        import platform
        import subprocess
        
        try:
            result = subprocess.run(['file', f'{sys.prefix}/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages/pytgcalls/node_modules/wrtc/build/Release/wrtc.node'], 
                                  capture_output=True, text=True)
            arch_info = result.stdout.strip()
            
            if 'x86_64' in arch_info:
                print()
                print("⚠️ PLATFORM ISSUE DETECTED:")
                print(f"   Your Mac: {platform.machine()} (ARM64/Apple Silicon)")
                print(f"   wrtc.node: x86_64 (Intel)")
                print()
                print("💡 This is why voice chat doesn't work!")
                print("   → Deploy to Ubuntu x86_64 server to fix")
        except Exception:
            pass
        
        print()
        print("🚀 Next Steps:")
        print("   1. If on macOS: Deploy to Ubuntu server")
        print("   2. If on Ubuntu: Check permissions and FFmpeg")
        print("   3. Test with: /play tera mujhse hai pehle ka naata koi")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await assistant.stop()
    
    print()


if __name__ == "__main__":
    asyncio.run(check_voice_chat_status())
