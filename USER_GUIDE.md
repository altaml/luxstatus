# 📖 Microphone Status Monitor - User Guide

## 🎯 What Does This App Do?

The **Microphone Status Monitor** automatically detects when you're in a meeting or call and displays your availability status to colleagues. It works with an optional Luxafor LED flag to provide visual indicators.

### Status Colors:
- 🟢 **GREEN** = Available (free to talk)
- 🔴 **RED** = In Meeting/Call (microphone in use)
- 🔵 **BLUE** = Do Not Disturb (manually set)
- 🟡 **YELLOW** = Away (break/lunch)

## 🚀 Quick Start Guide

### Installation

#### Windows
1. Download `MicrophoneStatusMonitor.exe` from the [latest release](https://github.com/yourusername/luxstatus/releases)
2. Run the installer as Administrator
3. The app will start automatically and appear in your system tray

#### macOS
1. Download `MicrophoneStatusMonitor.dmg` from the [latest release](https://github.com/yourusername/luxstatus/releases)
2. Open the DMG and drag the app to Applications
3. Right-click and select "Open" on first run (security bypass)
4. Grant microphone permission when prompted

### First Run
1. Look for the microphone icon in your system tray (Windows) or menu bar (macOS)
2. Right-click the icon to see the menu
3. The app starts in **Auto Mode** - it automatically detects microphone usage

## 💡 How to Use

### System Tray Icon (Windows) / Menu Bar (macOS)

The icon shows your current status at a glance:
- Hover over it to see detailed status
- Right-click for the full menu

### Status Menu Options

#### 🤖 Auto Mode (Default)
- Automatically detects when your microphone is in use
- Changes to RED when in a call
- Returns to GREEN when call ends
- No manual intervention needed

#### 🟢 Available
Set yourself as available when you want to signal you're free:
- **Until I change it** - Stays green regardless of mic activity
- **30 minutes / 1 hour / 2 hours** - Temporary override, then returns to Auto

#### 🔵 Do Not Disturb
Use when you need focused work time:
- **Until I change it** - Stay in DND mode
- **30 minutes / 1 hour / 2 hours** - Temporary DND, then returns to Auto

#### 🟡 Away
Use when stepping away from your desk:
- **Until I change it** - Stay away indefinitely
- **15 / 30 / 60 / 120 minutes** - Timed away status

### Status Widget
Click **"Show Status Widget"** to see:
- Current status with large visual indicator
- Which apps are using your microphone
- Quick status change buttons
- Time remaining for temporary statuses

## 🎮 Luxafor Flag Integration

If you have a Luxafor LED flag device:

1. **Plug in the Luxafor** before starting the app
2. The app automatically detects and connects
3. Colors sync with your status:
   - 🟢 Green light = Available
   - 🔴 Red light = In Meeting/Busy
   - 🔵 Blue light = Do Not Disturb
   - 🟡 Yellow light = Away

**Note**: The app works perfectly without a Luxafor device - it's optional!

## 🛠️ Settings & Customization

### Start with Windows/macOS
- **Windows**: Added to Startup folder during installation
- **macOS**: Added to Login Items if you chose this option

### Remove from Startup
- **Windows**: Open Task Manager → Startup tab → Disable "Microphone Status Monitor"
- **macOS**: System Preferences → Users & Groups → Login Items → Remove the app

## 🔍 Troubleshooting

### App doesn't detect my microphone
1. **Check permissions**:
   - Windows: Settings → Privacy → Microphone
   - macOS: System Preferences → Security & Privacy → Microphone
2. **Restart the app**
3. **Check if your meeting app is recognized** (Teams, Zoom, Slack, Discord, etc.)

### Luxafor not working
1. **Check USB connection** - Try a different port
2. **Restart the app** with Luxafor plugged in
3. **Windows only**: May need to install [Zadig drivers](https://zadig.akeo.ie/)
4. The app continues to work in the system tray even without Luxafor

### False positives (shows busy when not in call)
- Some apps keep microphone permission active even when not in use
- Use **Manual Override** to set your status
- The app filters out most false positives automatically

### App won't start
- **Windows**: Run as Administrator
- **macOS**: Right-click → Open (bypasses Gatekeeper)
- Check for antivirus blocking

## 📊 Understanding Microphone Detection

The app detects microphone usage by:
1. Checking Windows/macOS system APIs
2. Verifying which apps have active microphone access
3. Filtering out apps that have permission but aren't actively recording
4. Confirming with CPU usage patterns for accuracy

### Detected Apps
The following apps are automatically recognized:
- **Video Conferencing**: Teams, Zoom, Skype, WebEx, Google Meet
- **Communication**: Discord, Slack (in calls), WhatsApp, Telegram
- **Browsers**: Chrome, Edge, Firefox, Safari (during web calls)
- **Recording**: OBS, Audacity, QuickTime

## ⌨️ Keyboard Shortcuts

Currently, the app doesn't have global keyboard shortcuts. Use the system tray menu for all controls.

## 🔄 Updates

### Checking for Updates
- Check the [GitHub releases page](https://github.com/yourusername/luxstatus/releases)
- Download the latest version
- Run the installer (it will replace the old version)

### Update Notifications
Future versions will include automatic update checks.

## 🆘 Getting Help

### Quick Tips
- **Hover** over the tray icon for current status
- **Right-click** for all options
- **Status Widget** shows detailed information

### Support Channels
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/luxstatus/issues)
- **Documentation**: Check this guide and README.md
- **Logs Location**:
  - Windows: `%APPDATA%\MicrophoneStatusMonitor\logs`
  - macOS: `~/Library/Logs/MicrophoneStatusMonitor`

## 🎯 Use Cases

### Remote Workers
- Shows colleagues when you're in meetings
- Prevents interruptions during calls
- Signals availability for quick chats

### Open Office
- Visual indicator for desk visitors
- Reduces "are you busy?" interruptions
- Professional appearance with Luxafor flag

### Home Office
- Family members can see when you're in meetings
- Clear boundaries for work time
- Automatic detection means no manual switching

## 🔒 Privacy & Security

- **No network communication** - Completely offline
- **No data collection** - Your privacy is protected
- **Local only** - All processing happens on your computer
- **No accounts required** - Just install and use
- **Open source** - Review the code yourself

## 💡 Pro Tips

1. **Use timed statuses** instead of permanent overrides
2. **Set "Away" when going to lunch** - prevents false "available" status
3. **Use DND for deep work** - even if not in a meeting
4. **Check Status Widget** if unsure why status changed
5. **Position Luxafor flag** where colleagues can easily see it

## 🎨 Customization (Advanced)

For advanced users who want to modify behavior:

1. Clone the repository
2. Edit `secure_mic_monitor.py` for core behavior
3. Modify `mic_monitor/platform/` for OS-specific detection
4. Rebuild using `deploy_windows.py` or `deploy_macos.py`

## 📝 FAQ

**Q: Does it work without a Luxafor device?**
A: Yes! The system tray icon shows your status. Luxafor is optional.

**Q: Can I use multiple Luxafor devices?**
A: Currently supports one device at a time.

**Q: Does it detect phone calls?**
A: Only computer-based calls. Phone calls through separate devices aren't detected.

**Q: Can colleagues see my status remotely?**
A: No, this is local-only. Use Teams/Slack status for remote visibility.

**Q: Does it work with virtual cameras/microphones?**
A: Yes, it detects any microphone device recognized by your OS.

**Q: Can I schedule status changes?**
A: Not yet, but you can set timed statuses (30min, 1hr, 2hr).

## 🎉 Enjoy!

The Microphone Status Monitor is designed to make your work life easier by automatically managing your availability status. Set it up once and let it work in the background!

If you find this tool helpful, consider:
- ⭐ Starring the [GitHub repository](https://github.com/yourusername/luxstatus)
- 🐛 Reporting bugs or suggesting features
- 📢 Sharing with colleagues who might benefit

Thank you for using Microphone Status Monitor!
