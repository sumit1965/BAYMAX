# 🤖 BAYMAX Healthcare Assistant

**Your Personal Healthcare Companion** - Inspired by the healthcare robot from *Big Hero 6*

BAYMAX is an intelligent AI healthcare assistant that helps patients manage their medication schedules through advanced face recognition, voice interaction, and a friendly animated interface.

![BAYMAX Logo](assets/baymax_logo.png)

## ✨ Features

### 🎯 Core Functionality
- **🔊 Baymax Movie Voice Integration**: Authentic Baymax-like voice for all interactions
- **👤 Multi-User Registration System**: Support for multiple users with individual profiles
- **👁️ Face Recognition & Authentication**: Camera-based user identification for secure medicine confirmation
- **🗣️ Voice Commands & Emergency Override**: "Hey Baymax" wake word for hands-free operation
- **💊 Smart Medicine Scheduling**: Automated reminders with customizable schedules
- **📊 Medicine Intake Verification**: Comprehensive logging and adherence tracking
- **🎭 Animated GUI**: Friendly Baymax face with dynamic expressions

### 🚨 Safety Features
- **Emergency Voice Override**: When face recognition fails, voice authentication is available
- **Multiple Reminder System**: Up to 3 reminders with 20-second intervals
- **Missed Medicine Logging**: Comprehensive tracking for healthcare provider review
- **User Session Logging**: Complete audit trail of all interactions

## 🏗️ Architecture

```
BAYMAX/
├── src/
│   ├── face_recognition/     # Face detection and recognition
│   ├── voice_system/         # TTS and speech recognition
│   ├── medicine_system/      # Scheduling and reminders
│   ├── gui/                  # Animated interface
│   └── database/             # User management
├── data/                     # User data and logs
├── logs/                     # System logs
├── assets/                   # GUI assets
└── config/                   # Configuration files
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Webcam** (for face recognition)
- **Microphone** (for voice commands)
- **Speakers** (for voice output)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd workspace
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip python3-dev python3-opencv python3-numpy python3-pandas python3-pil portaudio19-dev
   ```

3. **Create and activate virtual environment:**
   ```bash
   python3 -m venv baymax_env
   source baymax_env/bin/activate
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### First Run

1. **Interactive Setup (Recommended):**
   ```bash
   python baymax_main.py --setup
   ```

2. **Direct Launch:**
   ```bash
   python baymax_main.py
   ```

## 📋 Usage Guide

### 🔧 Interactive Setup

The interactive setup allows you to:
- Register new users with face data
- Add medicine schedules
- Test voice and camera systems
- View system status

### 👤 User Registration

1. **Via Interactive Setup:**
   - Run `python baymax_main.py --setup`
   - Select option 1: "Register a new user"
   - Follow the prompts

2. **Via GUI:**
   - Click "Register User" button
   - Fill in user details
   - Complete face registration

### 💊 Medicine Scheduling

Schedule format:
- **Times**: HH:MM format (e.g., "08:00", "20:00")
- **Days**: All days by default, or specify specific days
- **Multiple medicines**: Each medicine gets its own schedule

Example:
```
User: John Doe
Medicine: Aspirin
Times: 08:00, 20:00
Days: Monday, Tuesday, Wednesday, Thursday, Friday
```

### 🔄 Medicine Reminder Flow

1. **Scheduled Time Reached**: BAYMAX wakes up and greets the user
2. **Face Recognition**: Camera attempts to identify the registered user
3. **Voice Confirmation**: If face recognition fails, voice override activates
4. **Medicine Confirmation**: User confirms medicine intake
5. **Logging**: All interactions are logged for healthcare tracking

### 🗣️ Voice Commands

- **"Hey Baymax"**: Wake up BAYMAX for emergency override
- **"Hello Baymax"**: Alternative wake command
- **"Baymax Help"**: Emergency assistance
- **"I took my medicine"**: Confirm medicine intake during voice mode

## 🎭 GUI Features

### Facial Expressions
- **Idle**: Normal, calm expression
- **Alert**: Wide eyes when reminding about medicine
- **Happy**: Smiling when medicine is confirmed taken
- **Concerned**: Worried expression for missed medicine
- **Speaking**: Animated mouth during voice output
- **Blinking**: Natural eye blinking animation

### Status Updates
- Real-time status messages
- Progress indicators for registration
- Medicine reminder notifications
- System health indicators

## 📊 Data Management

### User Data
- **SQLite Database**: Primary storage for user profiles
- **JSON Backup**: Compatibility and backup format
- **Face Encodings**: Secure storage of facial recognition data
- **Session Logs**: Complete interaction history

### Medicine Logs
- **CSV Format**: Easy integration with healthcare systems
- **Timestamps**: Precise timing of all medicine events
- **Methods**: Face recognition vs. voice confirmation tracking
- **Adherence Rates**: Automatic calculation of compliance

### Data Files
```
data/
├── baymax_users.db          # Main user database
├── users.json               # User data backup
├── face_encodings.pkl       # Face recognition data
├── medicine_schedules.json  # Medicine schedules
├── medicine_log.csv         # Medicine intake log
└── exports/                 # Data export files
```

## 🔧 Configuration

### Voice Settings
- **Rate**: Speech speed (default: 150 WPM)
- **Volume**: Audio level (default: 0.9)
- **Voice**: System voice selection (prefers male voices)

### Face Recognition
- **Tolerance**: Recognition sensitivity (default: 0.6)
- **Samples**: Number of face samples for registration (default: 5)
- **Camera**: Resolution and frame rate settings

### Medicine Reminders
- **Interval**: Time between reminders (default: 20 seconds)
- **Max Reminders**: Maximum attempts (default: 3)
- **Timeout**: Face recognition timeout (default: 30 seconds)

## 🛠️ Development

### Project Structure
```python
# Core Components
FaceRecognizer      # Face detection and recognition
BaymaxVoice        # Voice synthesis and recognition
MedicineScheduler  # Medicine scheduling system
BaymaxGUI         # Animated user interface
UserManager       # User database management
BaymaxAssistant   # Main application coordinator
```

### Adding New Features

1. **New Voice Phrases**: Add to `baymax_phrases` in `BaymaxVoice`
2. **GUI Expressions**: Add to `_draw_eyes()` and `_draw_mouth()` methods
3. **Medicine Types**: Extend `MedicineScheduler` with new fields
4. **User Fields**: Update database schema in `UserManager`

### Testing

```bash
# Test individual components
python -c "from src.voice_system.baymax_voice import BaymaxVoice; v = BaymaxVoice(); v.speak('Hello, I am BAYMAX')"
python -c "from src.face_recognition.face_recognizer import FaceRecognizer; f = FaceRecognizer(); f.initialize_camera()"
```

## 📈 Monitoring & Analytics

### System Status
```bash
# View system status in interactive mode
python baymax_main.py --setup
# Select option 5: "View system status"
```

### Medicine Adherence
- **Adherence Rate**: Percentage of medicines taken on time
- **Missed Medicines**: List of missed doses with timestamps
- **User Sessions**: Complete interaction history

### Export Data
```python
# Export user data to CSV
user_manager.export_user_data("backup.csv")

# Get medicine logs
logs = medicine_scheduler.get_medicine_log(user_name="john_doe", days=30)
```

## 🔒 Security & Privacy

### Data Protection
- **Local Storage**: All data stored locally, no cloud transmission
- **Face Data**: Encrypted facial encodings, not raw images
- **User Consent**: Explicit consent required for face registration
- **Data Retention**: Configurable data retention policies

### Access Control
- **Face Authentication**: Only registered users can confirm medicine
- **Emergency Override**: Voice authentication for accessibility
- **Session Logging**: Complete audit trail of all access

## 🚨 Troubleshooting

### Common Issues

**Camera Not Working:**
```bash
# Check camera permissions
ls /dev/video*
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

**Voice Not Working:**
```bash
# Check audio system
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

**Face Recognition Fails:**
- Ensure good lighting
- Position face clearly in camera view
- Re-register with more samples
- Check camera resolution settings

**Medicine Reminders Not Working:**
- Verify system time is correct
- Check medicine schedule format
- Ensure scheduler is running
- Review logs for errors

### Log Files
```bash
# System logs
tail -f logs/baymax.log

# Medicine logs
tail -f data/medicine_log.csv

# Error debugging
python baymax_main.py --debug
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black src/
flake8 src/
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Disney's Big Hero 6**: Inspiration for BAYMAX character and voice
- **OpenCV Community**: Computer vision capabilities
- **Face Recognition Library**: Facial recognition technology
- **pyttsx3**: Text-to-speech synthesis
- **SpeechRecognition**: Voice command processing

## 📞 Support

For support, please:
1. Check this README and troubleshooting section
2. Review the [FAQ](FAQ.md)
3. Open an issue on GitHub
4. Contact the development team

---

**"Hello. I am BAYMAX, your personal healthcare companion."**

*Stay healthy and never miss your medicine with BAYMAX!* 🏥💊🤖