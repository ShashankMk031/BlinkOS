# BlinkOS - Hands-Free Computer Control System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**BlinkOS** is an accessibility-focused application that enables completely hands-free computer control through eye tracking and voice commands. Perfect for users with mobility impairments or anyone seeking alternative input methods.

![BlinkOS Demo](assets/demo-screenshot.png)

## Features

### Eye Tracking
- **Head Movement Control**: Move your cursor by moving your head
- **Blink to Click**: Blink your eyes to perform mouse clicks
- **Adaptive Calibration**: Auto-adjusting sensitivity and thresholds
- **Visual Feedback**: Real-time tracking quality indicators
- **Customizable Settings**: Adjust smoothing, sensitivity, and click cooldown

### Voice Control
- **46+ Voice Commands** across multiple categories:
  - **Applications**: Open Safari, Chrome, Firefox, Notes, Terminal, Mail, Finder, Messages, Calendar
  - **Window Management**: Close, minimize, maximize, full screen, new tab/window
  - **Navigation**: Scroll, page up/down, go back/forward, refresh
  - **System Controls**: Volume, brightness, screenshots, sleep
  - **Dictation Mode**: Type text by speaking
  - **Web Search**: Voice-activated Google searches

### Modern UI
- Clean, professional interface with modern design
- Real-time activity logging
- Status indicators for all systems
- Comprehensive settings panel
- Built-in help and demo scenarios

## Installation

### Prerequisites
- **macOS** (tested on macOS 10.14+)
- **Python 3.8+**
- **Webcam** for eye tracking
- **Microphone** for voice control

### System Dependencies

Install PortAudio for audio support:
```bash
brew install portaudio
```

### Python Dependencies

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BlinkOS.git
cd BlinkOS
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. Launch the control panel:
```bash
python3 main.py
```

2. Click **"Start Both Systems"** for full hands-free control, or start eye tracking and voice control individually.

### Eye Tracking Controls

- **Move Head**: Control cursor position
- **Blink**: Perform mouse click
- **Press 'Q'**: Quit eye tracking
- **Press 'K'**: Toggle click mode on/off
- **Press '+/-'**: Adjust sensitivity

### Voice Commands Examples

```
"open safari"           # Launch Safari browser
"search machine learning"  # Google search
"scroll down"           # Scroll page down
"new tab"              # Open new browser tab
"volume up"            # Increase system volume
"take screenshot"      # Capture screenshot
"type"                 # Enter dictation mode
"stop typing"          # Exit dictation mode
"help"                 # List all commands
"exit"                 # Quit voice control
```

### Calibration

For best results:
1. Sit ~50cm from your webcam
2. Ensure good front lighting (avoid backlighting)
3. Run calibration from Settings window
4. Save calibration profile for future use

## Project Structure

```
BlinkOS/
├── main.py                 # Main application controller
├── modules/
│   ├── eye_tracker.py      # Eye tracking system
│   ├── voice_controller.py # Voice command system
│   ├── calibration.py      # Calibration engine
│   ├── settings.py         # Settings manager
│   ├── error_handler.py    # Error handling
│   └── logger.py           # Logging system
├── utils/
│   ├── audio_feedback.py   # Audio feedback utilities
│   ├── config_manager.py   # Configuration management
│   └── logger.py           # Logging utilities
├── tests/                  # Test suite
├── data/                   # Runtime data (calibration, settings)
├── logs/                   # Application logs
├── assets/                 # Images and resources
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Configuration

Settings can be adjusted through the GUI Settings window or by editing `data/settings.json`:

### Eye Tracking Settings
- `smooth_buffer_size`: Cursor smoothing (10-50)
- `update_rate`: Cursor update frequency (1-5)
- `click_cooldown`: Time between clicks (0.5-2.0s)

### Calibration Settings
- `range_expansion`: Screen coverage (1.0-1.5)
- `smoothing_factor`: Calibration smoothing (0.0-0.5)
- `corner_boost`: Edge sensitivity (1.0-1.5)

### System Settings
- `auto_start_eye_tracking`: Auto-start on launch
- `auto_start_voice_control`: Auto-start on launch
- `load_calibration_on_start`: Load saved calibration

## Troubleshooting

### Eye Tracking Issues
- **Not detecting face**: Improve lighting, adjust camera angle
- **Cursor jittery**: Increase smoothing in settings
- **Can't reach corners**: Increase range expansion in calibration
- **Clicks not registering**: Adjust click cooldown, blink more deliberately

### Voice Control Issues
- **Commands not recognized**: Speak clearly, reduce background noise
- **Microphone not working**: Check system permissions
- **Wrong microphone selected**: Use microphone selection in voice controller

### Performance Issues
- **Slow/laggy**: Close other applications, reduce smoothing
- **High CPU usage**: Adjust update rate in settings
- **Camera lag**: Reduce resolution or frame rate

## Development

### Running Tests
```bash
python3 -m pytest tests/
```

### Code Style
This project follows PEP 8 style guidelines. Format code with:
```bash
black .
flake8 .
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **MediaPipe** for face mesh detection
- **OpenCV** for computer vision capabilities
- **SpeechRecognition** for voice input
- **PyAutoGUI** for system automation

## Roadmap

- [ ] Cross-platform support (Windows, Linux)
- [ ] Gesture recognition for additional controls
- [ ] Multi-language voice command support
- [ ] Cloud-based calibration profiles
- [ ] Mobile companion app
- [ ] Advanced macro system
- [ ] Plugin architecture for extensibility

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub


---

**THANK YOU**
