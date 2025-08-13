#!/usr/bin/env python3
"""
BAYMAX Demo - Showcase the healthcare assistant features
This demo runs without camera or voice recognition for testing purposes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import csv
import os
from datetime import datetime, timedelta
import queue

class DemoBaymaxVoice:
    """Demo voice system that prints messages instead of speaking"""
    
    def __init__(self):
        self.speaking = False
        
    def speak(self, text):
        """Print Baymax's speech instead of speaking"""
        if self.speaking:
            return
            
        self.speaking = True
        print(f"🤖 BAYMAX: {text}")
        time.sleep(2)  # Simulate speech duration
        self.speaking = False
        
    def speak_async(self, text):
        """Speak asynchronously"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

class DemoUserManager:
    """Demo user management with sample data"""
    
    def __init__(self):
        self.users = {
            "1": {
                "name": "John Doe",
                "face_encoding": [0.1, 0.2, 0.3],  # Dummy encoding
                "medicine_schedule": ["08:00", "20:00"],
                "last_medicine_time": None,
                "missed_doses": [],
                "registration_date": datetime.now().isoformat()
            },
            "2": {
                "name": "Jane Smith",
                "face_encoding": [0.4, 0.5, 0.6],  # Dummy encoding
                "medicine_schedule": ["09:00", "21:00"],
                "last_medicine_time": datetime.now().isoformat(),
                "missed_doses": [],
                "registration_date": datetime.now().isoformat()
            }
        }
    
    def get_users(self):
        return self.users
    
    def register_user(self, name, face_encoding, medicine_schedule):
        """Register a new user"""
        user_id = str(len(self.users) + 1)
        self.users[user_id] = {
            "name": name,
            "face_encoding": face_encoding,
            "medicine_schedule": medicine_schedule,
            "last_medicine_time": None,
            "missed_doses": [],
            "registration_date": datetime.now().isoformat()
        }
        return user_id

class DemoMedicineReminder:
    """Demo medicine reminder system"""
    
    def __init__(self, user_manager, voice_system, gui_system):
        self.user_manager = user_manager
        self.voice_system = voice_system
        self.gui_system = gui_system
        self.missed_alerts_file = "demo_missed_alerts.csv"
        self.setup_missed_alerts_file()
        
    def setup_missed_alerts_file(self):
        """Initialize missed alerts CSV file"""
        if not os.path.exists(self.missed_alerts_file):
            with open(self.missed_alerts_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User ID', 'User Name', 'Scheduled Time', 'Missed Time', 'Date'])
    
    def trigger_demo_reminder(self, user_id):
        """Trigger a demo medicine reminder"""
        user_data = self.user_manager.users[user_id]
        user_name = user_data['name']
        
        # Wake up Baymax
        self.gui_system.set_expression("alert")
        greeting = f"Hello {user_name}. My name is Baymax, your personal healthcare companion. It's time for your medicine. Please take it now."
        self.voice_system.speak_async(greeting)
        
        # Simulate face recognition success
        time.sleep(3)
        self.confirm_medicine_taken(user_id, user_name)
    
    def confirm_medicine_taken(self, user_id, user_name):
        """Confirm medicine has been taken"""
        self.user_manager.users[user_id]['last_medicine_time'] = datetime.now().isoformat()
        self.gui_system.set_expression("happy")
        confirmation = f"Thank you {user_name}. I have recorded that you have taken your medicine. Is there anything else I can help you with?"
        self.voice_system.speak_async(confirmation)

class DemoBaymaxGUI:
    """Demo GUI with Baymax's animated face"""
    
    def __init__(self, voice_system, user_manager, medicine_reminder):
        self.voice_system = voice_system
        self.user_manager = user_manager
        self.medicine_reminder = medicine_reminder
        
        self.root = tk.Tk()
        self.root.title("BAYMAX Demo - Your Personal Healthcare Companion")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        self.current_expression = "idle"
        self.expressions = {
            "idle": "😐",
            "happy": "😊",
            "alert": "😮",
            "sad": "😔",
            "waiting": "🤔",
            "thinking": "🧐"
        }
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the demo GUI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="BAYMAX DEMO", 
            font=('Arial', 28, 'bold'), 
            fg='white', 
            bg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            main_frame,
            text="Your Personal Healthcare Companion (Demo Mode)",
            font=('Arial', 12, 'italic'),
            fg='#BDC3C7',
            bg='#2C3E50'
        )
        subtitle_label.pack(pady=5)
        
        # Baymax face display
        self.face_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=3)
        self.face_frame.pack(pady=20)
        
        self.face_label = tk.Label(
            self.face_frame, 
            text=self.expressions["idle"], 
            font=('Arial', 80), 
            bg='#34495E', 
            fg='white'
        )
        self.face_label.pack(padx=50, pady=50)
        
        # Status display
        self.status_label = tk.Label(
            main_frame, 
            text="BAYMAX Demo is ready! This is a demonstration of the healthcare assistant features.", 
            font=('Arial', 12), 
            fg='white', 
            bg='#2C3E50',
            wraplength=700
        )
        self.status_label.pack(pady=10)
        
        # Demo camera frame (simulated)
        self.camera_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=3)
        self.camera_frame.pack(pady=10)
        
        camera_title = tk.Label(
            self.camera_frame,
            text="Demo Camera Feed (Simulated)",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#34495E'
        )
        camera_title.pack(pady=5)
        
        self.camera_label = tk.Label(
            self.camera_frame, 
            text="📷 Camera Feed\n(Would show live video with face detection)", 
            font=('Arial', 12), 
            fg='white', 
            bg='#34495E',
            width=40,
            height=8
        )
        self.camera_label.pack(padx=10, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#2C3E50')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame, 
            text="Demo Medicine Reminder", 
            command=self.demo_medicine_reminder,
            bg='#3498DB', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=18
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="View Demo Users", 
            command=self.view_users_dialog,
            bg='#27AE60', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Test Voice Commands", 
            command=self.test_voice_commands,
            bg='#E74C3C', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Expression Test", 
            command=self.test_expressions,
            bg='#F39C12', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Demo info
        info_label = tk.Label(
            main_frame,
            text="💡 This demo shows BAYMAX's interface and features without requiring camera or microphone.",
            font=('Arial', 10),
            fg='#BDC3C7',
            bg='#2C3E50',
            wraplength=700
        )
        info_label.pack(pady=10)
        
    def set_expression(self, expression):
        """Change Baymax's facial expression"""
        if expression in self.expressions:
            self.current_expression = expression
            self.face_label.config(text=self.expressions[expression])
    
    def demo_medicine_reminder(self):
        """Demo a medicine reminder"""
        self.medicine_reminder.trigger_demo_reminder("1")  # Demo with John Doe
    
    def view_users_dialog(self):
        """Dialog for viewing demo users"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Demo Users")
        dialog.geometry("600x400")
        dialog.configure(bg='#2C3E50')
        
        # Create treeview
        tree = ttk.Treeview(dialog, columns=('ID', 'Name', 'Schedule', 'Last Medicine'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('Schedule', text='Medicine Schedule')
        tree.heading('Last Medicine', text='Last Medicine Time')
        
        # Set column widths
        tree.column('ID', width=50)
        tree.column('Name', width=100)
        tree.column('Schedule', width=150)
        tree.column('Last Medicine', width=150)
        
        # Add demo users to treeview
        for user_id, user_data in self.user_manager.users.items():
            schedule_str = ', '.join(user_data['medicine_schedule'])
            last_medicine = user_data.get('last_medicine_time', 'Never')
            if last_medicine != 'Never':
                last_medicine = datetime.fromisoformat(last_medicine).strftime('%Y-%m-%d %H:%M')
            
            tree.insert('', 'end', values=(user_id, user_data['name'], schedule_str, last_medicine))
        
        tree.pack(padx=20, pady=20, fill='both', expand=True)
    
    def test_voice_commands(self):
        """Test voice command responses"""
        commands = [
            ("Hey Baymax", "Hello. I am Baymax, your personal healthcare companion. How can I help you today?"),
            ("I took my medicine", "Thank you for confirming that you have taken your medicine."),
            ("Help", "I'm here to help you with your healthcare needs. I can remind you about medicine, track your health, and provide assistance when needed."),
            ("Goodbye", "Goodbye. I'll be here when you need me.")
        ]
        
        for command, response in commands:
            self.set_expression("alert")
            self.voice_system.speak_async(f"Command: '{command}'")
            time.sleep(1)
            self.voice_system.speak_async(response)
            time.sleep(2)
    
    def test_expressions(self):
        """Test all facial expressions"""
        expressions = ["idle", "happy", "alert", "sad", "waiting", "thinking"]
        
        for expression in expressions:
            self.set_expression(expression)
            self.voice_system.speak_async(f"Testing {expression} expression")
            time.sleep(1)
        
        self.set_expression("idle")
    
    def run(self):
        """Start the demo GUI"""
        # Welcome message
        self.voice_system.speak_async("Hello. I am Baymax, your personal healthcare companion. Welcome to the demo mode.")
        
        # Start GUI
        self.root.mainloop()

def main():
    """Main function to start BAYMAX demo"""
    print("Starting BAYMAX Demo - Your Personal Healthcare Companion")
    print("This demo showcases BAYMAX's features without requiring camera or microphone.")
    
    # Initialize demo components
    voice_system = DemoBaymaxVoice()
    user_manager = DemoUserManager()
    medicine_reminder = DemoMedicineReminder(user_manager, voice_system, None)  # GUI will be set later
    gui_system = DemoBaymaxGUI(voice_system, user_manager, medicine_reminder)
    
    # Connect components
    medicine_reminder.gui_system = gui_system
    
    # Start demo
    gui_system.run()

if __name__ == "__main__":
    main()