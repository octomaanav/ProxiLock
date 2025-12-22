"""Security / lock intent tracking (script vs manual lock)"""
import time
from enum import Enum
from lock_manager import is_screen_locked

class LockOwner(Enum):
    SCRIPT = "script"
    USER = "user"
    NONE = "none"

# Global state
lock_owner = LockOwner.NONE
script_lock_time = 0
SCRIPT_GRACE = 2.0  # Grace window to avoid race conditions

def mark_script_lock():
    """Mark that script initiated the lock - ONLY this function may mark SCRIPT"""
    global lock_owner, script_lock_time
    
    lock_owner = LockOwner.SCRIPT
    script_lock_time = time.time()
    print("   Lock owner: SCRIPT")

def update_lock_state():
    """Detect manual lock - THIS is what detects USER locks"""
    global lock_owner, script_lock_time
    
    locked = is_screen_locked()
    
    # Grace window: if script just locked it recently, preserve SCRIPT ownership
    # even if is_screen_locked() hasn't detected it yet (race condition protection)
    if lock_owner == LockOwner.SCRIPT:
        if time.time() - script_lock_time < SCRIPT_GRACE:
            # Within grace window - keep SCRIPT ownership regardless of current lock state
            # (screen might not be detected as locked yet due to timing)
            return
    
    # If screen is locked but script didn't just lock it → USER
    if locked and lock_owner != LockOwner.SCRIPT:
        lock_owner = LockOwner.USER
    
    # If screen is unlocked → reset (but only if not in grace window)
    if not locked:
        lock_owner = LockOwner.NONE

def get_lock_owner():
    """Get current lock owner"""
    return lock_owner

def reset_lock_owner():
    """Reset lock owner (after unlock)"""
    global lock_owner
    lock_owner = LockOwner.NONE

