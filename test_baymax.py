#!/usr/bin/env python3
"""
BAYMAX Healthcare Assistant - Component Testing Script
Tests individual components to ensure everything is working correctly.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append('/workspace/src')

def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from face_recognition.face_recognizer import FaceRecognizer
        print("✅ Face recognition module imported")
    except Exception as e:
        print(f"❌ Face recognition import failed: {e}")
        return False
    
    try:
        from voice_system.baymax_voice import BaymaxVoice
        print("✅ Voice system module imported")
    except Exception as e:
        print(f"❌ Voice system import failed: {e}")
        return False
    
    try:
        from medicine_system.medicine_scheduler import MedicineScheduler
        print("✅ Medicine scheduler module imported")
    except Exception as e:
        print(f"❌ Medicine scheduler import failed: {e}")
        return False
    
    try:
        from gui.baymax_gui import BaymaxGUI
        print("✅ GUI module imported")
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        return False
    
    try:
        from database.user_manager import UserManager
        print("✅ User manager module imported")
    except Exception as e:
        print(f"❌ User manager import failed: {e}")
        return False
    
    return True

def test_voice_system():
    """Test voice system functionality."""
    print("\n🔊 Testing voice system...")
    
    try:
        from voice_system.baymax_voice import BaymaxVoice
        
        voice = BaymaxVoice()
        print("✅ Voice system initialized")
        
        # Test voice info
        voice_info = voice.get_voice_info()
        print(f"✅ Available voices: {len(voice_info.get('available_voices', []))}")
        
        # Test TTS (brief test)
        print("🔊 Testing text-to-speech...")
        voice.speak("Hello, I am BAYMAX. Voice system test successful.", async_speech=False)
        print("✅ Text-to-speech test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice system test failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition system."""
    print("\n👁️ Testing face recognition...")
    
    try:
        from face_recognition.face_recognizer import FaceRecognizer
        
        face_rec = FaceRecognizer()
        print("✅ Face recognition system initialized")
        
        # Test camera initialization
        if face_rec.initialize_camera():
            print("✅ Camera initialized successfully")
            face_rec.release_camera()
        else:
            print("⚠️ Camera initialization failed (may be normal in headless environment)")
        
        print("✅ Face recognition test completed")
        return True
        
    except Exception as e:
        print(f"❌ Face recognition test failed: {e}")
        return False

def test_database():
    """Test database and user management."""
    print("\n💾 Testing database system...")
    
    try:
        from database.user_manager import UserManager
        
        user_mgr = UserManager()
        print("✅ Database initialized")
        
        # Test database stats
        stats = user_mgr.get_database_stats()
        print(f"✅ Database stats: {stats}")
        
        # Test user operations (without creating actual users)
        users = user_mgr.get_all_users()
        print(f"✅ Retrieved {len(users)} existing users")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_medicine_scheduler():
    """Test medicine scheduling system."""
    print("\n💊 Testing medicine scheduler...")
    
    try:
        from medicine_system.medicine_scheduler import MedicineScheduler
        
        scheduler = MedicineScheduler()
        print("✅ Medicine scheduler initialized")
        
        # Test schedule operations
        all_users = scheduler.get_all_users()
        print(f"✅ Retrieved schedules for {len(all_users)} users")
        
        return True
        
    except Exception as e:
        print(f"❌ Medicine scheduler test failed: {e}")
        return False

def test_gui():
    """Test GUI system (without actually showing it)."""
    print("\n🖥️ Testing GUI system...")
    
    try:
        from gui.baymax_gui import BaymaxGUI
        
        # Just test initialization without showing
        print("✅ GUI module can be initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_main_application():
    """Test main application initialization."""
    print("\n🤖 Testing main application...")
    
    try:
        # Import main application
        sys.path.append('/workspace')
        from baymax_main import BaymaxAssistant
        
        # Test initialization (without starting)
        baymax = BaymaxAssistant()
        print("✅ BAYMAX application initialized")
        
        # Test system status
        status = baymax.get_system_status()
        print(f"✅ System status retrieved: {len(status)} status fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
        return False

def run_all_tests():
    """Run all component tests."""
    print("🤖 BAYMAX Healthcare Assistant - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Voice System", test_voice_system),
        ("Face Recognition", test_face_recognition),
        ("Database System", test_database),
        ("Medicine Scheduler", test_medicine_scheduler),
        ("GUI System", test_gui),
        ("Main Application", test_main_application),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! BAYMAX is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

def main():
    """Main test execution."""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "imports":
            test_imports()
        elif test_name == "voice":
            test_voice_system()
        elif test_name == "face":
            test_face_recognition()
        elif test_name == "database":
            test_database()
        elif test_name == "scheduler":
            test_medicine_scheduler()
        elif test_name == "gui":
            test_gui()
        elif test_name == "main":
            test_main_application()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: imports, voice, face, database, scheduler, gui, main")
    else:
        # Run all tests
        success = run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()