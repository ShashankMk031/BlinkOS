#!/usr/bin/env python3
"""
Settings Module - Enhanced with visual feedback and performance settings
Manages user preferences and configuration
"""

import json
import os
from pathlib import Path


class Settings:
    """
    Enhanced settings manager with visual feedback options
    """
    
    def __init__(self, settings_path='data/settings.json'):
        """Initialize settings manager"""
        self.settings_path = settings_path
        
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
                'safe_zone_margin': 50,
            },
            
            # Visual feedback settings (NEW!)
            'visual_feedback': {
                'show_crosshair': True,
                'crosshair_size': 20,
                'show_cursor_trail': True,
                'trail_length': 10,
                'show_status_overlay': True,
                'show_accuracy_meter': True,
                'click_animation': True,
                'animation_duration': 0.5,
            },
            
            # Calibration settings
            'calibration': {
                'range_expansion': 1.15,
                'smoothing_factor': 0.1,
                'corner_boost': 1.1,
                'edge_threshold': 0.15,
                'auto_adjust_threshold': True,
            },
            
            # Voice control settings
            'voice_control': {
                'audio_feedback': True,
                'use_tts': True,
                'microphone_index': None,  # None = auto-select
                'phrase_time_limit': 10,
                'timeout': 5,
            },
            
            # Performance settings (NEW!)
            'performance': {
                'target_fps': 30,
                'quality_preset': 'balanced',  # 'performance', 'balanced', 'quality'
                'enable_quartz': True,  # macOS Quartz acceleration
                'optimize_for_battery': False,
            },
            
            # UI settings
            'ui': {
                'show_debug': True,
                'window_width': 700,
                'window_height': 800,
                'theme': 'dark',  # 'dark' or 'light'
            },
            
            # System settings
            'system': {
                'auto_start_eye_tracking': False,
                'auto_start_voice_control': False,
                'load_calibration_on_start': True,
                'minimize_to_tray': False,
            }
        }
        
        # Current settings
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
    
    def get_category(self, category):
        """Get all settings in a category"""
        return self.settings.get(category, self.defaults.get(category, {}))
    
    def get_all(self):
        """Get all settings"""
        return self.settings
    
    def apply_performance_preset(self, preset):
        """
        Apply a performance preset
        
        Args:
            preset: 'performance', 'balanced', or 'quality'
        """
        presets = {
            'performance': {
                'target_fps': 60,
                'smooth_buffer_size': 15,
                'update_rate': 2,
                'show_cursor_trail': False,
                'click_animation': False,
            },
            'balanced': {
                'target_fps': 30,
                'smooth_buffer_size': 25,
                'update_rate': 3,
                'show_cursor_trail': True,
                'click_animation': True,
            },
            'quality': {
                'target_fps': 30,
                'smooth_buffer_size': 35,
                'update_rate': 4,
                'show_cursor_trail': True,
                'click_animation': True,
            }
        }
        
        if preset not in presets:
            print(f" Unknown preset: {preset}")
            return False
        
        config = presets[preset]
        
        self.set('performance', 'quality_preset', preset)
        self.set('performance', 'target_fps', config['target_fps'])
        self.set('eye_tracking', 'smooth_buffer_size', config['smooth_buffer_size'])
        self.set('eye_tracking', 'update_rate', config['update_rate'])
        self.set('visual_feedback', 'show_cursor_trail', config['show_cursor_trail'])
        self.set('visual_feedback', 'click_animation', config['click_animation'])
        
        print(f"Applied '{preset}' preset")
        return True
    
    def toggle_visual_effects(self, enabled):
        """Enable or disable all visual effects"""
        self.set('visual_feedback', 'show_crosshair', enabled)
        self.set('visual_feedback', 'show_cursor_trail', enabled)
        self.set('visual_feedback', 'show_status_overlay', enabled)
        self.set('visual_feedback', 'show_accuracy_meter', enabled)
        self.set('visual_feedback', 'click_animation', enabled)
        
        print(f" Visual effects: {'ON' if enabled else 'OFF'}")
    
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
            print(f"  No settings file found, using defaults")
            self.reset_to_defaults()
            self.save_settings()
            return False
        
        try:
            with open(self.settings_path, 'r') as f:
                loaded = json.load(f)
            
            # Start with defaults
            self.settings = json.loads(json.dumps(self.defaults))
            
            # Update with loaded values (merge)
            for category, values in loaded.items():
                if category in self.settings:
                    self.settings[category].update(values)
                else:
                    # New category not in defaults
                    self.settings[category] = values
            
            print(f" Settings loaded from {self.settings_path}")
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
            print(f" Import failed: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of current settings"""
        print("\n" + "="*60)
        print("  BLINKOS SETTINGS SUMMARY")
        print("="*60)
        
        print("\n  Eye Tracking:")
        print(f"  • Smoothing: {self.get('eye_tracking', 'smooth_buffer_size')}")
        print(f"  • Update Rate: {self.get('eye_tracking', 'update_rate')}")
        print(f"  • Click Enabled: {self.get('eye_tracking', 'click_enabled')}")
        print(f"  • Click Cooldown: {self.get('eye_tracking', 'click_cooldown')}s")
        
        print("\n Visual Feedback:")
        print(f"  • Crosshair: {self.get('visual_feedback', 'show_crosshair')}")
        print(f"  • Cursor Trail: {self.get('visual_feedback', 'show_cursor_trail')}")
        print(f"  • Status Overlay: {self.get('visual_feedback', 'show_status_overlay')}")
        print(f"  • Click Animation: {self.get('visual_feedback', 'click_animation')}")
        
        print("\n Calibration:")
        print(f"  • Range Expansion: {self.get('calibration', 'range_expansion')}")
        print(f"  • Smoothing Factor: {self.get('calibration', 'smoothing_factor')}")
        print(f"  • Corner Boost: {self.get('calibration', 'corner_boost')}")
        
        print("\n Performance:")
        print(f"  • Preset: {self.get('performance', 'quality_preset')}")
        print(f"  • Target FPS: {self.get('performance', 'target_fps')}")
        print(f"  • Quartz Enabled: {self.get('performance', 'enable_quartz')}")
        
        print("\n Voice Control:")
        print(f"  • Audio Feedback: {self.get('voice_control', 'audio_feedback')}")
        print(f"  • TTS Enabled: {self.get('voice_control', 'use_tts')}")
        
        print("\n System:")
        print(f"  • Auto-start Eye Tracking: {self.get('system', 'auto_start_eye_tracking')}")
        print(f"  • Auto-start Voice: {self.get('system', 'auto_start_voice_control')}")
        print(f"  • Load Calibration: {self.get('system', 'load_calibration_on_start')}")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    """Test settings module"""
    print("\n Testing Enhanced Settings Module\n")
    
    settings = Settings()
    
    # Print summary
    settings.print_summary()
    
    # Test performance presets
    print("\nTesting Performance Presets:")
    for preset in ['performance', 'balanced', 'quality']:
        print(f"\nApplying '{preset}' preset...")
        settings.apply_performance_preset(preset)
        print(f"  Smoothing: {settings.get('eye_tracking', 'smooth_buffer_size')}")
        print(f"  FPS Target: {settings.get('performance', 'target_fps')}")
    
    # Test visual effects toggle
    print("\nTesting Visual Effects Toggle:")
    settings.toggle_visual_effects(False)
    print(f"  Crosshair: {settings.get('visual_feedback', 'show_crosshair')}")
    settings.toggle_visual_effects(True)
    print(f"  Crosshair: {settings.get('visual_feedback', 'show_crosshair')}")
    
    # Save
    print("\nSaving settings...")
    settings.save_settings()
    
    print("\nSettings test complete!")