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
import os
import time


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
    
    def is_display_active(self, display_name):
        """Check if a display is currently active (enabled and has geometry)"""
        try:
            result = subprocess.run(
                ['xrandr', '--query'],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                if display_name in line and ' connected' in line:
                    parts = line.split()
                    # Display is active if it has geometry info (e.g., 1920x1080+0+0)
                    # Look for pattern like "1920x1080+0+0" in the line
                    for part in parts:
                        if 'x' in part and '+' in part:
                            return True
                    return False

            return False

        except Exception as e:
            self.logger.error(f"Failed to check display status: {e}")
            return False

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
            # Run xrandr command (may produce spurious BadMatch errors on stderr)
            subprocess.run(
                ['xrandr', '--output', display_name, '--auto'],
                capture_output=True,
                timeout=5
            )

            # Verify the display is actually enabled by checking its state
            # Give X11 a moment to apply the change
            time.sleep(0.2)

            if self.is_display_active(display_name):
                self.logger.info(f"Enabled display: {display_name}")
                return True
            else:
                self.logger.error(f"Failed to enable display: {display_name} (display not active after command)")
                return False

        except Exception as e:
            self.logger.error(f"Failed to enable display: {e}")
            return False
    
    def disable_display(self, display_name):
        """Disable/turn off a display"""
        try:
            # Run xrandr command (may produce spurious BadMatch errors on stderr)
            subprocess.run(
                ['xrandr', '--output', display_name, '--off'],
                capture_output=True,
                timeout=5
            )

            # Verify the display is actually disabled by checking its state
            # Give X11 a moment to apply the change
            time.sleep(0.2)

            if not self.is_display_active(display_name):
                self.logger.info(f"Disabled display: {display_name}")
                return True
            else:
                self.logger.error(f"Failed to disable display: {display_name} (display still active after command)")
                return False

        except Exception as e:
            self.logger.error(f"Failed to disable display: {e}")
            return False

    def get_display_geometry(self, display_name):
        """Get the geometry (position and size) of a display using xrandr"""
        try:
            result = subprocess.run(
                ['xrandr', '--query'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse xrandr output to find the display geometry
            # Format: "eDP-2 connected 1200x1920+1920+0 ..."
            for line in result.stdout.split('\n'):
                if display_name in line and 'connected' in line:
                    # Look for the geometry pattern: WIDTHxHEIGHT+X+Y
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and '+' in part:
                            # Parse geometry: 1200x1920+1920+0
                            geo = part.split('+')
                            size = geo[0].split('x')
                            width = int(size[0])
                            height = int(size[1])
                            x_offset = int(geo[1]) if len(geo) > 1 else 0
                            y_offset = int(geo[2]) if len(geo) > 2 else 0

                            return {
                                'width': width,
                                'height': height,
                                'x': x_offset,
                                'y': y_offset
                            }

            self.logger.warning(f"Could not find geometry for {display_name}")
            return None

        except Exception as e:
            self.logger.error(f"Failed to get display geometry: {e}")
            return None

    def display_fullscreen_image(self, display_name, image_path):
        """
        Display a fullscreen image on a specific display.
        Works on X11 using feh, or falls back to imv for Wayland support.

        Args:
            display_name: Name of the display (e.g., 'eDP-2')
            image_path: Path to the PNG image file

        Returns:
            subprocess.Popen object if successful, None otherwise
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image file not found: {image_path}")
            return None

        # Get display geometry
        geometry = self.get_display_geometry(display_name)
        if not geometry:
            self.logger.error(f"Could not determine geometry for {display_name}")
            return None

        self.logger.info(f"Display {display_name} geometry: {geometry['width']}x{geometry['height']}+{geometry['x']}+{geometry['y']}")

        # Try feh first (works great on X11)
        if self._command_exists('feh'):
            try:
                # feh command to display fullscreen image at specific position
                cmd = [
                    'feh',
                    '--borderless',
                    '--no-menus',
                    '--geometry', f"{geometry['width']}x{geometry['height']}+{geometry['x']}+{geometry['y']}",
                    '--scale-down',
                    '--auto-zoom',
                    image_path
                ]

                self.logger.info(f"Displaying image on {display_name} using feh")
                process = subprocess.Popen(cmd)

                # Give it a moment to display
                time.sleep(0.5)

                return process

            except Exception as e:
                self.logger.error(f"Failed to display image with feh: {e}")

        # Try imv as fallback (works on both X11 and Wayland)
        elif self._command_exists('imv'):
            try:
                cmd = [
                    'imv',
                    '-f',  # fullscreen
                    image_path
                ]

                self.logger.info(f"Displaying image using imv (fullscreen mode)")
                self.logger.warning("imv may not position on correct display automatically")
                process = subprocess.Popen(cmd)

                time.sleep(0.5)
                return process

            except Exception as e:
                self.logger.error(f"Failed to display image with imv: {e}")

        else:
            self.logger.error("Neither feh nor imv is installed. Please install one:")
            self.logger.error("  For X11: sudo apt install feh")
            self.logger.error("  For Wayland: sudo apt install imv")
            return None

        return None

    def _command_exists(self, command):
        """Check if a command exists in PATH"""
        try:
            subprocess.run(
                ['which', command],
                capture_output=True,
                check=True,
                timeout=2
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False