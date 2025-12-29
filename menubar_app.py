import rumps
import asyncio
import threading
import time
import subprocess
import getpass
from bleak import BleakScanner
from config import get_config, KEYCHAIN_ITEM
from main import start_monitoring, stop_monitoring, is_monitoring
from native_dialogs import show_alert, show_text_input_dialog, show_confirm_dialog, show_password_dialog
from sleep_watcher import setup_sleep_watcher

class ProxiLockMenuBar(rumps.App):
    def __init__(self):
        super().__init__("Proxi-Lock")

        self.devices = {}
        self.lock = threading.Lock()
        self.config = get_config()
        
        setup_sleep_watcher()
        rumps.events.before_quit.register(self._on_quit)

        self.devices_menu = rumps.MenuItem("Devices")
        self.devices_menu.add("Scanning…")

        self.rssi_near_menu = rumps.MenuItem("Unlocking threshold (near)")
        self._build_rssi_menu(self.rssi_near_menu, "near")

        self.rssi_far_menu = rumps.MenuItem("Locking threshold (far)")
        self._build_rssi_menu(self.rssi_far_menu, "far")

        self.max_unlocking_rssi_menu = rumps.MenuItem("Max unlocking RSSI")
        self._build_max_unlocking_rssi_menu()

        self.consecutive_far_menu = rumps.MenuItem("Consecutive FAR required")
        self._build_consecutive_far_menu()

        self.screen_saver_lock_item = rumps.MenuItem("Use Screen Saver Lock", callback=self.toggle_screen_saver_lock)
        self.lock_only_mode_item = rumps.MenuItem("Lock Only Mode", callback=self.toggle_lock_only_mode)
        self.set_password_item = rumps.MenuItem("Set Password", callback=self.set_password)
        self.monitoring_item = rumps.MenuItem("Start Monitoring", callback=self.toggle_monitoring)

        self.menu = [
            self.devices_menu,
            rumps.separator,
            self.monitoring_item,
            rumps.separator,
            self.rssi_near_menu,
            self.rssi_far_menu,
            self.max_unlocking_rssi_menu,
            self.consecutive_far_menu,
            self.screen_saver_lock_item,
            self.lock_only_mode_item,
            self.set_password_item,
            rumps.separator
        ]

        threading.Thread(target=self._ble_thread, daemon=True).start()

        self.timer = rumps.Timer(self.update_menu, 1)
        self.timer.start()
        self.settings_timer = rumps.Timer(self.update_threshold_menus, 2)
        self.settings_timer.start()
        self.password_check_timer = rumps.Timer(self._check_password_setup_once, 0.5)
        self.password_check_timer.start()

    def _ble_thread(self):
        asyncio.run(self.scan_loop())

    async def scan_loop(self):
        def on_detect(device, adv):
            with self.lock:
                self.devices[device.address] = {
                    "address": device.address,
                    "name": device.name or device.address,
                    "rssi": adv.rssi,
                    "last_seen": time.time()
                }

        scanner = BleakScanner(on_detect)
        await scanner.start()

        while True:
            await asyncio.sleep(1)

    def update_menu(self, _):
        self.devices_menu.clear()

        now = time.time()
        with self.lock:
            devices = [
                d for d in self.devices.values()
                if now - d["last_seen"] < 5
            ]

        if not devices:
            self.devices_menu.add("Scanning…")
            return

        for d in sorted(devices, key=lambda x: x["rssi"], reverse=True):
            label = f'{d["name"]} ({d["rssi"]} dBm)'
            if d["name"] == self.config.target_name:
                label = "✓ " + label

            item = rumps.MenuItem(label, callback=self.on_device_clicked)
            item.device_address = d["address"]
            self.devices_menu.add(item)

    def on_device_clicked(self, sender):
        addr = getattr(sender, "device_address", None)
        if not addr:
            return

        with self.lock:
            d = self.devices.get(addr)

        if d:
            self.config.target_name = d['name']
            rumps.notification(
                "Proxi-Lock",
                "Device Selected",
                f"Now monitoring: {d['name']}"
            )

    def _build_rssi_menu(self, parent_menu, threshold_type):
        if parent_menu._menu is not None:
            parent_menu.clear()
        rssi_values = [-20, -30, -40, -50, -60, -70, -80, -90, -100]
        
        parent_menu.add(rumps.MenuItem("Closest", callback=None))
        parent_menu.add(rumps.separator)
        
        for value in rssi_values:
            current_value = self.config.rssi_near if threshold_type == "near" else self.config.rssi_far
            label = f"{value} dBm"
            if value == current_value:
                label = "✓ " + label
            
            menu_item = rumps.MenuItem(
                label,
                callback=lambda sender, v=value, t=threshold_type: self._set_rssi_threshold(t, v)
            )
            parent_menu.add(menu_item)
        
        parent_menu.add(rumps.separator)
        parent_menu.add(rumps.MenuItem("Farthest", callback=None))
    
    def _build_max_unlocking_rssi_menu(self):
        if self.max_unlocking_rssi_menu._menu is not None:
            self.max_unlocking_rssi_menu.clear()
        
        rssi_near = self.config.rssi_near
        rssi_far = self.config.rssi_far
        
        if rssi_near <= rssi_far:
            self.max_unlocking_rssi_menu.add("Invalid thresholds")
            return
        
        values = []
        current = rssi_far
        while current <= rssi_near:
            values.append(current)
            current += 5
        
        if rssi_near not in values:
            values.append(rssi_near)
        
        values = sorted(set(values), reverse=True)
        
        for value in values:
            current_value = self.config.max_unlocking_rssi
            label = f"{value} dBm"
            if value == current_value:
                label = "✓ " + label
            
            menu_item = rumps.MenuItem(
                label,
                callback=lambda sender, v=value: self._set_max_unlocking_rssi(v)
            )
            self.max_unlocking_rssi_menu.add(menu_item)
    
    def _build_consecutive_far_menu(self):
        if self.consecutive_far_menu._menu is not None:
            self.consecutive_far_menu.clear()
        
        values = [3, 4, 5, 6, 7, 8, 9, 10]
        
        for value in values:
            current_value = self.config.consecutive_far_required
            label = f"{value}"
            if value == current_value:
                label = "✓ " + label
            
            menu_item = rumps.MenuItem(
                label,
                callback=lambda sender, v=value: self._set_consecutive_far_required(v)
            )
            self.consecutive_far_menu.add(menu_item)
    
    def _set_consecutive_far_required(self, value):
        self.config.consecutive_far_required = value
        rumps.notification(
            "Proxi-Lock",
            "Consecutive FAR Updated",
            f"Set to {value} consecutive readings"
        )
        self._build_consecutive_far_menu()
    
    def _set_rssi_threshold(self, threshold_type, value):
        if threshold_type == "near":
            self.config.rssi_near = value
            rumps.notification(
                "Proxi-Lock",
                "Unlocking Threshold Updated",
                f"Set to {value} dBm (closer = unlock)"
            )
            self._build_rssi_menu(self.rssi_near_menu, "near")
            self._build_max_unlocking_rssi_menu()
        elif threshold_type == "far":
            self.config.rssi_far = value
            rumps.notification(
                "Proxi-Lock",
                "Locking Threshold Updated",
                f"Set to {value} dBm (farther = lock)"
            )
            self._build_rssi_menu(self.rssi_far_menu, "far")
            self._build_max_unlocking_rssi_menu()
    
    def _set_max_unlocking_rssi(self, value):
        self.config.max_unlocking_rssi = value
        rumps.notification(
            "Proxi-Lock",
            "Max Unlocking RSSI Updated",
            f"Set to {value} dBm (between {self.config.rssi_far} and {self.config.rssi_near})"
        )
        self._build_max_unlocking_rssi_menu()
    
    def update_threshold_menus(self, _):
        self.rssi_near_menu.title = f"Unlocking threshold (near): {self.config.rssi_near} dBm"
        self.rssi_far_menu.title = f"Locking threshold (far): {self.config.rssi_far} dBm"
        self.max_unlocking_rssi_menu.title = f"Max unlocking RSSI: {self.config.max_unlocking_rssi} dBm"
        self.consecutive_far_menu.title = f"Consecutive FAR required: {self.config.consecutive_far_required}"
        
        if self.config.use_screen_saver_lock:
            self.screen_saver_lock_item.title = "✓ Use Screen Saver Lock"
        else:
            self.screen_saver_lock_item.title = "Use Screen Saver Lock"
        
        if self.config.lock_only_mode:
            self.lock_only_mode_item.title = "✓ Lock Only Mode"
        else:
            self.lock_only_mode_item.title = "Lock Only Mode"
        
        if is_monitoring():
            self.monitoring_item.title = "Stop Monitoring"
        else:
            self.monitoring_item.title = "Start Monitoring"
    
    def toggle_screen_saver_lock(self, sender):
        self.config.use_screen_saver_lock = not self.config.use_screen_saver_lock
        status = "enabled" if self.config.use_screen_saver_lock else "disabled"
        rumps.notification(
            "Proxi-Lock",
            "Screen Saver Lock",
            f"Screen saver lock {status}"
        )
    
    def toggle_lock_only_mode(self, sender):
        self.config.lock_only_mode = not self.config.lock_only_mode
        status = "enabled" if self.config.lock_only_mode else "disabled"
        rumps.notification(
            "Proxi-Lock",
            "Lock Only Mode",
            f"Lock-only mode {status} (will lock but never unlock)"
        )
    
    def _check_password_setup_once(self, _):
        if hasattr(self, 'password_check_timer'):
            self.password_check_timer.stop()
        
        try:
            from lock_manager import get_password_from_keychain
            
            password = get_password_from_keychain()
            if password is None:
                show_alert(
                    "Welcome to Proxi-Lock",
                    "Please set your Mac password to enable auto-unlock functionality."
                )
                self.set_password(None)
        except Exception as e:
            pass
    
    def set_password(self, sender):
        password = show_password_dialog(
            title="Set Password",
            message="Enter your Mac password to enable auto-unlock:"
        )
        
        if password is None:
            return
        
        if not password:
            show_alert(
                "Invalid Password",
                "Password cannot be empty."
            )
            return
        
        password_confirm = show_password_dialog(
            title="Confirm Password",
            message="Confirm your Mac password:"
        )
        
        if password_confirm is None:
            return
        
        if password != password_confirm:
            show_alert(
                "Password Mismatch",
                "Passwords don't match. Please try again."
            )
            return
        
        try:
            try:
                subprocess.run([
                    "security",
                    "find-generic-password",
                    "-a", getpass.getuser(),
                    "-s", KEYCHAIN_ITEM
                ], check=True, capture_output=True)
                subprocess.run([
                    "security",
                    "add-generic-password",
                    "-a", getpass.getuser(),
                    "-s", KEYCHAIN_ITEM,
                    "-w", password,
                    "-U"
                ], check=True, capture_output=True)
                rumps.notification(
                    "Proxi-Lock",
                    "Password Updated",
                    "Your password has been updated in the keychain."
                )
            except subprocess.CalledProcessError:
                subprocess.run([
                    "security",
                    "add-generic-password",
                    "-a", getpass.getuser(),
                    "-s", KEYCHAIN_ITEM,
                    "-w", password
                ], check=True, capture_output=True)
                rumps.notification(
                    "Proxi-Lock",
                    "Password Set",
                    "Your password has been stored securely in the keychain."
                )
        except subprocess.CalledProcessError as e:
            show_alert(
                "Error",
                f"Failed to store password in keychain: {e}"
            )

    def toggle_monitoring(self, sender):
        if is_monitoring():
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        if not self.config.target_name:
            show_alert(
                "No Device Selected",
                "Please select a device from the Devices menu first."
            )
            return
        
        start_monitoring()
        self.monitoring_item.title = "Stop Monitoring"
        rumps.notification(
            "Proxi-Lock",
            "Monitoring Started",
            f"Monitoring device: {self.config.target_name}"
        )

    def stop_monitoring(self):
        stop_monitoring()
        self.monitoring_item.title = "Start Monitoring"
        rumps.notification(
            "Proxi-Lock",
            "Monitoring Stopped",
            "Proximity detection has been stopped"
        )

    def _on_quit(self, _):
        if is_monitoring():
            stop_monitoring()

if __name__ == "__main__":
    ProxiLockMenuBar().run()
