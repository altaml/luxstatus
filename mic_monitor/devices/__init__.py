"""Device integration for status indication"""
from abc import ABC, abstractmethod

class StatusDevice(ABC):
    """Base class for status indicator devices"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the device"""
        pass
        
    @abstractmethod
    def set_status(self, is_busy: bool) -> bool:
        """Set the device status"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the device"""
        pass
        
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if device is connected"""
        pass
        
    @property
    @abstractmethod
    def status(self) -> dict:
        """Get device status"""
        pass