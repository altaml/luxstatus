"""
Windows Audio Session API integration for real-time microphone detection
"""
import subprocess
import json
import logging
import psutil


class WindowsAudioMonitor:
    """Monitor microphone usage using Windows Audio Session API"""
    
    def get_active_microphone_apps(self):
        """
        Get applications currently using microphone using Windows native detection.
        This mirrors how Windows itself detects microphone usage.
        """
        try:
            # PowerShell script that checks for ACTUAL microphone usage
            # More conservative approach to avoid false positives
            powershell_script = '''
            try {
                $audioApps = @()
                $debugInfo = @()
                
                # Check microphone usage through Windows capability manager
                $micPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
                
                if (Test-Path $micPath) {
                    # Check NonPackaged apps (desktop applications)
                    $nonPackagedPath = "$micPath\\NonPackaged"
                    if (Test-Path $nonPackagedPath) {
                        $apps = Get-ChildItem $nonPackagedPath -ErrorAction SilentlyContinue
                        
                        foreach ($app in $apps) {
                            try {
                                $lastUsedStop = Get-ItemProperty -Path $app.PSPath -Name "LastUsedTimeStop" -ErrorAction SilentlyContinue
                                
                                # If LastUsedTimeStop is 0, the app claims to be using the microphone
                                if ($lastUsedStop -and $lastUsedStop.LastUsedTimeStop -eq 0) {
                                    # Extract process name from registry key
                                    $appName = $app.Name -replace ".*\\\\", "" -replace "#", "\\" 
                                    $exeName = ($appName -split "\\\\")[-1]
                                    
                                    # Verify the process is actually running
                                    $process = Get-Process -Name ($exeName -replace "\\.exe$", "") -ErrorAction SilentlyContinue
                                    if ($process) {
                                        # Additional check: see if the process has significant CPU usage
                                        # This helps filter out apps that just have permission but aren't active
                                        $cpuUsage = $process.CPU
                                        if ($cpuUsage -gt 0) {
                                            $audioApps += $exeName
                                            $debugInfo += "Found: $exeName (CPU: $cpuUsage)"
                                        } else {
                                            $debugInfo += "Skipped: $exeName (no CPU activity)"
                                        }
                                    }
                                }
                            } catch {
                                # Ignore individual app errors
                            }
                        }
                    }
                }
                
                # Remove duplicates and return as JSON
                $uniqueApps = $audioApps | Sort-Object -Unique
                if ($uniqueApps.Count -eq 0) {
                    Write-Output "[]"
                } else {
                    $uniqueApps | ConvertTo-Json
                }
            } catch {
                Write-Output "[]"
            }
            '''
            
            result = subprocess.run(
                ['powershell', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass', '-Command', powershell_script],
                capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    apps = json.loads(result.stdout.strip())
                    if isinstance(apps, list):
                        return [app for app in apps if app and isinstance(app, str)]
                    elif isinstance(apps, str) and apps:
                        return [apps]
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract app names from text output
                    lines = result.stdout.strip().split('\n')
                    return [line.strip() for line in lines if line.strip().endswith('.exe')]
                    
        except Exception as e:
            logging.debug(f"Windows Audio API check failed: {e}")
            
        return []


def test_audio_monitor():
    """Test function to verify audio monitoring works"""
    monitor = WindowsAudioMonitor()
    apps = monitor.get_active_microphone_apps()
    print(f"Detected audio apps: {apps}")
    return apps


if __name__ == "__main__":
    test_audio_monitor()