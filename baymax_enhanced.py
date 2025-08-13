#!/usr/bin/env python3
"""
BAYMAX Enhanced - Smart Healthcare Assistant
Complete integration with voice recognition and enhanced face recognition
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

# Import voice recognition module
try:
    from voice_recognition import VoiceRecognition, VoiceCommandHandler
    VOICE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("Voice recognition not available. Install SpeechRecognition and PyAudio.")
    VOICE_RECOGNITION_AVAILABLE = False

class BaymaxVoice:
    """Enhanced voice synthesis with Baymax characteristics"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_baymax_voice()
        self.speaking = False
        
    def setup_baymax_voice(self):
        """Configure voice to sound like Baymax"""
        voices = self.engine.getProperty('voices')
        
        # Try to use a male voice for Baymax
        for voice in voices:
            if 'male' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Baymax characteristics: slow, gentle, caring
        self.engine.setProperty('rate', 140)  # Slower speech rate
        self.engine.setProperty('volume', 0.9)  # Good volume
        self.engine.setProperty('pitch', 100)  # Normal pitch
        
    def speak(self, text):
        """Speak with Baymax's characteristic voice"""
        if self.speaking:
            return
            
        self.speaking = True
        print(f"BAYMAX: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        self.speaking = False
        
    def speak_async(self, text):
        """Speak asynchronously"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

class UserManager:
    """Enhanced user management with better face recognition"""
    
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
            'missed_doses': [],
            'registration_date': datetime.now().isoformat()
        }
        self.save_users()
        return user_id
    
    def get_user_by_face(self, face_encoding, tolerance=0.6):
        """Find user by face encoding with configurable tolerance"""
        for user_id, user_data in self.users.items():
            if len(user_data['face_encoding']) > 0:
                known_encoding = np.array(user_data['face_encoding'])
                matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=tolerance)
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
                'scheduled_time': medicine_time.strftime('%H:%M'),
                'date': medicine_time.strftime('%Y-%m-%d')
            })
            self.save_users()

class MedicineReminder:
    """Enhanced medicine reminder with voice and face recognition"""
    
    def __init__(self, user_manager, voice_system, gui_system, voice_handler=None):
        self.user_manager = user_manager
        self.voice_system = voice_system
        self.gui_system = gui_system
        self.voice_handler = voice_handler
        self.reminder_queue = queue.Queue()
        self.missed_alerts_file = "missed_alerts.csv"
        self.setup_missed_alerts_file()
        self.alert_count = {}  # Track alert attempts per user
        
    def setup_missed_alerts_file(self):
        """Initialize missed alerts CSV file"""
        if not os.path.exists(self.missed_alerts_file):
            with open(self.missed_alerts_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User ID', 'User Name', 'Scheduled Time', 'Missed Time', 'Date', 'Alert Attempts'])
    
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
        """Handle individual medicine reminder with enhanced recognition"""
        user_data = self.user_manager.users[user_id]
        user_name = user_data['name']
        
        # Initialize alert count for this user
        if user_id not in self.alert_count:
            self.alert_count[user_id] = 0
        
        # Wake up Baymax
        self.gui_system.set_expression("alert")
        greeting = f"Hello {user_name}. My name is Baymax, your personal healthcare companion. It's time for your medicine. Please take it now."
        self.voice_system.speak_async(greeting)
        
        # Try face recognition first
        if self.attempt_face_recognition(user_id):
            self.confirm_medicine_taken(user_id, user_name)
            self.alert_count[user_id] = 0  # Reset alert count
        else:
            # If face recognition fails, try voice command
            self.alert_count[user_id] += 1
            
            if self.alert_count[user_id] <= 3:  # Allow up to 3 attempts
                self.gui_system.set_expression("waiting")
                self.voice_system.speak_async("I cannot see your face clearly. Please say 'Hey Baymax' to confirm you've taken your medicine.")
                
                # Wait for voice command
                if self.wait_for_voice_command():
                    self.confirm_medicine_taken(user_id, user_name)
                    self.alert_count[user_id] = 0
                else:
                    # Schedule another reminder in 20 seconds
                    threading.Timer(20.0, lambda: self.retry_reminder(user_id, medicine_time)).start()
            else:
                # Max attempts reached, log as missed dose
                self.handle_missed_dose(user_id, user_name, medicine_time)
                self.alert_count[user_id] = 0
    
    def retry_reminder(self, user_id, medicine_time):
        """Retry medicine reminder after 20 seconds"""
        user_data = self.user_manager.users[user_id]
        user_name = user_data['name']
        
        self.gui_system.set_expression("alert")
        retry_message = f"{user_name}, this is your second reminder. Please take your medicine now."
        self.voice_system.speak_async(retry_message)
        
        # Try face recognition again
        if self.attempt_face_recognition(user_id):
            self.confirm_medicine_taken(user_id, user_name)
            self.alert_count[user_id] = 0
        else:
            # Final attempt with voice command
            self.gui_system.set_expression("waiting")
            self.voice_system.speak_async("Please say 'Hey Baymax' to confirm you've taken your medicine.")
            
            if self.wait_for_voice_command():
                self.confirm_medicine_taken(user_id, user_name)
                self.alert_count[user_id] = 0
            else:
                self.handle_missed_dose(user_id, user_name, medicine_time)
                self.alert_count[user_id] = 0
    
    def attempt_face_recognition(self, user_id):
        """Attempt to recognize user's face using camera"""
        if hasattr(self.gui_system, 'camera') and self.gui_system.camera.isOpened():
            ret, frame = self.gui_system.camera.read()
            if ret:
                # Find faces in the frame
                face_locations = face_recognition.face_locations(frame)
                if face_locations:
                    # Get face encodings
                    face_encodings = face_recognition.face_encodings(frame, face_locations)
                    if face_encodings:
                        # Check each face found
                        for face_encoding in face_encodings:
                            detected_user_id, _ = self.user_manager.get_user_by_face(face_encoding)
                            if detected_user_id == user_id:
                                return True
        return False
    
    def wait_for_voice_command(self):
        """Wait for voice command 'Hey Baymax'"""
        if self.voice_handler and VOICE_RECOGNITION_AVAILABLE:
            return self.voice_handler.voice_recognition.is_wake_word_detected(timeout=20)
        return False
    
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
                datetime.now().strftime('%Y-%m-%d'),
                self.alert_count.get(user_id, 0)
            ])
        
        self.gui_system.set_expression("sad")
        missed_message = f"I'm sorry {user_name}, but I couldn't confirm that you took your medicine. I've logged this as a missed dose. Please take your medicine as soon as possible."
        self.voice_system.speak_async(missed_message)

class BaymaxGUI:
    """Enhanced GUI with better face recognition and voice integration"""
    
    def __init__(self, voice_system, user_manager, medicine_reminder, voice_handler=None):
        self.voice_system = voice_system
        self.user_manager = user_manager
        self.medicine_reminder = medicine_reminder
        self.voice_handler = voice_handler
        
        self.root = tk.Tk()
        self.root.title("BAYMAX - Your Personal Healthcare Companion")
        self.root.geometry("900x700")
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
        self.setup_camera()
        
    def setup_gui(self):
        """Setup the enhanced GUI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="BAYMAX", 
            font=('Arial', 28, 'bold'), 
            fg='white', 
            bg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            main_frame,
            text="Your Personal Healthcare Companion",
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
            text="BAYMAX is ready to help you!", 
            font=('Arial', 12), 
            fg='white', 
            bg='#2C3E50',
            wraplength=700
        )
        self.status_label.pack(pady=10)
        
        # Camera feed with face detection overlay
        self.camera_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=3)
        self.camera_frame.pack(pady=10)
        
        camera_title = tk.Label(
            self.camera_frame,
            text="Face Recognition Camera",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#34495E'
        )
        camera_title.pack(pady=5)
        
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
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="View Users", 
            command=self.view_users_dialog,
            bg='#27AE60', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Voice Command", 
            command=self.voice_command_dialog,
            bg='#E74C3C', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="View Missed Doses", 
            command=self.view_missed_doses_dialog,
            bg='#F39C12', fg='white', font=('Arial', 10, 'bold'),
            relief='raised', bd=2, width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Voice status indicator
        if VOICE_RECOGNITION_AVAILABLE:
            self.voice_status_label = tk.Label(
                main_frame,
                text="🎤 Voice Recognition: Active",
                font=('Arial', 10),
                fg='#27AE60',
                bg='#2C3E50'
            )
        else:
            self.voice_status_label = tk.Label(
                main_frame,
                text="🎤 Voice Recognition: Not Available",
                font=('Arial', 10),
                fg='#E74C3C',
                bg='#2C3E50'
            )
        self.voice_status_label.pack(pady=5)
        
        # Start the update loop
        self.update_gui()
    
    def setup_camera(self):
        """Setup camera for face recognition"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.status_label.config(text="Camera not available")
    
    def update_gui(self):
        """Update GUI elements with face detection overlay"""
        # Update camera feed
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Detect faces in the frame
                face_locations = face_recognition.face_locations(frame)
                
                # Draw rectangles around detected faces
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, "Face Detected", (left, top - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
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
        
        # Process voice commands
        if self.voice_handler:
            self.voice_handler.process_voice_commands()
        
        # Schedule next update
        self.root.after(100, self.update_gui)
    
    def set_expression(self, expression):
        """Change Baymax's facial expression"""
        if expression in self.expressions:
            self.current_expression = expression
            self.face_label.config(text=self.expressions[expression])
    
    def register_user_dialog(self):
        """Enhanced dialog for registering new users"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New User")
        dialog.geometry("500x400")
        dialog.configure(bg='#2C3E50')
        
        # Name entry
        tk.Label(dialog, text="User Name:", bg='#2C3E50', fg='white', font=('Arial', 12)).pack(pady=5)
        name_entry = tk.Entry(dialog, font=('Arial', 12), width=30)
        name_entry.pack(pady=5)
        
        # Medicine schedule
        tk.Label(dialog, text="Medicine Times (HH:MM, separated by commas):", bg='#2C3E50', fg='white', font=('Arial', 12)).pack(pady=5)
        schedule_entry = tk.Entry(dialog, font=('Arial', 12), width=30)
        schedule_entry.pack(pady=5)
        schedule_entry.insert(0, "08:00, 20:00")
        
        # Instructions
        instructions = tk.Label(
            dialog,
            text="Please position your face in the camera view and click 'Capture Face & Register'",
            bg='#2C3E50',
            fg='#BDC3C7',
            font=('Arial', 10),
            wraplength=400
        )
        instructions.pack(pady=10)
        
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
                            
                            # Validate schedule format
                            try:
                                for time_str in medicine_schedule:
                                    datetime.strptime(time_str, '%H:%M')
                            except ValueError:
                                messagebox.showerror("Error", "Invalid time format. Please use HH:MM format (e.g., 08:00, 20:00)")
                                return
                            
                            # Register user
                            user_id = self.user_manager.register_user(
                                name_entry.get(), face_encoding, medicine_schedule
                            )
                            
                            messagebox.showinfo("Success", f"User {name_entry.get()} registered successfully with ID: {user_id}")
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
            bg='#3498DB', fg='white', font=('Arial', 12, 'bold'),
            relief='raised', bd=2
        ).pack(pady=20)
    
    def view_users_dialog(self):
        """Enhanced dialog for viewing registered users"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Registered Users")
        dialog.geometry("600x500")
        dialog.configure(bg='#2C3E50')
        
        # Create treeview
        tree = ttk.Treeview(dialog, columns=('ID', 'Name', 'Schedule', 'Last Medicine', 'Missed Doses'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('Schedule', text='Medicine Schedule')
        tree.heading('Last Medicine', text='Last Medicine Time')
        tree.heading('Missed Doses', text='Missed Doses')
        
        # Set column widths
        tree.column('ID', width=50)
        tree.column('Name', width=100)
        tree.column('Schedule', width=150)
        tree.column('Last Medicine', width=150)
        tree.column('Missed Doses', width=100)
        
        # Add users to treeview
        for user_id, user_data in self.user_manager.users.items():
            schedule_str = ', '.join(user_data['medicine_schedule'])
            last_medicine = user_data.get('last_medicine_time', 'Never')
            if last_medicine != 'Never':
                last_medicine = datetime.fromisoformat(last_medicine).strftime('%Y-%m-%d %H:%M')
            
            missed_count = len(user_data.get('missed_doses', []))
            
            tree.insert('', 'end', values=(user_id, user_data['name'], schedule_str, last_medicine, missed_count))
        
        tree.pack(padx=20, pady=20, fill='both', expand=True)
    
    def view_missed_doses_dialog(self):
        """Dialog for viewing missed doses"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Missed Doses Report")
        dialog.geometry("600x400")
        dialog.configure(bg='#2C3E50')
        
        # Create treeview
        tree = ttk.Treeview(dialog, columns=('User ID', 'User Name', 'Scheduled Time', 'Missed Time', 'Date'), show='headings')
        tree.heading('User ID', text='User ID')
        tree.heading('User Name', text='User Name')
        tree.heading('Scheduled Time', text='Scheduled Time')
        tree.heading('Missed Time', text='Missed Time')
        tree.heading('Date', text='Date')
        
        # Load missed doses from CSV
        if os.path.exists(self.medicine_reminder.missed_alerts_file):
            with open(self.medicine_reminder.missed_alerts_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 5:
                        tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4]))
        
        tree.pack(padx=20, pady=20, fill='both', expand=True)
    
    def voice_command_dialog(self):
        """Dialog for voice commands"""
        self.set_expression("alert")
        self.voice_system.speak_async("Hello. I am Baymax, your personal healthcare companion. How can I help you today?")
    
    def run(self):
        """Start the GUI main loop"""
        # Schedule medicine reminders
        self.medicine_reminder.schedule_medicine_reminders()
        
        # Activate voice recognition if available
        if self.voice_handler and VOICE_RECOGNITION_AVAILABLE:
            self.voice_handler.activate()
        
        # Start GUI
        self.root.mainloop()

def main():
    """Main function to start enhanced BAYMAX"""
    print("Starting BAYMAX Enhanced - Your Personal Healthcare Companion")
    
    # Initialize components
    voice_system = BaymaxVoice()
    user_manager = UserManager()
    
    # Initialize voice recognition if available
    voice_handler = None
    if VOICE_RECOGNITION_AVAILABLE:
        try:
            voice_recognition = VoiceRecognition()
            voice_handler = VoiceCommandHandler(voice_recognition, voice_system, None)  # GUI will be set later
        except Exception as e:
            print(f"Voice recognition initialization failed: {e}")
    
    medicine_reminder = MedicineReminder(user_manager, voice_system, None, voice_handler)  # GUI will be set later
    gui_system = BaymaxGUI(voice_system, user_manager, medicine_reminder, voice_handler)
    
    # Connect components
    medicine_reminder.gui_system = gui_system
    if voice_handler:
        voice_handler.gui_system = gui_system
    
    # Welcome message
    voice_system.speak_async("Hello. I am Baymax, your personal healthcare companion. I am now online and ready to help you.")
    
    # Start GUI
    gui_system.run()

if __name__ == "__main__":
    main()