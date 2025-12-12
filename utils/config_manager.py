#!/usr/bin/env python3
"""
Configuration Manager for BlinkOS
Handles loading and saving configuration files
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """
    Manages configuration files for BlinkOS
    Provides easy access to configuration values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file (default: data/settings.json)
        """
        if config_file is None:
            # Default to data/settings.json
            project_root = Path(__file__).parent.parent
            config_file = project_root / "data" / "settings.json"
        
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                return True
            else:
                # Create default configuration
                self.config = self._get_default_config()
                self.save()
                return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'eye_tracking.smooth_buffer_size')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            "eye_tracking": {
                "smooth_buffer_size": 30,
                "update_rate": 2,
                "click_cooldown": 1.0,
                "blink_threshold": 0.21
            },
            "calibration": {
                "range_expansion": 1.2,
                "smoothing_factor": 0.2,
                "corner_boost": 1.1
            },
            "voice_control": {
                "language": "en-US",
                "timeout": 5,
                "phrase_time_limit": 10
            },
            "system": {
                "auto_start_eye_tracking": False,
                "auto_start_voice_control": False,
                "load_calibration_on_start": True,
                "log_level": "INFO"
            },
            "ui": {
                "theme": "light",
                "window_width": 650,
                "window_height": 800
            }
        }
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults
        
        Returns:
            True if successful, False otherwise
        """
        self.config = self._get_default_config()
        return self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()


# Global instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """
    Get the global configuration manager instance
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """
    Convenience function to get configuration value
    
    Args:
        key: Configuration key
        default: Default value
        
    Returns:
        Configuration value
    """
    manager = get_config_manager()
    return manager.get(key, default)


def set_config(key: str, value: Any) -> bool:
    """
    Convenience function to set configuration value
    
    Args:
        key: Configuration key
        value: Value to set
        
    Returns:
        True if successful
    """
    manager = get_config_manager()
    return manager.set(key, value)
