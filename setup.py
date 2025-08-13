#!/usr/bin/env python3
"""
BAYMAX Setup Script
Helps users install dependencies and configure the healthcare assistant
"""

import subprocess
import sys
import os
import platform

def print_banner():
    """Print BAYMAX setup banner"""
    print("=" * 60)
    print("🤖 BAYMAX - Your Personal Healthcare Companion")
    print("=" * 60)
    print("Setup and Installation Script")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def install_package(package):
    """Install a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    # Core requirements
    core_packages = [
        "opencv-python==4.8.1.78",
        "face-recognition==1.3.0",
        "numpy==1.24.3",
        "Pillow==10.0.0",
        "pyttsx3==2.90",
        "pandas==2.0.3",
        "schedule==1.2.0"
    ]
    
    # Voice recognition packages (optional)
    voice_packages = [
        "SpeechRecognition==3.10.0",
        "PyAudio==0.2.11"
    ]
    
    print("Installing core packages...")
    for package in core_packages:
        print(f"   Installing {package}...")
        if install_package(package):
            print(f"   ✅ {package} installed successfully")
        else:
            print(f"   ❌ Failed to install {package}")
            return False
    
    print("\nInstalling voice recognition packages (optional)...")
    voice_success = True
    for package in voice_packages:
        print(f"   Installing {package}...")
        if install_package(package):
            print(f"   ✅ {package} installed successfully")
        else:
            print(f"   ⚠️  Failed to install {package} (voice recognition will be disabled)")
            voice_success = False
    
    return True, voice_success

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["data", "logs", "backups"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created {directory}/ directory")
        else:
            print(f"   ℹ️  {directory}/ directory already exists")

def test_imports():
    """Test if all packages can be imported"""
    print("\n🧪 Testing package imports...")
    
    packages = [
        ("cv2", "OpenCV"),
        ("face_recognition", "Face Recognition"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("pyttsx3", "Text-to-Speech"),
        ("pandas", "Pandas"),
        ("schedule", "Schedule")
    ]
    
    all_success = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"   ✅ {name} imported successfully")
        except ImportError:
            print(f"   ❌ Failed to import {name}")
            all_success = False
    
    # Test voice recognition separately
    try:
        import speech_recognition
        print("   ✅ Speech Recognition imported successfully")
    except ImportError:
        print("   ⚠️  Speech Recognition not available (voice commands will be disabled)")
    
    return all_success

def test_camera():
    """Test camera access"""
    print("\n📷 Testing camera access...")
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            print("   ✅ Camera access successful")
            camera.release()
            return True
        else:
            print("   ⚠️  Camera not accessible (face recognition will be limited)")
            return False
    except Exception as e:
        print(f"   ❌ Camera test failed: {e}")
        return False

def test_voice():
    """Test voice synthesis"""
    print("\n🎤 Testing voice synthesis...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("   ✅ Voice synthesis initialized successfully")
        return True
    except Exception as e:
        print(f"   ❌ Voice synthesis test failed: {e}")
        return False

def create_config_file():
    """Create a configuration file"""
    print("\n⚙️  Creating configuration file...")
    
    config_content = """# BAYMAX Configuration File

[Voice]
# Voice synthesis settings
rate = 140
volume = 0.9
pitch = 100

[Face_Recognition]
# Face recognition settings
tolerance = 0.6
camera_index = 0

[Medicine_Reminders]
# Medicine reminder settings
max_attempts = 3
retry_interval = 20
confirmation_timeout = 20

[System]
# System settings
log_level = INFO
backup_interval = 24
"""
    
    try:
        with open("baymax_config.ini", "w") as f:
            f.write(config_content)
        print("   ✅ Configuration file created: baymax_config.ini")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create configuration file: {e}")
        return False

def run_demo():
    """Ask user if they want to run the demo"""
    print("\n🎮 Would you like to run the BAYMAX demo?")
    print("   This will show you the interface without requiring camera or microphone.")
    
    while True:
        response = input("   Run demo? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n🚀 Starting BAYMAX demo...")
            try:
                subprocess.run([sys.executable, "demo.py"])
            except Exception as e:
                print(f"   ❌ Failed to start demo: {e}")
            break
        elif response in ['n', 'no']:
            print("   Demo skipped.")
            break
        else:
            print("   Please enter 'y' or 'n'")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 BAYMAX Setup Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Run the demo: python demo.py")
    print("2. Run basic version: python baymax_main.py")
    print("3. Run enhanced version: python baymax_enhanced.py")
    print("\n📖 Documentation:")
    print("- Read README.md for detailed usage instructions")
    print("- Check the troubleshooting section if you encounter issues")
    print("\n🎯 Features Available:")
    print("- ✅ Multi-user registration")
    print("- ✅ Medicine scheduling")
    print("- ✅ Face recognition (if camera available)")
    print("- ✅ Voice synthesis")
    print("- ✅ Beautiful GUI with animated expressions")
    print("- ⚠️  Voice commands (requires SpeechRecognition)")
    print("\n💡 Tips:")
    print("- Ensure good lighting for face recognition")
    print("- Speak clearly for voice commands")
    print("- Keep BAYMAX running for continuous medicine reminders")
    print("\n" + "=" * 60)
    print("🤖 BAYMAX is ready to help you!")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install packages
    success, voice_success = install_requirements()
    if not success:
        print("\n❌ Failed to install core packages. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Test imports
    if not test_imports():
        print("\n❌ Some packages failed to import. Please check the installation.")
        sys.exit(1)
    
    # Test hardware
    camera_available = test_camera()
    voice_available = test_voice()
    
    # Create configuration
    create_config_file()
    
    # Print status
    print("\n📊 Installation Summary:")
    print(f"   ✅ Core packages: Installed")
    print(f"   {'✅' if voice_success else '⚠️'} Voice recognition: {'Available' if voice_success else 'Not available'}")
    print(f"   {'✅' if camera_available else '⚠️'} Camera: {'Available' if camera_available else 'Not available'}")
    print(f"   {'✅' if voice_available else '⚠️'} Voice synthesis: {'Available' if voice_available else 'Not available'}")
    
    # Ask about demo
    run_demo()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()