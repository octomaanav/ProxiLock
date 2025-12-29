"""Security / lock intent tracking (script vs manual lock)"""
import time
from enum import Enum
from lock_manager import is_screen_locked
from sleep_watcher import get_time_since_wake

class LockOwner(Enum):
    SCRIPT = "script"
    USER = "user"
    NONE = "none"

lock_owner = LockOwner.NONE
script_lock_time = 0
last_unlocked_time = 0
WAKE_GRACE_PERIOD = 10.0
last_lock_state = None

def mark_script_lock():
    global lock_owner, script_lock_time
    
    lock_owner = LockOwner.SCRIPT
    script_lock_time = time.time()

def update_lock_state():
    global lock_owner, last_unlocked_time, last_lock_state

    locked = is_screen_locked()
    now = time.time()
    time_since_wake = get_time_since_wake()

    if last_lock_state is None:
        last_lock_state = locked
        return

    if last_lock_state is True and locked is False:
        last_unlocked_time = now
        lock_owner = LockOwner.NONE

    elif last_lock_state is False and locked is True:
        if time_since_wake < WAKE_GRACE_PERIOD:
            if lock_owner != LockOwner.SCRIPT:
                pass
        elif lock_owner != LockOwner.SCRIPT:
            lock_owner = LockOwner.USER

    last_lock_state = locked


def get_lock_owner():
    return lock_owner

def reset_lock_owner():
    global lock_owner, last_unlocked_time
    lock_owner = LockOwner.NONE
    last_unlocked_time = time.time()

