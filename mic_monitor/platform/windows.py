import winreg
import logging
import psutil
import time
import subprocess
import json
from .windows_audio_api import WindowsAudioMonitor

class WindowsMicrophoneMonitor:
    """Windows-specific implementation of microphone monitoring using Registry"""
    
    def __init__(self):
        self.registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\NonPackaged"
        self.audio_monitor = WindowsAudioMonitor()
    
    def get_active_apps(self):
        """
        Get list of applications currently using the microphone.
        Uses Windows Audio Session API first, then falls back to registry.
        
        Returns:
            list: Names of applications currently using the microphone
        """
        using_apps = []
        
        # First try Windows Audio Session API (like Windows itself uses)
        try:
            audio_apps = self.audio_monitor.get_active_microphone_apps()
            if audio_apps:
                # Filter the apps through our verification logic
                verified_apps = []
                for app in audio_apps:
                    if self._is_actually_recording(app):
                        verified_apps.append(app)
                        print(f"🎤 Process {app} detected and verified as actively recording")
                    else:
                        print(f"⏰ Process {app} has mic permission but not actively recording")
                
                if verified_apps:
                    return verified_apps
                # If no apps passed verification, continue to registry check
        except Exception as e:
            logging.debug(f"Audio API detection failed: {e}")
        
        # Fallback to registry method
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        app_key_name = winreg.EnumKey(key, i)
                        i += 1
                        
                        with winreg.OpenKey(key, app_key_name) as app_key:
                            try:
                                stop_time, reg_type = winreg.QueryValueEx(app_key, "LastUsedTimeStop")
                                
                                if stop_time == 0:  # App claims to be using mic
                                    # Clean up the path (e.g., 'C:#...#obs64.exe' -> 'obs64.exe')
                                    clean_name = app_key_name.replace('#', '\\')
                                    exe_name = clean_name.split('\\')[-1]
                                    
                                    # Check if process is actually running
                                    if self._is_process_running(exe_name):
                                        # Verify if the app is actually recording (not just has permission)
                                        if self._is_actually_recording(exe_name):
                                            using_apps.append(exe_name)
                                            logging.info(f"✅ Active microphone use detected: {exe_name}")
                                        else:
                                            logging.debug(f"⏰ {exe_name} has mic permission but not actively recording")
                                    else:
                                        logging.debug(f"❌ Registry shows {exe_name} using mic, but process not running (stale entry)")
                            except FileNotFoundError:
                                continue
                    except OSError:
                        break
                        
        except FileNotFoundError:
            logging.warning("Registry key not found. This may be normal if no apps have requested mic access.")
        except Exception as e:
            logging.error(f"Error reading Windows Registry: {e}")
            
        return using_apps
    
    def _is_process_running(self, exe_name):
        """Check if a process with the given executable name is actually running"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                    return True
            return False
        except Exception as e:
            logging.debug(f"Error checking if process {exe_name} is running: {e}")
            # If we can't check, assume it's running to be safe
            return True
    
    def _is_actually_recording(self, exe_name):
        """
        Check if an application is actually recording audio.
        We'll be MORE restrictive to avoid false positives.
        """
        try:
            # Known communication/recording apps that should be trusted when registry says they're using mic
            # BUT only when they're likely in an actual call
            known_communication_apps = [
                'teams.exe', 'ms-teams.exe', 'zoom.exe', 'zoomwebservice.exe',
                'discord.exe', 'skype.exe', 'webexmta.exe', 'ciscowebexstart.exe',
                'obs64.exe', 'obs32.exe', 'streamlabs obs.exe',
                'audacity.exe', 'vlc.exe'
            ]
            
            # Apps that need extra verification (often have permission but rarely use it)
            apps_needing_cpu_check = [
                'chrome.exe', 'msedge.exe', 'firefox.exe',
                'slack.exe', 'whatsapp.exe', 'telegram.exe'
            ]
            
            # Apps that often have mic permission but rarely actually use it
            # These need additional verification
            apps_needing_verification = [
                'nvidia broadcast.exe', 'nvidiabroadcast.exe',
                'krisp.exe', 'voicemod.exe', 'vb-audio.exe'
            ]
            
            exe_lower = exe_name.lower()
            
            # Check if it's a known communication app that we trust
            if exe_lower in known_communication_apps:
                # Trust these apps when registry says they're using mic
                logging.debug(f"✅ Known communication app {exe_name} is using microphone")
                return True
            
            # Check if it needs CPU verification (browsers, Slack, etc.)
            elif exe_lower in apps_needing_cpu_check:
                # These apps often have permission but aren't actively in calls
                # Check if process is actually running with significant activity
                for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
                    if proc.info['name'] and proc.info['name'].lower() == exe_lower:
                        try:
                            proc_obj = psutil.Process(proc.info['pid'])
                            # Get CPU usage over a short interval
                            cpu = proc_obj.cpu_percent(interval=0.5)
                            # Require significant CPU usage as indicator of active call
                            if cpu > 10.0:
                                logging.debug(f"✅ {exe_name} appears to be in active call (CPU: {cpu:.1f}%)")
                                return True
                            else:
                                logging.debug(f"⚠️ {exe_name} has mic permission but low activity (CPU: {cpu:.1f}%)")
                                return False
                        except:
                            pass
                return False
            
            # For apps that need verification
            elif exe_lower in apps_needing_verification:
                # These apps often have permission but aren't actively recording
                # Only consider them active if they have high CPU usage
                for proc in psutil.process_iter(['name', 'pid']):
                    if proc.info['name'] and proc.info['name'].lower() == exe_lower:
                        try:
                            proc_obj = psutil.Process(proc.info['pid'])
                            cpu = proc_obj.cpu_percent(interval=0.5)
                            if cpu > 15.0:  # Higher threshold for these apps
                                logging.debug(f"✅ {exe_name} appears to be processing audio (CPU: {cpu:.1f}%)")
                                return True
                            else:
                                logging.debug(f"⚠️ {exe_name} has permission but likely idle (CPU: {cpu:.1f}%)")
                                return False
                        except:
                            pass
                return False
            
            # Unknown apps - be very conservative
            else:
                logging.debug(f"❓ Unknown app {exe_name} - not considering as actively recording")
                return False
                
        except Exception as e:
            logging.debug(f"Error checking if {exe_name} is actually recording: {e}")
            # If we can't check, assume not recording to avoid false positives
            return False
    
    def get_status(self):
        """
        Get current microphone status.
        
        Returns:
            dict: Status object with 'in_use' and 'using_apps' fields
        """
        active_apps = self.get_active_apps()
        return {
            'in_use': len(active_apps) > 0,
            'using_apps': active_apps,
            'platform': 'windows'
        } 