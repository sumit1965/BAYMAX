import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
from PIL import Image, ImageDraw, ImageTk
import math
from typing import Dict, Callable, Optional
import os

class BaymaxGUI:
    """
    GUI system for BAYMAX healthcare assistant with animated face expressions.
    """
    
    def __init__(self, title: str = "BAYMAX Healthcare Assistant"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Make window stay on top and center it
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        
        # Center the window
        self._center_window()
        
        # Current state
        self.current_expression = "idle"
        self.is_speaking = False
        self.animation_active = False
        
        # Animation parameters
        self.eye_blink_timer = 0
        self.mouth_animation_timer = 0
        self.face_color = "#ffffff"
        self.eye_color = "#000000"
        
        # Callbacks
        self.on_close_callback = None
        
        # Create GUI elements
        self._create_widgets()
        
        # Start animation thread
        self._start_animation_thread()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_font = font.Font(family="Arial", size=24, weight="bold")
        self.title_label = tk.Label(
            self.main_frame, 
            text="BAYMAX", 
            font=title_font, 
            bg='#f0f0f0', 
            fg='#2c3e50'
        )
        self.title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_font = font.Font(family="Arial", size=12)
        self.subtitle_label = tk.Label(
            self.main_frame, 
            text="Your Personal Healthcare Companion", 
            font=subtitle_font, 
            bg='#f0f0f0', 
            fg='#7f8c8d'
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Face canvas
        self.face_canvas = tk.Canvas(
            self.main_frame, 
            width=300, 
            height=300, 
            bg='#f0f0f0', 
            highlightthickness=0
        )
        self.face_canvas.pack(pady=20)
        
        # Status label
        status_font = font.Font(family="Arial", size=14)
        self.status_label = tk.Label(
            self.main_frame, 
            text="Hello! I am ready to help.", 
            font=status_font, 
            bg='#f0f0f0', 
            fg='#34495e',
            wraplength=400,
            justify='center'
        )
        self.status_label.pack(pady=10)
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=300
        )
        
        # Button frame
        self.button_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        self.button_frame.pack(pady=20)
        
        # Buttons (initially hidden)
        button_font = font.Font(family="Arial", size=10)
        
        self.register_button = tk.Button(
            self.button_frame,
            text="Register User",
            font=button_font,
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            command=self._on_register_click
        )
        
        self.schedule_button = tk.Button(
            self.button_frame,
            text="Medicine Schedule",
            font=button_font,
            bg='#2ecc71',
            fg='white',
            padx=20,
            pady=10,
            command=self._on_schedule_click
        )
        
        self.test_button = tk.Button(
            self.button_frame,
            text="Test Voice",
            font=button_font,
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            command=self._on_test_voice_click
        )
        
        # Initially draw the face
        self._draw_face()
    
    def _draw_face(self):
        """Draw Baymax's face on the canvas."""
        self.face_canvas.delete("all")
        
        canvas_width = 300
        canvas_height = 300
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Face (white circle with black border)
        face_radius = 120
        self.face_canvas.create_oval(
            center_x - face_radius, center_y - face_radius,
            center_x + face_radius, center_y + face_radius,
            fill=self.face_color, outline='#2c3e50', width=3
        )
        
        # Eyes
        self._draw_eyes(center_x, center_y)
        
        # Mouth
        self._draw_mouth(center_x, center_y)
        
        # Optional: Add some Baymax-like details
        if self.current_expression == "happy":
            # Add slight blush
            self.face_canvas.create_oval(
                center_x - 80, center_y + 10,
                center_x - 60, center_y + 30,
                fill='#ffb3ba', outline='#ffb3ba'
            )
            self.face_canvas.create_oval(
                center_x + 60, center_y + 10,
                center_x + 80, center_y + 30,
                fill='#ffb3ba', outline='#ffb3ba'
            )
    
    def _draw_eyes(self, center_x: int, center_y: int):
        """Draw Baymax's eyes based on current expression."""
        eye_y = center_y - 30
        left_eye_x = center_x - 40
        right_eye_x = center_x + 40
        
        if self.current_expression == "idle":
            # Normal circular eyes
            eye_radius = 15
            self.face_canvas.create_oval(
                left_eye_x - eye_radius, eye_y - eye_radius,
                left_eye_x + eye_radius, eye_y + eye_radius,
                fill=self.eye_color, outline=self.eye_color
            )
            self.face_canvas.create_oval(
                right_eye_x - eye_radius, eye_y - eye_radius,
                right_eye_x + eye_radius, eye_y + eye_radius,
                fill=self.eye_color, outline=self.eye_color
            )
        
        elif self.current_expression == "blinking":
            # Closed eyes (horizontal lines)
            self.face_canvas.create_line(
                left_eye_x - 15, eye_y,
                left_eye_x + 15, eye_y,
                fill=self.eye_color, width=3
            )
            self.face_canvas.create_line(
                right_eye_x - 15, eye_y,
                right_eye_x + 15, eye_y,
                fill=self.eye_color, width=3
            )
        
        elif self.current_expression == "happy":
            # Happy eyes (crescents)
            self._draw_crescent_eye(left_eye_x, eye_y, "happy")
            self._draw_crescent_eye(right_eye_x, eye_y, "happy")
        
        elif self.current_expression == "concerned":
            # Concerned eyes (slightly tilted)
            eye_radius = 12
            self.face_canvas.create_oval(
                left_eye_x - eye_radius, eye_y - eye_radius - 5,
                left_eye_x + eye_radius, eye_y + eye_radius - 5,
                fill=self.eye_color, outline=self.eye_color
            )
            self.face_canvas.create_oval(
                right_eye_x - eye_radius, eye_y - eye_radius - 5,
                right_eye_x + eye_radius, eye_y + eye_radius - 5,
                fill=self.eye_color, outline=self.eye_color
            )
        
        elif self.current_expression == "alert":
            # Alert eyes (larger)
            eye_radius = 20
            self.face_canvas.create_oval(
                left_eye_x - eye_radius, eye_y - eye_radius,
                left_eye_x + eye_radius, eye_y + eye_radius,
                fill=self.eye_color, outline=self.eye_color
            )
            self.face_canvas.create_oval(
                right_eye_x - eye_radius, eye_y - eye_radius,
                right_eye_x + eye_radius, eye_y + eye_radius,
                fill=self.eye_color, outline=self.eye_color
            )
    
    def _draw_crescent_eye(self, x: int, y: int, expression: str):
        """Draw a crescent-shaped eye for happy expression."""
        if expression == "happy":
            # Draw a small arc for happy eyes
            self.face_canvas.create_arc(
                x - 15, y - 8,
                x + 15, y + 8,
                start=0, extent=180,
                fill=self.eye_color, outline=self.eye_color,
                style='arc', width=3
            )
    
    def _draw_mouth(self, center_x: int, center_y: int):
        """Draw Baymax's mouth based on current expression."""
        mouth_y = center_y + 40
        
        if self.current_expression == "idle":
            # Small neutral mouth
            self.face_canvas.create_line(
                center_x - 15, mouth_y,
                center_x + 15, mouth_y,
                fill=self.eye_color, width=2
            )
        
        elif self.current_expression == "speaking":
            # Animated speaking mouth (oval)
            mouth_width = 20 + int(10 * math.sin(self.mouth_animation_timer))
            mouth_height = 10 + int(5 * math.sin(self.mouth_animation_timer * 1.5))
            self.face_canvas.create_oval(
                center_x - mouth_width//2, mouth_y - mouth_height//2,
                center_x + mouth_width//2, mouth_y + mouth_height//2,
                fill=self.eye_color, outline=self.eye_color
            )
        
        elif self.current_expression == "happy":
            # Smiling mouth (upward arc)
            self.face_canvas.create_arc(
                center_x - 25, mouth_y - 10,
                center_x + 25, mouth_y + 10,
                start=0, extent=180,
                fill='', outline=self.eye_color,
                style='arc', width=3
            )
        
        elif self.current_expression == "concerned":
            # Concerned mouth (downward arc)
            self.face_canvas.create_arc(
                center_x - 20, mouth_y - 5,
                center_x + 20, mouth_y + 15,
                start=180, extent=180,
                fill='', outline=self.eye_color,
                style='arc', width=3
            )
        
        elif self.current_expression == "alert":
            # Alert mouth (small circle)
            self.face_canvas.create_oval(
                center_x - 8, mouth_y - 8,
                center_x + 8, mouth_y + 8,
                fill='', outline=self.eye_color, width=2
            )
    
    def set_expression(self, expression: str):
        """
        Set Baymax's facial expression.
        
        Args:
            expression: One of 'idle', 'happy', 'concerned', 'alert', 'speaking', 'blinking'
        """
        if expression != self.current_expression:
            self.current_expression = expression
            self._draw_face()
    
    def set_speaking(self, is_speaking: bool):
        """Set whether Baymax is currently speaking."""
        self.is_speaking = is_speaking
        if is_speaking:
            self.set_expression("speaking")
        else:
            self.set_expression("idle")
    
    def update_status(self, message: str, expression: str = None):
        """
        Update the status message and optionally change expression.
        
        Args:
            message: Status message to display
            expression: Optional expression to set
        """
        self.status_label.config(text=message)
        if expression:
            self.set_expression(expression)
    
    def show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        if show:
            self.progress_bar.pack(pady=10)
        else:
            self.progress_bar.pack_forget()
    
    def set_progress(self, value: float):
        """Set progress bar value (0-100)."""
        self.progress_var.set(value)
    
    def show_buttons(self, show: bool = True):
        """Show or hide the control buttons."""
        if show:
            self.register_button.pack(side='left', padx=5)
            self.schedule_button.pack(side='left', padx=5)
            self.test_button.pack(side='left', padx=5)
        else:
            self.register_button.pack_forget()
            self.schedule_button.pack_forget()
            self.test_button.pack_forget()
    
    def _start_animation_thread(self):
        """Start the animation thread for eye blinking and mouth movement."""
        self.animation_active = True
        
        def animation_loop():
            while self.animation_active:
                try:
                    # Update animation timers
                    self.eye_blink_timer += 0.1
                    self.mouth_animation_timer += 0.2
                    
                    # Random eye blinking
                    if self.eye_blink_timer > 3 and not self.is_speaking:
                        if self.current_expression == "idle":
                            self.set_expression("blinking")
                            time.sleep(0.1)
                            self.set_expression("idle")
                        self.eye_blink_timer = 0
                    
                    # Update speaking animation
                    if self.is_speaking and self.current_expression == "speaking":
                        self._draw_face()
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Animation error: {e}")
                    time.sleep(0.5)
        
        animation_thread = threading.Thread(target=animation_loop, daemon=True)
        animation_thread.start()
    
    def _on_register_click(self):
        """Handle register button click."""
        messagebox.showinfo("Register User", "User registration feature will be implemented.")
    
    def _on_schedule_click(self):
        """Handle schedule button click."""
        messagebox.showinfo("Medicine Schedule", "Medicine scheduling feature will be implemented.")
    
    def _on_test_voice_click(self):
        """Handle test voice button click."""
        messagebox.showinfo("Test Voice", "Voice test feature will be implemented.")
    
    def _on_closing(self):
        """Handle window closing event."""
        self.animation_active = False
        if self.on_close_callback:
            self.on_close_callback()
        self.root.quit()
        self.root.destroy()
    
    def set_close_callback(self, callback: Callable):
        """Set callback function for when window is closed."""
        self.on_close_callback = callback
    
    def run(self):
        """Start the GUI main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
    
    def update_gui(self):
        """Update the GUI (call this from other threads)."""
        try:
            self.root.update_idletasks()
        except:
            pass
    
    def show_medicine_reminder(self, user_name: str, medicine_name: str, reminder_count: int = 1):
        """
        Show medicine reminder dialog.
        
        Args:
            user_name: Name of the user
            medicine_name: Name of the medicine
            reminder_count: Which reminder this is (1, 2, 3)
        """
        self.set_expression("alert")
        
        if reminder_count == 1:
            title = "Medicine Reminder"
            message = f"Hello {user_name}!\n\nIt's time to take your {medicine_name}."
        else:
            title = f"Medicine Reminder #{reminder_count}"
            message = f"{user_name}, please remember to take your {medicine_name}.\n\nThis is reminder #{reminder_count}."
        
        self.update_status(f"Medicine reminder for {user_name}: {medicine_name}", "alert")
        
        # Show reminder dialog in a separate thread to avoid blocking
        def show_dialog():
            try:
                messagebox.showwarning(title, message)
            except:
                pass
        
        threading.Thread(target=show_dialog, daemon=True).start()
    
    def show_medicine_taken(self, user_name: str, medicine_name: str):
        """Show confirmation that medicine was taken."""
        self.set_expression("happy")
        self.update_status(f"Great! {user_name} took {medicine_name}.", "happy")
        
        # Reset to idle after a few seconds
        def reset_expression():
            time.sleep(3)
            self.set_expression("idle")
            self.update_status("Ready to help with your healthcare needs.")
        
        threading.Thread(target=reset_expression, daemon=True).start()
    
    def show_medicine_missed(self, user_name: str, medicine_name: str):
        """Show notification that medicine was missed."""
        self.set_expression("concerned")
        self.update_status(f"Medicine missed: {user_name} - {medicine_name}", "concerned")
    
    def show_face_recognition_status(self, status: str):
        """Show face recognition status."""
        if status == "recognizing":
            self.set_expression("alert")
            self.update_status("Looking for registered user...", "alert")
        elif status == "recognized":
            self.set_expression("happy")
            self.update_status("User recognized! Please confirm medicine intake.", "happy")
        elif status == "not_recognized":
            self.set_expression("concerned")
            self.update_status("Face not recognized. Using voice authentication...", "concerned")
        elif status == "no_face":
            self.set_expression("alert")
            self.update_status("No face detected. Please look at the camera.", "alert")
    
    def create_registration_dialog(self):
        """Create user registration dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New User")
        dialog.geometry("400x300")
        dialog.configure(bg='#f0f0f0')
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # User name entry
        tk.Label(dialog, text="User Name:", bg='#f0f0f0').pack(pady=10)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        # Medicine name entry
        tk.Label(dialog, text="Medicine Name:", bg='#f0f0f0').pack(pady=10)
        medicine_entry = tk.Entry(dialog, width=30)
        medicine_entry.pack(pady=5)
        
        # Time entries
        tk.Label(dialog, text="Medicine Times (HH:MM, comma separated):", bg='#f0f0f0').pack(pady=10)
        time_entry = tk.Entry(dialog, width=30)
        time_entry.pack(pady=5)
        time_entry.insert(0, "08:00, 20:00")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        def on_register():
            user_name = name_entry.get().strip()
            medicine_name = medicine_entry.get().strip()
            times = [t.strip() for t in time_entry.get().split(',')]
            
            if user_name and medicine_name and times:
                # This would call the actual registration function
                messagebox.showinfo("Success", f"User {user_name} registered successfully!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please fill in all fields.")
        
        tk.Button(
            button_frame, text="Register", 
            command=on_register, bg='#3498db', fg='white'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame, text="Cancel", 
            command=dialog.destroy, bg='#e74c3c', fg='white'
        ).pack(side='left', padx=10)
        
        return dialog