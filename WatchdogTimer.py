"""
Copyright (c) 2025 Jon Cox (joncox123). All rights reserved.

WARNING: This software is provided "AS IS", without any warranty of any kind. It may contain bugs or other defects
that result in data loss, corruption, hardware damage or other issues. Use at your own risk.
It may temporarily or permanently render your hardware inoperable.
It may corrupt or damage the Embedded Controller or eInk T-CON controller in your laptop.
The author is not responsible for any damage, data loss or lost productivity caused by use of this software. 
By downloading and using this software you agree to these terms and acknowledge the risks involved.
"""

import threading

class WatchdogTimer:
    """Watchdog timer that triggers shutdown if not reset"""
    
    def __init__(self, timeout, callback, logger):
        self.timeout = timeout
        self.callback = callback
        self.logger = logger
        self.timer = None
        self.lock = threading.Lock()
        self.reset()
    
    def reset(self):
        """Reset the watchdog timer"""
        with self.lock:
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.timeout, self._expired)
            self.timer.daemon = True
            self.timer.start()
    
    def _expired(self):
        """Called when timer expires"""
        self.logger.warning(f"Watchdog timer expired ({self.timeout}s), shutting down")
        self.callback()
    
    def cancel(self):
        """Cancel the watchdog timer"""
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None