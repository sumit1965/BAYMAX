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
import pyttsx3
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import schedule
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import speech_recognition as sr
from PIL import Image, ImageTk
import pygame

class BaymaxVoice:
    """Handles Baymax's voice synthesis with characteristic speech patterns"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        
    def setup_voice(self):
        """Configure voice to sound like Baymax - slow, gentle, and caring"""
        voices = self.engine.getProperty('voices')
        # Try to find a male voice
        for voice in voices:
            if 'male' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Baymax characteristics: slow, gentle, caring
        self.engine.setProperty('rate', 150)  # Slower speech
        self.engine.setProperty('volume', 0.8)  # Moderate volume
        self.engine.setProperty('pitch', 100)  # Lower pitch for gentle tone
        
    def speak(self, text):
        """Speak with Baymax's characteristic voice"""
        print(f"BAYMAX: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def greet(self, user_name):
        """Greet user in Baymax's style"""
        greetings = [
            f"Hello {user_name}. I am Baymax, your personal healthcare companion.",
            f"Greetings {user_name}. I am Baymax, here to assist with your healthcare needs.",
            f"Hello {user_name}. I am Baymax, your healthcare assistant."
        ]
        self.speak(np.random.choice(greetings))
        
    def medicine_reminder(self, user_name, medicine_name):
        """Remind user to take medicine"""
        reminders = [
            f"Hello {user_name}. It is time for your {medicine_name}. Please take it now.",
            f"{user_name}, your {medicine_name} is due. Please take it at this time.",
            f"Hello. My name is Baymax, your personal healthcare companion. It's time for your {medicine_name}. Please take it now."
        ]
        self.speak(np.random.choice(reminders))
        
    def confirm_medicine(self, user_name):
        """Confirm medicine has been taken"""
        self.speak(f"Thank you {user_name}. I have recorded that you have taken your medicine.")
        
    def missed_medicine_alert(self, user_name, medicine_name):
        """Alert for missed medicine"""
        self.speak(f"I notice you have not confirmed taking your {medicine_name}. Please take it as soon as possible.")
        
    def emergency_response(self):
        """Respond to emergency voice command"""
        self.speak("Hello. I am Baymax. How may I assist you with your healthcare needs?")

class FaceRecognition:
    """Handles facial recognition for user authentication"""
    
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_registered_users()
        
    def load_registered_users(self):
        """Load registered users from database"""
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                users_data = json.load(f)
                for user in users_data:
                    if 'face_encoding' in user:
                        self.known_face_encodings.append(np.array(user['face_encoding']))
                        self.known_face_names.append(user['name'])
                        
    def register_user(self, name, face_encoding):
        """Register a new user"""
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)
        self.save_users()
        
    def save_users(self):
        """Save users to database"""
        users_data = []
        for i, name in enumerate(self.known_face_names):
            users_data.append({
                'name': name,
                'face_encoding': self.known_face_encodings[i].tolist()
            })
        with open('users.json', 'w') as f:
            json.dump(users_data, f)
            
    def recognize_face(self, frame):
        """Recognize face in frame"""
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
                
            face_names.append(name)
            
        return face_names, face_locations

class MedicineScheduler:
    """Handles medicine scheduling and reminders"""
    
    def __init__(self):
        self.medicine_schedule = {}
        self.load_schedule()
        
    def load_schedule(self):
        """Load medicine schedule from file"""
        if os.path.exists('medicine_schedule.json'):
            with open('medicine_schedule.json', 'r') as f:
                self.medicine_schedule = json.load(f)
                
    def save_schedule(self):
        """Save medicine schedule to file"""
        with open('medicine_schedule.json', 'w') as f:
            json.dump(self.medicine_schedule, f, indent=2)
            
    def add_medicine(self, user_name, medicine_name, times):
        """Add medicine schedule for user"""
        if user_name not in self.medicine_schedule:
            self.medicine_schedule[user_name] = {}
        self.medicine_schedule[user_name][medicine_name] = times
        self.save_schedule()
        
    def get_current_medicines(self):
        """Get medicines due at current time"""
        current_time = datetime.now().strftime("%H:%M")
        due_medicines = []
        
        for user_name, medicines in self.medicine_schedule.items():
            for medicine_name, times in medicines.items():
                if current_time in times:
                    due_medicines.append((user_name, medicine_name))
                    
        return due_medicines
        
    def log_missed_dose(self, user_name, medicine_name):
        """Log missed medicine dose"""
        missed_data = {
            'user_name': user_name,
            'medicine_name': medicine_name,
            'scheduled_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'missed'
        }
        
        # Save to CSV
        df = pd.DataFrame([missed_data])
        if os.path.exists('missed_doses.csv'):
            df.to_csv('missed_doses.csv', mode='a', header=False, index=False)
        else:
            df.to_csv('missed_doses.csv', index=False)

class BaymaxGUI:
    """Graphical user interface with Baymax's animated face"""
    
    def __init__(self, baymax_system):
        self.baymax_system = baymax_system
        self.root = tk.Tk()
        self.root.title("BAYMAX - Healthcare Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        self.current_expression = "idle"
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="BAYMAX", 
                              font=("Arial", 24, "bold"), 
                              fg='#ECF0F1', bg='#2C3E50')
        title_label.pack(pady=10)
        
        # Baymax face display
        self.face_frame = tk.Frame(main_frame, bg='#34495E', width=400, height=300)
        self.face_frame.pack(pady=20)
        self.face_frame.pack_propagate(False)
        
        # Face canvas
        self.face_canvas = tk.Canvas(self.face_frame, bg='#34495E', width=400, height=300)
        self.face_canvas.pack()
        
        # Status display
        self.status_label = tk.Label(main_frame, text="Status: Idle", 
                                    font=("Arial", 12), 
                                    fg='#ECF0F1', bg='#2C3E50')
        self.status_label.pack(pady=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#2C3E50')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Register User", 
                 command=self.register_user_window,
                 bg='#3498DB', fg='white', font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Add Medicine", 
                 command=self.add_medicine_window,
                 bg='#E74C3C', fg='white', font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Emergency Call", 
                 command=self.emergency_call,
                 bg='#F39C12', fg='white', font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        
        # Draw initial face
        self.draw_face("idle")
        
    def draw_face(self, expression):
        """Draw Baymax's face with different expressions"""
        self.face_canvas.delete("all")
        
        # Face outline (white circle)
        self.face_canvas.create_oval(50, 50, 350, 350, fill='white', outline='#BDC3C7', width=3)
        
        if expression == "idle":
            # Idle expression - simple eyes and mouth
            self.face_canvas.create_oval(120, 120, 160, 160, fill='black')  # Left eye
            self.face_canvas.create_oval(240, 120, 280, 160, fill='black')  # Right eye
            self.face_canvas.create_arc(150, 180, 250, 280, start=0, extent=180, fill='black')  # Smile
            
        elif expression == "talking":
            # Talking expression - animated mouth
            self.face_canvas.create_oval(120, 120, 160, 160, fill='black')  # Left eye
            self.face_canvas.create_oval(240, 120, 280, 160, fill='black')  # Right eye
            self.face_canvas.create_oval(170, 200, 230, 260, fill='black')  # Open mouth
            
        elif expression == "alerting":
            # Alert expression - concerned look
            self.face_canvas.create_oval(120, 130, 160, 150, fill='black')  # Left eye (squinted)
            self.face_canvas.create_oval(240, 130, 280, 150, fill='black')  # Right eye (squinted)
            self.face_canvas.create_arc(150, 200, 250, 260, start=180, extent=180, fill='black')  # Concerned mouth
            
        elif expression == "sad":
            # Sad expression - droopy eyes and frown
            self.face_canvas.create_oval(120, 140, 160, 160, fill='black')  # Left eye (droopy)
            self.face_canvas.create_oval(240, 140, 280, 160, fill='black')  # Right eye (droopy)
            self.face_canvas.create_arc(150, 220, 250, 280, start=0, extent=-180, fill='black')  # Frown
            
        self.current_expression = expression
        
    def update_status(self, status):
        """Update status display"""
        self.status_label.config(text=f"Status: {status}")
        
    def register_user_window(self):
        """Open user registration window"""
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("400x300")
        register_window.configure(bg='#2C3E50')
        
        tk.Label(register_window, text="Register New User", 
                font=("Arial", 16, "bold"), 
                fg='#ECF0F1', bg='#2C3E50').pack(pady=20)
        
        tk.Label(register_window, text="Name:", 
                fg='#ECF0F1', bg='#2C3E50').pack()
        name_entry = tk.Entry(register_window, width=30)
        name_entry.pack(pady=10)
        
        def capture_face():
            name = name_entry.get().strip()
            if name:
                self.baymax_system.register_user(name)
                register_window.destroy()
                messagebox.showinfo("Success", f"User {name} registered successfully!")
            else:
                messagebox.showerror("Error", "Please enter a name")
                
        tk.Button(register_window, text="Capture Face & Register", 
                 command=capture_face,
                 bg='#3498DB', fg='white').pack(pady=20)
        
    def add_medicine_window(self):
        """Open medicine scheduling window"""
        medicine_window = tk.Toplevel(self.root)
        medicine_window.title("Add Medicine Schedule")
        medicine_window.geometry("500x400")
        medicine_window.configure(bg='#2C3E50')
        
        tk.Label(medicine_window, text="Add Medicine Schedule", 
                font=("Arial", 16, "bold"), 
                fg='#ECF0F1', bg='#2C3E50').pack(pady=20)
        
        # User selection
        tk.Label(medicine_window, text="User:", 
                fg='#ECF0F1', bg='#2C3E50').pack()
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(medicine_window, textvariable=user_var, 
                                 values=self.baymax_system.face_recognition.known_face_names)
        user_combo.pack(pady=10)
        
        # Medicine name
        tk.Label(medicine_window, text="Medicine Name:", 
                fg='#ECF0F1', bg='#2C3E50').pack()
        medicine_entry = tk.Entry(medicine_window, width=30)
        medicine_entry.pack(pady=10)
        
        # Time selection
        tk.Label(medicine_window, text="Time (HH:MM):", 
                fg='#ECF0F1', bg='#2C3E50').pack()
        time_entry = tk.Entry(medicine_window, width=30)
        time_entry.pack(pady=10)
        
        def save_medicine():
            user = user_var.get()
            medicine = medicine_entry.get().strip()
            time_str = time_entry.get().strip()
            
            if user and medicine and time_str:
                self.baymax_system.medicine_scheduler.add_medicine(user, medicine, [time_str])
                medicine_window.destroy()
                messagebox.showinfo("Success", f"Medicine schedule added for {user}")
            else:
                messagebox.showerror("Error", "Please fill all fields")
                
        tk.Button(medicine_window, text="Save Schedule", 
                 command=save_medicine,
                 bg='#E74C3C', fg='white').pack(pady=20)
        
    def emergency_call(self):
        """Trigger emergency voice command"""
        self.baymax_system.emergency_voice_command()

class BaymaxSystem:
    """Main BAYMAX system that coordinates all components"""
    
    def __init__(self):
        self.voice = BaymaxVoice()
        self.face_recognition = FaceRecognition()
        self.medicine_scheduler = MedicineScheduler()
        self.gui = BaymaxGUI(self)
        
        self.camera = cv2.VideoCapture(0)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.is_running = False
        self.current_user = None
        self.medicine_confirmation_pending = False
        
        # Start background threads
        self.start_background_tasks()
        
    def start_background_tasks(self):
        """Start background monitoring threads"""
        self.is_running = True
        
        # Medicine scheduler thread
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Face recognition thread
        face_thread = threading.Thread(target=self.run_face_recognition, daemon=True)
        face_thread.start()
        
        # Voice command thread
        voice_thread = threading.Thread(target=self.run_voice_recognition, daemon=True)
        voice_thread.start()
        
    def run_scheduler(self):
        """Run medicine scheduler"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
            
    def run_face_recognition(self):
        """Run continuous face recognition"""
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                face_names, face_locations = self.face_recognition.recognize_face(frame)
                
                if face_names and face_names[0] != "Unknown":
                    self.current_user = face_names[0]
                    self.gui.update_status(f"User detected: {self.current_user}")
                    
                    # Check if medicine is due
                    if self.medicine_confirmation_pending:
                        self.confirm_medicine_taken()
                        
            time.sleep(0.1)
            
    def run_voice_recognition(self):
        """Run voice command recognition"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
        while self.is_running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                try:
                    command = self.recognizer.recognize_google(audio).lower()
                    if "hey baymax" in command or "hello baymax" in command:
                        self.emergency_voice_command()
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
                    
            except sr.WaitTimeoutError:
                pass
                
    def register_user(self, name):
        """Register a new user with face capture"""
        self.gui.update_status("Capturing face for registration...")
        self.gui.draw_face("talking")
        
        # Capture face
        ret, frame = self.camera.read()
        if ret:
            face_encodings = face_recognition.face_encodings(frame)
            if face_encodings:
                self.face_recognition.register_user(name, face_encodings[0])
                self.voice.speak(f"Hello {name}. I have registered your face. I am Baymax, your personal healthcare companion.")
                self.gui.update_status(f"User {name} registered")
            else:
                self.voice.speak("I could not detect a face. Please look at the camera.")
                
        self.gui.draw_face("idle")
        
    def emergency_voice_command(self):
        """Handle emergency voice command"""
        self.gui.draw_face("talking")
        self.gui.update_status("Emergency voice command received")
        self.voice.emergency_response()
        
        # Check for medicine due
        due_medicines = self.medicine_scheduler.get_current_medicines()
        if due_medicines:
            for user_name, medicine_name in due_medicines:
                self.voice.medicine_reminder(user_name, medicine_name)
                self.medicine_confirmation_pending = True
                
        self.gui.draw_face("idle")
        
    def confirm_medicine_taken(self):
        """Confirm medicine has been taken"""
        if self.current_user and self.medicine_confirmation_pending:
            self.gui.draw_face("talking")
            self.voice.confirm_medicine(self.current_user)
            self.medicine_confirmation_pending = False
            self.gui.update_status("Medicine confirmed")
            self.gui.draw_face("idle")
            
    def check_medicine_schedule(self):
        """Check and handle medicine schedule"""
        due_medicines = self.medicine_scheduler.get_current_medicines()
        
        for user_name, medicine_name in due_medicines:
            self.gui.draw_face("alerting")
            self.gui.update_status(f"Medicine reminder: {medicine_name} for {user_name}")
            
            # Give medicine reminder
            self.voice.medicine_reminder(user_name, medicine_name)
            self.medicine_confirmation_pending = True
            
            # Wait for confirmation with retries
            for attempt in range(3):
                time.sleep(20)  # Wait 20 seconds
                if not self.medicine_confirmation_pending:
                    break
                    
                if attempt < 2:  # Not the last attempt
                    self.voice.missed_medicine_alert(user_name, medicine_name)
                    
            # If still not confirmed, log as missed
            if self.medicine_confirmation_pending:
                self.medicine_scheduler.log_missed_dose(user_name, medicine_name)
                self.gui.draw_face("sad")
                self.gui.update_status(f"Medicine missed: {medicine_name} for {user_name}")
                self.voice.speak(f"I have logged that {user_name} missed their {medicine_name}.")
                self.medicine_confirmation_pending = False
                
        self.gui.draw_face("idle")
        
    def run(self):
        """Start the BAYMAX system"""
        # Schedule medicine checks
        schedule.every().minute.do(self.check_medicine_schedule)
        
        # Start GUI
        self.gui.root.mainloop()
        
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        self.camera.release()
        cv2.destroyAllWindows()

def main():
    """Main function to start BAYMAX"""
    print("Starting BAYMAX - Healthcare Assistant")
    print("Inspired by Big Hero 6")
    
    baymax = BaymaxSystem()
    
    try:
        baymax.run()
    except KeyboardInterrupt:
        print("\nShutting down BAYMAX...")
    finally:
        baymax.cleanup()

if __name__ == "__main__":
    main()