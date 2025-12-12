# BlinkOS Data Directory

This directory stores runtime data, user settings, and calibration profiles for BlinkOS.

## Contents

### Files
- `settings.json` - User preferences and configuration (auto-generated)
- `calibration.pkl` - Saved calibration data (auto-generated)

### Directory Structure
```
data/
├── calibration.pkl     # Eye tracking calibration data
├── settings.json       # Application settings
└── README.md          # This file
```

## Important Notes

**Do not commit personal data files to version control**

The following files are automatically generated and should not be committed:
- `calibration.pkl` - Contains user-specific calibration data
- `settings.json` - Contains user preferences

These files are already excluded in `.gitignore`.

## Default Settings

On first run, BlinkOS will create `settings.json` with default values:

```json
{
  "eye_tracking": {
    "smooth_buffer_size": 30,
    "update_rate": 2,
    "click_cooldown": 1.0
  },
  "calibration": {
    "range_expansion": 1.2,
    "smoothing_factor": 0.2,
    "corner_boost": 1.1
  },
  "system": {
    "auto_start_eye_tracking": false,
    "auto_start_voice_control": false,
    "load_calibration_on_start": true
  }
}
```

## Calibration Data

Calibration data is stored in pickle format and includes:
- Face position mapping
- Screen coordinate transformation
- User-specific adjustment factors

To reset calibration:
1. Delete `calibration.pkl`
2. Restart BlinkOS
3. Run calibration from Settings window

## Backup

To backup your settings and calibration:
```bash
cp data/settings.json data/settings.backup.json
cp data/calibration.pkl data/calibration.backup.pkl
```

To restore:
```bash
cp data/settings.backup.json data/settings.json
cp data/calibration.backup.pkl data/calibration.pkl
```
