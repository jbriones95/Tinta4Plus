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

class WacomManager:
    """Manage Wacom/touch input (no root required)"""

    def __init__(self, logger):
        self.logger = logger
    
    def get_touch_devices(self):
        """Get all touch input devices, categorized by type"""
        try:
            result = subprocess.run(
                ['xinput', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            eink_devices = []
            oled_devices = []
            
            for line in result.stdout.split('\n'):
                lower_line = line.lower()
                
                # Look for touch-capable devices
                is_touch_device = False
                device_name_lower = ""
                
                if 'wacom' in lower_line:
                    is_touch_device = True
                    device_name_lower = lower_line
                elif 'goodix' in lower_line:
                    is_touch_device = True
                    device_name_lower = lower_line
                elif 'touchscreen' in lower_line or 'finger' in lower_line or 'touch' in lower_line:
                    is_touch_device = True
                    device_name_lower = lower_line
                
                if is_touch_device and 'id=' in line:
                    parts = line.split('id=')
                    if len(parts) >= 2:
                        device_id = parts[1].split()[0]
                        
                        # Extract device name (between ↳ and id=)
                        if '↳' in line:
                            name_part = line.split('↳')[1].split('id=')[0].strip()
                        else:
                            name_part = line.split('id=')[0].strip()
                        
                        device_info = {'name': name_part, 'id': device_id}
                        
                        # Categorize device based on name patterns
                        # E-Ink devices typically have certain patterns
                        # This is heuristic - may need adjustment based on actual device names
                        if 'goodix' in device_name_lower:
                            # Goodix is typically the E-Ink touchscreen on ThinkBook Plus
                            eink_devices.append(device_info)
                            self.logger.debug(f"Found E-Ink touch device: {name_part} (ID: {device_id})")
                        elif 'wacom' in device_name_lower:
                            # Wacom pen/touch - could be either display
                            # If it says "pen" or "stylus", it's likely OLED (the main display)
                            # If it says "finger" or "touch", we need more info
                            if 'pen' in device_name_lower or 'stylus' in device_name_lower:
                                oled_devices.append(device_info)
                                self.logger.debug(f"Found OLED pen device: {name_part} (ID: {device_id})")
                            elif 'finger' in device_name_lower or 'touch' in device_name_lower:
                                # Wacom touch/finger could be on either display
                                # Default to OLED (main display) unless we have better info
                                oled_devices.append(device_info)
                                self.logger.debug(f"Found OLED touch device: {name_part} (ID: {device_id})")
                        else:
                            # Other touch devices - default to OLED
                            oled_devices.append(device_info)
                            self.logger.debug(f"Found OLED touch device: {name_part} (ID: {device_id})")
            
            return {
                'eink': eink_devices,
                'oled': oled_devices
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get touch devices: {e}")
            return {'eink': [], 'oled': []}
    
    def set_touch_enabled(self, device_id, enabled):
        """Enable or disable touch input for a device"""
        try:
            cmd = 'enable' if enabled else 'disable'
            subprocess.run(
                ['xinput', cmd, str(device_id)],
                check=True,
                timeout=5
            )
            self.logger.info(f"{'Enabled' if enabled else 'Disabled'} touch for device {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set touch state: {e}")
            return False