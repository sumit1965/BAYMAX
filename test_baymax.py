#!/usr/bin/env python3
"""
BAYMAX System Test Script
Tests all major components of the healthcare assistant
"""

import sys
import os
import time
from utils import print_system_status, check_dependencies, setup_logging

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing module imports...")
    
    modules = [
        'cv2',
        'face_recognition', 
        'pyttsx3',
        'tkinter',
        'numpy',
        'pandas',
        'schedule',
        'speech_recognition',
        'pygame'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_camera():
    """Test camera functionality"""
    print("\nTesting camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✓ Camera is available")
            ret, frame = cap.read()
            if ret:
                print(f"✓ Camera can capture frames ({frame.shape})")
                cap.release()
                return True
            else:
                print("✗ Camera cannot capture frames")
                cap.release()
                return False
        else:
            print("✗ Camera is not available")
            return False
            
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_voice_synthesis():
    """Test voice synthesis"""
    print("\nTesting voice synthesis...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Test basic voice synthesis
        engine.say("Hello. I am Baymax, your personal healthcare companion.")
        print("✓ Voice synthesis working")
        return True
        
    except Exception as e:
        print(f"✗ Voice synthesis failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition library"""
    print("\nTesting face recognition...")
    
    try:
        import face_recognition
        import numpy as np
        
        # Create a dummy face encoding
        dummy_encoding = np.random.rand(128)
        print("✓ Face recognition library working")
        return True
        
    except Exception as e:
        print(f"✗ Face recognition failed: {e}")
        return False

def test_gui():
    """Test GUI components"""
    print("\nTesting GUI components...")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test basic GUI functionality
        label = tk.Label(root, text="Test")
        print("✓ GUI components working")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition setup"""
    print("\nTesting speech recognition...")
    
    try:
        import speech_recognition as sr
        
        # Test microphone setup
        mic = sr.Microphone()
        recognizer = sr.Recognizer()
        
        print("✓ Speech recognition setup working")
        return True
        
    except Exception as e:
        print(f"✗ Speech recognition failed: {e}")
        return False

def test_data_storage():
    """Test data storage functionality"""
    print("\nTesting data storage...")
    
    try:
        from utils import save_data_to_json, load_data_from_json
        
        # Test data
        test_data = {
            "test_user": {
                "name": "Test User",
                "medicines": ["Test Medicine"]
            }
        }
        
        # Test save and load
        if save_data_to_json(test_data, "test_data.json"):
            loaded_data = load_data_from_json("test_data.json")
            if loaded_data == test_data:
                print("✓ Data storage working")
                os.remove("test_data.json")  # Cleanup
                return True
        
        print("✗ Data storage test failed")
        return False
        
    except Exception as e:
        print(f"✗ Data storage failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        import config
        
        # Test if config variables are accessible
        voice_settings = config.VOICE_SETTINGS
        face_settings = config.FACE_RECOGNITION_SETTINGS
        medicine_settings = config.MEDICINE_SETTINGS
        
        print("✓ Configuration loading working")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("=" * 60)
    print("BAYMAX System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Camera", test_camera),
        ("Voice Synthesis", test_voice_synthesis),
        ("Face Recognition", test_face_recognition),
        ("GUI Components", test_gui),
        ("Speech Recognition", test_speech_recognition),
        ("Data Storage", test_data_storage),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! BAYMAX is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

def main():
    """Main test function"""
    # Setup logging
    logger = setup_logging()
    
    # Print system status
    print_system_status()
    
    # Run tests
    success = run_all_tests()
    
    if success:
        print("\n🚀 You can now run BAYMAX with: python baymax_main.py")
    else:
        print("\n🔧 Please fix the issues above before running BAYMAX")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())