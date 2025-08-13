# BAYMAX - Smart Healthcare Assistant 🤖💊

> *"Hello. I am Baymax, your personal healthcare companion."*

BAYMAX is an intelligent healthcare assistant inspired by the beloved robot from *Big Hero 6*. This system combines advanced facial recognition, voice synthesis, and medicine reminder capabilities to provide personalized healthcare support.

## 🌟 Features

### 🎭 Baymax Voice Integration
- **Authentic Voice**: Mimics Baymax's gentle, caring voice from the movie
- **Characteristic Speech**: Slow, gentle, and caring tone with proper pacing
- **Dynamic Responses**: Context-aware voice responses for different situations

### 👥 Multi-User Registration System
- **Face Registration**: Register users with facial data capture
- **User Management**: Support for multiple users with individual profiles
- **Persistent Storage**: User data saved in JSON format for persistence

### 🔍 Face Recognition & Authentication
- **Real-time Detection**: Continuous face recognition using camera feed
- **User Authentication**: Only registered users can interact with the system
- **Emergency Override**: Voice commands when face detection fails

### ⏰ Medicine Monitoring System
- **Scheduled Reminders**: Set multiple medicine times per day
- **Voice Alerts**: Baymax announces medicine times with his characteristic voice
- **Confirmation Tracking**: Automatic confirmation when user's face is detected
- **Missed Dose Logging**: Records missed medicines in CSV format

### 🎨 Animated GUI Interface
- **Baymax Face**: Animated facial expressions (idle, talking, alerting, sad)
- **Real-time Status**: Live status updates and user detection
- **Interactive Controls**: Easy-to-use buttons for registration and medicine management

### 🗣️ Voice-Activated Commands
- **Wake Phrases**: "Hey Baymax", "Hello Baymax"
- **Emergency Access**: Voice commands when face detection is unavailable
- **Natural Interaction**: Conversational interface with speech recognition

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Webcam for facial recognition
- Microphone for voice commands
- Speakers for Baymax's voice

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd BAYMAX
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: System Dependencies (Linux)
```bash
# Install system packages for face recognition
sudo apt-get update
sudo apt-get install cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
sudo apt-get install libboost-python-dev

# Install audio dependencies
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Step 4: Verify Installation
```bash
python utils.py
```
This will check all dependencies and system status.

## 🎯 Quick Start

### 1. Launch BAYMAX
```bash
python baymax_main.py
```

### 2. Register Your First User
1. Click "Register User" in the GUI
2. Enter your name
3. Click "Capture Face & Register"
4. Look at the camera when prompted

### 3. Add Medicine Schedule
1. Click "Add Medicine" in the GUI
2. Select your user name
3. Enter medicine name (e.g., "Blood Pressure Medicine")
4. Enter time in HH:MM format (e.g., "09:00")
5. Click "Save Schedule"

### 4. Test Voice Commands
- Say "Hey Baymax" to activate voice commands
- The system will respond with Baymax's characteristic voice

## 📋 Usage Guide

### User Registration
```
1. Open BAYMAX GUI
2. Click "Register User"
3. Enter name and capture face
4. Baymax will confirm registration
```

### Medicine Scheduling
```
1. Click "Add Medicine"
2. Select user from dropdown
3. Enter medicine name and time
4. Save schedule
5. Baymax will remind at scheduled times
```

### Voice Commands
```
Wake Phrases:
- "Hey Baymax"
- "Hello Baymax"
- "Baymax"

The system will respond and check for due medicines.
```

### Emergency Access
If face detection fails due to lighting or position:
1. Say "Hey Baymax" clearly
2. System will activate voice mode
3. You can still access medicine reminders

## 🔧 Configuration

### Voice Settings (`config.py`)
```python
VOICE_SETTINGS = {
    'rate': 150,          # Speech rate (words per minute)
    'volume': 0.8,        # Volume level (0.0 to 1.0)
    'pitch': 100,         # Voice pitch
    'voice_type': 'male'  # Preferred voice type
}
```

### Face Recognition Settings
```python
FACE_RECOGNITION_SETTINGS = {
    'tolerance': 0.6,     # Face matching tolerance (0.0 to 1.0)
    'frame_scale': 0.25,  # Frame scaling for processing
    'detection_interval': 0.1  # Detection interval in seconds
}
```

### Medicine Reminder Settings
```python
MEDICINE_SETTINGS = {
    'reminder_interval': 20,    # Seconds between reminders
    'max_reminders': 3,         # Maximum number of reminders
    'check_interval': 60,       # Check for due medicines every X seconds
}
```

## 📁 File Structure

```
BAYMAX/
├── baymax_main.py          # Main system file
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── users.json            # User database (created automatically)
├── medicine_schedule.json # Medicine schedules (created automatically)
├── missed_doses.csv      # Missed medicine log (created automatically)
└── baymax.log           # System logs (created automatically)
```

## 🎨 GUI Features

### Baymax's Animated Face
- **Idle**: Calm, friendly expression
- **Talking**: Animated mouth when speaking
- **Alerting**: Concerned expression for medicine reminders
- **Sad**: Disappointed expression for missed medicines

### Status Display
- Real-time user detection
- Current system status
- Medicine reminder status

### Control Buttons
- **Register User**: Add new users with face capture
- **Add Medicine**: Schedule medicine reminders
- **Emergency Call**: Manual voice command activation

## 🔍 Troubleshooting

### Common Issues

#### 1. Camera Not Working
```bash
# Check camera permissions
ls /dev/video*

# Test camera with OpenCV
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera available:', cap.isOpened())"
```

#### 2. Audio Issues
```bash
# Install audio dependencies
sudo apt-get install portaudio19-dev python3-pyaudio

# Test microphone
python -c "import speech_recognition as sr; print('Microphone available')"
```

#### 3. Face Recognition Errors
```bash
# Install face recognition dependencies
pip install dlib
pip install face-recognition

# If dlib fails, try:
sudo apt-get install cmake
sudo apt-get install libopenblas-dev liblapack-dev
```

#### 4. Voice Synthesis Issues
```bash
# Install text-to-speech dependencies
sudo apt-get install espeak

# Test voice synthesis
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
```

### System Status Check
```bash
python -c "from utils import print_system_status; print_system_status()"
```

## 📊 Data Management

### User Data (`users.json`)
```json
[
  {
    "name": "John Doe",
    "face_encoding": [0.123, 0.456, ...]
  }
]
```

### Medicine Schedule (`medicine_schedule.json`)
```json
{
  "John Doe": {
    "Blood Pressure Medicine": ["09:00", "21:00"],
    "Diabetes Medicine": ["08:00", "20:00"]
  }
}
```

### Missed Doses (`missed_doses.csv`)
```csv
user_name,medicine_name,scheduled_time,logged_time,status
John Doe,Blood Pressure Medicine,2024-01-15 09:00:00,2024-01-15 09:20:00,missed
```

## 🔒 Privacy & Security

- **Local Storage**: All data stored locally on your device
- **No Cloud**: No data transmitted to external servers
- **Face Data**: Facial encodings stored as numerical arrays
- **Secure**: No personal information shared

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Baymax from Disney's *Big Hero 6*
- Built with open-source libraries and tools
- Community contributions welcome

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review system logs in `baymax.log`
3. Run system status check
4. Create an issue in the repository

---

*"I am Baymax, your personal healthcare companion. I will always be here to help you."* 🤖💙