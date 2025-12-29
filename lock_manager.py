"""Screen lock/unlock system interactions"""
import subprocess
import getpass
import time
from config import KEYCHAIN_ITEM, get_config

def is_screen_locked():
    try:
        result = subprocess.run(
            '/usr/libexec/PlistBuddy -c "print :IOConsoleUsers:0:CGSSessionScreenIsLocked" /dev/stdin <<< "$(ioreg -n Root -d1 -a)"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            return result.stdout.strip().lower() == "true"
        
        if "Does Not Exist" in result.stderr:
            return False
        
        return False

    except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def lock_mac_screen():
    config = get_config()
    
    if config.use_screen_saver_lock:
        try:
            subprocess.run([
                "osascript",
                "-e",
                'tell application "ScreenSaverEngine" to activate'
            ], check=True, capture_output=True, timeout=1)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    try:
        result = subprocess.run([
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "q" using {command down, control down}'
        ], check=True, capture_output=True, timeout=2)
        return True
    except subprocess.CalledProcessError as e:
        if "not allowed" in str(e.stderr, 'utf-8', errors='ignore'):
            pass
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    if not config.use_screen_saver_lock:
        try:
            subprocess.run([
                "osascript",
                "-e",
                'tell application "ScreenSaverEngine" to activate'
            ], check=True, capture_output=True, timeout=1)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    return False

def get_password_from_keychain():
    try:
        result = subprocess.run([
            "security",
            "find-generic-password",
            "-w",
            "-a", getpass.getuser(),
            "-s", KEYCHAIN_ITEM
        ], check=True, capture_output=True, timeout=2)
        password = result.stdout.decode('utf-8').strip()
        return password
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None

def is_lock_screen_active():
    try:
        if not is_screen_locked():
            return False
        
        script = '''
        tell application "System Events"
            try
                set frontApp to name of first application process whose frontmost is true
                
                if frontApp is "loginwindow" or frontApp is "ScreenSaverEngine" then
                    return true
                end if
                
                if frontApp is not "WindowServer" then
                    return false
                end if
                
                return true
            on error
                return false
            end try
        end tell
        '''
        
        result = subprocess.run([
            "osascript",
            "-e",
            script
        ], check=True, capture_output=True, timeout=2, text=True)
        
        return "true" in result.stdout.strip().lower()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return is_screen_locked()

def wake_display():
    try:
        subprocess.run([
            "caffeinate",
            "-u",
            "-t",
            "2"
        ], check=True, capture_output=True, timeout=3)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    try:
        subprocess.run([
            "pmset",
            "wake"
        ], check=True, capture_output=True, timeout=2)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    try:
        subprocess.run([
            "osascript",
            "-e",
            'tell application "System Events" to key code 63'
        ], check=True, capture_output=True, timeout=2)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    try:
        subprocess.run([
            "osascript",
            "-e",
            'tell application "System Events" to keystroke " "'
        ], check=True, capture_output=True, timeout=2)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass

def unlock_mac_screen():
    screen_was_locked = is_screen_locked()
    
    wake_display()
    time.sleep(2.0) # maybe change to lower value (1.5?)
    
    # verify screen is locked (after waking)
    if not is_screen_locked():
        if not screen_was_locked:
            return False
        time.sleep(1.0)
        if not is_screen_locked():
            return False
    
    if not is_screen_locked():
        return False
    
    lock_screen_verified = is_lock_screen_active()
    if not lock_screen_verified:
        if not is_screen_locked():
            return False
    
    password = get_password_from_keychain()
    if not password:
        return False
    
    try:
        escaped_password = password.replace('\\', '\\\\').replace('"', '\\"')
        
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

        return True
    except subprocess.CalledProcessError as e:
        error_msg = str(e.stderr, 'utf-8', errors='ignore') if e.stderr else str(e)
        if "not allowed" in error_msg:
            pass
        else:
            if e.stdout:
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        pass

