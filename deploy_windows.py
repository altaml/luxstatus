#!/usr/bin/env python3
"""
Windows Deployment Script for Microphone Status Monitor
Creates a standalone executable and installer
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_windows_executable():
    """Create a Windows executable using PyInstaller"""
    print("Building Windows Executable...")
    print("=" * 60)
    
    # Install PyInstaller if needed
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Create spec file for PyInstaller
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['secure_mic_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('mic_monitor', 'mic_monitor'),
    ],
    hiddenimports=[
        'mic_monitor',
        'mic_monitor.platform',
        'mic_monitor.platform.windows',
        'mic_monitor.platform.windows_audio_api',
        'mic_monitor.devices',
        'mic_monitor.devices.luxafor',
        'mic_monitor.status_manager',
        'pystray',
        'PIL',
        'psutil',
        'luxafor',
        'pyusb',
        'usb',
        'usb.core',
        'usb.util',
        'usb.backend',
        'usb.backend.libusb1',
        'usb.backend.libusb0',
        'usb.backend.openusb',
        'flask',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MicrophoneStatusMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='mic_icon.ico' if os.path.exists('mic_icon.ico') else None
)
'''
    
    # Write spec file
    with open('mic_monitor.spec', 'w') as f:
        f.write(spec_content)
    
    # Create icon if it doesn't exist
    if not os.path.exists('mic_icon.ico'):
        create_icon()
    
    # Build executable
    print("\nBuilding executable with PyInstaller...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "mic_monitor.spec", "--clean"], check=True)
    
    print("\nExecutable created in: dist/MicrophoneStatusMonitor.exe")
    
    # Copy executable to root for easier installer access
    import shutil
    try:
        shutil.copy2("dist/MicrophoneStatusMonitor.exe", "MicrophoneStatusMonitor.exe")
        print("Copied executable to root directory for installer")
    except Exception as e:
        print(f"Warning: Could not copy to root directory: {e}")
    
    return "dist/MicrophoneStatusMonitor.exe"

def create_icon():
    """Create a simple icon for the application"""
    try:
        from PIL import Image, ImageDraw
        
        # Create icon
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw microphone shape
        draw.ellipse([80, 60, 176, 140], fill=(70, 70, 70))
        draw.rectangle([120, 140, 136, 180], fill=(70, 70, 70))
        draw.rectangle([100, 180, 156, 196], fill=(70, 70, 70))
        
        # Add status indicator
        draw.ellipse([160, 60, 196, 96], fill=(0, 255, 0))
        
        # Save as ICO
        img.save('mic_icon.ico', format='ICO')
        print("Created application icon")
    except Exception as e:
        print(f"Warning: Could not create icon: {e}")

def create_installer():
    """Create an installer using NSIS or Inno Setup"""
    print("\nCreating Windows Installer...")
    print("=" * 60)
    
    # Create Inno Setup script (using raw string to avoid unicode escape issues)
    inno_script = r'''
[Setup]
AppName=Microphone Status Monitor
AppVersion=2.0
AppPublisher=AltaML
AppPublisherURL=https://github.com/altaml/luxstatus
DefaultDirName={commonappdata}\AltaML\MicrophoneStatusMonitor
DefaultGroupName=Microphone Status Monitor
UninstallDisplayIcon={app}\MicrophoneStatusMonitor.exe
OutputDir=installer
OutputBaseFilename=MicrophoneStatusMonitor_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\MicrophoneStatusMonitor.exe"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\Microphone Status Monitor"; Filename: "{app}\MicrophoneStatusMonitor.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Microphone Status Monitor"; Filename: "{app}\MicrophoneStatusMonitor.exe"
Name: "{userstartup}\Microphone Status Monitor"; Filename: "{app}\MicrophoneStatusMonitor.exe"

[Run]
Filename: "{app}\MicrophoneStatusMonitor.exe"; Description: "Launch Microphone Status Monitor"; Flags: nowait postinstall skipifsilent
'''
    
    # Write Inno Setup script
    with open('installer.iss', 'w') as f:
        f.write(inno_script)
    
    print("Created Inno Setup script: installer.iss")
    print("\nTo create the installer:")
    print("1. Download Inno Setup from: https://jrsoftware.org/isdl.php")
    print("2. Open installer.iss in Inno Setup")
    print("3. Click 'Compile' to create the installer")
    
    # Alternative: Create a simple batch installer
    create_batch_installer()

def create_batch_installer():
    """Create a simple batch file installer"""
    batch_content = r'''@echo off
title Microphone Status Monitor - Installation
echo ===============================================
echo   Microphone Status Monitor Installation
echo ===============================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

:: Set installation directory (use ProgramData for system-wide access)
set "INSTALL_DIR=%ProgramData%\AltaML\MicrophoneStatusMonitor"

echo Installing to: %INSTALL_DIR%
echo.

:: Create directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy files
echo Copying files...

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

:: Check if the executable exists in the script directory first
if exist "%SCRIPT_DIR%MicrophoneStatusMonitor.exe" (
    copy /Y "%SCRIPT_DIR%MicrophoneStatusMonitor.exe" "%INSTALL_DIR%\" >nul
    echo Copied MicrophoneStatusMonitor.exe from script directory
) else if exist "%SCRIPT_DIR%dist\MicrophoneStatusMonitor.exe" (
    copy /Y "%SCRIPT_DIR%dist\MicrophoneStatusMonitor.exe" "%INSTALL_DIR%\" >nul
    echo Copied MicrophoneStatusMonitor.exe from dist directory
) else (
    echo ERROR: MicrophoneStatusMonitor.exe not found!
    echo Checked: %SCRIPT_DIR%MicrophoneStatusMonitor.exe
    echo Checked: %SCRIPT_DIR%dist\MicrophoneStatusMonitor.exe
    echo Please ensure the executable is available.
    pause
    exit /b 1
)

if exist "%SCRIPT_DIR%README.md" (
    copy /Y "%SCRIPT_DIR%README.md" "%INSTALL_DIR%\" >nul
)

:: Create start menu shortcut
echo Creating shortcuts...
set "STARTMENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\Microphone Status Monitor"
if not exist "%STARTMENU%" mkdir "%STARTMENU%"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\Microphone Status Monitor.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MicrophoneStatusMonitor.exe'; $Shortcut.Save()"

:: Create desktop shortcut
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Microphone Status Monitor.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MicrophoneStatusMonitor.exe'; $Shortcut.Save()"

:: Add to startup (optional)
echo.
set /p STARTUP="Add to Windows startup? (Y/N): "
if /i "%STARTUP%"=="Y" (
    :: Create a shortcut in startup folder instead of copying the exe
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Microphone Status Monitor.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MicrophoneStatusMonitor.exe'; $Shortcut.Save()"
    echo Added to startup.
)

echo.
echo ===============================================
echo   Installation Complete!
echo ===============================================
echo.
echo The application has been installed to:
echo   %INSTALL_DIR%
echo.
echo Shortcuts have been created on your Desktop
echo and in the Start Menu.
echo.

set /p RUN="Would you like to start the application now? (Y/N): "
if /i "%RUN%"=="Y" (
    start "" "%INSTALL_DIR%\MicrophoneStatusMonitor.exe"
)

pause
'''
    
    with open('install_windows.bat', 'w') as f:
        f.write(batch_content)
    
    print("\nCreated batch installer: install_windows.bat")

def create_uninstaller():
    """Create an uninstaller batch file"""
    uninstall_content = r'''@echo off
title Microphone Status Monitor - Uninstall
echo ===============================================
echo   Microphone Status Monitor Uninstallation
echo ===============================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This uninstaller requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramData%\AltaML\MicrophoneStatusMonitor"

echo This will uninstall Microphone Status Monitor.
echo.
set /p CONFIRM="Are you sure? (Y/N): "
if /i not "%CONFIRM%"=="Y" exit /b 0

:: Kill running process
echo Stopping application...
taskkill /F /IM MicrophoneStatusMonitor.exe >nul 2>&1

:: Remove from startup
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Microphone Status Monitor.lnk" >nul 2>&1

:: Remove shortcuts
echo Removing shortcuts...
del "%USERPROFILE%\Desktop\Microphone Status Monitor.lnk" >nul 2>&1
rmdir /S /Q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Microphone Status Monitor" >nul 2>&1

:: Remove installation directory
echo Removing program files...
rmdir /S /Q "%INSTALL_DIR%" >nul 2>&1

echo.
echo ===============================================
echo   Uninstallation Complete!
echo ===============================================
echo.
pause
'''
    
    with open('uninstall_windows.bat', 'w') as f:
        f.write(uninstall_content)
    
    print("Created uninstaller: uninstall_windows.bat")

def main():
    """Main deployment function"""
    print("Windows Deployment Tool")
    print("=" * 60)
    
    # Check if we're on Windows
    if sys.platform != 'win32':
        print("ERROR: This script must be run on Windows!")
        sys.exit(1)
    
    # Install dependencies
    print("\nInstalling dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
    
    # Create executable
    exe_path = create_windows_executable()
    
    # Create installer files
    create_installer()
    create_uninstaller()
    
    print("\n" + "=" * 60)
    print("Deployment package created successfully!")
    print("\nDeployment artifacts:")
    print(f"  - Executable: {exe_path}")
    print("  - Batch Installer: install_windows.bat")
    print("  - Batch Uninstaller: uninstall_windows.bat")
    print("  - Inno Setup Script: installer.iss")
    print("\nNext steps:")
    print("1. Test the executable: dist/MicrophoneStatusMonitor.exe")
    print("2. Run installer as Administrator: install_windows.bat")
    print("3. Or create professional installer with Inno Setup")

if __name__ == "__main__":
    main()
