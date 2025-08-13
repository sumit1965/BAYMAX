"""
BAYMAX Configuration File
Contains all settings and parameters for the healthcare assistant
"""

# Voice Settings
VOICE_SETTINGS = {
    'rate': 150,          # Speech rate (words per minute)
    'volume': 0.8,        # Volume level (0.0 to 1.0)
    'pitch': 100,         # Voice pitch
    'voice_type': 'male'  # Preferred voice type
}

# Face Recognition Settings
FACE_RECOGNITION_SETTINGS = {
    'tolerance': 0.6,     # Face matching tolerance (0.0 to 1.0)
    'frame_scale': 0.25,  # Frame scaling for processing
    'detection_interval': 0.1  # Detection interval in seconds
}

# Medicine Reminder Settings
MEDICINE_SETTINGS = {
    'reminder_interval': 20,    # Seconds between reminders
    'max_reminders': 3,         # Maximum number of reminders
    'check_interval': 60,       # Check for due medicines every X seconds
}

# GUI Settings
GUI_SETTINGS = {
    'window_width': 800,
    'window_height': 600,
    'face_size': 400,
    'colors': {
        'background': '#2C3E50',
        'secondary': '#34495E',
        'text': '#ECF0F1',
        'primary_button': '#3498DB',
        'danger_button': '#E74C3C',
        'warning_button': '#F39C12'
    }
}

# Voice Commands
VOICE_COMMANDS = {
    'wake_phrases': ['hey baymax', 'hello baymax', 'baymax'],
    'medicine_confirm': ['yes', 'taken', 'done', 'confirm'],
    'emergency_phrases': ['help', 'emergency', 'urgent']
}

# File Paths
FILE_PATHS = {
    'users_db': 'users.json',
    'medicine_schedule': 'medicine_schedule.json',
    'missed_doses': 'missed_doses.csv',
    'logs': 'baymax_logs.txt'
}

# Camera Settings
CAMERA_SETTINGS = {
    'device_id': 0,       # Camera device ID
    'width': 640,         # Camera width
    'height': 480,        # Camera height
    'fps': 30            # Frames per second
}

# Logging Settings
LOGGING_SETTINGS = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'baymax.log'
}

# Baymax Personality Settings
PERSONALITY_SETTINGS = {
    'greeting_templates': [
        "Hello {name}. I am Baymax, your personal healthcare companion.",
        "Greetings {name}. I am Baymax, here to assist with your healthcare needs.",
        "Hello {name}. I am Baymax, your healthcare assistant."
    ],
    'medicine_reminder_templates': [
        "Hello {name}. It is time for your {medicine}. Please take it now.",
        "{name}, your {medicine} is due. Please take it at this time.",
        "Hello. My name is Baymax, your personal healthcare companion. It's time for your {medicine}. Please take it now."
    ],
    'confirmation_templates': [
        "Thank you {name}. I have recorded that you have taken your medicine.",
        "Excellent {name}. Your medicine intake has been confirmed.",
        "Thank you {name}. I have logged your medicine consumption."
    ],
    'missed_medicine_templates': [
        "I notice you have not confirmed taking your {medicine}. Please take it as soon as possible.",
        "{name}, please remember to take your {medicine}. It is important for your health.",
        "Your {medicine} is still pending. Please take it when convenient."
    ]
}