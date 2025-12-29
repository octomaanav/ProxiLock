"""Sleep/wake event detection using NSWorkspace notifications"""
from AppKit import NSWorkspace, NSObject
from Foundation import NSLog
import time

class SleepWatcher(NSObject):
    def receiveSleepNote_(self, notification):
        NSLog("Mac is going to sleep")
        on_system_sleep()
    
    def receiveWakeNote_(self, notification):
        NSLog("Mac woke up")
        on_system_wake()

_watcher = None
_sleep_time = 0
_wake_time = 0

def on_system_sleep():
    global _sleep_time
    _sleep_time = time.time()

def on_system_wake():
    global _wake_time
    _wake_time = time.time()
    
    if _wake_callback:
        _wake_callback()

_wake_callback = None

def set_wake_callback(callback):
    global _wake_callback
    _wake_callback = callback

def get_sleep_time():
    return _sleep_time

def get_wake_time():
    return _wake_time

def get_time_since_wake():
    if _wake_time == 0:
        return float('inf')
    return time.time() - _wake_time

def setup_sleep_watcher():
    global _watcher
    
    if _watcher is not None:
        return  
    workspace = NSWorkspace.sharedWorkspace()
    center = workspace.notificationCenter()
    
    _watcher = SleepWatcher.alloc().init()
    
    center.addObserver_selector_name_object_(
        _watcher,
        "receiveSleepNote:",
        "NSWorkspaceWillSleepNotification",
        None
    )
    
    center.addObserver_selector_name_object_(
        _watcher,
        "receiveWakeNote:",
        "NSWorkspaceDidWakeNotification",
        None
    )

