# Changelog

All notable changes to Blink & Speak OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned Features
- Head gesture recognition (nod for yes, shake for no)
- Facial expression commands (smile, raise eyebrows)
- Multi-language voice command support
- Custom command builder UI
- Multi-user profile management
- Cloud sync for calibration profiles
- Mobile companion app
- Windows and Linux support

---

## [0.1.0] - 2024-11-08 - Hackathon Release 🎉

**Status**: Initial MVP Release for Hackathon Demo  
**Codename**: "First Blink"

### Added
- **Eye Tracking System**
  - Real-time face detection using MediaPipe Face Mesh
  - Gaze-based cursor control with <100ms latency
  - Eye Aspect Ratio (EAR) based blink detection
  - Blink-to-click functionality with >90% accuracy
  - 9-point calibration system with profile persistence
  - Cursor smoothing with 5-frame moving average buffer
  - Support for 720p+ webcam input at 25-30 FPS

- **Voice Control System**
  - Google Speech API integration for voice recognition
  - 20+ predefined voice commands
  - Application control (open, close, minimize, maximize)
  - Window and tab management
  - Navigation commands (scroll, back, forward)
  - System controls (volume, brightness, screenshot)
  - Web search functionality
  - Text-to-speech audio feedback

- **Voice Dictation Mode**
  - Continuous speech-to-text transcription
  - Punctuation commands (period, comma, question mark, etc.)
  - Basic editing commands (delete word, delete sentence, undo)
  - Enter/exit dictation mode via voice
  - Real-time typing into active application

- **Main Controller & Integration**
  - Concurrent operation of eye tracking and voice control via threading
  - Three operation modes: Eye-only, Voice-only, Hybrid
  - Mode switching via GUI or voice command
  - Startup calibration loading
  - Graceful shutdown of all systems

- **GUI Control Panel**
  - Tkinter-based user interface
  - Start/stop buttons for each module
  - Visual mode indicators
  - Status display panel
  - Calibration button with guided process
  - Settings access
  - Activity log display

- **Settings & Configuration**
  - JSON-based settings persistence
  - Adjustable eye tracking sensitivity
  - Configurable blink threshold
  - Voice recognition confidence adjustment
  - Audio feedback toggle
  - Reset to defaults option

- **Error Handling**
  - Camera disconnection detection and handling
  - Microphone issue detection
  - Automatic recovery mechanisms
  - Comprehensive error logging
  - User-friendly error messages

- **Documentation**
  - README with setup instructions
  - PLAN.md with development roadmap
  - REQUIREMENTS.md with technical specs
  - TODO.md with task tracking
  - PRD.md with product requirements
  - DEMO.md with demo scenarios
  - ARCHITECTURE.md with system design
  - Inline code comments and docstrings

- **Demo Scenarios**
  - Scenario 1: Web browsing with eye navigation and voice search
  - Scenario 2: Document creation with dictation
  - Scenario 3: Media control with voice commands
  - Recorded backup demo video

### Technical Details
- Python 3.10/3.11 support
- MacOS Monterey (12.0)+ compatibility
- OpenCV 4.8+ for computer vision
- MediaPipe 0.10+ for face mesh detection
- PyAutoGUI for cursor automation
- PyObjC for MacOS system integration
- SpeechRecognition 3.10+ for voice input
- pyttsx3 2.90 for text-to-speech
- NumPy for mathematical computations
- Tkinter for GUI

### Performance
- Eye tracking at 25-30 FPS
- Cursor latency <100ms
- Voice command execution <1s
- CPU usage <30%
- Memory usage <200MB
- Stable 30+ minute operation

### Known Issues
- Eye tracking accuracy decreases in low lighting conditions
- Voice recognition requires internet connection (Google API)
- Calibration needed after significant position changes
- Limited to single monitor setup
- Works best with front-facing lighting

---

## Changelog Guidelines

This section explains how to maintain this changelog file.

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New features (backwards compatible)
- **PATCH** version (0.0.X): Bug fixes (backwards compatible)

### Categories

Changes should be grouped in the following categories:

#### `Added`
For new features.

**Example:**
```markdown
### Added
- Voice command "open terminal" to launch Terminal app
- Support for Spanish language commands
- Keyboard shortcuts for mode switching
```

#### `Changed`
For changes in existing functionality.

**Example