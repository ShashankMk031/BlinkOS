"""
BlinkOS Utilities Package
Provides common utilities for the BlinkOS application
"""

from .audio_feedback import AudioFeedback, get_audio_feedback, speak, play_sound
from .config_manager import ConfigManager, get_config_manager, get_config, set_config

__all__ = [
    # Audio feedback
    'AudioFeedback',
    'get_audio_feedback',
    'speak',
    'play_sound',
    
    # Configuration
    'ConfigManager',
    'get_config_manager',
    'get_config',
    'set_config',
]
