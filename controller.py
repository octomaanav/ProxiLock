class ProximityController:
    def __init__(self, unlock_rssi, lock_rssi):
        self.unlock_rssi = unlock_rssi  # RSSI >= this = NEAR (unlock threshold)
        self.lock_rssi = lock_rssi      # RSSI <= this = FAR (lock threshold)
        # Dead zone: lock_rssi < RSSI < unlock_rssi = MID (no action)

    def get_proximity(self, rssi):
        """State machine: Return 'NEAR', 'FAR', or 'MID' based on strict RSSI thresholds"""
        if rssi is None:
            return "FAR"
        elif rssi >= self.unlock_rssi:
            return "NEAR"  # Truly near - unlock allowed
        elif rssi <= self.lock_rssi:
            return "FAR"   # Truly far - lock allowed
        else:
            return "MID"   # Dead zone - no action
    
    def get_midpoint(self):
        """Get the midpoint between UNLOCK_RSSI and LOCK_RSSI (for display only)"""
        return (self.unlock_rssi + self.lock_rssi) / 2
