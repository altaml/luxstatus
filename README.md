# 🎤 Microphone Status Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey)](https://github.com/YOUR_GITHUB_USERNAME/luxstatus)

Automatic availability status based on microphone usage. Perfect for remote work, open offices, and better workplace communication.

![Status Example](https://via.placeholder.com/600x200/f3f4f6/000000?text=Microphone+Status+Monitor)

## ✨ Features

- 🎯 **Automatic Detection** - Knows when you're in a meeting
- 🚦 **Visual Status** - System tray icon + optional Luxafor LED flag
- 🔒 **Privacy First** - No network access, completely offline
- 🎨 **Smart Filtering** - Eliminates false positives from apps with mic permission
- ⚡ **Lightweight** - Minimal CPU and memory usage
- 🌍 **Cross-Platform** - Windows and macOS support

## 📥 Installation

### Quick Install

Download the latest release for your platform:

| Platform | Download | Requirements |
|----------|----------|--------------|
| Windows | [MicrophoneStatusMonitor.exe](https://github.com/yourusername/luxstatus/releases) | Windows 10/11 |
| macOS | [MicrophoneStatusMonitor.dmg](https://github.com/yourusername/luxstatus/releases) | macOS 10.15+ |

### Build from Source

```bash
# Clone repository
git clone https://github.com/yourusername/luxstatus.git
cd luxstatus

# Install dependencies
pip install -r requirements.txt

# Run directly
python secure_mic_monitor.py

# Or build executable
python deploy_windows.py  # Windows
python deploy_macos.py    # macOS
```

## 🚀 Usage

1. **Launch** the application - it starts in the system tray
2. **Right-click** the tray icon for options
3. **Auto Mode** (default) - Automatically detects microphone usage

### Status Indicators

| Status | Color | Meaning |
|--------|-------|---------|
| 🟢 Green | Available | Free to talk |
| 🔴 Red | Busy | In meeting/call |
| 🔵 Blue | Do Not Disturb | Focused work |
| 🟡 Yellow | Away | Break/lunch |

## 🎮 Luxafor Integration (Optional)

The app works with [Luxafor LED flags](https://luxafor.com/) for physical status indication:

1. Plug in your Luxafor device
2. Start the application
3. Colors sync automatically

**Note**: The app works perfectly without a Luxafor device.

## 🔧 Configuration

The app works out-of-the-box with sensible defaults. For advanced configuration, see [USER_GUIDE.md](USER_GUIDE.md).

## 🏗️ Architecture

```
luxstatus/
├── secure_mic_monitor.py    # Main application
├── mic_monitor/
│   ├── platform/            # OS-specific implementations
│   │   ├── windows.py      # Windows mic detection
│   │   └── macos.py        # macOS mic detection
│   ├── devices/            # Hardware integrations
│   │   └── luxafor.py      # Luxafor flag control
│   └── status_manager.py   # Status logic
└── deploy_*.py             # Build scripts
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Development

### Prerequisites

- Python 3.8+
- Git
- Platform-specific tools:
  - **Windows**: Visual C++ Redistributable
  - **macOS**: Xcode Command Line Tools

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Optional dev tools
```

### Running Tests

```bash
# Run the application in debug mode
python secure_mic_monitor.py

# Test microphone detection
python -c "from mic_monitor.platform.windows import WindowsMicrophoneMonitor; m = WindowsMicrophoneMonitor(); print(m.get_status())"
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| App doesn't detect microphone | Check OS microphone permissions |
| Luxafor not working | Try different USB port, install drivers |
| False positives | App auto-filters most, use manual override if needed |
| Won't start on macOS | Right-click → Open to bypass Gatekeeper |

For detailed troubleshooting, see [USER_GUIDE.md](USER_GUIDE.md#-troubleshooting).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pystray](https://github.com/moses-palmer/pystray) - System tray integration
- [pyluxafor](https://github.com/fmartingr/pyluxafor) - Luxafor device control
- [psutil](https://github.com/giampaolo/psutil) - Process monitoring

## 📊 Project Status

- ✅ Windows support
- ✅ macOS support
- ✅ Luxafor integration
- ✅ Auto-detection
- ✅ Manual overrides
- 🚧 Linux support (planned)
- 🚧 Auto-updates (planned)

## 🔗 Links

- [User Guide](USER_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Issue Tracker](https://github.com/yourusername/luxstatus/issues)
- [Releases](https://github.com/yourusername/luxstatus/releases)

---

Made with ❤️ for better workplace communication