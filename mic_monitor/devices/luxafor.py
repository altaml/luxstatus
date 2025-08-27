"""
Luxafor device integration for status indication
"""
import logging
import time
from . import StatusDevice

try:
    from luxafor import luxafor
    LUXAFOR_AVAILABLE = True
    logging.debug("✅ Luxafor library imported successfully")
except ImportError:
    LUXAFOR_AVAILABLE = False
    logging.warning("Luxafor library not available. Install with: pip install git+https://github.com/fmartingr/pyluxafor.git#egg=luxafor")


class LuxaforDevice(StatusDevice):
    """Luxafor flag device for status indication"""
    
    def __init__(self):
        self.device = None
        self._status = {
            'connected': False,
            'error': None,
            'last_update': None,
            'last_color': [0, 0, 0]
        }
        
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._status['connected']
    
    @property  
    def status(self) -> dict:
        """Get device status"""
        return self._status
        
    @status.setter
    def status(self, value: dict):
        """Set device status"""
        self._status = value
        
    def connect(self, max_retries=3, retry_delay=1) -> bool:
        """Connect to the Luxafor device"""
        if not LUXAFOR_AVAILABLE:
            self._status['error'] = "Luxafor library not installed"
            return False
            
        for attempt in range(max_retries):
            try:
                self.device = luxafor.Luxafor()
                self._status['connected'] = True
                self._status['error'] = None
                logging.info("✅ Luxafor Flag connected successfully")
                return True
            except Exception as e:
                error_msg = f"Attempt {attempt + 1}/{max_retries}: {e}"
                logging.warning(error_msg)
                self._status['error'] = error_msg
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        self._status['connected'] = False
        logging.error("❌ Failed to connect to Luxafor Flag after all attempts")
        return False
        
    def disconnect(self):
        """Disconnect and turn off the device"""
        if self.device:
            try:
                self.set_color(0, 0, 0)  # Turn off
                self.device = None
                self._status['connected'] = False
                logging.info("Luxafor device disconnected")
            except Exception as e:
                logging.error(f"Error disconnecting Luxafor: {e}")
                
    def set_color(self, r: int, g: int, b: int) -> bool:
        """Set the Luxafor color"""
        if not self.device:
            if not self.connect():
                return False
                
        try:
            # Set all LEDs
            self.device.set_color(r, g, b, 255)
            self._status['last_update'] = time.time()
            self._status['last_color'] = [r, g, b]
            self._status['error'] = None
            return True
        except Exception as e:
            error_msg = f"Error setting color: {e}"
            logging.error(error_msg)
            self._status['error'] = error_msg
            self._status['connected'] = False
            return False
            
    def set_status(self, mic_in_use: bool, manual_busy: bool = False, 
                   manual_free: bool = False, ignore_until = None) -> bool:
        """
        Set status based on simplified color scheme:
        🟢 Green [0,255,0]   = Available/Free
        🔴 Red [255,0,0]     = Busy (DND or In Meeting)
        🟡 Yellow [255,255,0] = Away
        """
        
        # Priority order: manual overrides > ignore > mic status
        
        # Check for "Away" status (ignoring mic)
        if ignore_until:
            return self.set_color(255, 255, 0)  # Yellow for Away
            
        # Check for manual overrides or mic status
        if manual_busy or mic_in_use:
            return self.set_color(255, 0, 0)    # Red for Busy (DND or In Meeting)
        elif manual_free:
            return self.set_color(0, 255, 0)    # Green for Available
            
        # Default: Available
        return self.set_color(0, 255, 0)        # Green for Available