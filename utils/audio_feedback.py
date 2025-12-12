#!/usr/bin/env python3
"""
Audio Feedback Utilities for BlinkOS
Provides audio feedback for user actions and system events
"""

import threading
import queue
from typing import Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    print("Warning: pyttsx3 not installed. Audio feedback disabled.")


class AudioFeedback:
    """
    Manages audio feedback for BlinkOS
    Provides non-blocking text-to-speech feedback
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize audio feedback system
        
        Args:
            enabled: Whether audio feedback is enabled
        """
        self.enabled = enabled and pyttsx3 is not None
        self.engine = None
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        
        if self.enabled:
            self._initialize_engine()
            self._start_worker()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            # Configure voice properties
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.8)  # Volume (0-1)
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.enabled = False
    
    def _start_worker(self):
        """Start the worker thread for processing speech queue"""
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
    
    def _process_queue(self):
        """Process speech requests from the queue"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:  # Shutdown signal
                    break
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                print(f"Error in speech synthesis: {e}")
    
    def speak(self, text: str, blocking: bool = False):
        """
        Speak the given text
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not self.enabled or not text:
            return
        
        if blocking:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error in speech synthesis: {e}")
        else:
            self.speech_queue.put(text)
    
    def play_sound(self, sound_type: str):
        """
        Play a predefined sound
        
        Args:
            sound_type: Type of sound ('click', 'error', 'success', 'warning')
        """
        sounds = {
            'click': "Click",
            'error': "Error",
            'success': "Success",
            'warning': "Warning"
        }
        
        if sound_type in sounds:
            self.speak(sounds[sound_type])
    
    def shutdown(self):
        """Shutdown the audio feedback system"""
        if self.worker_thread and self.worker_thread.is_alive():
            self.speech_queue.put(None)  # Signal shutdown
            self.worker_thread.join(timeout=2)
        
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


# Global instance
_audio_feedback: Optional[AudioFeedback] = None


def get_audio_feedback(enabled: bool = True) -> AudioFeedback:
    """
    Get the global audio feedback instance
    
    Args:
        enabled: Whether audio feedback should be enabled
        
    Returns:
        AudioFeedback instance
    """
    global _audio_feedback
    if _audio_feedback is None:
        _audio_feedback = AudioFeedback(enabled=enabled)
    return _audio_feedback


def speak(text: str, blocking: bool = False):
    """
    Convenience function to speak text
    
    Args:
        text: Text to speak
        blocking: If True, wait for speech to complete
    """
    feedback = get_audio_feedback()
    feedback.speak(text, blocking=blocking)


def play_sound(sound_type: str):
    """
    Convenience function to play a sound
    
    Args:
        sound_type: Type of sound to play
    """
    feedback = get_audio_feedback()
    feedback.play_sound(sound_type)
