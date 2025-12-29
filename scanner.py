"""BLE scanning / proximity detection"""
from bleak import BleakScanner
from config import get_config
from controller import ProximityController

class ProximityScanner:
    def __init__(self, proximity_callback):
        self.config = get_config()
        self.controller = ProximityController(
            self.config.rssi_near, 
            self.config.rssi_far, 
            max_unlocking_rssi=self.config.max_unlocking_rssi
        )
        self.proximity_callback = proximity_callback
        self.last_proximity = None
        self.consecutive_far_count = 0

    def _detection_callback(self, device, advertisement_data):
        target_name = self.config.target_name
        if not target_name:
            return
        
        device_name = device.name or ""
        if device_name != target_name:
            return

        rssi = advertisement_data.rssi
        proximity = self.controller.get_proximity(rssi)
        
        if proximity == "FAR":
            self.consecutive_far_count += 1
        elif proximity == "NEAR":
            if self.consecutive_far_count > 0:
                print(f"NEAR detected | Reset FAR counter (was {self.consecutive_far_count})")
            self.consecutive_far_count = 0
        
        self.proximity_callback(
            proximity=proximity,
            rssi=rssi,
            consecutive_far_count=self.consecutive_far_count
        )
        
        self.last_proximity = proximity
    
    async def start(self):
        target_name = self.config.target_name
        if not target_name:
            return
        self.scanner = BleakScanner(self._detection_callback)
        await self.scanner.start()
    
    async def stop(self):
        await self.scanner.stop()
    
    def get_consecutive_far_count(self):
        return self.consecutive_far_count
    
    def reset_consecutive_far_count(self):
        self.consecutive_far_count = 0

