#!/usr/bin/env python3
"""
Voice Recognition Module for BAYMAX
Handles voice commands and emergency voice authentication
"""

import speech_recognition as sr
import threading
import time
import queue
from datetime import datetime

class VoiceRecognition:
    """Handles voice recognition for BAYMAX voice commands"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.wake_word = "hey baymax"
        self.emergency_commands = ["hey baymax", "hello baymax", "baymax"]
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def start_listening(self):
        """Start listening for voice commands"""
        self.is_listening = True
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
    
    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False
    
    def _listen_loop(self):
        """Main listening loop for voice commands"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    print("Listening for voice commands...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")
                    
                    # Check for wake word or emergency commands
                    if any(cmd in text for cmd in self.emergency_commands):
                        self.command_queue.put(("wake", text))
                    elif "medicine" in text or "taken" in text:
                        self.command_queue.put(("medicine_confirmed", text))
                    elif "help" in text:
                        self.command_queue.put(("help", text))
                    elif "stop" in text or "goodbye" in text:
                        self.command_queue.put(("stop", text))
                        
                except sr.UnknownValueError:
                    pass  # Speech was unintelligible
                except sr.RequestError as e:
                    print(f"Could not request results: {e}")
                    
            except sr.WaitTimeoutError:
                pass  # No speech detected
            except Exception as e:
                print(f"Error in voice recognition: {e}")
    
    def wait_for_command(self, timeout=30):
        """Wait for a specific command with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                command_type, text = self.command_queue.get_nowait()
                return command_type, text
            except queue.Empty:
                time.sleep(0.1)
        return None, None
    
    def is_wake_word_detected(self, timeout=10):
        """Check if wake word is detected within timeout"""
        command_type, _ = self.wait_for_command(timeout)
        return command_type == "wake"
    
    def confirm_medicine_voice(self, timeout=20):
        """Wait for medicine confirmation via voice"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                command_type, text = self.command_queue.get_nowait()
                if command_type == "medicine_confirmed":
                    return True
                elif command_type == "wake":
                    # User said wake word again, treat as confirmation
                    return True
            except queue.Empty:
                time.sleep(0.1)
        return False

class VoiceCommandHandler:
    """Handles voice commands and integrates with BAYMAX system"""
    
    def __init__(self, voice_recognition, voice_system, gui_system):
        self.voice_recognition = voice_recognition
        self.voice_system = voice_system
        self.gui_system = gui_system
        self.is_active = False
        
    def activate(self):
        """Activate voice command handling"""
        self.is_active = True
        self.voice_recognition.start_listening()
        
    def deactivate(self):
        """Deactivate voice command handling"""
        self.is_active = False
        self.voice_recognition.stop_listening()
    
    def handle_emergency_voice_command(self):
        """Handle emergency voice command for medicine confirmation"""
        self.gui_system.set_expression("alert")
        self.voice_system.speak_async("I heard you call for me. Please confirm that you have taken your medicine by saying 'I took my medicine' or 'medicine taken'.")
        
        # Wait for confirmation
        if self.voice_recognition.confirm_medicine_voice(timeout=20):
            self.gui_system.set_expression("happy")
            self.voice_system.speak_async("Thank you for confirming. I have recorded that you have taken your medicine.")
            return True
        else:
            self.gui_system.set_expression("sad")
            self.voice_system.speak_async("I couldn't confirm that you took your medicine. Please take it as soon as possible.")
            return False
    
    def process_voice_commands(self):
        """Process any pending voice commands"""
        if not self.is_active:
            return
            
        try:
            while not self.voice_recognition.command_queue.empty():
                command_type, text = self.voice_recognition.command_queue.get_nowait()
                self._handle_command(command_type, text)
        except queue.Empty:
            pass
    
    def _handle_command(self, command_type, text):
        """Handle individual voice commands"""
        if command_type == "wake":
            self.gui_system.set_expression("alert")
            self.voice_system.speak_async("Hello. I am Baymax, your personal healthcare companion. How can I help you today?")
            
        elif command_type == "medicine_confirmed":
            self.gui_system.set_expression("happy")
            self.voice_system.speak_async("Thank you for confirming that you have taken your medicine.")
            
        elif command_type == "help":
            self.gui_system.set_expression("alert")
            self.voice_system.speak_async("I'm here to help you with your healthcare needs. I can remind you about medicine, track your health, and provide assistance when needed.")
            
        elif command_type == "stop":
            self.gui_system.set_expression("idle")
            self.voice_system.speak_async("Goodbye. I'll be here when you need me.")