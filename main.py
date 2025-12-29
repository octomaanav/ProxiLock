"""Main entry point - orchestrates BLE scanning, proximity detection, and lock management"""
import asyncio
import threading
from datetime import datetime
from config import CONSECUTIVE_FAR_REQUIRED, SCAN_INTERVAL, get_config
from scanner import ProximityScanner
from lock_manager import lock_mac_screen, unlock_mac_screen, is_screen_locked
from lock_security import (
    LockOwner, 
    mark_script_lock, 
    update_lock_state, 
    get_lock_owner, 
    reset_lock_owner
)
from sleep_watcher import setup_sleep_watcher, set_wake_callback, get_time_since_wake

def proximity_callback(proximity, rssi, consecutive_far_count):
    global last_proximity
    
    if proximity == "FAR":
        print(f"FAR | RSSI: {rssi} | Consecutive: {consecutive_far_count}/{CONSECUTIVE_FAR_REQUIRED}")
        
        if consecutive_far_count >= CONSECUTIVE_FAR_REQUIRED:
            if not is_screen_locked():
                if consecutive_far_count == CONSECUTIVE_FAR_REQUIRED:
                    print(f"Attempting to lock screen (threshold reached: {consecutive_far_count}/{CONSECUTIVE_FAR_REQUIRED})")
                    if lock_mac_screen():
                        mark_script_lock()
                        if _monitor_instance.scanner_instance:
                            _monitor_instance.scanner_instance.reset_consecutive_far_count()
                    else:
                        print("Lock attempt failed")
                elif consecutive_far_count > CONSECUTIVE_FAR_REQUIRED:
                    print(f"Threshold exceeded but screen not locked (count: {consecutive_far_count}, screen locked: {is_screen_locked()})")
            else:
                if _monitor_instance.scanner_instance:
                    _monitor_instance.scanner_instance.reset_consecutive_far_count()
    elif proximity == "MID":
        print(f"MID | RSSI: {rssi} | Counter reset to 0")
        if _monitor_instance.scanner_instance:
            _monitor_instance.scanner_instance.reset_consecutive_far_count()
        
    else:
        if proximity == "NEAR":
            print(f"NEAR | RSSI: {rssi} | Counter reset to 0")
            
            config = get_config()
            if config.lock_only_mode:
                print("Lock-only mode enabled — skipping unlock")
        return
        if last_proximity != "NEAR":
            lock_owner = get_lock_owner()
            if lock_owner == LockOwner.SCRIPT:
                print(f"Unlocking (script-owned lock)")
                unlock_mac_screen()
                reset_lock_owner()
            elif lock_owner == LockOwner.USER:
                print("Locked by user — unlock blocked")
            else:
                print("Screen already unlocked (skipping unlock)")
    
    last_proximity = proximity

last_proximity = None

class ProximityMonitor:
    def __init__(self):
        self.scanner_instance = None
        self.monitoring = False
        self.loop = None
        self._wake_event = None
    
    async def _restart_scanner(self):
        if self.scanner_instance:
            try:
                await self.scanner_instance.stop()
            except Exception as e:
                print(f"Error stopping scanner: {e}")
            self.scanner_instance = None
        
        await asyncio.sleep(1.0)
        
        print("Restarting BLE scanner after wake...")
        self.scanner_instance = ProximityScanner(proximity_callback)
        await self.scanner_instance.start()
        print("BLE scanner restarted")
    
    def _on_wake(self):
        print("Handling system wake - restarting BLE scan")
        if self.loop and self.monitoring:
            asyncio.run_coroutine_threadsafe(self._restart_scanner(), self.loop)
    
    async def _monitor_loop(self):
        global last_proximity
        
        update_lock_state()
        
        self.scanner_instance = ProximityScanner(proximity_callback)
        await self.scanner_instance.start()
        
        try:
            while self.monitoring:
                update_lock_state()
                
                time_since_wake = get_time_since_wake()
                if time_since_wake < 2.0:
                    if self.scanner_instance:
                        self.scanner_instance.reset_consecutive_far_count()
                
                await asyncio.sleep(SCAN_INTERVAL)
        finally:
            if self.scanner_instance:
                try:
                    await self.scanner_instance.stop()
                except Exception as e:
                    print(f"Error stopping scanner: {e}")
                self.scanner_instance = None
    
    def start(self):
        if self.monitoring:
            return

        self.monitoring = True
        
        def run_monitor():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self._monitor_loop())
            except Exception as e:
                print(f"Monitoring error: {e}")
            finally:
                self.monitoring = False
                self.loop = None
        
        thread = threading.Thread(target=run_monitor, daemon=True)
        thread.start()
    
    def stop(self):
        self.monitoring = False
    
    def is_running(self):
        return self.monitoring

_monitor_instance = ProximityMonitor()

def start_monitoring():
    setup_sleep_watcher()
    set_wake_callback(_monitor_instance._on_wake)
    _monitor_instance.start()

def stop_monitoring():
    _monitor_instance.stop()

def is_monitoring():
    return _monitor_instance.is_running()


async def monitor():
    update_lock_state()
    
    scanner = ProximityScanner(proximity_callback)
    await scanner.start()

    try:
        while True:
            update_lock_state()
            await asyncio.sleep(SCAN_INTERVAL)
    finally:
        await scanner.stop()

if __name__ == "__main__":
    asyncio.run(monitor())
