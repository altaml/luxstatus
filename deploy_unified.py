#!/usr/bin/env python3
"""
Unified Deployment Script - Works on both Windows and macOS
Builds what's possible on the current platform and provides instructions for the other
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def detect_platform():
    """Detect current platform"""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'

def create_github_actions():
    """Create GitHub Actions workflow for automated builds"""
    workflow_content = '''name: Build Multi-Platform Releases

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        
    - name: Build Windows executable
      run: python deploy_windows.py
      
    - name: Upload Windows artifacts
      uses: actions/upload-artifact@v3
      with:
        name: windows-release
        path: |
          dist/MicrophoneStatusMonitor.exe
          install_windows.bat
          uninstall_windows.bat
          installer.iss

  build-macos:
    runs-on: macos-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python3 -m pip install --upgrade pip
        pip3 install -r requirements.txt
        pip3 install py2app pyobjc
        
    - name: Build macOS app
      run: python3 deploy_macos.py
      
    - name: Create DMG
      run: ./create_dmg.sh
      
    - name: Upload macOS artifacts
      uses: actions/upload-artifact@v3
      with:
        name: macos-release
        path: |
          dist/Microphone Status Monitor.app
          MicrophoneStatusMonitor.dmg
          install_macos.sh
          uninstall_macos.sh

  create-release:
    needs: [build-windows, build-macos]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    steps:
    - name: Download Windows artifacts
      uses: actions/download-artifact@v3
      with:
        name: windows-release
        path: windows/
        
    - name: Download macOS artifacts
      uses: actions/download-artifact@v3
      with:
        name: macos-release
        path: macos/
        
    - name: Create Release
      uses: ncipollo/release-action@v1
      with:
        artifacts: "windows/*,macos/*"
        token: ${{ secrets.GITHUB_TOKEN }}
'''

    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/build.yml', 'w') as f:
        f.write(workflow_content)
    
    print("✅ Created GitHub Actions workflow: .github/workflows/build.yml")

def create_docker_build():
    """Create Docker-based build with macOS container option"""
    
    # Standard Dockerfile for Linux/Windows builds
    dockerfile_content = '''# Multi-stage build for cross-platform compilation
FROM python:3.9-slim as base

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Windows build stage (using Wine - experimental)
FROM base as windows-build
RUN apt-get update && apt-get install -y wine
COPY . .
# Note: This is experimental and may not work reliably
RUN python deploy_windows.py

# Linux build stage
FROM base as linux-build
COPY . .
RUN python deploy_linux.py
'''

    # macOS Docker build (only legal on Apple hardware)
    dockerfile_macos_content = '''# macOS Docker Build
# WARNING: This only works legally on Apple hardware!
# Apple's Software License Agreement restricts macOS to Apple hardware

FROM sickcodes/docker-osx:monterey as macos-build

# Install Python and dependencies
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN brew install python@3.9

# Copy source code
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install py2app pyobjc

# Build macOS app
RUN python3 deploy_macos.py

# Extract built app
VOLUME ["/output"]
CMD cp -r "dist/Microphone Status Monitor.app" /output/
'''

    # Docker Compose for orchestrated builds
    docker_compose_content = '''version: '3.8'

services:
  # Linux build (always works)
  linux-build:
    build:
      context: .
      target: linux-build
    volumes:
      - ./dist/linux:/output
    platform: linux/amd64

  # Windows build (experimental with Wine)
  windows-build:
    build:
      context: .
      target: windows-build
    volumes:
      - ./dist/windows:/output
    platform: linux/amd64

  # macOS build (only legal on Apple hardware!)
  macos-build:
    build:
      dockerfile: Dockerfile.macos
      context: .
    volumes:
      - ./dist/macos:/output
    platform: linux/amd64
    # Uncomment only if running on Apple hardware:
    # privileged: true
    # devices:
    #   - /dev/kvm
    environment:
      - DISPLAY=:99
    # Only enable if you have legal rights to run macOS
    profiles:
      - apple-hardware-only
'''

    # Build script for Docker approach
    build_script = '''#!/bin/bash
# Docker-based multi-platform build script

echo "🐳 Docker Multi-Platform Build"
echo "================================"

# Check if running on Apple hardware
if [[ $(uname -m) == "arm64" ]] && [[ $(uname -s) == "Darwin" ]]; then
    echo "✅ Apple Silicon Mac detected - macOS build is legal"
    ENABLE_MACOS="--profile apple-hardware-only"
else
    echo "⚠️  Non-Apple hardware - macOS build disabled (legal restriction)"
    ENABLE_MACOS=""
fi

# Build for available platforms
echo "Building Linux version..."
docker-compose build linux-build
docker-compose run --rm linux-build

echo "Building Windows version (experimental)..."
docker-compose build windows-build
docker-compose run --rm windows-build

if [[ -n "$ENABLE_MACOS" ]]; then
    echo "Building macOS version..."
    docker-compose $ENABLE_MACOS build macos-build
    docker-compose $ENABLE_MACOS run --rm macos-build
else
    echo "Skipping macOS build (not on Apple hardware)"
fi

echo "✅ Docker builds complete!"
echo "Check dist/ directory for results"
'''

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    with open('Dockerfile.macos', 'w') as f:
        f.write(dockerfile_macos_content)
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)
    
    with open('docker-build.sh', 'w') as f:
        f.write(build_script)
    
    os.chmod('docker-build.sh', 0o755)
    
    print("✅ Created Docker build files:")
    print("   • Dockerfile - Linux/Windows builds")
    print("   • Dockerfile.macos - macOS build (Apple hardware only)")
    print("   • docker-compose.yml - Orchestrated builds")
    print("   • docker-build.sh - Build script")

def prepare_cross_platform_files():
    """Prepare files that work on both platforms"""
    
    # Update requirements to include platform-specific packages
    requirements_content = '''# Core requirements
flask==2.0.3
appdirs==1.4.4
pystray==0.19.4
pillow>=9.5.0
requests==2.31.0
pyusb==1.2.1

# Luxafor flag integration
git+https://github.com/fmartingr/pyluxafor.git#egg=luxafor

# Platform-specific requirements
psutil>=5.8.0

# Windows-specific
pywin32>=227; sys_platform == "win32"

# macOS-specific  
pyobjc>=7.0; sys_platform == "darwin"
py2app>=0.26; sys_platform == "darwin"

# Build tools
pyinstaller>=4.0; sys_platform == "win32"
'''

    with open('requirements-full.txt', 'w') as f:
        f.write(requirements_content)
    
    print("✅ Created requirements-full.txt with platform-specific dependencies")

def main():
    """Main unified deployment function"""
    current_platform = detect_platform()
    
    print("🚀 Unified Cross-Platform Deployment Tool")
    print("=" * 60)
    print(f"Current platform: {current_platform}")
    print(f"Python: {sys.version}")
    print(f"Architecture: {platform.machine()}")
    print()
    
    # Prepare cross-platform files
    prepare_cross_platform_files()
    create_github_actions()
    create_docker_build()
    
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT OPTIONS")
    print("=" * 60)
    
    if current_platform == 'windows':
        print("✅ You can build WINDOWS version on this machine:")
        print("   python deploy_windows.py")
        print()
        print("❌ You CANNOT build macOS version on Windows")
        print("   Options for macOS build:")
        print("   1. Use GitHub Actions (recommended)")
        print("   2. Access a Mac computer/VM")
        print("   3. Use cloud macOS service")
        
    elif current_platform == 'macos':
        print("✅ You can build MACOS version on this machine:")
        print("   python3 deploy_macos.py")
        print()
        print("❌ You CANNOT build Windows version on macOS")
        print("   Options for Windows build:")
        print("   1. Use GitHub Actions (recommended)")
        print("   2. Access a Windows computer/VM")
        print("   3. Use cloud Windows service")
        
    else:
        print("⚠️ Linux platform detected")
        print("   Neither Windows nor macOS builds are native")
        print("   Use GitHub Actions for both platforms")
    
    print()
    print("🌟 RECOMMENDED APPROACH:")
    print("   1. Push code to GitHub")
    print("   2. Create a release tag: git tag v1.0.0")
    print("   3. Push tag: git push origin v1.0.0") 
    print("   4. GitHub Actions will build both platforms automatically")
    print("   5. Download artifacts from GitHub Actions/Releases")
    
    print()
    print("📁 Files created:")
    print("   • .github/workflows/build.yml - GitHub Actions workflow")
    print("   • requirements-full.txt - Platform-specific dependencies")
    print("   • Dockerfile - Experimental cross-platform build")
    
    # Try to build for current platform
    print()
    choice = input(f"Build for {current_platform} now? (y/n): ").lower()
    if choice == 'y':
        if current_platform == 'windows':
            print("\n🔨 Building Windows version...")
            subprocess.run([sys.executable, 'deploy_windows.py'])
        elif current_platform == 'macos':
            print("\n🔨 Building macOS version...")
            subprocess.run([sys.executable, 'deploy_macos.py'])
        else:
            print("❌ No native build available for this platform")

if __name__ == "__main__":
    main()
