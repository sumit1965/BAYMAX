#!/usr/bin/env python3
"""
BAYMAX - Smart Healthcare Assistant
Inspired by Big Hero 6's healthcare robot

Features:
- Baymax voice synthesis
- Multi-user facial recognition
- Medicine reminder system
- Emergency voice commands
- Animated GUI with facial expressions
"""

import cv2
import face_recognition
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import pyttsx3
import pandas as pd
import schedule
import threading
import time
import json
import csv
import os
from datetime import datetime, timedelta
import queue

class BaymaxVoice:
    """Handles Baymax's voice synthesis with characteristic speech patterns"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_baymax_voice()
        
    def setup_baymax_voice(self):
        """Configure voice to sound like Baymax - slow, gentle, and caring"""
        voices = self.engine.getProperty('voices')
        # Try to use a male voice for Baymax
        for voice in voices:
            if 'male' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Baymax characteristics: slow, gentle, caring
        self.engine.setProperty('rate', 150)  # Slower speech rate
        self.engine.setProperty('volume', 0.8)  # Moderate volume
        
    def speak(self, text):
        """Speak with Baymax's characteristic voice"""
        print(f"BAYMAX: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def speak_async(self, text):
        """Speak asynchronously to avoid blocking the GUI"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

class UserManager:
    """Manages user registration and facial data"""
    
    def __init__(self):
        self.users_file = "users.json"
        self.users = self.load_users()
        
    def load_users(self):
        """Load registered users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def register_user(self, name, face_encoding, medicine_schedule):
        """Register a new user with face data and medicine schedule"""
        user_id = len(self.users) + 1
        self.users[user_id] = {
            'name': name,
            'face_encoding': face_encoding.tolist(),
            'medicine_schedule': medicine_schedule,
            'last_medicine_time': None,
            'missed_doses': []
        }
        self.save_users()
        return user_id
    
    def get_user_by_face(self, face_encoding):
        """Find user by face encoding"""
        for user_id, user_data in self.users.items():
            if len(user_data['face_encoding']) > 0:
                known_encoding = np.array(user_data['face_encoding'])
                matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
                if matches[0]:
                    return user_id, user_data
        return None, None
    
    def update_medicine_time(self, user_id):
        """Update last medicine time for user"""
        if user_id in self.users:
            self.users[user_id]['last_medicine_time'] = datetime.now().isoformat()
            self.save_users()
    
    def log_missed_dose(self, user_id, medicine_time):
        """Log a missed medicine dose"""
        if user_id in self.users:
            self.users[user_id]['missed_doses'].append({
                'time': medicine_time.isoformat(),
                'scheduled_time': medicine_time.strftime('%H:%M')
            })
            self.save_users()

class MedicineReminder:
    """Handles medicine scheduling and reminders"""
    
    def __init__(self, user_manager, voice_system, gui_system):
        self.user_manager = user_manager
        self.voice_system = voice_system
        self.gui_system = gui_system
        self.reminder_queue = queue.Queue()
        self.missed_alerts_file = "missed_alerts.csv"
        self.setup_missed_alerts_file()
        
    def setup_missed_alerts_file(self):
        """Initialize missed alerts CSV file"""
        if not os.path.exists(self.missed_alerts_file):
            with open(self.missed_alerts_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User ID', 'User Name', 'Scheduled Time', 'Missed Time', 'Date'])
    
    def schedule_medicine_reminders(self):
        """Schedule medicine reminders for all users"""
        schedule.clear()
        
        for user_id, user_data in self.user_manager.users.items():
            for medicine_time in user_data['medicine_schedule']:
                schedule.every().day.at(medicine_time).do(
                    self.trigger_medicine_reminder, user_id, medicine_time
                )
        
        # Start the scheduler in a separate thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def trigger_medicine_reminder(self, user_id, medicine_time):
        """Trigger medicine reminder for a specific user"""
        self.reminder_queue.put((user_id, medicine_time))
    
    def process_reminders(self):
        """Process pending medicine reminders"""
        try:
            while not self.reminder_queue.empty():
                user_id, medicine_time = self.reminder_queue.get_nowait()
                self.handle_medicine_reminder(user_id, medicine_time)
        except queue.Empty:
            pass
    
    def handle_medicine_reminder(self, user_id, medicine_time):
        """Handle individual medicine reminder with face recognition"""
        user_data = self.user_manager.users[user_id]
        user_name = user_data['name']
        
        # Wake up Baymax
        self.gui_system.set_expression("alert")
        greeting = f"Hello {user_name}. My name is Baymax, your personal healthcare companion. It's time for your medicine. Please take it now."
        self.voice_system.speak_async(greeting)
        
        # Try face recognition first
        if self.attempt_face_recognition(user_id):
            self.confirm_medicine_taken(user_id, user_name)
        else:
            # If face recognition fails, try voice command
            self.gui_system.set_expression("waiting")
            self.voice_system.speak_async("I cannot see your face clearly. Please say 'Hey Baymax' to confirm you've taken your medicine.")
            
            # Wait for voice command or timeout
            if not self.wait_for_voice_command():
                self.handle_missed_dose(user_id, user_name, medicine_time)
    
    def attempt_face_recognition(self, user_id):
        """Attempt to recognize user's face"""
        # This would integrate with the camera system
        # For now, return True to simulate successful recognition
        return True
    
    def wait_for_voice_command(self):
        """Wait for voice command 'Hey Baymax'"""
        # This would integrate with voice recognition
        # For now, return True to simulate successful command
        return True
    
    def confirm_medicine_taken(self, user_id, user_name):
        """Confirm medicine has been taken"""
        self.user_manager.update_medicine_time(user_id)
        self.gui_system.set_expression("happy")
        confirmation = f"Thank you {user_name}. I have recorded that you have taken your medicine. Is there anything else I can help you with?"
        self.voice_system.speak_async(confirmation)
    
    def handle_missed_dose(self, user_id, user_name, medicine_time):
        """Handle missed medicine dose"""
        self.user_manager.log_missed_dose(user_id, datetime.now())
        
        # Log to CSV
        with open(self.missed_alerts_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                user_id, user_name, medicine_time, 
                datetime.now().strftime('%H:%M'), 
                datetime.now().strftime('%Y-%m-%d')
            ])
        
        self.gui_system.set_expression("sad")
        missed_message = f"I'm sorry {user_name}, but I couldn't confirm that you took your medicine. I've logged this as a missed dose. Please take your medicine as soon as possible."
        self.voice_system.speak_async(missed_message)

class BaymaxGUI:
    """Graphical user interface with Baymax's animated face"""
    
    def __init__(self, voice_system, user_manager, medicine_reminder):
        self.voice_system = voice_system
        self.user_manager = user_manager
        self.medicine_reminder = medicine_reminder
        
        self.root = tk.Tk()
        self.root.title("BAYMAX - Your Personal Healthcare Companion")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        self.current_expression = "idle"
        self.expressions = {
            "idle": "😐",
            "happy": "😊",
            "alert": "😮",
            "sad": "😔",
            "waiting": "🤔"
        }
        
        self.setup_gui()
        self.setup_camera()
        
    def setup_gui(self):
        """Setup the main GUI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="BAYMAX", 
            font=('Arial', 24, 'bold'), 
            fg='white', 
            bg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        # Baymax face display
        self.face_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=3)
        self.face_frame.pack(pady=20)
        
        self.face_label = tk.Label(
            self.face_frame, 
            text=self.expressions["idle"], 
            font=('Arial', 72), 
            bg='#34495E', 
            fg='white'
        )
        self.face_label.pack(padx=40, pady=40)
        
        # Status display
        self.status_label = tk.Label(
            main_frame, 
            text="BAYMAX is ready to help you!", 
            font=('Arial', 12), 
            fg='white', 
            bg='#2C3E50',
            wraplength=600
        )
        self.status_label.pack(pady=10)
        
        # Camera feed
        self.camera_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=3)
        self.camera_frame.pack(pady=10)
        
        self.camera_label = tk.Label(self.camera_frame, bg='#34495E')
        self.camera_label.pack(padx=10, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#2C3E50')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame, 
            text="Register New User", 
            command=self.register_user_dialog,
            bg='#3498DB', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="View Users", 
            command=self.view_users_dialog,
            bg='#27AE60', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Voice Command", 
            command=self.voice_command_dialog,
            bg='#E74C3C', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        # Start the update loop
        self.update_gui()
    
    def setup_camera(self):
        """Setup camera for face recognition"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.status_label.config(text="Camera not available")
    
    def update_gui(self):
        """Update GUI elements"""
        # Update camera feed
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Resize frame for display
                frame = cv2.resize(frame, (320, 240))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                
                self.camera_label.configure(image=img_tk)
                self.camera_label.image = img_tk
        
        # Process medicine reminders
        self.medicine_reminder.process_reminders()
        
        # Schedule next update
        self.root.after(100, self.update_gui)
    
    def set_expression(self, expression):
        """Change Baymax's facial expression"""
        if expression in self.expressions:
            self.current_expression = expression
            self.face_label.config(text=self.expressions[expression])
    
    def register_user_dialog(self):
        """Dialog for registering new users"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New User")
        dialog.geometry("400x300")
        dialog.configure(bg='#2C3E50')
        
        # Name entry
        tk.Label(dialog, text="User Name:", bg='#2C3E50', fg='white').pack(pady=5)
        name_entry = tk.Entry(dialog, font=('Arial', 12))
        name_entry.pack(pady=5)
        
        # Medicine schedule
        tk.Label(dialog, text="Medicine Times (HH:MM, separated by commas):", bg='#2C3E50', fg='white').pack(pady=5)
        schedule_entry = tk.Entry(dialog, font=('Arial', 12))
        schedule_entry.pack(pady=5)
        schedule_entry.insert(0, "08:00, 20:00")
        
        def capture_face():
            """Capture user's face for registration"""
            if self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    # Find faces in the frame
                    face_locations = face_recognition.face_locations(frame)
                    if face_locations:
                        # Get face encoding
                        face_encodings = face_recognition.face_encodings(frame, face_locations)
                        if face_encodings:
                            # Use the first face found
                            face_encoding = face_encodings[0]
                            
                            # Parse medicine schedule
                            schedule_text = schedule_entry.get()
                            medicine_schedule = [time.strip() for time in schedule_text.split(',')]
                            
                            # Register user
                            user_id = self.user_manager.register_user(
                                name_entry.get(), face_encoding, medicine_schedule
                            )
                            
                            messagebox.showinfo("Success", f"User {name_entry.get()} registered successfully!")
                            dialog.destroy()
                            
                            # Reschedule reminders
                            self.medicine_reminder.schedule_medicine_reminders()
                        else:
                            messagebox.showerror("Error", "Could not encode face. Please try again.")
                    else:
                        messagebox.showerror("Error", "No face detected. Please position your face in the camera.")
                else:
                    messagebox.showerror("Error", "Could not capture image from camera.")
            else:
                messagebox.showerror("Error", "Camera not available.")
        
        # Capture face button
        tk.Button(
            dialog, 
            text="Capture Face & Register", 
            command=capture_face,
            bg='#3498DB', fg='white', font=('Arial', 10, 'bold')
        ).pack(pady=20)
    
    def view_users_dialog(self):
        """Dialog for viewing registered users"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Registered Users")
        dialog.geometry("500x400")
        dialog.configure(bg='#2C3E50')
        
        # Create treeview
        tree = ttk.Treeview(dialog, columns=('ID', 'Name', 'Schedule', 'Last Medicine'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('Schedule', text='Medicine Schedule')
        tree.heading('Last Medicine', text='Last Medicine Time')
        
        # Add users to treeview
        for user_id, user_data in self.user_manager.users.items():
            schedule_str = ', '.join(user_data['medicine_schedule'])
            last_medicine = user_data.get('last_medicine_time', 'Never')
            if last_medicine != 'Never':
                last_medicine = datetime.fromisoformat(last_medicine).strftime('%Y-%m-%d %H:%M')
            
            tree.insert('', 'end', values=(user_id, user_data['name'], schedule_str, last_medicine))
        
        tree.pack(padx=20, pady=20, fill='both', expand=True)
    
    def voice_command_dialog(self):
        """Dialog for voice commands"""
        self.set_expression("alert")
        self.voice_system.speak_async("Hello. I am Baymax, your personal healthcare companion. How can I help you today?")
    
    def run(self):
        """Start the GUI main loop"""
        # Schedule medicine reminders
        self.medicine_reminder.schedule_medicine_reminders()
        
        # Start GUI
        self.root.mainloop()

def main():
    """Main function to start BAYMAX"""
    print("Starting BAYMAX - Your Personal Healthcare Companion")
    
    # Initialize components
    voice_system = BaymaxVoice()
    user_manager = UserManager()
    medicine_reminder = MedicineReminder(user_manager, voice_system, None)  # GUI will be set later
    gui_system = BaymaxGUI(voice_system, user_manager, medicine_reminder)
    
    # Connect medicine reminder to GUI
    medicine_reminder.gui_system = gui_system
    
    # Welcome message
    voice_system.speak_async("Hello. I am Baymax, your personal healthcare companion. I am now online and ready to help you.")
    
    # Start GUI
    gui_system.run()

if __name__ == "__main__":
    main()