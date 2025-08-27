import argparse
import sys
import os
import subprocess
import venv
import logging
from pathlib import Path

def create_luxafor_env():
    """Create Luxafor virtual environment and install dependencies"""
    venv_path = Path('luxafor_env')
    if not venv_path.exists():
        print("Creating Luxafor virtual environment...")
        venv.create(venv_path, with_pip=True)
        
        # Install Luxafor dependencies
        pip = venv_path / 'Scripts' / 'pip.exe'
        subprocess.run([str(pip), 'install', '-r', 'luxafor_requirements.txt'], check=True)
    return venv_path

def setup_environments(args):
    """Set up virtual environments and install dependencies"""
    # Main environment is already set up through pip install
    print("Setting up Luxafor environment...")
    try:
        create_luxafor_env()
        print("Setup complete!")
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

def run_monitor(args):
    """Run the microphone monitor"""
    from . import run_mic_monitor
    run_mic_monitor.main()

def main():
    parser = argparse.ArgumentParser(description="Microphone Monitor CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up virtual environments')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the microphone monitor')

    args = parser.parse_args()

    if args.command == 'setup':
        setup_environments(args)
    elif args.command == 'run':
        run_monitor(args)
    else:
        # Default to run if no command specified
        run_monitor(args) 