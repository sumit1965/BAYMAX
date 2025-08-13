# BAYMAX - Your Personal Healthcare Companion 🤖

> *"Hello. I am Baymax, your personal healthcare companion."*

BAYMAX is an intelligent healthcare assistant inspired by the beloved robot from *Big Hero 6*. This AI-powered system helps patients manage their medication schedules through voice interaction, facial recognition, and a friendly animated interface.

## 🌟 Features

### 🎤 Baymax Voice Integration
- **Authentic Voice**: Mimics Baymax's gentle, caring voice from the movie
- **Slow, Gentle Speech**: Configured to sound like the original character
- **Asynchronous Speech**: Non-blocking voice synthesis for smooth operation

### 👥 Multi-User Registration System
- **Facial Registration**: Capture and store user face data for recognition
- **Medicine Scheduling**: Set multiple daily medicine reminders per user
- **User Management**: View, edit, and manage registered users
- **Persistent Storage**: User data saved in JSON format

### 🔍 Face Recognition & Emergency Override
- **Real-time Recognition**: Continuous face detection using camera feed
- **User Authentication**: Only registered users can confirm medicine intake
- **Emergency Voice Commands**: Fallback to voice commands when face recognition fails
- **Visual Feedback**: Green rectangles highlight detected faces

### ⏰ Medicine Monitoring & Verification
- **Scheduled Reminders**: Automatic alerts at specified medicine times
- **Multiple Attempts**: Up to 3 reminder attempts with 20-second intervals
- **Confirmation Tracking**: Records when medicine is taken
- **Missed Dose Logging**: Tracks and reports missed medications

### 🎯 Voice-Activated & Face-Driven Flow
- **Wake Word**: "Hey Baymax" activates the system
- **Dual Authentication**: Face recognition + voice confirmation
- **Emergency Override**: Voice commands when face recognition fails
- **Smart Interaction**: Only speaks when necessary

### 🖥️ Beautiful GUI with Animated Expressions
- **Baymax Face**: Large animated emoji face with different expressions
- **Real-time Camera**: Live camera feed with face detection overlay
- **Status Indicators**: Voice recognition status and system state
- **Modern Design**: Dark theme with professional healthcare aesthetics

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Webcam for face recognition
- Microphone for voice commands (optional)
- Speakers for Baymax's voice

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BAYMAX
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run BAYMAX**
   ```bash
   # Basic version (without voice recognition)
   python baymax_main.py
   
   # Enhanced version (with voice recognition)
   python baymax_enhanced.py
   ```

## 📋 System Requirements

### Required Dependencies
- `opencv-python` - Camera and image processing
- `face-recognition` - Facial recognition library
- `numpy` - Numerical computing
- `Pillow` - Image processing
- `pyttsx3` - Text-to-speech synthesis
- `pandas` - Data manipulation
- `schedule` - Task scheduling
- `tkinter` - GUI framework (usually included with Python)

### Optional Dependencies (for voice recognition)
- `SpeechRecognition` - Voice command recognition
- `PyAudio` - Audio input/output

## 🎮 Usage Guide

### 1. Starting BAYMAX
When you launch BAYMAX, you'll see:
- Baymax's animated face (😐 idle expression)
- Live camera feed with face detection
- Control buttons for system management
- Status indicators

### 2. Registering Users
1. Click **"Register New User"**
2. Enter the user's name
3. Set medicine schedule (e.g., "08:00, 20:00")
4. Position face in camera view
5. Click **"Capture Face & Register"**

### 3. Medicine Reminders
- **Automatic**: BAYMAX wakes up at scheduled times
- **Face Recognition**: Looks for registered user's face
- **Voice Confirmation**: Says "Hey Baymax" if face not detected
- **Multiple Attempts**: Up to 3 reminders with 20-second intervals
- **Confirmation**: Records when medicine is taken

### 4. Voice Commands
- **"Hey Baymax"** - Wake up the system
- **"I took my medicine"** - Confirm medicine intake
- **"Help"** - Get assistance information
- **"Goodbye"** - Put BAYMAX to sleep

### 5. Monitoring
- **View Users**: See all registered users and their schedules
- **View Missed Doses**: Check missed medication reports
- **Voice Status**: Monitor voice recognition availability

## 🎨 Baymax's Expressions

BAYMAX displays different facial expressions based on system state:

- **😐 Idle** - System ready, waiting
- **😊 Happy** - Medicine confirmed, user helped
- **😮 Alert** - Medicine reminder, attention needed
- **😔 Sad** - Medicine missed, concern
- **🤔 Waiting** - Waiting for user response
- **🧐 Thinking** - Processing information

## 📊 Data Storage

### User Data (`users.json`)
```json
{
  "1": {
    "name": "John Doe",
    "face_encoding": [...],
    "medicine_schedule": ["08:00", "20:00"],
    "last_medicine_time": "2024-01-15T08:05:00",
    "missed_doses": [...],
    "registration_date": "2024-01-01T10:00:00"
  }
}
```

### Missed Doses (`missed_alerts.csv`)
- User ID, Name, Scheduled Time, Missed Time, Date, Alert Attempts

## 🔧 Configuration

### Voice Settings
- **Rate**: 140 (slower, more Baymax-like)
- **Volume**: 0.9 (clear but not overwhelming)
- **Pitch**: 100 (natural male voice)

### Face Recognition
- **Tolerance**: 0.6 (balanced accuracy)
- **Detection**: Real-time with visual feedback
- **Fallback**: Voice commands when face not detected

### Medicine Reminders
- **Max Attempts**: 3 per scheduled time
- **Retry Interval**: 20 seconds
- **Confirmation Timeout**: 20 seconds for voice commands

## 🛠️ Troubleshooting

### Common Issues

1. **Camera not working**
   - Check camera permissions
   - Ensure no other application is using the camera
   - Try different camera index (change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`)

2. **Voice recognition not working**
   - Install PyAudio: `pip install PyAudio`
   - Check microphone permissions
   - Ensure microphone is not muted

3. **Face recognition errors**
   - Ensure good lighting
   - Position face clearly in camera view
   - Check if face_recognition library is properly installed

4. **Medicine reminders not triggering**
   - Check system time is correct
   - Verify medicine schedule format (HH:MM)
   - Ensure BAYMAX is running continuously

### Performance Tips
- **Close unnecessary applications** to free up system resources
- **Good lighting** improves face recognition accuracy
- **Clear speech** enhances voice command recognition
- **Regular restarts** if running for extended periods

## 🔒 Privacy & Security

- **Local Storage**: All data stored locally on your device
- **No Cloud Upload**: No personal data sent to external servers
- **Face Data**: Encoded face data stored securely in JSON format
- **Optional Voice**: Voice recognition can be disabled if preferred

## 🤝 Contributing

We welcome contributions to improve BAYMAX! Areas for enhancement:
- Additional voice commands
- More facial expressions
- Health monitoring features
- Mobile app integration
- Multi-language support

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by the wonderful character Baymax from *Big Hero 6*
- Built with love for healthcare and technology
- Special thanks to the open-source community

---

*"I am satisfied with my care."* - Baymax

**BAYMAX** - Making healthcare more personal, one reminder at a time. 🤖💙