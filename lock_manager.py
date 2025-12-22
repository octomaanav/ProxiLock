"""Screen lock/unlock system interactions"""
import subprocess
import getpass
import time
from config import KEYCHAIN_ITEM

def is_screen_locked():
    """Check if the Mac screen is currently locked using ioreg and PlistBuddy"""
    try:
        result = subprocess.run(
            '/usr/libexec/PlistBuddy -c "print :IOConsoleUsers:0:CGSSessionScreenIsLocked" /dev/stdin <<< "$(ioreg -n Root -d1 -a)"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=2
        )
        
        # If return code is 0, the key exists - check its value
        if result.returncode == 0:
            return result.stdout.strip().lower() == "true"
        
        # If return code is non-zero, check if it's because the key doesn't exist (unlocked)
        if "Does Not Exist" in result.stderr:
            # Key doesn't exist = screen is unlocked
            return False
        
        # Other error - can't determine, assume unlocked (fail open)
        return False

    except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Can't determine, assume unlocked (fail open)
        return False

def lock_mac_screen():
    """Lock the Mac screen when device moves away"""
    try:
        result = subprocess.run([
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "q" using {command down, control down}'
        ], check=True, capture_output=True, timeout=2)
        print("🔒 Screen locked")
        return True
    except subprocess.CalledProcessError as e:
        if "not allowed" in str(e.stderr, 'utf-8', errors='ignore'):
            print("⚠️  Need Accessibility permissions - grant Terminal access in System Settings → Privacy & Security → Accessibility")
        pass
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    try:
        subprocess.run([
            "osascript",
            "-e",
            'tell application "ScreenSaverEngine" to activate'
        ], check=True, capture_output=True, timeout=1)
        print("🔒 Screen locked (via screen saver)")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  Failed to lock screen")
    return False

def get_password_from_keychain():
    """Retrieve password from macOS keychain"""
    try:
        result = subprocess.run([
            "security",
            "find-generic-password",
            "-w",  # Write password to stdout
            "-a", getpass.getuser(),  # Account (username)
            "-s", KEYCHAIN_ITEM  # Service name
        ], check=True, capture_output=True, timeout=2)
        password = result.stdout.decode('utf-8').strip()
        return password
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None

def unlock_mac_screen():
    """Wake and unlock the Mac screen when device comes near"""
    print("🔓 Attempting to unlock screen...")
    
    # Wake the display
    try:
        subprocess.run([
            "caffeinate",
            "-u",
            "-t",
            "1"
        ], check=True, capture_output=True, timeout=2)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Wait a moment for lock screen to appear
    time.sleep(0.5)
    
    # Get password from keychain
    password = get_password_from_keychain()
    if not password:
        print("⚠️  Password not found in keychain. Run: python setup_password.py")
        return
    
    # Type password directly as a single string
    try:
        # Escape special characters for AppleScript
        escaped_password = password.replace('\\', '\\\\').replace('"', '\\"')
        
        # Type entire password at once, then press Enter
        script = f'''
        tell application "System Events"
            keystroke "{escaped_password}"
            delay 0.1
            key code 36
        end tell
        '''
        
        subprocess.run([
            "osascript",
            "-e",
            script
        ], check=True, capture_output=True, timeout=2)
        
        print("✅ Unlock command executed")
        return
    except subprocess.CalledProcessError as e:
        error_msg = str(e.stderr, 'utf-8', errors='ignore') if e.stderr else str(e)
        if "not allowed" in error_msg:
            print("⚠️  Need Accessibility permissions for auto-unlock")
            print("   Grant Terminal access in: System Settings → Privacy & Security → Accessibility")
        else:
            print(f"⚠️  Unlock failed: {error_msg}")
            if e.stdout:
                print(f"   stdout: {str(e.stdout, 'utf-8', errors='ignore')}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"⚠️  Unlock error: {e}")

