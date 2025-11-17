#!/usr/bin/env python3
"""
BlinkOS - Voice Controller (Complete Extended Version)
Comprehensive voice commands for completely hands-free computer control
"""

import speech_recognition as sr
import pyttsx3
import subprocess
import os
import time
import threading
import re
import urllib.parse


class VoiceController:
    """
    Extended Voice Controller with 100+ commands
    Makes computer completely hands-free
    """
    
    def __init__(self):
        """Initialize voice controller"""
        print("Initializing Voice Controller...")
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        
        # Select microphone (with auto-detection)
        self.select_microphone()
        
        # Adjust for ambient noise
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Text-to-speech for feedback
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.8)
            self.tts_enabled = True
            print("Text-to-speech enabled")
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            self.tts_enabled = False
        
        # State
        self.dictation_mode = False
        self.is_listening = False
        self.running = True
        self.command_count = 0
        self.last_command = None
        self.audio_feedback = True
        
        print("Voice Controller initialized!")
        print("100+ commands available - Say 'help' to see them all")
    
    def select_microphone(self):
        """List and select microphone device"""
        print("\nAvailable Microphones:")
        print('-' * 50)
        
        mic_list = sr.Microphone.list_microphone_names()
        
        for index, name in enumerate(mic_list):
            print(f"{index}: {name}")
        
        print('-' * 50)
        
        # Try to auto-select the built-in microphone (avoid AirPods, etc.)
        built_in_index = None
        for index, name in enumerate(mic_list):
            name_lower = name.lower()
            if 'built-in' in name_lower or 'macbook' in name_lower or 'internal' in name_lower:
                built_in_index = index
                print(f"\nAuto-selected: {index} - {name}")
                break
        
        if built_in_index is not None:
            self.microphone = sr.Microphone(device_index=built_in_index)
        else:
            # Default to the first microphone
            print(f"\n Using default microphone: 0 - {mic_list[0]}")
            self.microphone = sr.Microphone(device_index=0)
        
        print("\nTIP: If voice recognition is poor, edit voice_controller.py")
        print("     and manually set device_index to your preferred microphone\n")
    
    def speak(self, text, blocking=False):
        """
        Text-to-speech output
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to finish
        """
        if not self.audio_feedback or not self.tts_enabled:
            return
        
        try:
            if blocking:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Non-blocking speech
                def speak_thread():
                    self.engine.say(text)
                    self.engine.runAndWait()
                
                threading.Thread(target=speak_thread, daemon=True).start()
        except Exception as e:
            print(f"TTS error: {e}")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Listen for voice input
        
        Args:
            timeout: Max time to wait for speech to start
            phrase_time_limit: Max time for phrase
            
        Returns:
            str: Recognized text or None
        """
        try:
            with self.microphone as source:
                print("\nListening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            print("Processing...")
            
            # Recognize speech using Google
            text = self.recognizer.recognize_google(audio).lower()
            print(f"Heard: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            print("No speech detected")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def execute_command(self, command):
        """Execute voice command"""
        if not command:
            return False
        
        command = command.lower().strip()
        
        # ==================== DICTATION MODE ====================
        if self.dictation_mode:
            if "stop typing" in command or "exit dictation" in command:
                self.dictation_mode = False
                print("Exited dictation mode")
                self.speak("Dictation mode off")
                return True
            else:
                # Type whatever was said
                self.type_text(command)
                return True
        
        # ==================== APPLICATIONS ====================
        
        # Browsers
        if "open safari" in command or "launch safari" in command:
            self.open_app("Safari")
        
        elif "open chrome" in command or "launch chrome" in command:
            self.open_app("Google Chrome")
        
        elif "open firefox" in command or "launch firefox" in command:
            self.open_app("Firefox")
        
        elif "open brave" in command or "launch brave" in command:
            self.open_app("Brave Browser")
        
        # Productivity
        elif "open notes" in command or "launch notes" in command:
            self.open_app("Notes")
        
        elif "open mail" in command or "launch mail" in command:
            self.open_app("Mail")
        
        elif "open calendar" in command or "launch calendar" in command:
            self.open_app("Calendar")
        
        elif "open reminders" in command or "launch reminders" in command:
            self.open_app("Reminders")
        
        elif "open messages" in command or "launch messages" in command:
            self.open_app("Messages")
        
        # System
        elif "open finder" in command or "launch finder" in command:
            self.open_app("Finder")
        
        elif "open terminal" in command or "launch terminal" in command:
            self.open_app("Terminal")
        
        elif "open settings" in command or "system preferences" in command:
            self.open_app("System Preferences")
        
        # Microsoft Office
        elif "open word" in command or "launch word" in command:
            self.open_app("Microsoft Word")
        
        elif "open excel" in command or "launch excel" in command:
            self.open_app("Microsoft Excel")
        
        elif "open powerpoint" in command or "launch powerpoint" in command:
            self.open_app("Microsoft PowerPoint")
        
        # Creative
        elif "open photoshop" in command or "launch photoshop" in command:
            self.open_app("Adobe Photoshop")
        
        elif "open preview" in command or "launch preview" in command:
            self.open_app("Preview")
        
        elif "open music" in command or "launch music" in command:
            self.open_app("Music")
        
        elif "open spotify" in command or "launch spotify" in command:
            self.open_app("Spotify")
        
        # Development
        elif "open vs code" in command or "open visual studio code" in command:
            self.open_app("Visual Studio Code")
        
        elif "open xcode" in command or "launch xcode" in command:
            self.open_app("Xcode")
        
        # ==================== WINDOW MANAGEMENT ====================
        
        elif "close window" in command:
            self._send_key('w', ['command'])
            print(" Closed window")
            self.speak("Closing window")
        
        elif "close tab" in command:
            self._send_key('w', ['command'])
            print(" Closed tab")
            self.speak("Closing tab")
        
        elif "new window" in command:
            self._send_key('n', ['command'])
            print(" New window")
            self.speak("New window")
        
        elif "new tab" in command:
            self._send_key('t', ['command'])
            print(" New tab")
            self.speak("New tab")
        
        elif "minimize" in command or "minimize window" in command:
            self._send_key('m', ['command'])
            print("Minimized window")
            self.speak("Minimizing")
        
        elif "maximize" in command or "maximize window" in command:
            script = '''
            tell application "System Events"
                tell process (name of first application process whose frontmost is true)
                    click button 2 of window 1
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            print("Maximized window")
            self.speak("Maximizing")
        
        elif "full screen" in command or "fullscreen" in command:
            self._send_key('f', ['control', 'command'])
            print("Full screen toggled")
            self.speak("Full screen")
        
        elif "next window" in command or "switch window" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to keystroke "`" using command down'])
            print("Next window")
            self.speak("Next window")
        
        elif "previous window" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to keystroke "`" using {command down, shift down}'])
            print("Previous window")
            self.speak("Previous window")
        
        elif "quit app" in command or "quit application" in command:
            self._send_key('q', ['command'])
            print("Quit application")
            self.speak("Quitting application")
        
        elif "hide window" in command or "hide app" in command:
            self._send_key('h', ['command'])
            print("Hidden window")
            self.speak("Hidden")
        
        elif "show desktop" in command or "hide all windows" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 103'])  # F11
            print("Show desktop")
            self.speak("Show desktop")
        
        # ==================== SCROLLING (ENHANCED) ====================
        
        elif "scroll down" in command:
            amount = self.extract_number(command, default=3)
            for _ in range(amount):
                subprocess.run(['osascript', '-e',
                              'tell application "System Events" to key code 125'])
            print(f"Scrolled down ({amount}x)")
            self.speak("Scrolling down")
        
        elif "scroll up" in command:
            amount = self.extract_number(command, default=3)
            for _ in range(amount):
                subprocess.run(['osascript', '-e',
                              'tell application "System Events" to key code 126'])
            print(f"Scrolled up ({amount}x)")
            self.speak("Scrolling up")
        
        elif "scroll left" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 123'])
            print("Scrolled left")
            self.speak("Scrolling left")
        
        elif "scroll right" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 124'])
            print("Scrolled right")
            self.speak("Scrolling right")
        
        elif "scroll to top" in command or "go to top" in command:
            self._send_key('up', ['command'])
            print("Scrolled to top")
            self.speak("Top of page")
        
        elif "scroll to bottom" in command or "go to bottom" in command:
            self._send_key('down', ['command'])
            print("Scrolled to bottom")
            self.speak("Bottom of page")
        
        elif "page down" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 121'])
            print("Page down")
            self.speak("Page down")
        
        elif "page up" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 116'])
            print("Page up")
            self.speak("Page up")
        
        # ==================== NAVIGATION ====================
        
        elif "go back" in command or command == "back":
            self._send_key('[', ['command'])
            print("Go back")
            self.speak("Going back")
        
        elif "go forward" in command or command == "forward":
            self._send_key(']', ['command'])
            print("Go forward")
            self.speak("Going forward")
        
        elif "refresh" in command or "reload" in command:
            self._send_key('r', ['command'])
            print("Refreshed")
            self.speak("Refreshing")
        
        elif "home page" in command or "go home" in command:
            self._send_key('h', ['command', 'shift'])
            print("Home page")
            self.speak("Home page")
        
        # ==================== TAB MANAGEMENT ====================
        
        elif "next tab" in command or "switch tab" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to keystroke tab using {control down}'])
            print("Next tab")
            self.speak("Next tab")
        
        elif "previous tab" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to keystroke tab using {control down, shift down}'])
            print("Previous tab")
            self.speak("Previous tab")
        
        elif "reopen tab" in command or "restore tab" in command:
            self._send_key('t', ['command', 'shift'])
            print("Reopened tab")
            self.speak("Reopening tab")
        
        elif "close all tabs" in command:
            self._send_key('w', ['command', 'shift'])
            print("Closed all tabs")
            self.speak("Closing all tabs")
        
        elif command.startswith("tab ") or command.startswith("go to tab "):
            tab_number = self.extract_number(command)
            if tab_number and 1 <= tab_number <= 9:
                self._send_key(str(tab_number), ['command'])
                print(f"Switched to tab {tab_number}")
                self.speak(f"Tab {tab_number}")
        
        # ==================== TEXT EDITING ====================
        
        elif "select all" in command:
            self._send_key('a', ['command'])
            print("Selected all")
            self.speak("Select all")
        
        elif command == "copy":
            self._send_key('c', ['command'])
            print("Copied")
            self.speak("Copied")
        
        elif command == "cut":
            self._send_key('x', ['command'])
            print("Cut")
            self.speak("Cut")
        
        elif command == "paste":
            self._send_key('v', ['command'])
            print("Pasted")
            self.speak("Pasted")
        
        elif command == "undo":
            self._send_key('z', ['command'])
            print("Undo")
            self.speak("Undo")
        
        elif command == "redo":
            self._send_key('z', ['command', 'shift'])
            print("Redo")
            self.speak("Redo")
        
        elif "find" in command or "search on page" in command:
            self._send_key('f', ['command'])
            print("Find")
            self.speak("Find")
        
        elif "save as" in command:
            self._send_key('s', ['command', 'shift'])
            print("Save as")
            self.speak("Save as")
        
        elif command == "save":
            self._send_key('s', ['command'])
            print("Saved")
            self.speak("Saved")
        
        elif command == "print":
            self._send_key('p', ['command'])
            print("Print dialog")
            self.speak("Print")
        
        elif command == "bold":
            self._send_key('b', ['command'])
            print("Bold")
            self.speak("Bold")
        
        elif command == "italic":
            self._send_key('i', ['command'])
            print("Italic")
            self.speak("Italic")
        
        elif command == "underline":
            self._send_key('u', ['command'])
            print("_Underline_")
            self.speak("Underline")
        
        elif "new line" in command or command == "enter":
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to keystroke return'])
            print(" New line")
            self.speak("New line")
        
        elif "delete line" in command:
            self._send_key('k', ['command', 'shift'])
            print("Deleted line")
            self.speak("Delete line")
        
        elif command == "backspace":
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 51'])
            print(" Backspace")
        
        elif command == "delete" and "line" not in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 117'])
            print(" Delete")
        
        # ==================== SYSTEM CONTROLS ====================
        
        elif "volume up" in command or "increase volume" in command:
            amount = self.extract_number(command, default=10)
            subprocess.run(['osascript', '-e',
                          f'set volume output volume ((output volume of (get volume settings)) + {amount})'])
            print(f"Volume up (+{amount})")
            self.speak("Volume up")
        
        elif "volume down" in command or "decrease volume" in command:
            amount = self.extract_number(command, default=10)
            subprocess.run(['osascript', '-e',
                          f'set volume output volume ((output volume of (get volume settings)) - {amount})'])
            print(f" Volume down (-{amount})")
            self.speak("Volume down")
        
        elif command == "mute":
            subprocess.run(['osascript', '-e', 'set volume output muted true'])
            print("Muted")
            self.speak("Muted")
        
        elif command == "unmute":
            subprocess.run(['osascript', '-e', 'set volume output muted false'])
            print(" Unmuted")
            self.speak("Unmuted")
        
        elif "brightness up" in command or "increase brightness" in command:
            amount = self.extract_number(command, default=2)
            for _ in range(amount):
                subprocess.run(['osascript', '-e',
                              'tell application "System Events" to key code 144'])
            print(f"Brightness up ({amount}x)")
            self.speak("Brightness up")
        
        elif "brightness down" in command or "decrease brightness" in command:
            amount = self.extract_number(command, default=2)
            for _ in range(amount):
                subprocess.run(['osascript', '-e',
                              'tell application "System Events" to key code 145'])
            print(f"Brightness down ({amount}x)")
            self.speak("Brightness down")
        
        elif "take screenshot" in command or "screenshot" in command or "screen shot" in command:
            if "window" in command:
                self._send_key('4', ['command', 'shift'])
                subprocess.run(['osascript', '-e',
                              'tell application "System Events" to keystroke space'])
                print("Screenshot window")
                self.speak("Screenshot window")
            elif "selection" in command:
                self._send_key('4', ['command', 'shift'])
                print("Screenshot selection")
                self.speak("Screenshot selection")
            else:
                self._send_key('3', ['command', 'shift'])
                print("Screenshot taken")
                self.speak("Screenshot taken")
        
        elif "lock screen" in command or "lock computer" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to keystroke "q" using {control down, command down}'])
            print("Screen locked")
            self.speak("Locking screen")
        
        elif "sleep" in command and "don't" not in command:
            subprocess.run(['pmset', 'displaysleepnow'])
            print("Display sleeping")
            self.speak("Going to sleep")
        
        # ==================== SPOTLIGHT & SEARCH ====================
        
        elif "spotlight" in command or "open spotlight" in command:
            self._send_key('space', ['command'])
            print("Spotlight opened")
            self.speak("Spotlight")
        
        elif command.startswith("search ") or command.startswith("google "):
            query = command.replace("search ", "").replace("google ", "")
            self.search_web(query)
        
        elif command.startswith("open website ") or command.startswith("go to "):
            url = command.replace("open website ", "").replace("go to ", "")
            self.open_url(url)
        
        # ==================== MEDIA CONTROLS ====================
        
        elif "play" in command and "pause" not in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 16'])  # Play/Pause
            print("Play")
            self.speak("Play")
        
        elif "pause" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 16'])
            print("Pause")
            self.speak("Pause")
        
        elif "next song" in command or "next track" in command or "skip" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 19'])  # Next track
            print("Next track")
            self.speak("Next track")
        
        elif "previous song" in command or "previous track" in command:
            subprocess.run(['osascript', '-e',
                          'tell application "System Events" to key code 20'])  # Previous track
            print("Previous track")
            self.speak("Previous track")
        
        # ==================== DICTATION MODE ====================
        
        elif "type" in command or "start typing" in command or "dictation" in command:
            self.dictation_mode = True
            print("Dictation mode ON - speak to type, say 'stop typing' to exit")
            self.speak("Dictation mode on")
        
        # ==================== SPECIAL COMMANDS ====================
        
        elif "what time is it" in command or "current time" in command:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            print(f"Current time: {current_time}")
            self.speak(f"It's {current_time}")
        
        elif "what date is it" in command or "today's date" in command:
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            print(f" Today's date: {current_date}")
            self.speak(current_date)
        
        elif "help" in command or "list commands" in command or "show commands" in command:
            self.show_help()
        
        elif "exit" in command or "quit" in command or "stop listening" in command:
            print("Exiting voice control...")
            self.speak("Goodbye")
            self.running = False
        
        else:
            print(f"Unknown command: '{command}'")
            print("Say 'help' to see available commands")
            return False
        
        self.command_count += 1
        self.last_command = command
        return True
    
    def open_app(self, app_name):
        """Open macOS application"""
        try:
            subprocess.Popen(['open', '-a', app_name])
            print(f"Opening {app_name}")
            self.speak(f"Opening {app_name}")
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            self.speak("Application not found")
    
    def search_web(self, query):
        """Search on Google"""
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        subprocess.run(['open', url])
        print(f"Searching for: {query}")
        self.speak(f"Searching for {query}")
    
    def open_url(self, url):
        """Open URL in browser"""
        if not url.startswith('http'):
            url = 'https://' + url.replace(" dot ", ".").replace(" ", "")
        subprocess.run(['open', url])
        print(f" Opening: {url}")
        self.speak(f"Opening {url}")
    
    def type_text(self, text):
        """Type text (for dictation mode)"""
        text = self.format_dictation(text)
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        script = f'tell application "System Events" to keystroke "{escaped_text}"'
        subprocess.run(['osascript', '-e', script])
        print(f"Typed: {text}")
    
    def format_dictation(self, text):
        """Format dictated text with punctuation"""
        replacements = {
            " comma ": ", ",
            " period ": ". ",
            " question mark ": "? ",
            " exclamation mark ": "! ",
            " exclamation point ": "! ",
            " colon ": ": ",
            " semicolon ": "; ",
            " dash ": " - ",
            " hyphen ": "-",
            " at sign ": "@",
            " hashtag ": "#",
            " dollar sign ": "$",
            " percent ": "%",
            " ampersand ": "&",
            " and sign ": "&",
            " open parenthesis ": "(",
            " close parenthesis ": ")",
            " open bracket ": "[",
            " close bracket ": "]",
            " new line ": "\n",
            " new paragraph ": "\n\n",
            " quote ": "\"",
            " apostrophe ": "'",
        }
        
        for speech, symbol in replacements.items():
            text = text.replace(speech, symbol)
        
        return text
    
    def extract_number(self, text, default=1):
        """Extract number from command"""
        words_to_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "once": 1, "twice": 2, "thrice": 3
        }
        
        for word, number in words_to_numbers.items():
            if word in text:
                return number
        
        # Try to find digit
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return default
    
    def _send_key(self, key, modifiers=None):
        """Send keyboard shortcut using AppleScript"""
        if modifiers:
            mod_str = ', '.join([f'{m} down' for m in modifiers])
            script = f'tell application "System Events" to keystroke "{key}" using {{{mod_str}}}'
        else:
            script = f'tell application "System Events" to keystroke "{key}"'
        
        subprocess.run(['osascript', '-e', script])
    
    def show_help(self):
        """Show available commands"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║              BLINKOS VOICE COMMANDS (100+)                 ║
╠════════════════════════════════════════════════════════════╣
║ APPLICATIONS (20+):                                        ║
║  • open [safari/chrome/firefox/brave]                      ║
║  • open [notes/mail/calendar/messages/reminders]           ║
║  • open [finder/terminal/settings]                         ║
║  • open [word/excel/powerpoint/photoshop]                  ║
║  • open [music/spotify/vs code/xcode]                      ║
║                                                            ║
║ WINDOW MANAGEMENT (10+):                                   ║
║  • close window/tab, new window/tab                        ║
║  • minimize, maximize, full screen                         ║
║  • next/previous window, quit app                          ║
║  • hide window, show desktop                               ║
║                                                            ║
║ SCROLLING (10+):                                           ║
║  • scroll [up/down/left/right] [number]                    ║
║  • scroll to [top/bottom]                                  ║
║  • page [up/down]                                          ║
║                                                            ║
║ NAVIGATION (5):                                            ║
║  • go [back/forward], refresh, home page                   ║
║                                                            ║
║ TAB MANAGEMENT (5):                                        ║
║  • next/previous tab, reopen tab                           ║
║  • close all tabs, tab [number]                            ║
║                                                            ║
║ TEXT EDITING (15+):                                        ║
║  • select all, copy, cut, paste                            ║
║  • undo, redo, find, save, save as, print                  ║
║  • bold, italic, underline                                 ║
║  • new line, delete line, backspace, delete                ║
║                                                            ║
║ SYSTEM CONTROLS (10+):                                     ║
║  • volume [up/down] [number], mute/unmute                  ║
║  • brightness [up/down] [number]                           ║
║  • take screenshot [window/selection]                      ║
║  • lock screen, sleep                                      ║
║                                                            ║
║ MEDIA CONTROLS (5):                                        ║
║  • play, pause                                             ║
║  • next/previous song/track, skip                          ║
║                                                            ║
║ DICTATION:                                                 ║
║  • type / start typing (enter dictation mode)              ║
║  • [speak naturally with punctuation]                      ║
║  • stop typing (exit dictation mode)                       ║
║                                                            ║
║ SEARCH & WEB:                                              ║
║  • search [query], google [query]                          ║
║  • open website [url], spotlight                           ║
║                                                            ║
║ SPECIAL:                                                   ║
║  • help, exit, what time is it, what date is it            ║
╚════════════════════════════════════════════════════════════╝

DICTATION PUNCTUATION:
  Say "comma" for ,    Say "period" for .
  Say "question mark" for ?    Say "exclamation mark" for !
  Say "new line" for line break    Say "new paragraph" for ¶

EXAMPLES:
  "open safari" → Opens Safari browser
  "scroll down five" → Scrolls down 5 times
  "volume up three" → Increases volume 3x
  "search artificial intelligence" → Google search
  "type" → Enter dictation mode, then speak to type
  "stop typing" → Exit dictation mode
"""
        print(help_text)
        self.speak("Commands listed in terminal")
    
    def run(self):
        """Main voice control loop"""
        print("\n" + "="*60)
        print("🎤 VOICE CONTROL ACTIVE")
        print("="*60)
        print("\nSay 'help' for command list")
        print("Say 'exit' to quit")
        print("-" * 60 + "\n")
        
        self.is_listening = True
        self.running = True
        self.speak("Voice controller activated")
        
        try:
            while self.running:
                # Listen for command
                command = self.listen()
                
                if command:
                    self.execute_command(command)
                
                # Small delay between commands
                time.sleep(0.3)
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        except Exception as e:
            print(f"\n\nError: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.is_listening = False
            self.running = False
            print("\n" + "="*60)
            print(f"Voice Control Stopped - {self.command_count} commands executed")
            print("="*60)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("BlinkOS - Voice Controller")
    print("Complete Hands-Free Computer Control")
    print("="*60 + "\n")
    
    try:
        controller = VoiceController()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()