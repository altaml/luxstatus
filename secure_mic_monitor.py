#!/usr/bin/env python3
"""
🎤 Secure Microphone Status Monitor
A unified, port-free application for monitoring microphone usage with Luxafor integration
"""

import os
import sys
import time
import json
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, List
import pystray
from PIL import Image, ImageDraw

# Add mic_monitor to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mic_monitor'))

# Import platform-specific monitor
if sys.platform == 'win32':
    from mic_monitor.platform.windows import WindowsMicrophoneMonitor as MicrophoneMonitor
elif sys.platform == 'darwin':
    from mic_monitor.platform.macos import MacOSMicrophoneMonitor as MicrophoneMonitor
else:
    # Linux or other platforms
    logging.warning(f"Platform {sys.platform} not fully supported yet")
    from mic_monitor.platform.windows import WindowsMicrophoneMonitor as MicrophoneMonitor

from mic_monitor.status_manager import StatusManager

class StatusWidget:
    """Desktop widget showing detailed status information"""
    
    def __init__(self, status_monitor):
        self.status_monitor = status_monitor
        self.window = None
        self.is_visible = False
        
    def create_window(self):
        """Create the status widget window"""
        if self.window:
            self.show()
            return
            
        self.window = tk.Toplevel()
        self.window.title("🎤 Microphone Status")
        self.window.geometry("400x300")
        self.window.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status display
        self.status_label = ttk.Label(main_frame, text="🟢 Available", font=('Segoe UI', 14, 'bold'))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10")
        details_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.details_text = tk.Text(details_frame, height=8, width=45, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=scrollbar.set)
        
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="🟢 Available", command=lambda: self.set_status('available')).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="🔵 Do Not Disturb", command=lambda: self.set_status('busy')).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🟡 Away (1hr)", command=lambda: self.set_status('away')).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="🤖 Auto Mode", command=lambda: self.set_status('auto')).grid(row=0, column=3, padx=5)
        
        # Close button
        ttk.Button(main_frame, text="Close Widget", command=self.hide).grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Start updating
        self.update_display()
        
    def show(self):
        """Show the status widget"""
        if not self.window:
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()
            self.window.focus()
            
    def hide(self):
        """Hide the status widget"""
        if self.window:
            self.window.withdraw()
            
    def set_status(self, status_type):
        """Set status from widget buttons"""
        if status_type == 'available':
            self.status_monitor.set_available()
        elif status_type == 'busy':
            self.status_monitor.set_do_not_disturb()
        elif status_type == 'away':
            self.status_monitor.set_away_for(60)  # 1 hour
        elif status_type == 'auto':
            self.status_monitor.return_to_auto()
            
    def update_display(self):
        """Update widget display"""
        if not self.window:
            return
            
        status = self.status_monitor.get_full_status()
        
        # Update status text
        status_text = self._get_status_text(status)
        self.status_label.configure(text=status_text)
        
        # Update details
        details = self._format_details(status)
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', details)
        
        # Schedule next update
        self.window.after(1000, self.update_display)
        
    def _get_status_text(self, status):
        """Get friendly status text"""
        if status.get('ignore_until'):
            remaining = status['ignore_until'] - datetime.now()
            minutes = max(0, int(remaining.total_seconds() / 60))
            return f"🟡 Away ({minutes}m left)"
        elif status.get('manual_busy'):
            return "🔵 Do Not Disturb"
        elif status.get('manual_free'):
            return "🟢 Available"
        elif status.get('mic_in_use'):
            return "🔴 In Meeting"
        else:
            return "🟢 Available"
            
    def _format_details(self, status):
        """Format detailed status information"""
        lines = []
        
        # Show override status
        if status.get('ignore_until'):
            remaining = status['ignore_until'] - datetime.now()
            minutes = max(0, int(remaining.total_seconds() / 60))
            lines.append(f"🟡 Away Mode active")
            lines.append(f"Will return to Auto Mode in {minutes} minutes")
            
        elif status.get('manual_busy'):
            lines.append("🔵 Do Not Disturb Mode active")
            lines.append("Manually set to busy")
            
        elif status.get('manual_free'):
            lines.append("🟢 Available Mode active")
            lines.append("Manually set to available")
            
        else:
            lines.append("🤖 Auto Mode active")
            lines.append("Following microphone status")
            
        # Show microphone status
        if status.get('mic_in_use'):
            apps = status.get('using_apps', [])
            if apps:
                lines.append(f"\nMicrophone in use by:")
                for app in apps:
                    lines.append(f"  • {app}")
            else:
                lines.append("\nMicrophone in use")
        else:
            lines.append("\nMicrophone not in use")
            
        # Show Luxafor status if available
        luxafor = status.get('luxafor', {})
        if luxafor:
            lines.append("\nLuxafor Flag:")
            if luxafor.get('connected'):
                color = luxafor.get('last_color', [])
                if color:
                    lines.append(f"  • {self._get_color_name(color)}")
            else:
                lines.append("  • Not connected")
                
        return "\n".join(lines)
        
    def _get_color_name(self, color):
        """Get friendly color name"""
        r, g, b = color
        if r == 255 and g == 0 and b == 0:
            return "🔴 Red (In Meeting)"
        elif r == 0 and g == 255 and b == 0:
            return "🟢 Green (Available)"
        elif r == 255 and g == 255 and b == 0:
            return "🟡 Yellow (Away)"
        elif r == 0 and g == 0 and b == 255:
            return "🔵 Blue (Do Not Disturb)"
        elif r == 0 and g == 0 and b == 0:
            return "⚫ Off"
        else:
            return f"RGB({r}, {g}, {b})"

class SecureMicrophoneMonitor:
    """Main application - secure microphone monitor with no open ports"""
    
    def __init__(self):
        self.mic_monitor = MicrophoneMonitor()
        self.status_manager = StatusManager()
        self.status_widget = StatusWidget(self)
        self.current_status = "🟢 Available"
        self.icon = None
        self.running = True
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def get_full_status(self):
        """Get complete status information"""
        mic_status = self.mic_monitor.get_status()
        return {
            'mic_in_use': mic_status['in_use'],
            'using_apps': mic_status['using_apps'],
            'manual_busy': self.status_manager.manual_busy,
            'manual_free': self.status_manager.manual_free,
            'ignore_until': self.status_manager.ignore_until,
            'luxafor': self.status_manager.get_device_status()[0] if self.status_manager.get_device_status() else {}
        }
        
    def set_manual_status(self, is_busy: bool):
        """Set manual status"""
        self.status_manager.set_manual_status(is_busy)
        # Update devices immediately
        self.status_manager.update_status(False)  # mic_in_use will be overridden by manual status
        
    def set_away_for(self, minutes: int):
        """Set away status"""
        self.status_manager.ignore_mic_for(minutes)
        # Update devices immediately
        self.status_manager.update_status(False)
        
    def set_away_permanently(self):
        """Set away status until manually changed"""
        # Set ignore for a very long time (10 years = effectively permanent)
        self.status_manager.ignore_mic_for(10 * 365 * 24 * 60)  # 10 years in minutes
        # Update devices immediately
        self.status_manager.update_status(False)
        print("🟡 Set to Away")
        
    def clear_override(self):
        """Clear all overrides"""
        self.status_manager.clear_override()
        # Update devices immediately
        self.status_manager.update_status(False)
        
    def create_icon_image(self):
        """Create system tray icon with status indicator"""
        # Create base icon
        image = Image.new('RGB', (64, 64), color=(245, 245, 245))
        draw = ImageDraw.Draw(image)
        
        # Draw microphone shape
        draw.ellipse([20, 15, 44, 35], fill=(100, 100, 100))
        draw.rectangle([30, 35, 34, 45], fill=(100, 100, 100))
        draw.rectangle([25, 45, 39, 50], fill=(100, 100, 100))
        
        # Add status indicator dot
        status_color = self._get_status_color()
        draw.ellipse([45, 15, 55, 25], fill=status_color)
        
        return image
            
    def _get_status_color(self):
        """Get status indicator color for tray icon"""
        status = self.get_full_status()
        
        if status.get('ignore_until'):
            return (255, 255, 0)  # Yellow - Away
        elif status.get('manual_busy') or status.get('mic_in_use'):
            return (255, 0, 0)    # Red - Do Not Disturb/In Meeting
        elif status.get('manual_free'):
            return (0, 255, 0)    # Green - Available
        else:
            return (0, 255, 0)    # Green - Available
            
    def update_status_text(self):
        """Update status text for tray"""
        status = self.get_full_status()
        
        if status.get('ignore_until'):
            remaining = status['ignore_until'] - datetime.now()
            minutes = max(0, int(remaining.total_seconds() / 60))
            # If more than 24 hours (1440 minutes), treat as permanent
            if minutes > 1440:
                self.current_status = "◐ Away"
            else:
                self.current_status = f"◐ Away ({minutes}m left)"
        elif status.get('manual_busy'):
            self.current_status = "● Do Not Disturb (Busy)"
        elif status.get('manual_free'):
            self.current_status = "○ Available"
        elif status.get('mic_in_use'):
            apps = status.get('using_apps', [])
            app_text = f" • {apps[0]}" if apps else ""
            self.current_status = f"● In Meeting{app_text}"
        else:
            self.current_status = "○ Available"
            
    def create_menu(self):
        """Create enhanced tray menu"""
        status = self.get_full_status()
        
        # Determine current state for checkmarks
        is_auto = not any([
            status.get('manual_busy', False),
            status.get('manual_free', False),
            status.get('ignore_until')
        ])
        is_away = bool(status.get('ignore_until'))
        is_dnd = status.get('manual_busy', False)
        is_available_manual = status.get('manual_free', False)
        is_in_meeting = status.get('mic_in_use', False) and is_auto
        
        menu_items = [
            # === CURRENT STATUS ===
            pystray.MenuItem(f"Status: {self.current_status}", None, enabled=False),
            pystray.MenuItem("Show Status Widget", lambda: self.status_widget.show()),
            pystray.Menu.SEPARATOR,
            
            # === STATUS CONTROLS ===
            pystray.MenuItem(
                "○ Available (Free to Talk)", 
                pystray.Menu(
                    pystray.MenuItem("Until I change it", lambda: self.set_available()),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("30 minutes", lambda: self.set_available(30)),
                    pystray.MenuItem("1 hour", lambda: self.set_available(60)),
                    pystray.MenuItem("2 hours", lambda: self.set_available(120))
                ),
                checked=lambda _: is_available_manual
            ),
            
            pystray.MenuItem(
                "● Do Not Disturb (Busy)", 
                pystray.Menu(
                    pystray.MenuItem("Until I change it", lambda: self.set_do_not_disturb()),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("30 minutes", lambda: self.set_do_not_disturb(30)),
                    pystray.MenuItem("1 hour", lambda: self.set_do_not_disturb(60)),
                    pystray.MenuItem("2 hours", lambda: self.set_do_not_disturb(120))
                ),
                checked=lambda _: is_dnd
            ),
            
            pystray.MenuItem(
                "◐ Away", 
                pystray.Menu(
                    pystray.MenuItem("Until I change it", lambda: self.set_away_permanently()),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("15 minutes", lambda: self.set_away_for(15)),
                    pystray.MenuItem("30 minutes", lambda: self.set_away_for(30)),
                    pystray.MenuItem("1 hour", lambda: self.set_away_for(60)),
                    pystray.MenuItem("2 hours", lambda: self.set_away_for(120))
                ),
                checked=lambda _: is_away
            ),
            
            pystray.Menu.SEPARATOR,
            
            # === AUTO MODE ===
            pystray.MenuItem(
                "○ Auto Mode (follow microphone)", 
                self.return_to_auto,
                checked=lambda _: is_auto
            )
        ]
        
        # Add detected status when in auto mode and mic is active
        if is_in_meeting:
            menu_items.append(
                pystray.MenuItem(
                    "● In Meeting (detected)", 
                    None,
                    enabled=False,
                    checked=lambda _: True
                )
            )
        
        menu_items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Help & Color Guide", self.show_help),
            pystray.MenuItem("About", self.show_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda: self.stop())
        ])
        
        return pystray.Menu(*menu_items)
        
    def set_available(self, minutes=None):
        """Set available status with optional duration"""
        self.set_manual_status(False)
        if minutes:
            # Schedule return to auto
            timer = threading.Timer(minutes * 60, self.return_to_auto)
            timer.daemon = True
            timer.start()
            print(f"👋 Set to Available for {minutes} minutes")
        else:
            print("👋 Set to Available")
        
    def set_do_not_disturb(self, minutes=None):
        """Set do not disturb status with optional duration"""
        self.set_manual_status(True)
        if minutes:
            # Schedule return to auto
            timer = threading.Timer(minutes * 60, self.return_to_auto)
            timer.daemon = True
            timer.start()
            print(f"🔵 Set to Do Not Disturb for {minutes} minutes")
        else:
            print("🔵 Set to Do Not Disturb")
        
    def return_to_auto(self):
        """Return to automatic mode"""
        self.clear_override()
        print("🤖 Returned to Auto Mode")
        
    def show_help(self):
        """Show help information"""
        help_text = """🎤 Microphone Status Monitor - Help

🎯 Status Colors:
🟢 Green = Available (free to talk)
🔴 Red = In Meeting (microphone in use)
🔵 Blue = Do Not Disturb (focused work)
🟡 Yellow = Away (break/offline)

⚡ Quick Actions:
• Right-click tray icon for status menu
• Use "Show Status Widget" for detailed view
• Set timed statuses (auto-return to normal)
• Auto Mode follows your microphone usage

🔧 Luxafor Flag Colors:
The physical flag shows the same colors as above
when connected and enabled.

💡 Tips:
• Manual statuses override microphone detection
• Away mode ignores microphone completely
• Auto mode = smart detection based on mic usage
• All timed statuses return to Auto mode automatically

🔒 Security:
This app uses NO network ports - completely local!
"""
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("🎤 Microphone Monitor - Help", help_text)
            root.destroy()
        except:
            print(help_text)
            
    def show_about(self):
        """Show about information"""
        about_text = """🎤 Microphone Status Monitor v2.0

A secure, local-only application for managing your availability status.

Features:
• Zero open network ports
• Direct hardware integration
• No web server required
• Local-only operation

Made with ❤️ by your friends at PySimpleGUI"""
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("🎤 About", about_text)
            root.destroy()
        except:
            print(about_text)
            
    def update_icon(self):
        """Update system tray icon"""
        self.update_status_text()
        self.icon.icon = self.create_icon_image()
        self.icon.menu = self.create_menu()
        self.icon.title = self.current_status
        
    def monitor_loop(self):
        """Main monitoring loop"""
        last_mic_status = None
        while self.running:
            try:
                # Check microphone status and update devices
                mic_status = self.mic_monitor.get_status()
                
                # Log mic status changes for debugging
                if mic_status['in_use'] != last_mic_status:
                    if mic_status['in_use']:
                        print(f"🎤 Microphone detected in use by: {mic_status['using_apps']}")
                    else:
                        print("🎤 Microphone not in use")
                    last_mic_status = mic_status['in_use']
                
                self.status_manager.update_status(mic_status['in_use'])
                
                # Update icon every second
                self.update_icon()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")
                time.sleep(5)  # Wait longer on error
                
    def run(self):
        """Run the application"""
        # Print startup banner
        print("=" * 60)
        print("🔒 Secure Microphone Status Monitor v2.0")
        print("=" * 60)
        print("Security Features:")
        print("  🔒 Zero open network ports")
        print("  🚀 Direct hardware integration")
        print("  💪 No web server required")
        print("  🎯 Local-only operation")
        print("=" * 60)
        
        print("🔒 Starting Secure Microphone Monitor...")
        print("✅ Zero open ports - maximum security")
        print("🎯 Tray icon should appear shortly")
        
        # Create and start system tray icon
        self.icon = pystray.Icon(
            "MicrophoneMonitor",
            self.create_icon_image(),
            self.current_status,
            self.create_menu()
        )
        
        # Start monitor thread
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run icon (blocks until quit)
        self.icon.run()
        
    def stop(self):
        """Stop the application"""
        self.running = False
        self.icon.stop()

def main():
    monitor = SecureMicrophoneMonitor()
    monitor.run()

if __name__ == '__main__':
    main()