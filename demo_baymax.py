#!/usr/bin/env python3
"""
BAYMAX Healthcare Assistant - Demo Version
Simplified version that demonstrates core functionality without face recognition.
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append('/workspace/src')

def demo_voice_system():
    """Demo the voice system."""
    print("🔊 BAYMAX Voice System Demo")
    print("=" * 40)
    
    try:
        from voice_system.baymax_voice import BaymaxVoice
        
        voice = BaymaxVoice()
        print("✅ Voice system initialized")
        
        # Demo different Baymax phrases
        phrases = [
            ("greeting", "Greeting"),
            ("medicine_time", "Medicine Time Alert"),
            ("medicine_taken", "Medicine Confirmed"),
            ("goodbye", "Goodbye Message")
        ]
        
        for phrase_type, description in phrases:
            print(f"\n🔊 Playing: {description}")
            voice.speak("", phrase_type, async_speech=False)
            time.sleep(1)
        
        print("\n✅ Voice system demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Voice system demo failed: {e}")
        return False

def demo_gui():
    """Demo the GUI system."""
    print("\n🖥️ BAYMAX GUI Demo")
    print("=" * 40)
    
    try:
        from gui.baymax_gui import BaymaxGUI
        
        print("Creating BAYMAX GUI...")
        gui = BaymaxGUI("BAYMAX Demo")
        
        # Demo different expressions
        expressions = ["idle", "happy", "alert", "concerned", "speaking"]
        
        def demo_expressions():
            for expr in expressions:
                print(f"Setting expression: {expr}")
                gui.set_expression(expr)
                gui.update_status(f"Current expression: {expr.title()}", expr)
                time.sleep(2)
            
            # Demo medicine reminder
            gui.show_medicine_reminder("Demo User", "Demo Medicine", 1)
            time.sleep(3)
            
            # Demo medicine taken
            gui.show_medicine_taken("Demo User", "Demo Medicine")
            time.sleep(3)
            
            gui.update_status("Demo completed! You can close this window.", "happy")
        
        # Start expression demo in background
        threading.Thread(target=demo_expressions, daemon=True).start()
        
        print("✅ GUI demo started! Close the window when done.")
        gui.run()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI demo failed: {e}")
        return False

def demo_database():
    """Demo the database system."""
    print("\n💾 BAYMAX Database Demo")
    print("=" * 40)
    
    try:
        from database.user_manager import UserManager
        
        user_mgr = UserManager()
        print("✅ Database initialized")
        
        # Demo user registration
        demo_users = [
            {"user_name": "demo_user1", "full_name": "Alice Demo", "age": 30},
            {"user_name": "demo_user2", "full_name": "Bob Demo", "age": 45}
        ]
        
        for user_data in demo_users:
            if not user_mgr.get_user(user_data["user_name"]):
                if user_mgr.register_user(**user_data):
                    print(f"✅ Registered demo user: {user_data['user_name']}")
                else:
                    print(f"⚠️ User {user_data['user_name']} already exists")
        
        # Show all users
        users = user_mgr.get_all_users()
        print(f"\n📊 Total users in database: {len(users)}")
        
        for user in users:
            print(f"  - {user['user_name']} ({user.get('full_name', 'No name')})")
        
        # Show database stats
        stats = user_mgr.get_database_stats()
        print(f"\n📈 Database Statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database demo failed: {e}")
        return False

def demo_medicine_scheduler():
    """Demo the medicine scheduling system."""
    print("\n💊 BAYMAX Medicine Scheduler Demo")
    print("=" * 40)
    
    try:
        from medicine_system.medicine_scheduler import MedicineScheduler
        
        scheduler = MedicineScheduler()
        print("✅ Medicine scheduler initialized")
        
        # Add demo schedules
        current_time = datetime.now()
        future_time = (current_time + timedelta(minutes=1)).strftime('%H:%M')
        
        demo_schedules = [
            ("demo_user1", "Vitamin D", [future_time]),
            ("demo_user2", "Aspirin", ["08:00", "20:00"])
        ]
        
        for user_name, medicine, times in demo_schedules:
            scheduler.add_user_schedule(user_name, medicine, times)
            print(f"✅ Added schedule: {user_name} - {medicine} at {times}")
        
        # Show all schedules
        all_users = scheduler.get_all_users()
        print(f"\n📋 Users with medicine schedules: {len(all_users)}")
        
        for user_name in all_users:
            schedules = scheduler.get_user_schedules(user_name)
            print(f"  - {user_name}: {len(schedules)} medicines")
            for schedule in schedules:
                print(f"    * {schedule['medicine_name']} at {schedule['times']}")
        
        # Demo medicine log
        log_df = scheduler.get_medicine_log(days=1)
        print(f"\n📊 Medicine log entries (last 24h): {len(log_df)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Medicine scheduler demo failed: {e}")
        return False

def demo_full_system():
    """Demo the complete system integration."""
    print("\n🤖 BAYMAX Complete System Demo")
    print("=" * 40)
    
    try:
        # Import required modules
        from voice_system.baymax_voice import BaymaxVoice
        from database.user_manager import UserManager
        from medicine_system.medicine_scheduler import MedicineScheduler
        
        # Initialize systems
        voice = BaymaxVoice()
        user_mgr = UserManager()
        scheduler = MedicineScheduler()
        
        print("✅ All systems initialized")
        
        # Demo scenario: Medicine reminder for demo user
        demo_user = "demo_patient"
        demo_medicine = "Morning Vitamins"
        
        # Register demo user if not exists
        if not user_mgr.get_user(demo_user):
            user_mgr.register_user(demo_user, full_name="Demo Patient", age=35)
            print(f"✅ Registered demo user: {demo_user}")
        
        # Add medicine schedule for immediate demo (1 minute from now)
        current_time = datetime.now()
        demo_time = (current_time + timedelta(minutes=1)).strftime('%H:%M')
        scheduler.add_user_schedule(demo_user, demo_medicine, [demo_time])
        
        print(f"✅ Added medicine schedule: {demo_medicine} at {demo_time}")
        
        # Demo medicine reminder sequence
        print("\n🔊 Simulating medicine reminder sequence...")
        
        # Greeting
        voice.speak(f"Hello {demo_user}. My name is BAYMAX, your personal healthcare companion.", async_speech=False)
        time.sleep(1)
        
        # Medicine reminder
        voice.speak(f"It is time for your {demo_medicine}. Please take it now.", async_speech=False)
        time.sleep(1)
        
        # Simulate medicine taken
        scheduler.confirm_medicine_taken(demo_user, demo_medicine, "demo")
        voice.speak("Thank you for taking your medicine. Your health is my priority.", async_speech=False)
        
        # Log session
        user_mgr.log_user_session(demo_user, "demo_session", "completed", 
                                 {"medicine": demo_medicine, "demo": True})
        
        print("✅ Complete system demo finished!")
        
        # Show final status
        print(f"\n📊 Final System Status:")
        print(f"  - Registered users: {len(user_mgr.get_all_users())}")
        print(f"  - Medicine schedules: {len(scheduler.get_all_users())}")
        print(f"  - Medicine log entries: {len(scheduler.get_medicine_log(days=1))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete system demo failed: {e}")
        return False

def main():
    """Main demo execution."""
    print("🤖 BAYMAX Healthcare Assistant - Demo")
    print("=" * 50)
    print("This demo showcases BAYMAX functionality without requiring camera.")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        demo_type = sys.argv[1].lower()
        
        if demo_type == "voice":
            demo_voice_system()
        elif demo_type == "gui":
            demo_gui()
        elif demo_type == "database":
            demo_database()
        elif demo_type == "scheduler":
            demo_medicine_scheduler()
        elif demo_type == "full":
            demo_full_system()
        else:
            print(f"Unknown demo: {demo_type}")
            print("Available demos: voice, gui, database, scheduler, full")
    else:
        # Interactive menu
        while True:
            print("\n🤖 BAYMAX Demo Menu:")
            print("1. Voice System Demo")
            print("2. GUI Demo (opens window)")
            print("3. Database Demo")
            print("4. Medicine Scheduler Demo")
            print("5. Complete System Demo")
            print("0. Exit")
            
            choice = input("\nSelect demo (0-5): ").strip()
            
            if choice == '1':
                demo_voice_system()
            elif choice == '2':
                demo_gui()
            elif choice == '3':
                demo_database()
            elif choice == '4':
                demo_medicine_scheduler()
            elif choice == '5':
                demo_full_system()
            elif choice == '0':
                print("👋 Thank you for trying BAYMAX!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()