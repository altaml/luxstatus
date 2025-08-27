#!/usr/bin/env python3
"""
macOS Deployment Script for Microphone Status Monitor
Creates a standalone app bundle and installer
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_macos_app():
    """Create a macOS app bundle using py2app"""
    print("🍎 Building macOS Application...")
    print("=" * 60)
    
    # Install py2app if needed
    print("📦 Installing py2app...")
    subprocess.run([sys.executable, "-m", "pip", "install", "py2app"], check=True)
    
    # Create setup_mac.py for py2app
    setup_content = '''
from setuptools import setup
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

APP = ['secure_mic_monitor.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'mic_monitor',
        'pystray',
        'PIL',
        'psutil',
        'tkinter',
    ],
    'includes': [
        'mic_monitor.platform.macos',
        'mic_monitor.devices.luxafor', 
        'mic_monitor.status_manager',
        'threading',
        'time',
        'logging',
        'datetime',
        'subprocess',
        'json',
        'os',
        'sys'
    ],
    'excludes': [
        'flask',
        'jinja2',
        'werkzeug',
        'click',
        'itsdangerous',
        'markupsafe'
    ],
    'resources': [],
    'plist': {
        'CFBundleName': 'Microphone Status Monitor',
        'CFBundleDisplayName': 'Microphone Status Monitor', 
        'CFBundleIdentifier': 'com.altaml.micmonitor',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'LSUIElement': True,
        'NSMicrophoneUsageDescription': 'This app monitors microphone usage to display your availability status.',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0'
    },
    'iconfile': None,
    'strip': True,
    'optimize': 2
}

setup(
    name='Microphone Status Monitor',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
'''
    
    with open('setup_mac.py', 'w') as f:
        f.write(setup_content)
    
    # Build the app
    print("\n🚀 Building app bundle with py2app...")
    try:
        # Run py2app with verbose output for debugging
        result = subprocess.run([sys.executable, "setup_mac.py", "py2app", "--verbose"], 
                              capture_output=True, text=True, check=True)
        print("Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        
        # Try a simpler build without optional dependencies
        print("\nTrying simplified build...")
        simple_setup = '''
from setuptools import setup

APP = ['secure_mic_monitor.py']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['mic_monitor'],
    'plist': {
        'CFBundleName': 'Microphone Status Monitor',
        'CFBundleIdentifier': 'com.altaml.micmonitor',
        'LSUIElement': True,
    }
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
'''
        with open('setup_mac_simple.py', 'w') as f:
            f.write(simple_setup)
        
        subprocess.run([sys.executable, "setup_mac_simple.py", "py2app"], check=True)
    
    print("\n✅ App bundle created in: dist/Microphone Status Monitor.app")
    return "dist/Microphone Status Monitor.app"

def create_dmg():
    """Create a DMG installer for easy distribution"""
    print("\n💿 Creating DMG installer...")
    print("=" * 60)
    
    dmg_script = '''#!/bin/bash
# Create DMG installer for macOS app

APP_NAME="Microphone Status Monitor"
DMG_NAME="MicrophoneStatusMonitor"
DMG_FILE="${DMG_NAME}.dmg"
VOLUME_NAME="${APP_NAME}"
SOURCE_FOLDER="dist"

# Create a temporary disk image
echo "Creating temporary disk image..."
hdiutil create -srcfolder "${SOURCE_FOLDER}" -volname "${VOLUME_NAME}" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size 100m temp.dmg

# Mount the disk image
echo "Mounting disk image..."
device=$(hdiutil attach -readwrite -noverify -noautoopen temp.dmg | \
    egrep '^/dev/' | sed 1q | awk '{print $1}')

# Create background and setup
echo "Setting up disk image..."
mkdir "/Volumes/${VOLUME_NAME}/.background"

# Create symbolic link to Applications folder
ln -s /Applications "/Volumes/${VOLUME_NAME}/Applications"

# Set custom icon positions and window settings using AppleScript
echo '
tell application "Finder"
    tell disk "'${VOLUME_NAME}'"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 885, 430}
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 72
        set position of item "'${APP_NAME}'.app" of container window to {100, 100}
        set position of item "Applications" of container window to {375, 100}
        update without registering applications
        delay 5
        close
    end tell
end tell
' | osascript

# Unmount the disk image
echo "Finalizing disk image..."
hdiutil detach ${device}

# Convert to compressed DMG
echo "Compressing disk image..."
hdiutil convert temp.dmg -format UDZO -imagekey zlib-level=9 -o "${DMG_FILE}"
rm temp.dmg

echo "✅ DMG created: ${DMG_FILE}"
'''
    
    with open('create_dmg.sh', 'w') as f:
        f.write(dmg_script)
    
    os.chmod('create_dmg.sh', 0o755)
    print("✅ Created DMG creation script: create_dmg.sh")
    print("Run './create_dmg.sh' to create the DMG installer")

def create_launch_agent():
    """Create a launch agent for auto-start on login"""
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourcompany.micmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Microphone Status Monitor.app/Contents/MacOS/Microphone Status Monitor</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardErrorPath</key>
    <string>/tmp/micmonitor.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/micmonitor.out</string>
</dict>
</plist>
'''
    
    with open('com.yourcompany.micmonitor.plist', 'w') as f:
        f.write(plist_content)
    
    print("✅ Created launch agent: com.yourcompany.micmonitor.plist")
    print("To install: cp com.yourcompany.micmonitor.plist ~/Library/LaunchAgents/")
    print("Then: launchctl load ~/Library/LaunchAgents/com.yourcompany.micmonitor.plist")

def create_installer_script():
    """Create an installation script for macOS"""
    install_script = '''#!/bin/bash
# macOS Installation Script for Microphone Status Monitor

echo "======================================"
echo "  Microphone Status Monitor Installer"
echo "======================================"
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS only!"
    exit 1
fi

# Set installation paths
APP_NAME="Microphone Status Monitor"
APP_SOURCE="dist/${APP_NAME}.app"
APP_DEST="/Applications/${APP_NAME}.app"
LAUNCH_AGENT_SOURCE="com.yourcompany.micmonitor.plist"
LAUNCH_AGENT_DEST="$HOME/Library/LaunchAgents/com.yourcompany.micmonitor.plist"

# Check if app exists
if [ ! -d "$APP_SOURCE" ]; then
    echo "❌ App bundle not found. Please run deploy_macos.py first."
    exit 1
fi

# Install application
echo "📦 Installing application..."
if [ -d "$APP_DEST" ]; then
    echo "Removing previous installation..."
    rm -rf "$APP_DEST"
fi

cp -R "$APP_SOURCE" "$APP_DEST"
echo "✅ Application installed to /Applications"

# Install launch agent for auto-start
echo
read -p "Would you like to start the app automatically at login? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$HOME/Library/LaunchAgents"
    
    # Copy launch agent
    cp "$LAUNCH_AGENT_SOURCE" "$LAUNCH_AGENT_DEST"
    
    # Load launch agent
    launchctl load "$LAUNCH_AGENT_DEST" 2>/dev/null
    echo "✅ Auto-start enabled"
fi

# Request microphone permission
echo
echo "📱 The app needs microphone access permission."
echo "You'll be prompted to grant permission when you first run it."

# Start the application
echo
read -p "Would you like to start the application now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "$APP_DEST"
    echo "✅ Application started"
fi

echo
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo
echo "The application has been installed to:"
echo "  $APP_DEST"
echo
echo "You can find it in your Applications folder"
echo "or launch it from Spotlight."
'''
    
    with open('install_macos.sh', 'w') as f:
        f.write(install_script)
    
    os.chmod('install_macos.sh', 0o755)
    print("✅ Created installer script: install_macos.sh")

def create_uninstaller_script():
    """Create an uninstallation script for macOS"""
    uninstall_script = '''#!/bin/bash
# macOS Uninstallation Script for Microphone Status Monitor

echo "======================================"
echo "  Microphone Status Monitor Uninstaller"
echo "======================================"
echo

APP_NAME="Microphone Status Monitor"
APP_PATH="/Applications/${APP_NAME}.app"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.yourcompany.micmonitor.plist"

echo "This will uninstall Microphone Status Monitor."
read -p "Are you sure? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# Stop the application
echo "🛑 Stopping application..."
osascript -e 'quit app "Microphone Status Monitor"' 2>/dev/null
pkill -f "Microphone Status Monitor" 2>/dev/null

# Remove launch agent
if [ -f "$LAUNCH_AGENT" ]; then
    echo "🗑 Removing auto-start..."
    launchctl unload "$LAUNCH_AGENT" 2>/dev/null
    rm "$LAUNCH_AGENT"
fi

# Remove application
if [ -d "$APP_PATH" ]; then
    echo "🗑 Removing application..."
    rm -rf "$APP_PATH"
fi

# Remove preferences
PREFS="$HOME/Library/Preferences/com.yourcompany.micmonitor.plist"
if [ -f "$PREFS" ]; then
    echo "🗑 Removing preferences..."
    rm "$PREFS"
fi

echo
echo "======================================"
echo "  Uninstallation Complete!"
echo "======================================"
echo
'''
    
    with open('uninstall_macos.sh', 'w') as f:
        f.write(uninstall_script)
    
    os.chmod('uninstall_macos.sh', 0o755)
    print("✅ Created uninstaller script: uninstall_macos.sh")

def main():
    """Main deployment function"""
    print("🍎 macOS Deployment Tool")
    print("=" * 60)
    
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("⚠️ Warning: This script is intended for macOS!")
        print("You're running it on:", sys.platform)
        print("The scripts will be created but building will fail on non-macOS systems.")
        print()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "pyobjc"], check=True)
    
    if sys.platform == 'darwin':
        # Create app bundle
        app_path = create_macos_app()
    else:
        print("⚠️ Skipping app bundle creation (not on macOS)")
    
    # Create installer files
    create_dmg()
    create_launch_agent()
    create_installer_script()
    create_uninstaller_script()
    
    print("\n" + "=" * 60)
    print("✅ Deployment package created successfully!")
    print("\nDeployment artifacts:")
    if sys.platform == 'darwin':
        print("  • App Bundle: dist/Microphone Status Monitor.app")
    print("  • DMG Script: create_dmg.sh")
    print("  • Installer: install_macos.sh")
    print("  • Uninstaller: uninstall_macos.sh")
    print("  • Launch Agent: com.yourcompany.micmonitor.plist")
    print("\nNext steps:")
    if sys.platform == 'darwin':
        print("1. Test the app: open 'dist/Microphone Status Monitor.app'")
        print("2. Create DMG: ./create_dmg.sh")
        print("3. Install: ./install_macos.sh")
    else:
        print("1. Copy these files to a macOS system")
        print("2. Run deploy_macos.py on macOS to build the app")
        print("3. Use the installer scripts for deployment")

if __name__ == "__main__":
    main()
