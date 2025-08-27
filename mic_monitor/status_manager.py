import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from .devices import StatusDevice

class StatusManager:
    """Manages microphone status and connected devices"""
    
    def __init__(self):
        self.manual_busy = False
        self.manual_free = False
        self.ignore_until: Optional[datetime] = None
        self._devices: List[StatusDevice] = []
        
        # Try to initialize Luxafor device
        self._init_luxafor()
        
    def _init_luxafor(self):
        """Initialize Luxafor device if available"""
        try:
            from .devices.luxafor import LuxaforDevice
            device = LuxaforDevice()
            if device.connect(max_retries=3, retry_delay=1):
                self._devices.append(device)
                logging.info("✅ Luxafor Flag integration enabled")
                # Set initial color to green (available)
                device.set_color(0, 255, 0)
            else:
                logging.warning(f"⚠️ Luxafor Flag not available: {device.status.get('error')}")
        except Exception as e:
            logging.error(f"❌ Error initializing Luxafor: {e}", exc_info=True)
            
    def update_status(self, is_mic_in_use: bool) -> bool:
        """Update status based on mic usage and manual overrides"""
        # Check if we should ignore mic status
        if self.ignore_until:
            if datetime.now() > self.ignore_until:
                self.ignore_until = None
            else:
                is_mic_in_use = False
                
        # Apply manual overrides
        if self.manual_busy:
            is_mic_in_use = True
        elif self.manual_free:
            is_mic_in_use = False
            
        # Update all connected devices with enhanced status
        for device in self._devices:
            try:
                # Pass enhanced status information for better color control
                if hasattr(device, 'set_status') and len(device.set_status.__code__.co_varnames) > 2:
                    # Enhanced device (like Luxafor) that supports detailed status
                    if not device.set_status(
                        mic_in_use=is_mic_in_use,
                        manual_busy=self.manual_busy,
                        manual_free=self.manual_free,
                        ignore_until=self.ignore_until
                    ):
                        logging.warning(f"Failed to update device: {device.status['error']}")
                else:
                    # Legacy device interface
                    if not device.set_status(is_mic_in_use):
                        logging.warning(f"Failed to update device: {device.status['error']}")
            except Exception as e:
                logging.error(f"Error updating device: {e}")
                
        return is_mic_in_use
        
    def set_manual_status(self, is_busy: bool):
        """Set manual busy/free status"""
        self.manual_busy = is_busy
        self.manual_free = not is_busy
        self.ignore_until = None
        
    def ignore_mic_for(self, minutes: int):
        """Ignore microphone status for specified duration"""
        self.ignore_until = datetime.now() + timedelta(minutes=minutes)
        self.manual_busy = False
        self.manual_free = False
        
    def clear_override(self):
        """Clear all manual overrides"""
        self.manual_busy = False
        self.manual_free = False
        self.ignore_until = None
        
    def get_device_status(self) -> list:
        """Get status of all connected devices"""
        return [device.status for device in self._devices]
        
    def cleanup(self):
        """Clean up all devices"""
        for device in self._devices:
            try:
                device.disconnect()
            except Exception as e:
                logging.error(f"Error disconnecting device: {e}") 