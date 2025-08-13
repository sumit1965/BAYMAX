#!/usr/bin/env python3
"""
BAYMAX Healthcare Assistant - Main Application
Integrates face recognition, voice system, medicine scheduling, and GUI
"""

import sys
import os
import threading
import time
from datetime import datetime

# Add src directory to path
sys.path.append('/workspace/src')

from face_recognition.face_recognizer import FaceRecognizer
from voice_system.baymax_voice import BaymaxVoice
from medicine_system.medicine_scheduler import MedicineScheduler
from gui.baymax_gui import BaymaxGUI
from database.user_manager import UserManager

class BaymaxAssistant:
    """
    Main BAYMAX Healthcare Assistant application.
    Integrates all subsystems for complete healthcare assistance.
    """
    
    def __init__(self):
        print("🤖 Initializing BAYMAX Healthcare Assistant...")
        
        # Initialize all subsystems
        self.face_recognizer = FaceRecognizer()
        self.voice_system = BaymaxVoice()
        self.medicine_scheduler = MedicineScheduler()
        self.user_manager = UserManager()
        self.gui = None
        
        # Application state
        self.running = False
        self.current_user = None
        self.active_reminder = None
        
        # Setup callbacks
        self._setup_callbacks()
        
        print("✅ BAYMAX initialized successfully!")
    
    def _setup_callbacks(self):
        """Setup callbacks between different subsystems."""
        # Medicine scheduler callbacks
        self.medicine_scheduler.set_reminder_callback(self._on_medicine_reminder)
        self.medicine_scheduler.set_missed_callback(self._on_medicine_missed)
    
    def _on_medicine_reminder(self, user_name: str, medicine_name: str, 
                            scheduled_time: str, reminder_id: str, 
                            reminder_count: int = 1):
        """Handle medicine reminder callback."""
        print(f"📋 Medicine reminder: {user_name} - {medicine_name} at {scheduled_time}")
        
        # Update GUI
        if self.gui:
            self.gui.show_medicine_reminder(user_name, medicine_name, reminder_count)
        
        # Set active reminder
        self.active_reminder = {
            'user_name': user_name,
            'medicine_name': medicine_name,
            'scheduled_time': scheduled_time,
            'reminder_id': reminder_id,
            'reminder_count': reminder_count
        }
        
        # Start medicine reminder sequence
        threading.Thread(target=self._handle_medicine_reminder, daemon=True).start()
    
    def _on_medicine_missed(self, user_name: str, medicine_name: str, scheduled_time: str):
        """Handle missed medicine callback."""
        print(f"❌ Medicine missed: {user_name} - {medicine_name} at {scheduled_time}")
        
        # Update GUI
        if self.gui:
            self.gui.show_medicine_missed(user_name, medicine_name)
        
        # Speak missed medicine notification
        self.voice_system.speak("", "medicine_missed", async_speech=False)
        
        # Log session
        self.user_manager.log_user_session(
            user_name, "medicine_reminder", "missed",
            {"medicine_name": medicine_name, "scheduled_time": scheduled_time}
        )
        
        # Clear active reminder
        self.active_reminder = None
    
    def _handle_medicine_reminder(self):
        """Handle the complete medicine reminder flow."""
        if not self.active_reminder:
            return
        
        user_name = self.active_reminder['user_name']
        medicine_name = self.active_reminder['medicine_name']
        reminder_count = self.active_reminder['reminder_count']
        
        try:
            # Log session start
            self.user_manager.log_user_session(
                user_name, "medicine_reminder", "started",
                {"medicine_name": medicine_name, "reminder_count": reminder_count}
            )
            
            # Speak medicine reminder
            if reminder_count == 1:
                self.voice_system.medicine_reminder_sequence(user_name)
            else:
                self.voice_system.speak("", "medicine_reminder", async_speech=False)
            
            # Update GUI status
            if self.gui:
                self.gui.show_face_recognition_status("recognizing")
            
            # Try face recognition first
            print("👁️ Starting face recognition...")
            recognized_user = self.face_recognizer.continuous_recognition(timeout=30)
            
            if recognized_user and recognized_user == user_name:
                # Face recognized successfully
                print(f"✅ Face recognized: {recognized_user}")
                
                if self.gui:
                    self.gui.show_face_recognition_status("recognized")
                
                # Confirm medicine taken
                self._confirm_medicine_taken(user_name, medicine_name, "face")
                
            else:
                # Face not recognized, try emergency voice override
                print("⚠️ Face not recognized, trying voice authentication...")
                
                if self.gui:
                    self.gui.show_face_recognition_status("not_recognized")
                
                # Listen for wake word
                if self.voice_system.listen_for_wake_word(timeout=20):
                    # Wake word detected, try voice authentication
                    if self.voice_system.emergency_voice_authentication():
                        self._confirm_medicine_taken(user_name, medicine_name, "voice")
                    else:
                        print("❌ Voice authentication failed")
                        # This will be handled by the scheduler timeout
                else:
                    print("❌ No wake word detected")
                    # This will be handled by the scheduler timeout
        
        except Exception as e:
            print(f"Error in medicine reminder handling: {e}")
            self.user_manager.log_user_session(
                user_name, "medicine_reminder", "error",
                {"error": str(e), "medicine_name": medicine_name}
            )
    
    def _confirm_medicine_taken(self, user_name: str, medicine_name: str, method: str):
        """Confirm that medicine has been taken."""
        print(f"✅ Medicine confirmed taken: {user_name} - {medicine_name} via {method}")
        
        # Update medicine scheduler
        self.medicine_scheduler.confirm_medicine_taken(user_name, medicine_name, method)
        
        # Update GUI
        if self.gui:
            self.gui.show_medicine_taken(user_name, medicine_name)
        
        # Speak confirmation
        self.voice_system.speak("", "medicine_taken", async_speech=False)
        
        # Log session
        self.user_manager.log_user_session(
            user_name, "medicine_reminder", "completed",
            {"medicine_name": medicine_name, "method": method}
        )
        
        # Clear active reminder
        self.active_reminder = None
    
    def register_new_user(self, user_name: str, full_name: str = None, 
                         medicine_name: str = None, medicine_times: list = None):
        """
        Register a new user with face data and medicine schedule.
        
        Args:
            user_name: Username
            full_name: Full name
            medicine_name: Medicine name
            medicine_times: List of medicine times
        """
        print(f"👤 Registering new user: {user_name}")
        
        try:
            # Register user in database
            if not self.user_manager.register_user(user_name, full_name=full_name):
                print(f"❌ Failed to register user {user_name} in database")
                return False
            
            # Capture face data
            print("📷 Starting face registration...")
            if self.gui:
                self.gui.update_status(f"Please look at the camera for face registration", "alert")
            
            self.voice_system.speak(f"Hello {user_name}. Please look at the camera for face registration.", async_speech=False)
            
            if self.face_recognizer.capture_face_for_registration(user_name):
                # Mark face as registered
                self.user_manager.mark_face_registered(user_name)
                print(f"✅ Face registered for {user_name}")
                
                if self.gui:
                    self.gui.update_status(f"Face registered successfully for {user_name}", "happy")
                
                self.voice_system.speak(f"Face registration successful for {user_name}.", async_speech=False)
            else:
                print(f"❌ Face registration failed for {user_name}")
                if self.gui:
                    self.gui.update_status(f"Face registration failed for {user_name}", "concerned")
                return False
            
            # Add medicine schedule if provided
            if medicine_name and medicine_times:
                print(f"💊 Adding medicine schedule for {user_name}")
                self.medicine_scheduler.add_user_schedule(
                    user_name, medicine_name, medicine_times
                )
                
                # Also add to user manager
                self.user_manager.add_medicine_schedule(
                    user_name, medicine_name, "As prescribed", 
                    medicine_times, None, "Registered via BAYMAX"
                )
            
            # Log registration session
            self.user_manager.log_user_session(
                user_name, "registration", "completed",
                {"face_registered": True, "medicine_added": bool(medicine_name)}
            )
            
            print(f"🎉 User {user_name} registered successfully!")
            return True
            
        except Exception as e:
            print(f"Error registering user {user_name}: {e}")
            self.user_manager.log_user_session(
                user_name, "registration", "failed",
                {"error": str(e)}
            )
            return False
    
    def load_sample_data(self):
        """Load sample users and medicine schedules for demonstration."""
        print("📋 Loading sample data...")
        
        sample_users = [
            {
                'user_name': 'john_doe',
                'full_name': 'John Doe',
                'medicine_name': 'Aspirin',
                'medicine_times': ['08:00', '20:00']
            },
            {
                'user_name': 'jane_smith',
                'full_name': 'Jane Smith',
                'medicine_name': 'Vitamin D',
                'medicine_times': ['09:00']
            }
        ]
        
        for user_data in sample_users:
            user_name = user_data['user_name']
            
            # Check if user already exists
            if self.user_manager.get_user(user_name):
                print(f"User {user_name} already exists, skipping...")
                continue
            
            # Register user (without face data for demo)
            if self.user_manager.register_user(user_name, full_name=user_data['full_name']):
                # Add medicine schedule
                self.medicine_scheduler.add_user_schedule(
                    user_name, 
                    user_data['medicine_name'], 
                    user_data['medicine_times']
                )
                print(f"✅ Sample user {user_name} added")
    
    def start_gui(self):
        """Start the GUI interface."""
        print("🖥️ Starting GUI...")
        
        self.gui = BaymaxGUI("BAYMAX Healthcare Assistant")
        
        # Set up GUI callbacks
        self.gui.set_close_callback(self._on_gui_close)
        
        # Show initial status
        self.gui.update_status("BAYMAX is ready to help with your healthcare needs!", "idle")
        self.gui.show_buttons(True)
        
        # Override button callbacks with actual functionality
        self.gui._on_register_click = self._gui_register_user
        self.gui._on_test_voice_click = self._gui_test_voice
        
        # Start GUI main loop
        self.gui.run()
    
    def _gui_register_user(self):
        """Handle GUI register user button."""
        dialog = self.gui.create_registration_dialog()
        # This would integrate with actual registration logic
    
    def _gui_test_voice(self):
        """Handle GUI test voice button."""
        self.voice_system.speak("", "greeting", async_speech=False)
    
    def _on_gui_close(self):
        """Handle GUI close event."""
        print("🛑 Stopping BAYMAX...")
        self.stop()
    
    def start(self):
        """Start the BAYMAX assistant."""
        print("🚀 Starting BAYMAX Healthcare Assistant...")
        
        self.running = True
        
        # Initialize camera
        if not self.face_recognizer.initialize_camera():
            print("⚠️ Warning: Camera initialization failed. Face recognition will be limited.")
        
        # Start medicine scheduler
        self.medicine_scheduler.start_scheduler()
        
        # Load sample data (for demonstration)
        self.load_sample_data()
        
        # Start GUI in main thread
        self.start_gui()
    
    def stop(self):
        """Stop the BAYMAX assistant."""
        print("🛑 Stopping BAYMAX Healthcare Assistant...")
        
        self.running = False
        
        # Stop medicine scheduler
        self.medicine_scheduler.stop_scheduler()
        
        # Stop voice recognition
        self.voice_system.stop_recognition()
        
        # Release camera
        self.face_recognizer.release_camera()
        
        print("👋 BAYMAX stopped. Stay healthy!")
    
    def get_system_status(self) -> dict:
        """Get current system status."""
        return {
            'running': self.running,
            'current_user': self.current_user,
            'active_reminder': self.active_reminder,
            'registered_users': len(self.user_manager.get_all_users()),
            'face_registered_users': len(self.user_manager.get_users_with_face_registration()),
            'active_schedules': len(self.medicine_scheduler.get_active_reminders()),
            'database_stats': self.user_manager.get_database_stats()
        }
    
    def interactive_setup(self):
        """Interactive setup for first-time users."""
        print("\n🤖 Welcome to BAYMAX Healthcare Assistant Setup!")
        print("=" * 50)
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Register a new user")
            print("2. Add medicine schedule for existing user")
            print("3. Test voice system")
            print("4. Test face recognition")
            print("5. View system status")
            print("6. Start BAYMAX")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == '1':
                self._interactive_register_user()
            elif choice == '2':
                self._interactive_add_medicine()
            elif choice == '3':
                self._interactive_test_voice()
            elif choice == '4':
                self._interactive_test_face()
            elif choice == '5':
                self._show_system_status()
            elif choice == '6':
                break
            elif choice == '0':
                print("👋 Goodbye!")
                return False
            else:
                print("❌ Invalid choice. Please try again.")
        
        return True
    
    def _interactive_register_user(self):
        """Interactive user registration."""
        print("\n👤 User Registration")
        print("-" * 20)
        
        user_name = input("Enter username: ").strip()
        if not user_name:
            print("❌ Username cannot be empty")
            return
        
        full_name = input("Enter full name (optional): ").strip() or None
        
        medicine_name = input("Enter medicine name (optional): ").strip() or None
        medicine_times = []
        
        if medicine_name:
            times_input = input("Enter medicine times (HH:MM, comma separated, e.g., 08:00,20:00): ").strip()
            if times_input:
                medicine_times = [t.strip() for t in times_input.split(',')]
        
        if self.register_new_user(user_name, full_name, medicine_name, medicine_times):
            print(f"✅ User {user_name} registered successfully!")
        else:
            print(f"❌ Failed to register user {user_name}")
    
    def _interactive_add_medicine(self):
        """Interactive medicine schedule addition."""
        print("\n💊 Add Medicine Schedule")
        print("-" * 25)
        
        users = self.user_manager.get_all_users()
        if not users:
            print("❌ No users registered. Please register a user first.")
            return
        
        print("Available users:")
        for i, user in enumerate(users):
            print(f"{i+1}. {user['user_name']} ({user.get('full_name', 'No full name')})")
        
        try:
            choice = int(input("Select user (number): ")) - 1
            if 0 <= choice < len(users):
                user_name = users[choice]['user_name']
                
                medicine_name = input("Enter medicine name: ").strip()
                times_input = input("Enter medicine times (HH:MM, comma separated): ").strip()
                
                if medicine_name and times_input:
                    medicine_times = [t.strip() for t in times_input.split(',')]
                    
                    self.medicine_scheduler.add_user_schedule(
                        user_name, medicine_name, medicine_times
                    )
                    print(f"✅ Medicine schedule added for {user_name}")
                else:
                    print("❌ Medicine name and times are required")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _interactive_test_voice(self):
        """Interactive voice system test."""
        print("\n🔊 Testing Voice System...")
        self.voice_system.speak("", "greeting", async_speech=False)
        print("✅ Voice test completed")
    
    def _interactive_test_face(self):
        """Interactive face recognition test."""
        print("\n👁️ Testing Face Recognition...")
        print("Please look at the camera. Press 'q' to quit.")
        
        if not self.face_recognizer.initialize_camera():
            print("❌ Failed to initialize camera")
            return
        
        try:
            recognized_user = self.face_recognizer.continuous_recognition(timeout=10)
            if recognized_user:
                print(f"✅ Recognized user: {recognized_user}")
            else:
                print("❌ No user recognized")
        except Exception as e:
            print(f"❌ Face recognition error: {e}")
        finally:
            self.face_recognizer.release_camera()
    
    def _show_system_status(self):
        """Show system status."""
        print("\n📊 System Status")
        print("-" * 15)
        
        status = self.get_system_status()
        
        print(f"Running: {status['running']}")
        print(f"Current User: {status['current_user'] or 'None'}")
        print(f"Active Reminder: {bool(status['active_reminder'])}")
        print(f"Registered Users: {status['registered_users']}")
        print(f"Face Registered Users: {status['face_registered_users']}")
        print(f"Active Schedules: {status['active_schedules']}")
        
        if status['database_stats']:
            print(f"Database: {status['database_stats']['database_path']}")


def main():
    """Main entry point."""
    print("🤖 BAYMAX Healthcare Assistant")
    print("=" * 40)
    
    try:
        # Create BAYMAX instance
        baymax = BaymaxAssistant()
        
        # Check if this is first run or interactive setup
        if len(sys.argv) > 1 and sys.argv[1] == '--setup':
            # Interactive setup mode
            if baymax.interactive_setup():
                baymax.start()
        else:
            # Direct start
            baymax.start()
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 Thank you for using BAYMAX!")


if __name__ == "__main__":
    main()