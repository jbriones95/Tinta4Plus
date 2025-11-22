"""
Copyright (c) 2025 Jon Cox (joncox123). All rights reserved.

WARNING: This software is provided "AS IS", without any warranty of any kind. It may contain bugs or other defects
that result in data loss, corruption, hardware damage or other issues. Use at your own risk.
It may temporarily or permanently render your hardware inoperable.
It may corrupt or damage the Embedded Controller or eInk T-CON controller in your laptop.
The author is not responsible for any damage, data loss or lost productivity caused by use of this software. 
By downloading and using this software you agree to these terms and acknowledge the risks involved.
"""

import subprocess


class DisplayManager:
    """Manage display switching and configuration (no root required)"""
    def __init__(self, logger):
        self.logger = logger
    
    def get_displays(self):
        """Get list of connected displays using xrandr"""
        try:
            result = subprocess.run(
                ['xrandr', '--query'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            displays = []
            for line in result.stdout.split('\n'):
                if ' connected' in line:
                    parts = line.split()
                    name = parts[0]
                    primary = 'primary' in line
                    displays.append({'name': name, 'primary': primary})
            
            return displays
            
        except Exception as e:
            self.logger.error(f"Failed to get displays: {e}")
            return []
    
    def set_primary(self, display_name):
        """Set primary display"""
        try:
            subprocess.run(
                ['xrandr', '--output', display_name, '--primary'],
                check=True,
                timeout=5
            )
            self.logger.info(f"Set {display_name} as primary display")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set primary display: {e}")
            return False
    
    def enable_display(self, display_name):
        """Enable/turn on a display"""
        try:
            subprocess.run(
                ['xrandr', '--output', display_name, '--auto'],
                check=True,
                timeout=5
            )
            self.logger.info(f"Enabled display: {display_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable display: {e}")
            return False
    
    def disable_display(self, display_name):
        """Disable/turn off a display"""
        try:
            subprocess.run(
                ['xrandr', '--output', display_name, '--off'],
                check=True,
                timeout=5
            )
            self.logger.info(f"Disabled display: {display_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable display: {e}")
            return False