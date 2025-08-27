# 🚀 Deployment Guide - Microphone Status Monitor

This guide covers deployment for Windows and macOS systems.

## 📋 Prerequisites

### All Platforms
- Python 3.8 or higher
- Git (for cloning the repository)
- Luxafor device (optional, for light integration)

### Windows Specific
- Windows 10/11
- Administrator access (for installation)
- Visual C++ Redistributable (usually pre-installed)

### macOS Specific
- macOS 10.15 (Catalina) or later
- Xcode Command Line Tools: `xcode-select --install`
- Administrator access

## 🪟 Windows Deployment

### Quick Deploy (For End Users)

1. **Download the installer package** (if provided)
2. **Run as Administrator**: `install_windows.bat`
3. **Follow the prompts** to:
   - Install to Program Files
   - Create desktop shortcut
   - Add to startup (optional)

### Build from Source (For Developers)

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/luxstatus.git
cd luxstatus
```

2. **Run the deployment script**:
```bash
python deploy_windows.py
```

This will:
- Install all dependencies
- Create a standalone `.exe` file
- Generate installer scripts
- Create an Inno Setup script for professional installer

3. **Test the executable**:
```bash
dist\MicrophoneStatusMonitor.exe
```

4. **Create installer** (optional):
   - Install [Inno Setup](https://jrsoftware.org/isdl.php)
   - Open `installer.iss` in Inno Setup
   - Click "Compile" to create professional installer

### Windows Auto-Start Setup

#### Method 1: Startup Folder
1. Press `Win + R`, type `shell:startup`
2. Copy `MicrophoneStatusMonitor.exe` to this folder

#### Method 2: Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "When I log on"
4. Set action: Start `MicrophoneStatusMonitor.exe`

#### Method 3: Registry (Advanced)
```reg
[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run]
"MicrophoneStatusMonitor"="C:\\Program Files\\MicrophoneStatusMonitor\\MicrophoneStatusMonitor.exe"
```

## 🍎 macOS Deployment

### Quick Deploy (For End Users)

1. **Download the DMG file** (if provided)
2. **Open the DMG** and drag app to Applications
3. **First run**: Right-click and select "Open" (security bypass)
4. **Grant microphone permission** when prompted

### Build from Source (For Developers)

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/luxstatus.git
cd luxstatus
```

2. **Run the deployment script**:
```bash
python3 deploy_macos.py
```

This will:
- Install all dependencies
- Create a `.app` bundle
- Generate installer scripts
- Create launch agent for auto-start

3. **Test the app**:
```bash
open "dist/Microphone Status Monitor.app"
```

4. **Create DMG** (optional):
```bash
./create_dmg.sh
```

5. **Install system-wide**:
```bash
sudo ./install_macos.sh
```

### macOS Auto-Start Setup

#### Method 1: Login Items (GUI)
1. System Preferences → Users & Groups
2. Select your user → Login Items tab
3. Click "+" and add "Microphone Status Monitor.app"

#### Method 2: Launch Agent (Recommended)
```bash
# Copy launch agent
cp com.yourcompany.micmonitor.plist ~/Library/LaunchAgents/

# Load the agent
launchctl load ~/Library/LaunchAgents/com.yourcompany.micmonitor.plist
```

### macOS Security & Permissions

1. **Microphone Access**:
   - System Preferences → Security & Privacy → Privacy → Microphone
   - Check "Microphone Status Monitor"

2. **Accessibility Access** (for some features):
   - System Preferences → Security & Privacy → Privacy → Accessibility
   - Add and check "Microphone Status Monitor"

3. **Gatekeeper Bypass** (first run):
   - Right-click the app → Open
   - Click "Open" in the security dialog

## 🔧 Configuration

### Environment Variables

```bash
# Set custom port for API (if using API module)
export MIC_MONITOR_PORT=37456

# Set log level
export MIC_MONITOR_LOG_LEVEL=INFO

# Disable Luxafor
export MIC_MONITOR_NO_LUXAFOR=1
```

### Configuration File

Create `~/.micmonitor/config.json`:

```json
{
  "auto_start": true,
  "check_interval": 1,
  "luxafor_enabled": true,
  "api_enabled": false,
  "api_port": 37456,
  "log_level": "INFO",
  "colors": {
    "available": [0, 255, 0],
    "busy": [255, 0, 0],
    "away": [255, 255, 0],
    "dnd": [0, 0, 255]
  }
}
```

## 📦 Distribution

### Windows Distribution

1. **Standalone EXE**:
   - Single file: `dist/MicrophoneStatusMonitor.exe`
   - No Python required on target machine
   - Include Visual C++ Redistributable if needed

2. **MSI Installer** (Professional):
   - Use WiX Toolset or Inno Setup
   - Includes uninstaller
   - Registry entries for auto-start

3. **Portable ZIP**:
   ```bash
   # Create portable package
   zip -r MicrophoneStatusMonitor_Portable.zip dist/
   ```

### macOS Distribution

1. **DMG Image**:
   - Professional appearance
   - Drag-and-drop installation
   - Background image and layout

2. **PKG Installer**:
   ```bash
   # Create PKG installer
   productbuild --component "dist/Microphone Status Monitor.app" \
                /Applications MicrophoneStatusMonitor.pkg
   ```

3. **Homebrew Cask** (Advanced):
   ```ruby
   cask "microphone-status-monitor" do
     version "2.0.0"
     sha256 "..."
     url "https://github.com/yourusername/luxstatus/releases/..."
     app "Microphone Status Monitor.app"
   end
   ```

## 🐛 Troubleshooting

### Windows Issues

1. **"Windows protected your PC" error**:
   - Click "More info" → "Run anyway"
   - Or right-click → Properties → Unblock

2. **Luxafor not detected**:
   - Install [Zadig](https://zadig.akeo.ie/) 
   - Replace driver with WinUSB or libusb-win32

3. **Missing DLL errors**:
   - Install Visual C++ Redistributable
   - Install Python 3.8+ system-wide

### macOS Issues

1. **"App is damaged" error**:
   ```bash
   xattr -cr "/Applications/Microphone Status Monitor.app"
   ```

2. **Microphone permission denied**:
   ```bash
   tccutil reset Microphone com.yourcompany.micmonitor
   ```

3. **App won't start**:
   - Check Console.app for errors
   - Verify Python 3.8+ is installed
   - Check launch agent logs: `/tmp/micmonitor.err`

## 🔄 Updates

### Windows Update Process

1. **Manual Update**:
   - Download new version
   - Run uninstaller: `uninstall_windows.bat`
   - Install new version: `install_windows.bat`

2. **In-App Update** (Future):
   - Check for updates via Help menu
   - Download and install automatically

### macOS Update Process

1. **Manual Update**:
   - Download new DMG
   - Replace app in Applications folder
   - Restart the app

2. **Sparkle Framework** (Future):
   - Automatic update checks
   - Delta updates for efficiency

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Test on clean system
- [ ] Verify all dependencies included
- [ ] Test Luxafor integration
- [ ] Check auto-start functionality
- [ ] Verify uninstaller works
- [ ] Test microphone detection accuracy

### Windows Deployment
- [ ] Build executable with PyInstaller
- [ ] Create installer with Inno Setup
- [ ] Sign executable (optional)
- [ ] Test on Windows 10 and 11
- [ ] Verify admin rights handling
- [ ] Test with/without Luxafor

### macOS Deployment
- [ ] Build app bundle with py2app
- [ ] Create DMG with background
- [ ] Notarize app (for distribution)
- [ ] Test on multiple macOS versions
- [ ] Verify permissions requests
- [ ] Test Gatekeeper bypass

### Post-Deployment
- [ ] Monitor error reports
- [ ] Gather user feedback
- [ ] Plan update schedule
- [ ] Document known issues
- [ ] Update installation guide

## 🆘 Support

### Getting Help
- GitHub Issues: [Report bugs](https://github.com/yourusername/luxstatus/issues)
- Documentation: Check README.md
- Logs: 
  - Windows: `%APPDATA%\MicrophoneStatusMonitor\logs`
  - macOS: `~/Library/Logs/MicrophoneStatusMonitor`

### Debug Mode
```bash
# Windows
set MIC_MONITOR_DEBUG=1
MicrophoneStatusMonitor.exe

# macOS
export MIC_MONITOR_DEBUG=1
open "/Applications/Microphone Status Monitor.app"
```

## 📄 License

This software is distributed under the MIT License. See LICENSE file for details.
