class ProximityController:
    def __init__(self, rssi_near, rssi_far, max_unlocking_rssi):
        self.rssi_near = rssi_near
        self.rssi_far = rssi_far
        self.max_unlocking_rssi = max_unlocking_rssi

    def get_proximity(self, rssi):
        UNLOCKING_RSSI_MAX = self.max_unlocking_rssi
        """State machine: Return 'NEAR' or 'FAR' based on RSSI thresholds"""
        if rssi is None:
            return "FAR"
        elif rssi <= self.rssi_far:
            return "FAR"
        elif UNLOCKING_RSSI_MAX > rssi >= self.rssi_far:
            return "MID"
        
        elif UNLOCKING_RSSI_MAX < rssi < self.rssi_near:
            return "NEAR"
        elif rssi >= self.rssi_near:
            return "NEAR"
        else:
            return "NEAR"
