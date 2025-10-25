#!/usr/bin/env python3
"""
BlinkOS - Main Controller (Simplified)
Launches eye tracking and voice control as separate processes
"""

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import os


class BlinkOS:
    """
    Main application controller
    Manages eye tracking and voice control as separate processes
    """
    
    def __init__(self):
        """Initialize BlinkOS"""
        print("Initializing BlinkOS...")
        
        # Process handles
        self.eye_process = None
        self.voice_process = None
        
        # System state
        self.eye_tracking_active = False
        self.voice_control_active = False
        
        # Activity log
        self.activity_log = []
        self.max_log_entries = 100
        
        # Setup GUI
        self.setup_gui()
        
        print("BlinkOS initialized!")
    
    def setup_gui(self):
        """Create the control panel GUI"""
        self.root = tk.Tk()
        self.root.title("BlinkOS - Hands-Free Computer Control")
        self.root.geometry("600x750")
        self.root.resizable(True, True)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # ==================== TITLE ====================
        title_label = tk.Label(
            main_frame,
            text="BlinkOS",
            font=("Arial", 24, "bold"),
            fg="#2c3e50"
        )
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Hands-Free Computer Control System",
            font=("Arial", 12),
            fg="#7f8c8d"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 10))
        
        version_label = tk.Label(
            main_frame,
            text="Hackathon Demo v0.1.0",
            font=("Arial", 9),
            fg="#95a5a6"
        )
        version_label.grid(row=2, column=0, pady=(0, 15))
        
        # ==================== EYE TRACKING SECTION ====================
        eye_frame = ttk.LabelFrame(main_frame, text="Eye Tracking", padding="10")
        eye_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        eye_frame.columnconfigure(0, weight=1)
        
        self.eye_status_label = tk.Label(
            eye_frame,
            text="Inactive",
            font=("Arial", 12, "bold"),
            fg="red"
        )
        self.eye_status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.eye_button = tk.Button(
            eye_frame,
            text="Start Eye Tracking",
            command=self.toggle_eye_tracking,
            width=25,
            height=2,
            bg="#3498db",
            fg="black",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief= tk.RAISED, 
            bd = 3, 
            activebackground="#114e77" ,
            activeforeground="white"
        )
        self.eye_button.grid(row=1, column=0, pady=5)
        
        eye_info = """Control cursor with head movement
Blink to click • Press Q to quit
Opens in separate window"""
        
        self.eye_info_label = tk.Label(
            eye_frame,
            text=eye_info,
            font=("Arial", 9),
            fg="#7f8c8d",
            justify=tk.LEFT
        )
        self.eye_info_label.grid(row=2, column=0, pady=5)
        
        # ==================== VOICE CONTROL SECTION ====================
        voice_frame = ttk.LabelFrame(main_frame, text="Voice Control", padding="10")
        voice_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        voice_frame.columnconfigure(0, weight=1)
        
        self.voice_status_label = tk.Label(
            voice_frame,
            text="Inactive",
            font=("Arial", 12, "bold"),
            fg="red"
        )
        self.voice_status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.voice_button = tk.Button(
            voice_frame,
            text="Start Voice Control",
            command=self.toggle_voice_control,
            width=25,
            height=2,
            bg="#2ecc71",
            fg="black",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        )
        self.voice_button.grid(row=1, column=0, pady=5)
        
        voice_info = """46+ voice commands available
Say 'help' to list commands
Say 'exit' to quit"""
        
        self.voice_info_label = tk.Label(
            voice_frame,
            text=voice_info,
            font=("Arial", 9),
            fg="#7f8c8d",
            justify=tk.LEFT
        )
        self.voice_info_label.grid(row=2, column=0, pady=5)
        
        # ==================== QUICK START ====================
        quickstart_frame = ttk.LabelFrame(main_frame, text="Quick Start", padding="10")
        quickstart_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        quickstart_frame.columnconfigure(0, weight=1)
        
        tk.Button(
            quickstart_frame,
            text="Start Both Systems",
            command=self.start_both,
            width=25,
            height=2,
            bg="#e67e22",
            fg="black",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).grid(row=0, column=0, pady=5)
        
        tk.Label(
            quickstart_frame,
            text="Starts eye tracking and voice control together",
            font=("Arial", 9),
            fg="#7f8c8d"
        ).grid(row=1, column=0, pady=2)
        
        # ==================== QUICK ACTIONS ====================
        actions_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding="10")
        actions_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)

        actions_inner = tk.Frame(actions_frame)
        actions_inner.grid(row=0, column=0)
        
        tk.Button(
            actions_inner,
            text="Commands",
            command=self.show_commands,
            width=12,
            bg="#95a5a6",
            fg="black",
            font=("Arial", 10)
        ).grid(row=0, column=0, padx=3, pady=5)
        
        tk.Button(
            actions_inner,
            text="ℹHelp",
            command=self.show_help,
            width=12,
            bg="#3498db",
            fg="black",
            font=("Arial", 10)
        ).grid(row=0, column=1, padx=3, pady=5)
        
        tk.Button(
            actions_inner,
            text="Demo",
            command=self.show_demo_scenarios,
            width=12,
            bg="#9b59b6",
            fg="black",
            font=("Arial", 10)
        ).grid(row=0, column=2, padx=3, pady=5)
        
        # ==================== ACTIVITY LOG ====================
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure main_frame row weight for log expansion
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            width=70,
            font=("Courier", 9),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ==================== STATUS BAR ====================
        status_frame = tk.Frame(main_frame, relief=tk.SUNKEN, bd=1)
        status_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to start - Click buttons above to begin",
            anchor=tk.W,
            font=("Arial", 9),
            fg="#27ae60"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add initial log entries
        self.log_activity("BlinkOS Control Panel initialized")
        self.log_activity("TIP: Start both systems for full hands-free control")
        self.log_activity("Ready to begin!")
    
    def log_activity(self, message):
        """Add entry to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.activity_log.append(log_entry)
        
        if len(self.activity_log) > self.max_log_entries:
            self.activity_log.pop(0)
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        print(f"{message}")
    
    def update_status(self, message, color="#2c3e50"):
        """Update status bar"""
        self.status_label.config(text=message, fg=color)
    
    def toggle_eye_tracking(self):
        """Start/stop eye tracking"""
        if not self.eye_tracking_active:
            self.log_activity("Launching eye tracking system...")
            self.update_status("Starting eye tracker...", "#e67e22")
            
            try:
                # Launch eye tracker as separate process
                self.eye_process = subprocess.Popen(
                    [sys.executable, 'modules/eye_tracker.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.eye_tracking_active = True
                self._update_eye_tracking_ui(True)
                
                # Monitor process
                self.root.after(1000, self.check_eye_tracking_status)
                
            except Exception as e:
                self.log_activity(f"Error starting eye tracking: {e}")
                self.update_status("Error starting eye tracking", "#e74c3c")
        else:
            self.stop_eye_tracking()
    
    def stop_eye_tracking(self):
        """Stop eye tracking"""
        if self.eye_process:
            self.eye_process.terminate()
            self.eye_process = None
        
        self.eye_tracking_active = False
        self._update_eye_tracking_ui(False)
        self.log_activity("Eye tracking stopped")
        self.update_status("Eye tracking stopped", "#7f8c8d")
    
    def check_eye_tracking_status(self):
        """Check if eye tracking process is still running"""
        if self.eye_tracking_active and self.eye_process:
            if self.eye_process.poll() is not None:
                # Process ended
                self.eye_tracking_active = False
                self._update_eye_tracking_ui(False)
                self.log_activity("Eye tracking window closed")
            else:
                # Still running, check again
                self.root.after(1000, self.check_eye_tracking_status)
    
    def _update_eye_tracking_ui(self, active):
        """Update eye tracking UI"""
        if active:
            self.eye_status_label.config(text="Active", fg="green")
            self.eye_button.config(
                text="Stop Eye Tracking",
                bg="#e74c3c"
            )
            self.log_activity("Eye tracking active")
            self.update_status("Eye tracking running - check separate window", "#27ae60")
        else:
            self.eye_status_label.config(text="● Inactive", fg="red")
            self.eye_button.config(
                text="▶ Start Eye Tracking",
                bg="#3498db"
            )
    
    def toggle_voice_control(self):
        """Start/stop voice control"""
        if not self.voice_control_active:
            self.log_activity("Launching voice control system...")
            self.update_status("Starting voice control...", "#e67e22")
            
            try:
                # Launch voice controller as separate process
                self.voice_process = subprocess.Popen(
                    [sys.executable, 'modules/voice_controller.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.voice_control_active = True
                self._update_voice_control_ui(True)
                
                # Monitor process
                self.root.after(1000, self.check_voice_control_status)
                
            except Exception as e:
                self.log_activity(f"Error starting voice control: {e}")
                self.update_status("Error starting voice control", "#e74c3c")
        else:
            self.stop_voice_control()
    
    def stop_voice_control(self):
        """Stop voice control"""
        if self.voice_process:
            self.voice_process.terminate()
            self.voice_process = None
        
        self.voice_control_active = False
        self._update_voice_control_ui(False)
        self.log_activity("Voice control stopped")
        self.update_status("Voice control stopped", "#7f8c8d")
    
    def check_voice_control_status(self):
        """Check if voice control process is still running"""
        if self.voice_control_active and self.voice_process:
            if self.voice_process.poll() is not None:
                # Process ended
                self.voice_control_active = False
                self._update_voice_control_ui(False)
                self.log_activity("Voice control ended")
            else:
                # Still running, check again
                self.root.after(1000, self.check_voice_control_status)
    
    def _update_voice_control_ui(self, active):
        """Update voice control UI"""
        if active:
            self.voice_status_label.config(text="● Active", fg="green")
            self.voice_button.config(
                text="Stop Voice Control",
                bg="#e74c3c"
            )
            self.log_activity("Voice control active - say commands now!")
            self.update_status("Voice control listening ", "#27ae60")
        else:
            self.voice_status_label.config(text="Inactive", fg="red")
            self.voice_button.config(
                text="Start Voice Control",
                bg="#2ecc71"
            )
    
    def start_both(self):
        """Start both systems"""
        self.log_activity("Starting BOTH systems for full control!")
        
        if not self.eye_tracking_active:
            self.toggle_eye_tracking()
        
        # Delay voice control start slightly
        self.root.after(1000, lambda: self.toggle_voice_control() if not self.voice_control_active else None)
        
        self.update_status("Full hands-free control active!", "#27ae60")
    
    def show_commands(self):
        """Show voice commands"""
        commands_window = tk.Toplevel(self.root)
        commands_window.title("Voice Commands Reference")
        commands_window.geometry("550x650")
        
        tk.Label(
            commands_window,
            text="Voice Commands",
            font=("Arial", 18, "bold")
        ).pack(pady=15)
        
        text = scrolledtext.ScrolledText(
            commands_window,
            width=65,
            height=32,
            font=("Courier", 10),
            bg="#ecf0f1"
        )
        text.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        
        commands_text = """
* APPLICATIONS (9 commands):
  • open safari / chrome / firefox
  • open notes / terminal / mail
  • open finder / messages / calendar

* WINDOW MANAGEMENT (10 commands):
  • close window / close tab
  • new tab / new window
  • minimize / maximize / full screen
  • next window / previous window
  • quit app

* NAVIGATION (10 commands):
  • scroll down / scroll up
  • page down / page up
  • go back / go forward
  • refresh / reload

* TAB MANAGEMENT (3 commands):
  • next tab / previous tab
  • reopen tab

* SYSTEM CONTROLS (8 commands):
  • volume up / volume down / mute / unmute
  • brightness up / brightness down
  • take screenshot / screen shot
  • sleep

* DICTATION (2 commands):
  • type / start typing (then speak text)
  • stop typing (exit dictation mode)

* SEARCH (2 commands):
  • search [your query]
  • google [your query]

* SPECIAL (2 commands):
  • help / list commands
  • exit / quit voice / stop listening

TOTAL: 46+ Commands Available!
"""
        
        text.insert("1.0", commands_text)
        text.config(state=tk.DISABLED)
        
        tk.Button(
            commands_window,
            text="Close",
            command=commands_window.destroy,
            width=15,
            height=2,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(pady=15)
    
    def show_help(self):
        """Show help window"""
        help_window = tk.Toplevel(self.root)
        help_window.title("BlinkOS Help")
        help_window.geometry("500x600")
        
        tk.Label(
            help_window,
            text="How to Use BlinkOS",
            font=("Arial", 18, "bold")
        ).pack(pady=15)
        
        text = scrolledtext.ScrolledText(
            help_window,
            width=60,
            height=28,
            font=("Arial", 10),
            bg="#ecf0f1"
        )
        text.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        
        help_text = """
GETTING STARTED:
================

1. Click "Start Both Systems" for full control
   OR start them individually

2. Eye Tracking Window:
   - Move your HEAD to control cursor
   - BLINK to click
   - Press 'Q' to quit
   - Press 'K' to toggle clicking
   - Press '+/-' to adjust sensitivity

3. Voice Control:
   - Say commands clearly
   - Wait for "Listening..." prompt
   - Say "help" to list all commands
   - Say "exit" to quit

BEST PRACTICES:
===============

Eye Tracking:
  ✓ Sit ~50cm from camera
  ✓ Good front lighting (no backlighting)
  ✓ Keep head movements smooth
  ✓ Blink deliberately for clicks

Voice Control:
  ✓ Speak clearly and at normal volume
  ✓ Wait for recognition before next command
  ✓ Use exact command phrases
  ✓ Say "type" to enter dictation mode

DEMO SCENARIOS:
===============

Scenario 1: Web Browsing
  1. Say "open safari"
  2. Move head to address bar, blink
  3. Say "search artificial intelligence"
  4. Say "scroll down"

Scenario 2: Document Creation
  1. Say "open notes"
  2. Say "new window"
  3. Say "type"
  4. Speak your text
  5. Say "stop typing"

Scenario 3: System Control
  1. Say "volume up"
  2. Say "brightness down"
  3. Say "take screenshot"
  4. Say "minimize"

TROUBLESHOOTING:
================

Eye tracking not working:
  → Check camera permissions
  → Improve lighting
  → Adjust sensitivity with +/-

Voice not recognized:
  → Speak louder/clearer
  → Check microphone permissions
  → Reduce background noise

System slow:
  → Close other applications
  → Restart BlinkOS
  → Check CPU usage

For more help, see README.md
"""
        
        text.insert("1.0", help_text)
        text.config(state=tk.DISABLED)
        
        tk.Button(
            help_window,
            text="Close",
            command=help_window.destroy,
            width=15,
            height=2,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(pady=15)
    
    def show_demo_scenarios(self):
        """Show demo scenarios"""
        demo_window = tk.Toplevel(self.root)
        demo_window.title("Demo Scenarios")
        demo_window.geometry("550x600")
        
        tk.Label(
            demo_window,
            text="Hackathon Demo Scenarios",
            font=("Arial", 18, "bold")
        ).pack(pady=15)
        
        text = scrolledtext.ScrolledText(
            demo_window,
            width=65,
            height=28,
            font=("Arial", 10),
            bg="#ecf0f1"
        )
        text.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        
        demo_text = """
DEMO SCENARIO 1: Web Research (2 min)
========================================

Goal: Search for information hands-free

Steps:
1. Voice: "open safari"
2. Head: Move cursor to address bar
3. Blink: Click address bar
4. Voice: "search machine learning basics"
5. Head + Blink: Click first result
6. Voice: "scroll down"
7. Voice: "scroll down"
8. Voice: "go back"
9. Voice: "close tab"

Impact: Shows seamless browsing without hands!


DEMO SCENARIO 2: Document Creation (2 min)
==============================================

Goal: Create and edit a document

Steps:
1. Voice: "open notes"
2. Voice: "new window"
3. Voice: "type"
4. Voice: "Dear Team comma I am excited to present 
   BlinkOS comma a hands free computer control 
   system period New paragraph This system uses 
   eye tracking and voice recognition period"
5. Voice: "stop typing"
6. Head + Blink: Select text (optional)
7. Voice: "close window"

Impact: Shows accessibility for typing!


DEMO SCENARIO 3: System Control (1.5 min)
============================================

Goal: Control system without touching anything

Steps:
1. Voice: "open finder"
2. Head + Blink: Navigate folders
3. Voice: "volume up"
4. Voice: "brightness down"
5. Voice: "take screenshot"
6. Voice: "minimize"
7. Voice: "open terminal"
8. Voice: "quit app"

Impact: Shows system-wide control!


DEMO SCENARIO 4: Multi-App Workflow (2.5 min)
================================================

Goal: Complete workflow across multiple apps

Steps:
1. Voice: "open safari"
2. Voice: "search github"
3. Head + Blink: Click GitHub
4. Voice: "open notes"
5. Voice: "type"
6. Voice: "GitHub is a platform for... (description)"
7. Voice: "stop typing"
8. Voice: "next window" (back to Safari)
9. Voice: "scroll down"
10. Voice: "previous window" (back to Notes)
11. Voice: "close window"

Impact: Shows real-world usage!


PRESENTATION TIPS:
==================

✓ Start with problem statement (accessibility)
✓ Show live demo (2-3 scenarios)
✓ Have backup video ready
✓ Explain technology briefly
✓ Emphasize impact on users
✓ Practice transitions between scenarios
✓ Time yourself (< 5 minutes total)
"""
        
        text.insert("1.0", demo_text)
        text.config(state=tk.DISABLED)
        
        tk.Button(
            demo_window,
            text="Close",
            command=demo_window.destroy,
            width=15,
            height=2,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(pady=15)
    
    def on_closing(self):
        """Handle window close"""
        self.log_activity("Shutting down BlinkOS...")
        
        # Stop processes
        if self.eye_tracking_active:
            self.stop_eye_tracking()
        
        if self.voice_control_active:
            self.stop_voice_control()
        
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        print("\n" + "="*60)
        print("BlinkOS - Hands-Free Computer Control System")
        print("="*60)
        print("\nControl Panel launched!")
        print("Use the GUI to control the system\n")
        
        # Start GUI main loop
        self.root.mainloop()
        
        print("\nBlinkOS shutdown complete")


def main():
    """Main entry point"""
    try:
        app = BlinkOS()
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()