#!/usr/bin/env python3
"""
BAYMAX Demo Script
Showcases the key features of the healthcare assistant
"""

import time
import sys
import os

def print_banner():
    """Print BAYMAX banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██████╗  █████╗ ██╗   ██╗███╗   ███╗ █████╗ ██╗  ██╗    ║
    ║    ██╔══██╗██╔══██╗╚██╗ ██╔╝████╗ ████║██╔══██╗╚██╗██╔╝    ║
    ║    ██████╔╝███████║ ╚████╔╝ ██╔████╔██║███████║ ╚███╔╝     ║
    ║    ██╔══██╗██╔══██║  ╚██╔╝  ██║╚██╔╝██║██╔══██║ ██╔██╗     ║
    ║    ██████╔╝██║  ██║   ██║   ██║ ╚═╝ ██║██║  ██║██╔╝ ██╗    ║
    ║    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ║
    ║                                                              ║
    ║              Healthcare Assistant Demo                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def demo_voice_synthesis():
    """Demo voice synthesis capabilities"""
    print("\n🎭 Demo: Baymax Voice Synthesis")
    print("=" * 50)
    
    try:
        import pyttsx3
        
        print("Initializing voice synthesis...")
        engine = pyttsx3.init()
        
        # Configure Baymax-like voice
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
        engine.setProperty('pitch', 100)
        
        # Demo phrases
        phrases = [
            "Hello. I am Baymax, your personal healthcare companion.",
            "It is time for your medicine. Please take it now.",
            "Thank you. I have recorded that you have taken your medicine.",
            "I notice you have not confirmed taking your medicine. Please take it as soon as possible."
        ]
        
        for i, phrase in enumerate(phrases, 1):
            print(f"\n{i}. Speaking: {phrase}")
            engine.say(phrase)
            engine.runAndWait()
            time.sleep(1)
            
        print("\n✅ Voice synthesis demo completed!")
        
    except ImportError:
        print("❌ pyttsx3 not available. Install with: pip install pyttsx3")
    except Exception as e:
        print(f"❌ Voice synthesis error: {e}")

def demo_face_recognition():
    """Demo face recognition capabilities"""
    print("\n🔍 Demo: Face Recognition")
    print("=" * 50)
    
    try:
        import face_recognition
        import numpy as np
        
        print("Testing face recognition library...")
        
        # Create dummy face encodings
        face1 = np.random.rand(128)
        face2 = np.random.rand(128)
        face3 = np.random.rand(128)
        
        # Test face comparison
        similarity_12 = face_recognition.face_distance([face1], face2)[0]
        similarity_13 = face_recognition.face_distance([face1], face3)[0]
        
        print(f"Face 1 vs Face 2 similarity: {similarity_12:.3f}")
        print(f"Face 1 vs Face 3 similarity: {similarity_13:.3f}")
        
        # Test face matching
        matches = face_recognition.compare_faces([face1], face2, tolerance=0.6)
        print(f"Face 1 matches Face 2: {matches[0]}")
        
        print("\n✅ Face recognition demo completed!")
        
    except ImportError:
        print("❌ face_recognition not available. Install with: pip install face-recognition")
    except Exception as e:
        print(f"❌ Face recognition error: {e}")

def demo_gui():
    """Demo GUI capabilities"""
    print("\n🎨 Demo: GUI Interface")
    print("=" * 50)
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        print("Creating demo GUI window...")
        
        # Create demo window
        root = tk.Tk()
        root.title("BAYMAX Demo")
        root.geometry("400x300")
        root.configure(bg='#2C3E50')
        
        # Demo content
        title = tk.Label(root, text="BAYMAX Demo", 
                        font=("Arial", 18, "bold"), 
                        fg='#ECF0F1', bg='#2C3E50')
        title.pack(pady=20)
        
        # Face canvas
        canvas = tk.Canvas(root, bg='#34495E', width=200, height=200)
        canvas.pack(pady=20)
        
        # Draw Baymax face
        canvas.create_oval(20, 20, 180, 180, fill='white', outline='#BDC3C7', width=3)
        canvas.create_oval(70, 70, 90, 90, fill='black')  # Left eye
        canvas.create_oval(110, 70, 130, 90, fill='black')  # Right eye
        canvas.create_arc(80, 100, 120, 140, start=0, extent=180, fill='black')  # Smile
        
        # Status label
        status = tk.Label(root, text="Status: Demo Mode", 
                         font=("Arial", 12), 
                         fg='#ECF0F1', bg='#2C3E50')
        status.pack(pady=10)
        
        # Demo button
        def show_message():
            messagebox.showinfo("BAYMAX", "Hello. I am Baymax, your personal healthcare companion.")
            
        demo_btn = tk.Button(root, text="Test Baymax Voice", 
                            command=show_message,
                            bg='#3498DB', fg='white', font=("Arial", 10, "bold"))
        demo_btn.pack(pady=10)
        
        print("GUI window created. Close the window to continue...")
        root.mainloop()
        
        print("\n✅ GUI demo completed!")
        
    except ImportError:
        print("❌ tkinter not available")
    except Exception as e:
        print(f"❌ GUI error: {e}")

def demo_medicine_scheduler():
    """Demo medicine scheduling capabilities"""
    print("\n⏰ Demo: Medicine Scheduler")
    print("=" * 50)
    
    try:
        import json
        from datetime import datetime
        
        # Demo medicine schedule
        demo_schedule = {
            "John Doe": {
                "Blood Pressure Medicine": ["09:00", "21:00"],
                "Diabetes Medicine": ["08:00", "20:00"]
            },
            "Jane Smith": {
                "Heart Medicine": ["07:00", "19:00"],
                "Vitamin D": ["12:00"]
            }
        }
        
        print("Demo medicine schedule:")
        for user, medicines in demo_schedule.items():
            print(f"\n👤 {user}:")
            for medicine, times in medicines.items():
                print(f"   💊 {medicine}: {', '.join(times)}")
        
        # Save demo schedule
        with open('demo_schedule.json', 'w') as f:
            json.dump(demo_schedule, f, indent=2)
        
        print(f"\n📁 Demo schedule saved to: demo_schedule.json")
        
        # Check current time
        current_time = datetime.now().strftime("%H:%M")
        print(f"🕐 Current time: {current_time}")
        
        # Find due medicines
        due_medicines = []
        for user, medicines in demo_schedule.items():
            for medicine, times in medicines.items():
                if current_time in times:
                    due_medicines.append((user, medicine))
        
        if due_medicines:
            print(f"\n🔔 Medicines due now:")
            for user, medicine in due_medicines:
                print(f"   {user}: {medicine}")
        else:
            print(f"\n✅ No medicines due at {current_time}")
        
        print("\n✅ Medicine scheduler demo completed!")
        
    except Exception as e:
        print(f"❌ Medicine scheduler error: {e}")

def demo_data_management():
    """Demo data management capabilities"""
    print("\n📊 Demo: Data Management")
    print("=" * 50)
    
    try:
        import json
        import csv
        from datetime import datetime
        
        # Demo user data
        demo_users = [
            {
                "name": "John Doe",
                "face_encoding": [0.1, 0.2, 0.3, 0.4, 0.5] * 25 + [0.6, 0.7, 0.8]  # 128 values
            },
            {
                "name": "Jane Smith", 
                "face_encoding": [0.2, 0.3, 0.4, 0.5, 0.6] * 25 + [0.7, 0.8, 0.9]  # 128 values
            }
        ]
        
        # Save demo users
        with open('demo_users.json', 'w') as f:
            json.dump(demo_users, f, indent=2)
        
        print("👥 Demo users saved to: demo_users.json")
        
        # Demo missed doses
        demo_missed = [
            {
                'user_name': 'John Doe',
                'medicine_name': 'Blood Pressure Medicine',
                'scheduled_time': '2024-01-15 09:00:00',
                'logged_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'missed'
            }
        ]
        
        # Save demo missed doses
        with open('demo_missed_doses.csv', 'w', newline='') as f:
            fieldnames = ['user_name', 'medicine_name', 'scheduled_time', 'logged_time', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(demo_missed)
        
        print("📝 Demo missed doses saved to: demo_missed_doses.csv")
        
        # Display demo data
        print(f"\n📋 Demo Data Summary:")
        print(f"   Users: {len(demo_users)}")
        print(f"   Missed Doses: {len(demo_missed)}")
        
        print("\n✅ Data management demo completed!")
        
    except Exception as e:
        print(f"❌ Data management error: {e}")

def cleanup_demo_files():
    """Clean up demo files"""
    demo_files = ['demo_schedule.json', 'demo_users.json', 'demo_missed_doses.csv']
    
    for file in demo_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Cleaned up: {file}")

def main():
    """Main demo function"""
    print_banner()
    
    print("Welcome to the BAYMAX Healthcare Assistant Demo!")
    print("This demo showcases the key features of the system.")
    print("\nPress Enter to start the demo...")
    input()
    
    # Run demos
    demos = [
        ("Voice Synthesis", demo_voice_synthesis),
        ("Face Recognition", demo_face_recognition),
        ("GUI Interface", demo_gui),
        ("Medicine Scheduler", demo_medicine_scheduler),
        ("Data Management", demo_data_management)
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*60}")
        print(f"Running: {demo_name}")
        print(f"{'='*60}")
        
        try:
            demo_func()
        except KeyboardInterrupt:
            print(f"\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
        
        print(f"\nPress Enter to continue to next demo...")
        input()
    
    # Cleanup
    print("\n🧹 Cleaning up demo files...")
    cleanup_demo_files()
    
    print("\n🎉 Demo completed!")
    print("\nTo run the full BAYMAX system:")
    print("1. Install dependencies: ./install.sh")
    print("2. Run BAYMAX: python3 baymax_main.py")
    print("\nThank you for trying BAYMAX! 🤖💙")

if __name__ == "__main__":
    main()