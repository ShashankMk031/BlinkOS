#!/usr/bin/env python3
"""
Voice Controller Module - Voice command recognition and execution
Uses Google Speech Recognition for voice-to-text
"""

import speech_recognition as sr
import pyttsx3
import subprocess
import os
import time
import threading


class VoiceController:
    """
    Voice control system for hands-free computer control
    Recognizes commands and executes system actions
    """
    
    def __init__(self):
        """Initialize voice controller"""
        print("Initializing Voice Controller...")
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
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
        
        # Command mapping
        self.commands = {
            # Application commands
            'open safari': self.open_safari,
            'open chrome': self.open_chrome,
            'open firefox': self.open_firefox,
            'open notes': self.open_notes,
            'open terminal': self.open_terminal,
            'open mail': self.open_mail,
            'open finder': self.open_finder,
            'open messages': self.open_messages,
            'open calendar': self.open_calendar,
            
            # Window management
            'close window': self.close_window,
            'close tab': self.close_tab,
            'new tab': self.new_tab,
            'new window': self.new_window,
            'minimize': self.minimize_window,
            'maximize': self.maximize_window,
            'full screen': self.fullscreen,
            'next window': self.next_window,
            'previous window': self.previous_window,
            'quit app': self.quit_app,
            'quit application': self.quit_app,
            
            # Navigation
            'scroll down': self.scroll_down,
            'scroll up': self.scroll_up,
            'page down': self.page_down,
            'page up': self.page_up,
            'go back': self.go_back,
            'go forward': self.go_forward,
            'refresh': self.refresh_page,
            'refresh page': self.refresh_page,
            'reload': self.refresh_page,
            
            # Tab management
            'next tab': self.next_tab,
            'previous tab': self.previous_tab,
            'reopen tab': self.reopen_tab,
            
            # System controls
            'volume up': self.volume_up,
            'volume down': self.volume_down,
            'mute': self.mute,
            'unmute': self.unmute,
            'brightness up': self.brightness_up,
            'brightness down': self.brightness_down,
            'take screenshot': self.screenshot,
            'screen shot': self.screenshot,
            'sleep': self.sleep_display,
            
            # Dictation mode
            'start typing': self.enter_dictation_mode,
            'stop typing': self.exit_dictation_mode,
            'type': self.enter_dictation_mode,
            
            # Search
            'search': self.search_google,
            'google': self.search_google,
        }
        
        # State
        self.dictation_mode = False
        self.is_listening = False
        self.command_count = 0
        self.last_command = None
        
        # Audio feedback toggle
        self.audio_feedback = True
        
        print("Voice Controller initialized!")
        print(f"{len(self.commands)} commands available")
    
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
    
    def listen(self, timeout=5, phrase_time_limit=5):
        """
        Listen for voice input
        
        Args:
            timeout: Max time to wait for speech to start
            phrase_time_limit: Max time for phrase
            
        Returns:
            str: Recognized text or None
        """
        if not self.is_listening:
            return None
        
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech using Google
            text = self.recognizer.recognize_google(audio).lower()
            print(f"Heard: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            # No speech detected
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
    
    # ==================== APPLICATION COMMANDS ====================
    
    def open_safari(self):
        """Open Safari browser"""
        subprocess.Popen(['open', '-a', 'Safari'])
        self.speak("Opening Safari")
    
    def open_chrome(self):
        """Open Google Chrome"""
        subprocess.Popen(['open', '-a', 'Google Chrome'])
        self.speak("Opening Chrome")
    
    def open_firefox(self):
        """Open Firefox"""
        subprocess.Popen(['open', '-a', 'Firefox'])
        self.speak("Opening Firefox")
    
    def open_notes(self):
        """Open Notes app"""
        subprocess.Popen(['open', '-a', 'Notes'])
        self.speak("Opening Notes")
    
    def open_terminal(self):
        """Open Terminal"""
        subprocess.Popen(['open', '-a', 'Terminal'])
        self.speak("Opening Terminal")
    
    def open_mail(self):
        """Open Mail app"""
        subprocess.Popen(['open', '-a', 'Mail'])
        self.speak("Opening Mail")
    
    def open_finder(self):
        """Open Finder"""
        subprocess.Popen(['open', '-a', 'Finder'])
        self.speak("Opening Finder")
    
    def open_messages(self):
        """Open Messages"""
        subprocess.Popen(['open', '-a', 'Messages'])
        self.speak("Opening Messages")
    
    def open_calendar(self):
        """Open Calendar"""
        subprocess.Popen(['open', '-a', 'Calendar'])
        self.speak("Opening Calendar")
    
    # ==================== WINDOW MANAGEMENT ====================
    
    def close_window(self):
        """Close current window (Cmd+W)"""
        self._send_key('w', ['command'])
        self.speak("Closing window")
    
    def close_tab(self):
        """Close current tab (Cmd+W)"""
        self._send_key('w', ['command'])
        self.speak("Closing tab")
    
    def new_tab(self):
        """Open new tab (Cmd+T)"""
        self._send_key('t', ['command'])
        self.speak("New tab")
    
    def new_window(self):
        """Open new window (Cmd+N)"""
        self._send_key('n', ['command'])
        self.speak("New window")
    
    def minimize_window(self):
        """Minimize window (Cmd+M)"""
        self._send_key('m', ['command'])
        self.speak("Minimizing")
    
    def maximize_window(self):
        """Maximize window (green button)"""
        # AppleScript to click green button
        script = '''
        tell application "System Events"
            tell process (name of first application process whose frontmost is true)
                click button 2 of window 1
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        self.speak("Maximizing")
    
    def fullscreen(self):
        """Toggle fullscreen (Ctrl+Cmd+F)"""
        self._send_key('f', ['control', 'command'])
        self.speak("Full screen")
    
    def next_window(self):
        """Switch to next window (Cmd+`)"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to keystroke "`" using command down'])
        self.speak("Next window")
    
    def previous_window(self):
        """Switch to previous window (Cmd+Shift+`)"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to keystroke "`" using {command down, shift down}'])
        self.speak("Previous window")
    
    def quit_app(self):
        """Quit application (Cmd+Q)"""
        self._send_key('q', ['command'])
        self.speak("Quitting application")
    
    # ==================== NAVIGATION ====================
    
    def scroll_down(self):
        """Scroll down"""
        for _ in range(3):
            subprocess.run(['osascript', '-e', 
                           'tell application "System Events" to key code 125'])  # Down arrow
        self.speak("Scrolling down")
    
    def scroll_up(self):
        """Scroll up"""
        for _ in range(3):
            subprocess.run(['osascript', '-e', 
                           'tell application "System Events" to key code 126'])  # Up arrow
        self.speak("Scrolling up")
    
    def page_down(self):
        """Page down"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 121'])  # Page Down
        self.speak("Page down")
    
    def page_up(self):
        """Page up"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 116'])  # Page Up
        self.speak("Page up")
    
    def go_back(self):
        """Go back (Cmd+[)"""
        self._send_key('[', ['command'])
        self.speak("Going back")
    
    def go_forward(self):
        """Go forward (Cmd+])"""
        self._send_key(']', ['command'])
        self.speak("Going forward")
    
    def refresh_page(self):
        """Refresh page (Cmd+R)"""
        self._send_key('r', ['command'])
        self.speak("Refreshing")
    
    # ==================== TAB MANAGEMENT ====================
    
    def next_tab(self):
        """Switch to next tab (Ctrl+Tab)"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to keystroke tab using {control down}'])
        self.speak("Next tab")
    
    def previous_tab(self):
        """Switch to previous tab (Ctrl+Shift+Tab)"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to keystroke tab using {control down, shift down}'])
        self.speak("Previous tab")
    
    def reopen_tab(self):
        """Reopen closed tab (Cmd+Shift+T)"""
        self._send_key('t', ['command', 'shift'])
        self.speak("Reopening tab")
    
    # ==================== SYSTEM CONTROLS ====================
    
    def volume_up(self):
        """Increase volume"""
        subprocess.run(['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) + 10)'])
        self.speak("Volume up")
    
    def volume_down(self):
        """Decrease volume"""
        subprocess.run(['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) - 10)'])
        self.speak("Volume down")
    
    def mute(self):
        """Mute volume"""
        subprocess.run(['osascript', '-e', 'set volume output muted true'])
        self.speak("Muted")
    
    def unmute(self):
        """Unmute volume"""
        subprocess.run(['osascript', '-e', 'set volume output muted false'])
        self.speak("Unmuted")
    
    def brightness_up(self):
        """Increase brightness"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 144'])  # Brightness up key
        self.speak("Brightness up")
    
    def brightness_down(self):
        """Decrease brightness"""
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 145'])  # Brightness down key
        self.speak("Brightness down")
    
    def screenshot(self):
        """Take screenshot (Cmd+Shift+3)"""
        self._send_key('3', ['command', 'shift'])
        self.speak("Screenshot taken")
    
    def sleep_display(self):
        """Sleep display"""
        subprocess.run(['pmset', 'displaysleepnow'])
        self.speak("Sleeping display")
    
    # ==================== DICTATION MODE ====================
    
    def enter_dictation_mode(self):
        """Enter dictation mode for typing"""
        self.dictation_mode = True
        self.speak("Dictation mode activated")
        print("Dictation mode ON - Say 'stop typing' to exit")
    
    def exit_dictation_mode(self):
        """Exit dictation mode"""
        self.dictation_mode = False
        self.speak("Dictation mode deactivated")
        print("Dictation mode OFF")
    
    def type_text(self, text):
        """
        Type text using AppleScript
        
        Args:
            text: Text to type
        """
        # Escape quotes in text
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        
        # Type using AppleScript
        script = f'tell application "System Events" to keystroke "{escaped_text}"'
        subprocess.run(['osascript', '-e', script])
    
    # ==================== SEARCH ====================
    
    def search_google(self, query=None):
        """
        Search Google
        
        Args:
            query: Search query (if None, will listen for it)
        """
        if query is None:
            self.speak("What do you want to search?")
            query = self.listen(timeout=3, phrase_time_limit=5)
            
            if not query:
                self.speak("No search query heard")
                return
        
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        
        # Open in browser
        url = f"https://www.google.com/search?q={encoded_query}"
        subprocess.run(['open', url])
        
        self.speak(f"Searching for {query}")
    
    # ==================== HELPER METHODS ====================
    
    def _send_key(self, key, modifiers=None):
        """
        Send keyboard shortcut using AppleScript
        
        Args:
            key: Key to press
            modifiers: List of modifiers (command, shift, control, option)
        """
        if modifiers:
            mod_str = ', '.join([f'{m} down' for m in modifiers])
            script = f'tell application "System Events" to keystroke "{key}" using {{{mod_str}}}'
        else:
            script = f'tell application "System Events" to keystroke "{key}"'
        
        subprocess.run(['osascript', '-e', script])
    
    def process_command(self, text):
        """
        Process voice command
        
        Args:
            text: Recognized text from speech
            
        Returns:
            bool: True if command was found and executed
        """
        if not text:
            return False
        
        text = text.lower().strip()
        
        # Handle dictation mode
        if self.dictation_mode:
            if 'stop typing' in text:
                self.exit_dictation_mode()
                return True
            else:
                # Type the text
                self.type_text(text)
                return True
        
        # Handle search commands (extract query)
        if text.startswith('search '):
            query = text.replace('search ', '', 1)
            self.search_google(query)
            return True
        elif text.startswith('google '):
            query = text.replace('google ', '', 1)
            self.search_google(query)
            return True
        
        # Check for exact command matches
        for command_phrase, command_function in self.commands.items():
            if command_phrase in text:
                try:
                    command_function()
                    self.command_count += 1
                    self.last_command = command_phrase
                    return True
                except Exception as e:
                    print(f"Error executing command '{command_phrase}': {e}")
                    self.speak("Command failed")
                    return False
        
        # No command found
        print(f"Unknown command: '{text}'")
        self.speak("Command not recognized")
        return False
    
    def list_commands(self):
        """Print all available commands"""
        print("\nAvailable Commands:")
        print("\nApplications:")
        for cmd in ['open safari', 'open chrome', 'open notes', 'open terminal', 'open mail', 'open finder']:
            print(f"  - {cmd}")
        
        print("\nWindow Management:")
        for cmd in ['close window', 'new tab', 'minimize', 'maximize', 'quit app']:
            print(f"  - {cmd}")
        
        print("\n Navigation:")
        for cmd in ['scroll down', 'scroll up', 'go back', 'go forward', 'refresh']:
            print(f"  - {cmd}")
        
        print("\n System:")
        for cmd in ['volume up', 'volume down', 'mute', 'take screenshot']:
            print(f"  - {cmd}")
        
        print("\n Dictation:")
        print("  - type / start typing (then speak to type)")
        print("  - stop typing (to exit)")
        
        print("\n Search:")
        print("  - search [query]")
        print("  - google [query]")
        print()
    
    def run(self):
        """
        Main voice control loop
        """
        print("\nVoice Controller Started!")
        print("Say 'help' or 'list commands' to see all commands")
        print("Say 'exit' or 'quit' to stop")
        print("-" * 50)
        
        self.is_listening = True
        self.speak("Voice controller activated")
        
        try:
            while self.is_listening:
                # Listen for command
                text = self.listen()
                
                if text:
                    # Check for exit commands
                    if 'exit' in text or 'quit voice' in text or 'stop listening' in text:
                        self.speak("Stopping voice controller")
                        break
                    
                    # Check for help
                    if 'help' in text or 'list commands' in text:
                        self.list_commands()
                        self.speak("Commands listed in terminal")
                        continue
                    
                    # Process command
                    self.process_command(text)
                
                # Small delay
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.is_listening = False
            print("\nVoice Controller stopped")
            print(f"Total commands executed: {self.command_count}")


if __name__ == "__main__":
    """Test voice controller directly"""
    try:
        controller = VoiceController()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()