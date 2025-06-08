import threading
import time

class RateLimiter:
    """
    Simple thread-safe rate limiter using the token bucket algorithm.
    rate_limit_config example: { 'rate': 5, 'per': 1 }  # 5 requests per 1 second
    """
    def __init__(self, config=None):
        config = config or {}
        self.rate = config.get('rate', 10)  # default: 10 requests
        self.per = config.get('per', 1)     # default: per 1 second
        self.allowance = self.rate
        self.last_check = time.monotonic()
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            current = time.monotonic()
            time_passed = current - self.last_check
            self.last_check = current
            self.allowance += time_passed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate
            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                time.sleep(sleep_time)
                self.allowance = 0
            else:
                self.allowance -= 1.0
