import sys
import platform
import logging
from .windows import WindowsMicrophoneMonitor
from .macos import MacOSMicrophoneMonitor
from .linux import LinuxMicrophoneMonitor

def get_platform_monitor():
    """
    Factory function to get the appropriate microphone monitor for the current platform.
    
    Returns:
        object: Platform-specific microphone monitor instance
    """
    system = platform.system().lower()
    
    if system == 'windows':
        return WindowsMicrophoneMonitor()
    elif system == 'darwin':
        return MacOSMicrophoneMonitor()
    elif system == 'linux':
        return LinuxMicrophoneMonitor()
    else:
        logging.error(f"Unsupported platform: {system}")
        raise NotImplementedError(f"Microphone monitoring not supported on {system}") 