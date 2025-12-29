"""Configuration management"""
import json
import os
import sys
import threading

class ProxiLockConfig:
    """Thread-safe configuration manager with auto-persistence"""
    
    _DEFAULTS = {
        "target_name": None,
        "rssi_near": -30,
        "rssi_far": -70,
        "max_unlocking_rssi": -50,
        "scan_interval": 0.2,
        "device_timeout": 3.0,
        "state_debounce_time": 1.0,
        "consecutive_far_required": 5,
        "keychain_item": "proxi-lock-password",
        "use_screen_saver_lock": False,
        "lock_only_mode": False
    }
    
    def __init__(self, path=None):
        if path is None:
            if getattr(sys, 'frozen', False):
                app_support = os.path.join(
                    os.path.expanduser("~"),
                    "Library",
                    "Application Support",
                    "Proxi-Lock"
                )
                os.makedirs(app_support, exist_ok=True)
                self.path = os.path.join(app_support, ".proxi_lock_config.json")
            else:
                config_dir = os.path.dirname(os.path.abspath(__file__))
                self.path = os.path.join(config_dir, ".proxi_lock_config.json")
        else:
            self.path = os.path.expanduser(path)
        
        self._lock = threading.Lock()
        self._data = {}
        self._load()
    
    def _load(self):
        if not os.path.exists(self.path):
            self._data = self._DEFAULTS.copy()
            self._save()
            return
        
        try:
            with open(self.path, "r") as f:
                loaded = json.load(f)
                self._data = {**self._DEFAULTS, **loaded}
                self._validate_max_unlocking_rssi()
        except (json.JSONDecodeError, IOError) as e:
            self._data = self._DEFAULTS.copy()
            self._save()
    
    def _validate_max_unlocking_rssi(self):
        rssi_near = self._data.get("rssi_near", self._DEFAULTS["rssi_near"])
        rssi_far = self._data.get("rssi_far", self._DEFAULTS["rssi_far"])
        max_unlocking = self._data.get("max_unlocking_rssi", self._DEFAULTS["max_unlocking_rssi"])
        
        if rssi_near <= rssi_far:
            self._data["rssi_near"] = self._DEFAULTS["rssi_near"]
            self._data["rssi_far"] = self._DEFAULTS["rssi_far"]
            rssi_near = self._DEFAULTS["rssi_near"]
            rssi_far = self._DEFAULTS["rssi_far"]
        
        if max_unlocking < rssi_far:
            self._data["max_unlocking_rssi"] = rssi_far
        elif max_unlocking > rssi_near:
            self._data["max_unlocking_rssi"] = rssi_near
    
    def _save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError as e:
            pass
    
    @property
    def target_name(self):
        with self._lock:
            return self._data["target_name"]
    
    @target_name.setter
    def target_name(self, value):
        with self._lock:
            self._data["target_name"] = value
            self._save()
    
    @property
    def rssi_near(self):
        return self._data["rssi_near"]
    
    @rssi_near.setter
    def rssi_near(self, value):
        self._data["rssi_near"] = value
        self._validate_max_unlocking_rssi()
        self._save()
    
    @property
    def rssi_far(self):
        return self._data["rssi_far"]
    
    @rssi_far.setter
    def rssi_far(self, value):
        self._data["rssi_far"] = value
        self._validate_max_unlocking_rssi()
        self._save()
    
    @property
    def max_unlocking_rssi(self):
        return self._data["max_unlocking_rssi"]
    
    @max_unlocking_rssi.setter
    def max_unlocking_rssi(self, value):
        rssi_near = self._data["rssi_near"]
        rssi_far = self._data["rssi_far"]
        
        if rssi_near <= rssi_far:
            value = self._DEFAULTS["max_unlocking_rssi"]
        else:
            if value < rssi_far:
                value = rssi_far
            elif value > rssi_near:
                value = rssi_near
        
        self._data["max_unlocking_rssi"] = value
        self._save()
    
    @property
    def scan_interval(self):
        return self._data["scan_interval"]
    
    @scan_interval.setter
    def scan_interval(self, value):
        self._data["scan_interval"] = value
        self._save()
    
    @property
    def device_timeout(self):
        return self._data["device_timeout"]
    
    @device_timeout.setter
    def device_timeout(self, value):
        self._data["device_timeout"] = value
        self._save()
    
    @property
    def state_debounce_time(self):
        return self._data["state_debounce_time"]
    
    @state_debounce_time.setter
    def state_debounce_time(self, value):
        self._data["state_debounce_time"] = value
        self._save()
    
    @property
    def consecutive_far_required(self):
        return self._data["consecutive_far_required"]
    
    @consecutive_far_required.setter
    def consecutive_far_required(self, value):
        self._data["consecutive_far_required"] = value
        self._save()
    
    @property
    def keychain_item(self):
        return self._data["keychain_item"]
    
    @keychain_item.setter
    def keychain_item(self, value):
        self._data["keychain_item"] = value
        self._save()
    
    @property
    def use_screen_saver_lock(self):
        return self._data["use_screen_saver_lock"]
    
    @use_screen_saver_lock.setter
    def use_screen_saver_lock(self, value):
        self._data["use_screen_saver_lock"] = value
        self._save()
    
    @property
    def lock_only_mode(self):
        return self._data["lock_only_mode"]
    
    @lock_only_mode.setter
    def lock_only_mode(self, value):
        self._data["lock_only_mode"] = value
        self._save()
    
    @property
    def unlocking_rssi_max(self):
        return self.max_unlocking_rssi


_config = ProxiLockConfig()

TARGET_NAME = _config.target_name
RSSI_NEAR = _config.rssi_near
RSSI_FAR = _config.rssi_far
SCAN_INTERVAL = _config.scan_interval
DEVICE_TIMEOUT = _config.device_timeout
STATE_DEBOUNCE_TIME = _config.state_debounce_time
CONSECUTIVE_FAR_REQUIRED = _config.consecutive_far_required
KEYCHAIN_ITEM = _config.keychain_item
UNLOCKING_RSSI_MAX = _config.unlocking_rssi_max

def get_config():
    return _config

def reload_config():
    global TARGET_NAME, RSSI_NEAR, RSSI_FAR, SCAN_INTERVAL, DEVICE_TIMEOUT
    global STATE_DEBOUNCE_TIME, CONSECUTIVE_FAR_REQUIRED, KEYCHAIN_ITEM, UNLOCKING_RSSI_MAX
    
    _config._load()
    TARGET_NAME = _config.target_name
    RSSI_NEAR = _config.rssi_near
    RSSI_FAR = _config.rssi_far
    SCAN_INTERVAL = _config.scan_interval
    DEVICE_TIMEOUT = _config.device_timeout
    STATE_DEBOUNCE_TIME = _config.state_debounce_time
    CONSECUTIVE_FAR_REQUIRED = _config.consecutive_far_required
    KEYCHAIN_ITEM = _config.keychain_item
    UNLOCKING_RSSI_MAX = _config.unlocking_rssi_max
