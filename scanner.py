"""BLE scanning / proximity detection"""
from bleak import BleakScanner
from config import TARGET_NAME, UNLOCK_RSSI, LOCK_RSSI
from controller import ProximityController

class ProximityScanner:
    def __init__(self, proximity_callback):
        self.controller = ProximityController(UNLOCK_RSSI, LOCK_RSSI)
        self.proximity_callback = proximity_callback
        self.last_proximity = None
        self.consecutive_far_count = 0
        
    def _detection_callback(self, device, advertisement_data):
        """Internal callback that processes BLE detections"""
        if device.name != TARGET_NAME:
            return

        rssi = advertisement_data.rssi
        proximity = self.controller.get_proximity(rssi)
        midpoint = self.controller.get_midpoint()
        
        # State machine logic
        # Reset consecutive counter if RSSI >= UNLOCK_RSSI (truly NEAR - signal improving)
        if proximity == "NEAR":
            if self.consecutive_far_count > 0:
                print(f"RSSI: {rssi} >= UNLOCK_RSSI ({UNLOCK_RSSI}) | Reset FAR counter (was {self.consecutive_far_count})")
            self.consecutive_far_count = 0
        
        # Update internal state BEFORE calling callback
        if proximity == "FAR":
            self.consecutive_far_count += 1
        
        # Call the user's proximity callback with processed data
        self.proximity_callback(
            proximity=proximity,
            rssi=rssi,
            midpoint=midpoint,
            consecutive_far_count=self.consecutive_far_count
        )
        
        self.last_proximity = proximity
    
    async def start(self):
        """Start scanning for the target device"""
        self.scanner = BleakScanner(self._detection_callback)
        await self.scanner.start()
        print("Scanning for", TARGET_NAME)
    
    async def stop(self):
        """Stop scanning"""
        await self.scanner.stop()
    
    def get_consecutive_far_count(self):
        """Get current consecutive FAR count"""
        return self.consecutive_far_count
    
    def reset_consecutive_far_count(self):
        """Reset consecutive FAR count"""
        self.consecutive_far_count = 0

