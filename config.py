TARGET_NAME = "Manav"

# Strict thresholds with dead zone
UNLOCK_RSSI = -40  # Only unlock when RSSI >= -40 (truly near)
LOCK_RSSI = -70    # Lock when RSSI <= -70 (truly far)
# Dead zone: -69 to -41 (no action)

SCAN_INTERVAL = 0.2 
DEVICE_TIMEOUT = 3.0
STATE_DEBOUNCE_TIME = 1.0
CONSECUTIVE_FAR_REQUIRED = 3

KEYCHAIN_ITEM = "proxi-lock-password" 
