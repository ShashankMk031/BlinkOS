#!/usr/bin/env python3
"""
Settings Module - Manages user preferences and configuration
"""

import json
import os
from pathlib import Path


class Settings:
    """
    Manages application settings with save/load functionality
    """
    
    def __init__(self, settings_path='data/settings.json'):
        """
        Initialize settings manager
        
        Args:
            settings_path: Path to settings file
        """
        self.settings_path = settings_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        
        # Default settings
        self.defaults = {
            # Eye tracking settings
            'eye_tracking': {
                'smooth_buffer_size': 25,
                'update_rate': 3,  # Update every Nth frame
                'click_enabled': True,
                'click_cooldown': 1.0,
                'blink_threshold': 0.20,
                'audio_feedback': True,
            },
            
            # Calibration settings
            'calibration': {
                'range_expansion': 1.15,
                'smoothing_factor': 0.1,
                'corner_boost': 1.1,
                'edge_threshold': 0.15,
            },
            
            # Voice control settings
            'voice_control': {
                'audio_feedback': True,
                'use_tts': True,
                'microphone_index': None,  # None = auto-select
            },
            
            # UI settings
            'ui': {
                'show_debug': True,
                'window_width': 700,
                'window_height': 800,
            },
            
            # System settings
            'system': {
                'auto_start_eye_tracking': False,
                'auto_start_voice_control': False,
                'load_calibration_on_start': True,
            }
        }
        
        # Current settings (will be loaded or set to defaults)
        self.settings = {}
        
        # Load settings or use defaults
        self.load_settings()
    
    def get(self, category, key, default=None):
        """
        Get a setting value
        
        Args:
            category: Setting category (e.g., 'eye_tracking')
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            return self.settings[category][key]
        except KeyError:
            if default is not None:
                return default
            return self.defaults.get(category, {}).get(key)
    
    def set(self, category, key, value):
        """
        Set a setting value
        
        Args:
            category: Setting category
            key: Setting key
            value: New value
        """
        if category not in self.settings:
            self.settings[category] = {}
        
        self.settings[category][key] = value
    
    def get_all(self):
        """Get all settings"""
        return self.settings
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = json.loads(json.dumps(self.defaults))  # Deep copy
        print("Settings reset to defaults")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings saved to {self.settings_path}")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self):
        """Load settings from file"""
        if not os.path.exists(self.settings_path):
            print(f"No settings file found, using defaults")
            self.reset_to_defaults()
            self.save_settings()
            return False
        
        try:
            with open(self.settings_path, 'r') as f:
                loaded = json.load(f)
            
            # Merge with defaults (in case new settings were added)
            self.settings = json.loads(json.dumps(self.defaults))  # Start with defaults
            
            # Update with loaded values
            for category, values in loaded.items():
                if category in self.settings:
                    self.settings[category].update(values)
            
            print(f"Settings loaded from {self.settings_path}")
            return True
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.reset_to_defaults()
            return False
    
    def export_settings(self, export_path):
        """
        Export settings to a file
        
        Args:
            export_path: Path to export to
            
        Returns:
            bool: Success
        """
        try:
            with open(export_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings exported to {export_path}")
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def import_settings(self, import_path):
        """
        Import settings from a file
        
        Args:
            import_path: Path to import from
            
        Returns:
            bool: Success
        """
        try:
            with open(import_path, 'r') as f:
                imported = json.load(f)
            
            self.settings = imported
            self.save_settings()
            print(f"Settings imported from {import_path}")
            return True
        except Exception as e:
            print(f"Import failed: {e}")
            return False


if __name__ == "__main__":
    """Test settings module"""
    settings = Settings()
    
    print("\nCurrent Settings:")
    print(json.dumps(settings.get_all(), indent=2))
    
    print("\n🔧 Testing get/set:")
    print(f"Eye tracking buffer size: {settings.get('eye_tracking', 'smooth_buffer_size')}")
    
    settings.set('eye_tracking', 'smooth_buffer_size', 30)
    print(f"After change: {settings.get('eye_tracking', 'smooth_buffer_size')}")
    
    print("\nSaving...")
    settings.save_settings()
    
    print("\nSettings test complete!")