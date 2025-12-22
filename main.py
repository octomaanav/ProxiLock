# import asyncio
# import subprocess
# import getpass
# import time
# from enum import Enum
# from bleak import BleakScanner
# from config import *
# from controller import ProximityController

# class LockOwner(Enum):
#     SCRIPT = "script"
#     USER = "user"
#     NONE = "none"

# controller = ProximityController(
#     RSSI_NEAR, 
#     RSSI_FAR
# )

# last_proximity = None
# consecutive_far_count = 0
# lock_owner = LockOwner.NONE
# script_lock_time = 0
# SCRIPT_GRACE = 2.0  # Grace window to avoid race conditions

# def lock_mac_screen():
#     """Lock the Mac screen when device moves away - ONLY this function may mark SCRIPT"""
#     global lock_owner, script_lock_time
#     try:
#         result = subprocess.run([
#             "osascript",
#             "-e",
#             'tell application "System Events" to keystroke "q" using {command down, control down}'
#         ], check=True, capture_output=True, timeout=2)
#         print("🔒 Screen locked by script")
#         if not is_screen_locked():
#             lock_owner = LockOwner.SCRIPT
#             script_lock_time = time.time()
#         return
#     except subprocess.CalledProcessError as e:
#         if "not allowed" in str(e.stderr, 'utf-8', errors='ignore'):
#             print("⚠️ Need Accessibility permissions - grant Terminal access in System Settings → Privacy & Security → Accessibility")
#         pass
#     except (subprocess.TimeoutExpired, FileNotFoundError):
#         pass

#     try:
#         subprocess.run([
#             "osascript",
#             "-e",
#             'tell application "ScreenSaverEngine" to activate'
#         ], check=True, capture_output=True, timeout=1)
#         print("🔒 Screen locked by script (via screen saver)")
#         lock_owner = LockOwner.SCRIPT
#         script_lock_time = time.time()
#         return
#     except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
#         pass

#     print("⚠️ Failed to lock screen")

# def update_lock_state():
#     """Detect manual lock - THIS is what detects USER locks"""
#     global lock_owner
#     locked = is_screen_locked()

#     # Grace window: if screen is locked and script just locked it recently, keep SCRIPT
#     if locked and lock_owner == LockOwner.SCRIPT:
#         if time.time() - script_lock_time < SCRIPT_GRACE:
#             return  # Still within grace window, keep SCRIPT

#     # If screen is locked but script didn't just lock it → USER
#     if locked and lock_owner != LockOwner.SCRIPT:
#         lock_owner = LockOwner.USER

#     # If screen is unlocked → reset
#     if not locked:
#         lock_owner = LockOwner.NONE

# def is_screen_locked():
#     """Check if the Mac screen is currently locked using ioreg and PlistBuddy"""
#     try:
#         result = subprocess.run(
#             '/usr/libexec/PlistBuddy -c "print :IOConsoleUsers:0:CGSSessionScreenIsLocked" /dev/stdin <<< "$(ioreg -n Root -d1 -a)"',
#             shell=True,
#             capture_output=True,
#             text=True,
#             timeout=2
#         )
#         # If return code is 0, the key exists - check its value
#         if result.returncode == 0:
#             return result.stdout.strip().lower() == "true"
#         # If return code is non-zero, check if it's because the key doesn't exist (unlocked)
#         # or an actual error
#         if "Does Not Exist" in result.stderr:
#             # Key doesn't exist = screen is unlocked
#             return False
#         # Other error - can't determine, assume unlocked (fail open)
#         return False
#     except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
#         # Can't determine, assume unlocked (fail open)
#         return False

# def get_password_from_keychain():
#     """Retrieve password from macOS keychain"""
#     try:
#         result = subprocess.run([
#             "security",
#             "find-generic-password",
#             "-w",  # Write password to stdout
#             "-a", getpass.getuser(),  # Account (username)
#             "-s", KEYCHAIN_ITEM  # Service name
#         ], check=True, capture_output=True, timeout=2)
#         password = result.stdout.decode('utf-8').strip()
#         return password
#     except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
#         return None

# def unlock_mac_screen():
#     """Wake and unlock the Mac screen when device comes near"""
#     import time
#     print("🔓 Attempting to unlock screen...")
#     # Wake the display
#     try:
#         subprocess.run([
#             "caffeinate",
#             "-u",
#             "-t",
#             "1"
#         ], check=True, capture_output=True, timeout=2)
#     except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
#         pass

#     # Wait a moment for lock screen to appear
#     time.sleep(0.5)

#     # Get password from keychain
#     password = get_password_from_keychain()
#     if not password:
#         print("⚠️ Password not found in keychain. Run: python setup_password.py")
#         return

#     # Type password as a single string (much faster than character by character)
#     try:
#         # Escape special characters for AppleScript
#         escaped_password = password.replace('\\', '\\\\').replace('"', '\\"')
#         # Type entire password at once, then press Enter
#         script = f'''
#         tell application "System Events"
#             keystroke "{escaped_password}"
#             delay 0.1
#             key code 36
#         end tell
#         '''
#         subprocess.run([
#             "osascript",
#             "-e",
#             script
#         ], check=True, capture_output=True, timeout=2)
#         print("🔓 Screen unlocked")
#         return
#     except subprocess.CalledProcessError as e:
#         error_msg = str(e.stderr, 'utf-8', errors='ignore') if e.stderr else str(e)
#         if "not allowed" in error_msg:
#             print("⚠️ Need Accessibility permissions for auto-unlock")
#             print(" Grant Terminal access in: System Settings → Privacy & Security → Accessibility")
#         else:
#             print(f"⚠️ Unlock failed: {error_msg}")
#         pass
#     except (subprocess.TimeoutExpired, FileNotFoundError) as e:
#         print(f"⚠️ Unlock error: {e}")
#         pass

# def setup_password():
#     """Setup function to store password in keychain"""
#     print("Setting up password in keychain...")
#     password = getpass.getpass("Enter your Mac password: ")
#     try:
#         # Store password in keychain
#         subprocess.run([
#             "security",
#             "add-generic-password",
#             "-a", getpass.getuser(),
#             "-s", KEYCHAIN_ITEM,
#             "-w", password,
#             "-U"  # Update if exists
#         ], check=True, capture_output=True)
#         print("✅ Password stored securely in keychain")
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Failed to store password: {e}")

# def detection_callback(device, advertisement_data):
#     global last_proximity, consecutive_far_count, lock_owner
#     if device.name != TARGET_NAME:
#         return

#     rssi = advertisement_data.rssi
#     proximity = controller.get_proximity(rssi)
#     midpoint = controller.get_midpoint()

#     # State machine logic
#     # ONLY reset consecutive counter if RSSI > midpoint (signal improving)
#     if rssi > midpoint:
#         if consecutive_far_count > 0:
#             print(f"RSSI: {rssi} > Midpoint ({midpoint:.1f}) | Reset FAR counter (was {consecutive_far_count})")
#         consecutive_far_count = 0

#     if proximity == "FAR":
#         consecutive_far_count += 1
#         print(f"FAR | RSSI: {rssi} | FAR_POINT={RSSI_FAR}, NEAR_POINT={RSSI_NEAR}, Midpoint={midpoint:.1f} | Consecutive: {consecutive_far_count}/{CONSECUTIVE_FAR_REQUIRED}")
#         if consecutive_far_count >= CONSECUTIVE_FAR_REQUIRED:
#             if last_proximity != "FAR" or consecutive_far_count == CONSECUTIVE_FAR_REQUIRED:
#                 print(f"🔒 Locking screen (FAR confirmed after {consecutive_far_count} consecutive readings)")
#                 lock_mac_screen()  # This sets lock_owner = SCRIPT
#     else:
#         # NEAR detected - but don't reset counter unless RSSI > midpoint
#         if proximity == "NEAR":
#             print(f"NEAR | RSSI: {rssi} | Counter: {consecutive_far_count} (reset only if RSSI > {midpoint:.1f})")
#             # Rule C: Unlock only if lock_owner == SCRIPT
#             if last_proximity != "NEAR":
#                 if lock_owner == LockOwner.SCRIPT:
#                     print("🔓 Unlocking (script-owned lock)")
#                     unlock_mac_screen()
#                     lock_owner = LockOwner.NONE
#                     consecutive_far_count = 0
#                 elif lock_owner == LockOwner.USER:
#                     print("🔐 Locked by user — unlock blocked")
#                 else:
#                     print("ℹ️ Screen already unlocked (skipping unlock)")

#     last_proximity = proximity

# async def monitor():
#     global lock_owner
#     # Initialize lock state
#     update_lock_state()
#     if lock_owner == LockOwner.USER:
#         print("ℹ️ Screen is locked at startup (assumed user-locked)")
#     else:
#         print("ℹ️ Screen is unlocked at startup")

#     scanner = BleakScanner(detection_callback)
#     await scanner.start()
#     print("Scanning for", TARGET_NAME)

#     try:
#         while True:
#             update_lock_state()  # Continuously check for manual locks
#             await asyncio.sleep(SCAN_INTERVAL)
#     finally:
#         await scanner.stop()

# if __name__ == "__main__":
#     asyncio.run(monitor())



"""Main entry point - orchestrates BLE scanning, proximity detection, and lock management"""
import asyncio
from config import CONSECUTIVE_FAR_REQUIRED, SCAN_INTERVAL, UNLOCK_RSSI, LOCK_RSSI
from scanner import ProximityScanner
from lock_manager import lock_mac_screen, unlock_mac_screen, is_screen_locked
from lock_security import (
    LockOwner, 
    mark_script_lock, 
    update_lock_state, 
    get_lock_owner, 
    reset_lock_owner
)

def proximity_callback(proximity, rssi, midpoint, consecutive_far_count):
    """Handle proximity state changes"""
    global last_proximity, scanner_instance
    
    if proximity == "FAR":
        print(f"FAR | RSSI: {rssi} (≤ {LOCK_RSSI}) | Consecutive: {consecutive_far_count}/{CONSECUTIVE_FAR_REQUIRED}")
        
        if consecutive_far_count >= CONSECUTIVE_FAR_REQUIRED:
            if last_proximity != "FAR" or consecutive_far_count == CONSECUTIVE_FAR_REQUIRED:
                print(f"🔒 Locking screen (FAR confirmed after {consecutive_far_count} consecutive readings)")
                # Only mark as SCRIPT if screen wasn't already locked
                if not is_screen_locked():
                    if lock_mac_screen():
                        mark_script_lock()  # Rule A: Mark script as lock owner
                        # Reset consecutive counter after successful lock
                        if scanner_instance:
                            scanner_instance.reset_consecutive_far_count()
                else:
                    # Reset counter since screen is already locked - no need to keep counting
                    if scanner_instance:
                        scanner_instance.reset_consecutive_far_count()
    
    elif proximity == "NEAR":
        # Only unlock when truly NEAR (RSSI >= UNLOCK_RSSI)
        print(f"NEAR | RSSI: {rssi} (≥ {UNLOCK_RSSI}) | Counter: {consecutive_far_count}")
        
        # Rule C: Unlock only if lock_owner == SCRIPT AND device is truly NEAR
        if last_proximity != "NEAR":
            lock_owner = get_lock_owner()
            if lock_owner == LockOwner.SCRIPT:
                print("🔓 Unlocking (script-owned lock, device is truly near)")
                unlock_mac_screen()
                reset_lock_owner()
                if scanner_instance:
                    scanner_instance.reset_consecutive_far_count()
            elif lock_owner == LockOwner.USER:
                print("🔐 Locked by user — unlock blocked")
            else:
                print("ℹ️  Screen already unlocked (skipping unlock)")
    
    elif proximity == "MID":
        # Dead zone: no action (RSSI between LOCK_RSSI and UNLOCK_RSSI)
        print(f"MID  | RSSI: {rssi} (dead zone: {LOCK_RSSI} < RSSI < {UNLOCK_RSSI}) | Counter: {consecutive_far_count} | No action")
    
    last_proximity = proximity

# Global state
last_proximity = None
scanner_instance = None

async def monitor():
    global scanner_instance
    
    # Initialize lock state
    update_lock_state()
    lock_owner = get_lock_owner()
    
    # Initialize scanner
    scanner_instance = ProximityScanner(proximity_callback)
    await scanner_instance.start()

    try:
        while True:
            update_lock_state()
            await asyncio.sleep(SCAN_INTERVAL)
    finally:
        await scanner_instance.stop()

if __name__ == "__main__":
    asyncio.run(monitor())
