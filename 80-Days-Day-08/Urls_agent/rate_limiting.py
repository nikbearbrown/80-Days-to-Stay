import threading
import time 
from config import RPM_LIMIT

class RateLimiter:
    def __init__(self) -> None:
        self.max_per_minute = RPM_LIMIT
        self.calls = []
        self.lock = threading.Lock()

    def wait(self):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < 60]

        if len(self.calls) >= self.max_per_minute:
            oldest_call = self.calls[0]
            time_since_oldest_call = now - oldest_call
            wait_time = 60 - time_since_oldest_call + 0.1
            time.sleep(wait_time)

        self.calls.append(now)