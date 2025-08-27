import logging
import subprocess
import json
import os

class MacOSMicrophoneMonitor:
    """macOS implementation of microphone monitoring"""
    
    def __init__(self):
        self.last_known_state = False
        
    def get_active_apps(self):
        """
        Get list of applications currently using the microphone.
        
        Returns:
            list: Names of applications currently using the microphone
        """
        using_apps = []
        
        try:
            # Method 1: Check using system logs for microphone access
            # This checks the TCC (Transparency, Consent, and Control) database
            result = subprocess.run(
                ['log', 'show', '--predicate', 'eventMessage contains "microphone"', 
                 '--style', 'json', '--last', '1m'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse log entries for microphone access
                for line in result.stdout.split('\n'):
                    if 'microphone' in line.lower() and 'granted' in line.lower():
                        # Extract app name from log
                        # This is a simplified approach
                        pass
        except Exception as e:
            logging.debug(f"Log-based detection failed: {e}")
        
        # Method 2: Check using CoreAudio via Python script
        try:
            # Use osascript to check microphone usage
            script = '''
            tell application "System Events"
                set micInUse to false
                try
                    -- Check if any audio input is active
                    do shell script "ioreg -c AppleHDAEngineInput | grep -i 'IOAudioEngineState' | grep -i '1'"
                    set micInUse to true
                end try
                return micInUse
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode == 0 and 'true' in result.stdout.lower():
                # Microphone is in use, try to identify which app
                using_apps = self._identify_audio_apps()
        except Exception as e:
            logging.debug(f"AppleScript detection failed: {e}")
        
        # Method 3: Check common communication apps
        if not using_apps:
            using_apps = self._check_known_apps()
        
        return using_apps
    
    def _identify_audio_apps(self):
        """Identify which apps are using audio"""
        apps = []
        
        # Check if common communication apps are running and likely using mic
        known_apps = {
            'zoom.us': 'Zoom',
            'Teams': 'Microsoft Teams',
            'Slack': 'Slack',
            'Discord': 'Discord',
            'Skype': 'Skype',
            'FaceTime': 'FaceTime',
            'Google Chrome': 'Chrome',
            'Safari': 'Safari',
            'Firefox': 'Firefox'
        }
        
        try:
            # Get list of running applications
            script = 'tell application "System Events" to get name of every process whose background only is false'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode == 0:
                running_apps = result.stdout.strip().split(', ')
                
                for app_name, display_name in known_apps.items():
                    if any(app_name in running for running in running_apps):
                        # Check if the app has microphone permission and is likely using it
                        if self._check_app_mic_permission(app_name):
                            apps.append(display_name)
        except Exception as e:
            logging.debug(f"Failed to identify audio apps: {e}")
        
        return apps
    
    def _check_app_mic_permission(self, app_name):
        """Check if an app has microphone permission and might be using it"""
        try:
            # Check TCC database for microphone permissions
            # Note: This requires appropriate permissions to access
            tcc_db = os.path.expanduser('~/Library/Application Support/com.apple.TCC/TCC.db')
            
            if os.path.exists(tcc_db):
                # Use sqlite3 to check permissions (requires appropriate access)
                result = subprocess.run(
                    ['sqlite3', tcc_db, 
                     f"SELECT allowed FROM access WHERE service='kTCCServiceMicrophone' AND client LIKE '%{app_name}%';"],
                    capture_output=True, text=True, timeout=2
                )
                
                if result.returncode == 0 and '1' in result.stdout:
                    # App has microphone permission
                    # Now check if it's actively using it (simplified check)
                    return self._is_app_active(app_name)
        except Exception as e:
            logging.debug(f"Failed to check app permission: {e}")
        
        # Default to checking if the app is in the foreground and likely in a call
        return self._is_app_active(app_name)
    
    def _is_app_active(self, app_name):
        """Check if an app is actively using resources (likely in a call)"""
        try:
            # Get CPU usage for the app
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True, text=True, timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if app_name.lower() in line.lower():
                        # Parse CPU usage (third column)
                        parts = line.split()
                        if len(parts) > 2:
                            try:
                                cpu_usage = float(parts[2])
                                # If CPU usage is significant, might be in a call
                                if cpu_usage > 5.0:
                                    return True
                            except ValueError:
                                pass
        except Exception as e:
            logging.debug(f"Failed to check app activity: {e}")
        
        return False
    
    def _check_known_apps(self):
        """Check if known communication apps are in an active call"""
        active_apps = []
        
        # Check Zoom
        if self._check_zoom_meeting():
            active_apps.append('Zoom')
        
        # Check Teams
        if self._check_teams_meeting():
            active_apps.append('Microsoft Teams')
        
        # Check for browser-based meetings
        if self._check_browser_meeting():
            active_apps.append('Browser')
        
        return active_apps
    
    def _check_zoom_meeting(self):
        """Check if Zoom is in an active meeting"""
        try:
            # Check if Zoom is running and in a meeting
            script = '''
            tell application "System Events"
                if exists (process "zoom.us") then
                    set windowList to name of every window of process "zoom.us"
                    repeat with windowName in windowList
                        if windowName contains "Meeting" or windowName contains "Zoom" then
                            return true
                        end if
                    end repeat
                end if
                return false
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=2
            )
            
            return result.returncode == 0 and 'true' in result.stdout.lower()
        except:
            return False
    
    def _check_teams_meeting(self):
        """Check if Microsoft Teams is in an active meeting"""
        try:
            # Check if Teams is running and in a meeting
            script = '''
            tell application "System Events"
                if exists (process "Microsoft Teams") then
                    set windowList to name of every window of process "Microsoft Teams"
                    repeat with windowName in windowList
                        if windowName contains "Meeting" or windowName contains "Call" then
                            return true
                        end if
                    end repeat
                end if
                return false
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=2
            )
            
            return result.returncode == 0 and 'true' in result.stdout.lower()
        except:
            return False
    
    def _check_browser_meeting(self):
        """Check if a browser might be in a web-based meeting"""
        try:
            # Check browser tabs for meeting-related content
            browsers = ['Google Chrome', 'Safari', 'Firefox']
            
            for browser in browsers:
                script = f'''
                tell application "System Events"
                    if exists (process "{browser}") then
                        set windowList to name of every window of process "{browser}"
                        repeat with windowName in windowList
                            if windowName contains "Meet" or windowName contains "Zoom" or windowName contains "Teams" then
                                return true
                            end if
                        end repeat
                    end if
                    return false
                end tell
                '''
                
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True, text=True, timeout=2
                )
                
                if result.returncode == 0 and 'true' in result.stdout.lower():
                    return True
        except:
            pass
        
        return False
    
    def get_status(self):
        """
        Get current microphone status.
        
        Returns:
            dict: Status object with 'in_use' and 'using_apps' fields
        """
        active_apps = self.get_active_apps()
        
        # Log status changes
        is_in_use = len(active_apps) > 0
        if is_in_use != self.last_known_state:
            if is_in_use:
                logging.info(f"🎤 Microphone detected in use by: {active_apps}")
            else:
                logging.info("🎤 Microphone not in use")
            self.last_known_state = is_in_use
        
        return {
            'in_use': is_in_use,
            'using_apps': active_apps,
            'platform': 'macos'
        } 