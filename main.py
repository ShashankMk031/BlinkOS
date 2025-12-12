#!/usr/bin/env python3
"""
BlinkOS - Main Controller (Simplified)
Launches eye tracking and voice control as separate processes
"""

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox
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
        self.root.geometry("650x800")
        self.root.resizable(True, True)
        
        # Modern background gradient effect
        self.root.configure(bg="#f0f4f8")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container with modern styling
        main_frame = tk.Frame(self.root, bg="#f0f4f8", padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # ==================== TITLE ====================
        title_label = tk.Label(
            main_frame,
            text="BlinkOS",
            font=("Helvetica", 32, "bold"),
            fg="#1e40af",
            bg="#f0f4f8"
        )
        title_label.grid(row=0, column=0, pady=(0, 8))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Hands-Free Computer Control System",
            font=("Helvetica", 14),
            fg="#64748b",
            bg="#f0f4f8"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 5))
        
        version_label = tk.Label(
            main_frame,
            text="Hackathon Demo v0.1.0",
            font=("Helvetica", 10),
            fg="#94a3b8",
            bg="#f0f4f8"
        )
        version_label.grid(row=2, column=0, pady=(0, 20))
        
        # ==================== EYE TRACKING SECTION ====================
        eye_frame = tk.LabelFrame(
            main_frame,
            text="Eye Tracking",
            font=("Helvetica", 13, "bold"),
            fg="#1e40af",
            bg="#ffffff",
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=0
        )
        eye_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=8, ipady=10, ipadx=10)
        eye_frame.columnconfigure(0, weight=1)
        eye_frame.configure(bg="#ffffff")
        
        self.eye_status_label = tk.Label(
            eye_frame,
            text="Inactive",
            font=("Helvetica", 13, "bold"),
            fg="#ef4444",
            bg="#ffffff"
        )
        self.eye_status_label.grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        
        self.eye_button = tk.Button(
            eye_frame,
            text="Start Eye Tracking",
            command=self.toggle_eye_tracking,
            width=28,
            height=2,
            bg="#3b82f6",
            fg="white",
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#2563eb",
            activeforeground="white",
            highlightthickness=0
        )
        self.eye_button.grid(row=1, column=0, pady=8, padx=10)
        
        eye_info = """Move your head to control cursor • Blink to click
Press Q to quit • Press K to toggle clicking
Opens in separate window"""
        
        self.eye_info_label = tk.Label(
            eye_frame,
            text=eye_info,
            font=("Helvetica", 10),
            fg="#64748b",
            bg="#ffffff",
            justify=tk.LEFT
        )
        self.eye_info_label.grid(row=2, column=0, pady=(0, 8), padx=10)
        
        # ==================== VOICE CONTROL SECTION ====================
        voice_frame = tk.LabelFrame(
            main_frame,
            text="Voice Control",
            font=("Helvetica", 13, "bold"),
            fg="#059669",
            bg="#ffffff",
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=0
        )
        voice_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=8, ipady=10, ipadx=10)
        voice_frame.columnconfigure(0, weight=1)
        voice_frame.configure(bg="#ffffff")
        
        self.voice_status_label = tk.Label(
            voice_frame,
            text="Inactive",
            font=("Helvetica", 13, "bold"),
            fg="#ef4444",
            bg="#ffffff"
        )
        self.voice_status_label.grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        
        self.voice_button = tk.Button(
            voice_frame,
            text="Start Voice Control",
            command=self.toggle_voice_control,
            width=28,
            height=2,
            bg="#10b981",
            fg="white",
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#059669",
            activeforeground="white",
            highlightthickness=0
        )
        self.voice_button.grid(row=1, column=0, pady=8, padx=10)
        
        voice_info = """46+ voice commands available
Say 'help' to list all commands • Say 'exit' to quit
Supports dictation, apps, navigation & more"""
        
        self.voice_info_label = tk.Label(
            voice_frame,
            text=voice_info,
            font=("Helvetica", 10),
            fg="#64748b",
            bg="#ffffff",
            justify=tk.LEFT
        )
        self.voice_info_label.grid(row=2, column=0, pady=(0, 8), padx=10)
        
        # ==================== QUICK START ====================
        quickstart_frame = tk.LabelFrame(
            main_frame,
            text="Quick Start",
            font=("Helvetica", 13, "bold"),
            fg="#d97706",
            bg="#ffffff",
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=0
        )
        quickstart_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=8, ipady=10, ipadx=10)
        quickstart_frame.columnconfigure(0, weight=1)
        quickstart_frame.configure(bg="#ffffff")
        
        tk.Button(
            quickstart_frame,
            text="Start Both Systems",
            command=self.start_both,
            width=28,
            height=2,
            bg="#f59e0b",
            fg="white",
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#d97706",
            activeforeground="white",
            highlightthickness=0
        ).grid(row=0, column=0, pady=8, padx=10)
        
        tk.Label(
            quickstart_frame,
            text="Launch eye tracking and voice control together for full hands-free experience",
            font=("Helvetica", 10),
            fg="#64748b",
            bg="#ffffff"
        ).grid(row=1, column=0, pady=(0, 8), padx=10)
        
        # ==================== QUICK ACTIONS ====================
        actions_frame = tk.LabelFrame(
            main_frame,
            text="Quick Actions",
            font=("Helvetica", 13, "bold"),
            fg="#6366f1",
            bg="#ffffff",
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=0
        )
        actions_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=8, ipady=10, ipadx=10)
        actions_frame.configure(bg="#ffffff")

        actions_inner = tk.Frame(actions_frame, bg="#ffffff")
        actions_inner.grid(row=0, column=0, pady=5)
        
        tk.Button(
            actions_inner,
            text="Commands",
            command=self.show_commands,
            width=13,
            bg="#8b5cf6",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#7c3aed",
            activeforeground="white",
            highlightthickness=0
        ).grid(row=0, column=0, padx=4, pady=5)
        
        tk.Button(
            actions_inner,
            text="Help",
            command=self.show_help,
            width=13,
            bg="#3b82f6",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#2563eb",
            activeforeground="white",
            highlightthickness=0
        ).grid(row=0, column=1, padx=4, pady=5)
        
        tk.Button(
            actions_inner,
            text="Demo",
            command=self.show_demo_scenarios,
            width=13,
            bg="#ec4899",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#db2777",
            activeforeground="white",
            highlightthickness=0
        ).grid(row=0, column=2, padx=4, pady=5)
        
        tk.Button(
            actions_inner,
            text="Settings",
            command=self.show_settings,
            width=13,
            bg="#64748b",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#475569",
            activeforeground="white",
            highlightthickness=0
        ).grid(row=0, column=3, padx=4, pady=5)
        
        # ==================== ACTIVITY LOG ====================
        log_frame = tk.LabelFrame(
            main_frame,
            text="Activity Log",
            font=("Helvetica", 13, "bold"),
            fg="#0891b2",
            bg="#ffffff",
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=0
        )
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=8, ipady=10, ipadx=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        log_frame.configure(bg="#ffffff")
        
        # Configure main_frame row weight for log expansion
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            width=70,
            font=("Menlo", 10),
            bg="#f8fafc",
            fg="#334155",
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=0
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # ==================== STATUS BAR ====================
        status_frame = tk.Frame(main_frame, bg="#e0f2fe", relief=tk.FLAT, bd=0, height=40)
        status_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to start - Click buttons above to begin",
            anchor=tk.W,
            font=("Helvetica", 11),
            fg="#0369a1",
            bg="#e0f2fe",
            padx=15,
            pady=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
    
    def update_status(self, message, color="#334155"):
        """Update status bar"""
        self.status_label.config(text=message, fg=color)
        # Update background color based on status type
        if "error" in message.lower() or "failed" in message.lower():
            self.status_label.config(bg="#fee2e2")
        elif "active" in message.lower() or "running" in message.lower():
            self.status_label.config(bg="#d1fae5")
        elif "starting" in message.lower():
            self.status_label.config(bg="#fef3c7")
        else:
            self.status_label.config(bg="#e0f2fe")
    
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
            self.eye_status_label.config(text="● Active", fg="#10b981")
            self.eye_button.config(
                text="■ Stop Eye Tracking",
                bg="#ef4444",
                activebackground="#dc2626"
            )
            self.log_activity("Eye tracking active")
            self.update_status("Eye tracking running - check separate window", "#059669")
        else:
            self.eye_status_label.config(text="● Inactive", fg="#ef4444")
            self.eye_button.config(
                text="▶ Start Eye Tracking",
                bg="#3b82f6",
                activebackground="#2563eb"
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
            self.voice_status_label.config(text="● Active", fg="#10b981")
            self.voice_button.config(
                text="■ Stop Voice Control",
                bg="#ef4444",
                activebackground="#dc2626"
            )
            self.log_activity("Voice control active - say commands now!")
            self.update_status("Voice control listening for commands", "#059669")
        else:
            self.voice_status_label.config(text="● Inactive", fg="#ef4444")
            self.voice_button.config(
                text="▶ Start Voice Control",
                bg="#10b981",
                activebackground="#059669"
            )
    
    def start_both(self):
        """Start both systems"""
        self.log_activity("Starting BOTH systems for full control!")
        
        if not self.eye_tracking_active:
            self.toggle_eye_tracking()
        
        # Delay voice control start slightly
        self.root.after(1000, lambda: self.toggle_voice_control() if not self.voice_control_active else None)
        
        self.update_status("Full hands-free control active!", "#059669")
    
    def show_commands(self):
        """Show voice commands"""
        commands_window = tk.Toplevel(self.root)
        commands_window.title("Voice Commands Reference")
        commands_window.geometry("600x700")
        commands_window.configure(bg="#f0f4f8")
        
        header_frame = tk.Frame(commands_window, bg="#3b82f6", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Voice Commands",
            font=("Helvetica", 22, "bold"),
            fg="white",
            bg="#3b82f6"
        ).pack(pady=20)
        
        text = scrolledtext.ScrolledText(
            commands_window,
            width=68,
            height=30,
            font=("Menlo", 11),
            bg="#ffffff",
            fg="#1e293b",
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15
        )
        text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
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
        
        button_frame = tk.Frame(commands_window, bg="#f0f4f8")
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Close",
            command=commands_window.destroy,
            width=18,
            height=2,
            bg="#64748b",
            fg="white",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#475569",
            activeforeground="white"
        ).pack()
    
    def show_help(self):
        """Show help window"""
        help_window = tk.Toplevel(self.root)
        help_window.title("BlinkOS Help")
        help_window.geometry("550x650")
        help_window.configure(bg="#f0f4f8")
        
        header_frame = tk.Frame(help_window, bg="#10b981", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="How to Use BlinkOS",
            font=("Helvetica", 22, "bold"),
            fg="white",
            bg="#10b981"
        ).pack(pady=20)
        
        text = scrolledtext.ScrolledText(
            help_window,
            width=65,
            height=28,
            font=("Helvetica", 11),
            bg="#ffffff",
            fg="#1e293b",
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15
        )
        text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
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
  - Sit ~50cm from camera
  - Good front lighting (no backlighting)
  - Keep head movements smooth
  - Blink deliberately for clicks

Voice Control:
  - Speak clearly and at normal volume
  - Wait for recognition before next command
  - Use exact command phrases
  - Say "type" to enter dictation mode

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
        
        button_frame = tk.Frame(help_window, bg="#f0f4f8")
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Close",
            command=help_window.destroy,
            width=18,
            height=2,
            bg="#10b981",
            fg="white",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#059669",
            activeforeground="white"
        ).pack()
    
    def show_demo_scenarios(self):
        """Show demo scenarios"""
        demo_window = tk.Toplevel(self.root)
        demo_window.title("Demo Scenarios")
        demo_window.geometry("600x650")
        demo_window.configure(bg="#f0f4f8")
        
        header_frame = tk.Frame(demo_window, bg="#f59e0b", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Demo Scenarios",
            font=("Helvetica", 22, "bold"),
            fg="white",
            bg="#f59e0b"
        ).pack(pady=20)
        
        text = scrolledtext.ScrolledText(
            demo_window,
            width=68,
            height=28,
            font=("Helvetica", 11),
            bg="#ffffff",
            fg="#1e293b",
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15
        )
        text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
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


"""
        
        text.insert("1.0", demo_text)
        text.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(demo_window, bg="#f0f4f8")
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Close",
            command=demo_window.destroy,
            width=18,
            height=2,
            bg="#f59e0b",
            fg="white",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#d97706",
            activeforeground="white"
        ).pack()
    
    def show_settings(self):
        """Show settings window with adjustable parameters"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("650x750")
        settings_window.configure(bg="#f0f4f8")
        
        # Load settings
        from modules.settings import Settings
        settings = Settings()
        
        header_frame = tk.Frame(settings_window, bg="#6366f1", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Settings",
            font=("Helvetica", 22, "bold"),
            fg="white",
            bg="#6366f1"
        ).pack(pady=20)
        
        # Create notebook (tabs) with modern styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.TNotebook', background='#f0f4f8', borderwidth=0)
        style.configure('Custom.TNotebook.Tab', padding=[20, 10], font=('Helvetica', 11, 'bold'))
        
        notebook = ttk.Notebook(settings_window, style='Custom.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === TAB 1: EYE TRACKING ===
        eye_tab = tk.Frame(notebook, bg="#ffffff")
        notebook.add(eye_tab, text="Eye Tracking")
        
        tk.Label(eye_tab, text="Eye Tracking Settings", font=("Helvetica", 16, "bold"),
                bg="#ffffff", fg="#1e293b").pack(pady=15)
        
        # Smoothing slider
        smooth_frame = tk.Frame(eye_tab, bg="#ffffff")
        smooth_frame.pack(fill=tk.X, padx=25, pady=12)
        
        tk.Label(smooth_frame, text="Cursor Smoothing:", font=("Helvetica", 12, "bold"),
                bg="#ffffff", fg="#1e293b").pack(anchor=tk.W)
        tk.Label(smooth_frame, text="(Higher = smoother but slower)", font=("Helvetica", 10),
                fg="#64748b", bg="#ffffff").pack(anchor=tk.W, pady=(0, 5))
        
        smooth_var = tk.IntVar(value=settings.get('eye_tracking', 'smooth_buffer_size'))
        smooth_slider = tk.Scale(smooth_frame, from_=10, to=50, orient=tk.HORIZONTAL,
                                variable=smooth_var, length=450, bg="#ffffff",
                                highlightthickness=0, troughcolor="#e2e8f0",
                                activebackground="#3b82f6")
        smooth_slider.pack(fill=tk.X, pady=8)
        tk.Label(smooth_frame, textvariable=smooth_var, font=("Helvetica", 11, "bold"),
                bg="#ffffff", fg="#3b82f6").pack()
        
        # Update rate slider
        rate_frame = tk.Frame(eye_tab, bg="#ffffff")
        rate_frame.pack(fill=tk.X, padx=25, pady=12)
        
        tk.Label(rate_frame, text="Cursor Update Rate:", font=("Helvetica", 12, "bold"),
                bg="#ffffff", fg="#1e293b").pack(anchor=tk.W)
        tk.Label(rate_frame, text="(Higher = slower updates, more stable)", font=("Helvetica", 10),
                fg="#64748b", bg="#ffffff").pack(anchor=tk.W, pady=(0, 5))
        
        rate_var = tk.IntVar(value=settings.get('eye_tracking', 'update_rate'))
        rate_slider = tk.Scale(rate_frame, from_=1, to=5, orient=tk.HORIZONTAL,
                            variable=rate_var, length=450, bg="#ffffff",
                            highlightthickness=0, troughcolor="#e2e8f0",
                            activebackground="#3b82f6")
        rate_slider.pack(fill=tk.X, pady=8)
        tk.Label(rate_frame, textvariable=rate_var, font=("Helvetica", 11, "bold"),
                bg="#ffffff", fg="#3b82f6").pack()
        
        # Click cooldown slider
        cooldown_frame = tk.Frame(eye_tab, bg="#ffffff")
        cooldown_frame.pack(fill=tk.X, padx=25, pady=12)
        
        tk.Label(cooldown_frame, text="Click Cooldown (seconds):", font=("Helvetica", 12, "bold"),
                bg="#ffffff", fg="#1e293b").pack(anchor=tk.W)
        tk.Label(cooldown_frame, text="(Time between clicks)", font=("Helvetica", 10),
                fg="#64748b", bg="#ffffff").pack(anchor=tk.W, pady=(0, 5))
        
        cooldown_var = tk.DoubleVar(value=settings.get('eye_tracking', 'click_cooldown'))
        cooldown_slider = tk.Scale(cooldown_frame, from_=0.5, to=2.0, resolution=0.1,
                                orient=tk.HORIZONTAL, variable=cooldown_var,
                                length=450, bg="#ffffff",
                                highlightthickness=0, troughcolor="#e2e8f0",
                                activebackground="#3b82f6")
        cooldown_slider.pack(fill=tk.X, pady=8)
        tk.Label(cooldown_frame, textvariable=cooldown_var, font=("Helvetica", 11, "bold"),
                bg="#ffffff", fg="#3b82f6").pack()
        
        # === TAB 2: CALIBRATION ===
        calib_tab = tk.Frame(notebook, bg="#ffffff")
        notebook.add(calib_tab, text="Calibration")
        
        tk.Label(calib_tab, text="Calibration Settings", font=("Helvetica", 16, "bold"),
                bg="#ffffff", fg="#1e293b").pack(pady=15)
        
        # Range expansion slider
        range_frame = tk.Frame(calib_tab, bg="#ecf0f1")
        range_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(range_frame, text="Range Expansion:", font=("Arial", 11),
                bg="#ecf0f1").pack(anchor=tk.W)
        tk.Label(range_frame, text="(Higher = easier to reach corners)", font=("Arial", 9),
                fg="#7f8c8d", bg="#ecf0f1").pack(anchor=tk.W)
        
        range_var = tk.DoubleVar(value=settings.get('calibration', 'range_expansion'))
        range_slider = tk.Scale(range_frame, from_=1.0, to=1.5, resolution=0.05,
                            orient=tk.HORIZONTAL, variable=range_var,
                            length=400, bg="#ecf0f1")
        range_slider.pack(fill=tk.X, pady=5)
        tk.Label(range_frame, textvariable=range_var, font=("Arial", 10, "bold"),
                bg="#ecf0f1").pack()
        
        # Smoothing factor slider
        calib_smooth_frame = tk.Frame(calib_tab, bg="#ecf0f1")
        calib_smooth_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(calib_smooth_frame, text="Calibration Smoothing:", font=("Arial", 11),
                bg="#ecf0f1").pack(anchor=tk.W)
        tk.Label(calib_smooth_frame, text="(Higher = smoother but less precise)", font=("Arial", 9),
                fg="#7f8c8d", bg="#ecf0f1").pack(anchor=tk.W)
        
        calib_smooth_var = tk.DoubleVar(value=settings.get('calibration', 'smoothing_factor'))
        calib_smooth_slider = tk.Scale(calib_smooth_frame, from_=0.0, to=0.5, resolution=0.05,
                                    orient=tk.HORIZONTAL, variable=calib_smooth_var,
                                    length=400, bg="#ecf0f1")
        calib_smooth_slider.pack(fill=tk.X, pady=5)
        tk.Label(calib_smooth_frame, textvariable=calib_smooth_var, font=("Arial", 10, "bold"),
                bg="#ecf0f1").pack()
        
        # Corner boost slider
        boost_frame = tk.Frame(calib_tab, bg="#ecf0f1")
        boost_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(boost_frame, text="Corner Boost:", font=("Arial", 11),
                bg="#ecf0f1").pack(anchor=tk.W)
        tk.Label(boost_frame, text="(Higher = more sensitive at edges)", font=("Arial", 9),
                fg="#7f8c8d", bg="#ecf0f1").pack(anchor=tk.W)
        
        boost_var = tk.DoubleVar(value=settings.get('calibration', 'corner_boost'))
        boost_slider = tk.Scale(boost_frame, from_=1.0, to=1.5, resolution=0.05,
                            orient=tk.HORIZONTAL, variable=boost_var,
                            length=400, bg="#ecf0f1")
        boost_slider.pack(fill=tk.X, pady=5)
        tk.Label(boost_frame, textvariable=boost_var, font=("Arial", 10, "bold"),
                bg="#ecf0f1").pack()
        
        # === TAB 3: SYSTEM ===
        system_tab = tk.Frame(notebook, bg="#ffffff")
        notebook.add(system_tab, text="⚙️ System")
        
        tk.Label(system_tab, text="System Settings", font=("Helvetica", 16, "bold"),
                bg="#ffffff", fg="#1e293b").pack(pady=15)
        
        # Checkboxes
        checks_frame = tk.Frame(system_tab, bg="#ffffff")
        checks_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        auto_eye_var = tk.BooleanVar(value=settings.get('system', 'auto_start_eye_tracking'))
        tk.Checkbutton(checks_frame, text="Auto-start eye tracking on launch",
                    variable=auto_eye_var, font=("Helvetica", 12),
                    bg="#ffffff", fg="#1e293b", selectcolor="#ffffff",
                    activebackground="#ffffff").pack(anchor=tk.W, pady=8)
        
        auto_voice_var = tk.BooleanVar(value=settings.get('system', 'auto_start_voice_control'))
        tk.Checkbutton(checks_frame, text="Auto-start voice control on launch",
                    variable=auto_voice_var, font=("Helvetica", 12),
                    bg="#ffffff", fg="#1e293b", selectcolor="#ffffff",
                    activebackground="#ffffff").pack(anchor=tk.W, pady=8)
        
        auto_calib_var = tk.BooleanVar(value=settings.get('system', 'load_calibration_on_start'))
        tk.Checkbutton(checks_frame, text="Load calibration on start",
                    variable=auto_calib_var, font=("Helvetica", 12),
                    bg="#ffffff", fg="#1e293b", selectcolor="#ffffff",
                    activebackground="#ffffff").pack(anchor=tk.W, pady=8)
        
        # === BUTTONS ===
        button_frame = tk.Frame(settings_window, bg="#f0f4f8")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Define nested functions for button commands
        def save_and_close():
            """Save all settings and close window"""
            # Save all settings
            settings.set('eye_tracking', 'smooth_buffer_size', smooth_var.get())
            settings.set('eye_tracking', 'update_rate', rate_var.get())
            settings.set('eye_tracking', 'click_cooldown', cooldown_var.get())
            
            settings.set('calibration', 'range_expansion', range_var.get())
            settings.set('calibration', 'smoothing_factor', calib_smooth_var.get())
            settings.set('calibration', 'corner_boost', boost_var.get())
            
            settings.set('system', 'auto_start_eye_tracking', auto_eye_var.get())
            settings.set('system', 'auto_start_voice_control', auto_voice_var.get())
            settings.set('system', 'load_calibration_on_start', auto_calib_var.get())
            
            settings.save_settings()
            
            self.log_activity("Settings saved! Restart systems to apply changes.")
            settings_window.destroy()
        
        def reset_defaults():
            """Reset all settings to defaults"""
            if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
                settings.reset_to_defaults()
                settings.save_settings()
                self.log_activity("Settings reset to defaults")
                settings_window.destroy()
        
        tk.Button(button_frame, text="Save & Close", command=save_and_close,
                 width=16, height=2, bg="#10b981", fg="white",
                 font=("Helvetica", 11, "bold"), cursor="hand2",
                 relief=tk.FLAT, bd=0, activebackground="#059669",
                 activeforeground="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Reset to Defaults", command=reset_defaults,
                 width=16, height=2, bg="#f59e0b", fg="white",
                 font=("Helvetica", 11, "bold"), cursor="hand2",
                 relief=tk.FLAT, bd=0, activebackground="#d97706",
                 activeforeground="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=settings_window.destroy,
                 width=16, height=2, bg="#64748b", fg="white",
                 font=("Helvetica", 11, "bold"), cursor="hand2",
                 relief=tk.FLAT, bd=0, activebackground="#475569",
                 activeforeground="white").pack(side=tk.LEFT, padx=5)
    
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