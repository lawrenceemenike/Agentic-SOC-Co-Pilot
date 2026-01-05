import numpy as np
from typing import List

class AnomalyDetector:
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.history: List[float] = []

    def is_anomaly(self, value: float) -> bool:
        """
        Checks if the value is an anomaly using Z-Score.
        """
        self.history.append(value)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        if len(self.history) < 10:
            return False # Not enough data
            
        mean = np.mean(self.history)
        std = np.std(self.history)
        
        if std == 0:
            return False
            
        z_score = (value - mean) / std
        
        # Threshold of 3 std devs
        if abs(z_score) > 3:
            return True
            
        return False
