import pyttsx3
import speech_recognition as sr
import threading
import time
from typing import Optional, Callable, List
import os

class BaymaxVoice:
    """
    Voice system for BAYMAX healthcare assistant.
    Handles text-to-speech with Baymax-like characteristics and speech recognition.
    """
    
    def __init__(self):
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self._setup_baymax_voice()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Voice settings
        self.is_speaking = False
        self.recognition_active = False
        
        # Baymax phrases and responses
        self.baymax_phrases = {
            'greeting': [
                "Hello. My name is Baymax, your personal healthcare companion.",
                "Hello there. I am Baymax, your healthcare assistant.",
                "Greetings. I am Baymax, here to assist with your healthcare needs."
            ],
            'medicine_time': [
                "It is time for your medicine. Please take it now.",
                "Your scheduled medication time has arrived. Please take your medicine.",
                "Time for your medicine. Please ensure you take it as prescribed."
            ],
            'medicine_reminder': [
                "You have not confirmed taking your medicine. Please take it now.",
                "This is a reminder to take your medicine. Your health is important.",
                "Please remember to take your medicine. I am here to help you stay healthy."
            ],
            'medicine_taken': [
                "Thank you for taking your medicine. Your health is my priority.",
                "Medicine intake confirmed. You are taking good care of yourself.",
                "Excellent. Your medicine has been taken. Stay healthy."
            ],
            'medicine_missed': [
                "I notice you have missed your medicine. Please consult your healthcare provider.",
                "Your medicine was not taken at the scheduled time. This has been logged.",
                "Missed medication noted. Please speak with your doctor about this."
            ],
            'face_not_recognized': [
                "I do not recognize your face. Please ensure you are registered.",
                "Face authentication failed. Only registered users can confirm medicine intake.",
                "I cannot identify you. Please register your face first."
            ],
            'emergency_override': [
                "Emergency override activated. Please confirm your medicine intake verbally.",
                "Voice authentication mode enabled. Please state that you have taken your medicine.",
                "Emergency mode. Please verbally confirm your medication intake."
            ],
            'goodbye': [
                "Take care of yourself. I will see you at your next medicine time.",
                "Goodbye. Remember to stay healthy and take your medicine on time.",
                "Until next time, please maintain your health routine."
            ],
            'error': [
                "I am experiencing a technical difficulty. Please try again.",
                "There seems to be an error. Let me try to help you again.",
                "Something went wrong. Please be patient while I resolve this."
            ]
        }
        
        # Wake words for emergency override
        self.wake_words = ["hey baymax", "hello baymax", "baymax help", "baymax emergency"]
        
        # Calibrate microphone for ambient noise
        self._calibrate_microphone()
    
    def _setup_baymax_voice(self):
        """Configure TTS engine to sound more like Baymax."""
        try:
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a suitable voice (prefer male, slower speech)
            selected_voice = None
            for voice in voices:
                if voice.id:
                    # Prefer voices that might sound more robotic/gentle
                    if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                        selected_voice = voice.id
                        break
            
            if selected_voice:
                self.tts_engine.setProperty('voice', selected_voice)
            
            # Set speech rate (slower for Baymax-like speech)
            self.tts_engine.setProperty('rate', 150)  # Default is usually 200
            
            # Set volume
            self.tts_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"Error setting up Baymax voice: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone calibration complete.")
        except Exception as e:
            print(f"Error calibrating microphone: {e}")
    
    def speak(self, text: str, phrase_type: str = None, async_speech: bool = True):
        """
        Make Baymax speak the given text.
        
        Args:
            text: Text to speak (if phrase_type is None)
            phrase_type: Type of predefined phrase to speak
            async_speech: Whether to speak asynchronously
        """
        if phrase_type and phrase_type in self.baymax_phrases:
            import random
            text = random.choice(self.baymax_phrases[phrase_type])
        
        if async_speech:
            threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        """Synchronous speech method."""
        try:
            self.is_speaking = True
            print(f"BAYMAX: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
        finally:
            self.is_speaking = False
    
    def listen_for_wake_word(self, timeout: int = 30) -> bool:
        """
        Listen for wake words for emergency override.
        
        Args:
            timeout: How long to listen in seconds
            
        Returns:
            bool: True if wake word detected, False if timeout
        """
        print("Listening for wake word...")
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                
                # Check if any wake word is in the recognized text
                for wake_word in self.wake_words:
                    if wake_word in text:
                        print(f"Wake word detected: {wake_word}")
                        return True
                        
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                
        except sr.WaitTimeoutError:
            print("Listening timeout")
            
        return False
    
    def listen_for_confirmation(self, timeout: int = 10) -> Optional[str]:
        """
        Listen for medicine confirmation.
        
        Args:
            timeout: How long to listen in seconds
            
        Returns:
            str: Recognized text, None if no speech or error
        """
        try:
            with self.microphone as source:
                print("Listening for confirmation...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                return text
                
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return None
                
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
    
    def check_medicine_confirmation(self, text: str) -> bool:
        """
        Check if the recognized text confirms medicine intake.
        
        Args:
            text: Recognized speech text
            
        Returns:
            bool: True if medicine intake confirmed
        """
        confirmation_phrases = [
            "taken", "took", "medicine taken", "medication taken",
            "done", "finished", "yes", "confirmed", "complete",
            "took my medicine", "took my medication", "taken my medicine",
            "i took it", "i have taken", "medicine done"
        ]
        
        text = text.lower().strip()
        
        for phrase in confirmation_phrases:
            if phrase in text:
                return True
                
        return False
    
    def emergency_voice_authentication(self) -> bool:
        """
        Handle emergency voice authentication when face recognition fails.
        
        Returns:
            bool: True if authentication successful
        """
        self.speak("", "emergency_override", async_speech=False)
        
        # Give user time to respond
        time.sleep(2)
        
        # Listen for confirmation
        confirmation = self.listen_for_confirmation(timeout=15)
        
        if confirmation and self.check_medicine_confirmation(confirmation):
            self.speak("", "medicine_taken", async_speech=False)
            return True
        else:
            self.speak("Voice confirmation not received. Please try again.", async_speech=False)
            return False
    
    def medicine_reminder_sequence(self, user_name: str = None) -> bool:
        """
        Execute the complete medicine reminder sequence.
        
        Args:
            user_name: Name of the user (optional)
            
        Returns:
            bool: True if medicine confirmed taken
        """
        # Initial greeting and medicine reminder
        if user_name:
            greeting = f"Hello {user_name}. " + self.baymax_phrases['medicine_time'][0]
            self.speak(greeting, async_speech=False)
        else:
            self.speak("", "medicine_time", async_speech=False)
        
        # Wait for face recognition or voice confirmation
        # This will be handled by the main application logic
        return False
    
    def continuous_wake_word_detection(self, callback: Callable = None, stop_event: threading.Event = None):
        """
        Continuously listen for wake words in the background.
        
        Args:
            callback: Function to call when wake word detected
            stop_event: Threading event to stop listening
        """
        self.recognition_active = True
        
        while self.recognition_active and (not stop_event or not stop_event.is_set()):
            try:
                if self.listen_for_wake_word(timeout=5):
                    if callback:
                        callback()
                    break
            except Exception as e:
                print(f"Error in continuous wake word detection: {e}")
                time.sleep(1)
        
        self.recognition_active = False
    
    def stop_recognition(self):
        """Stop continuous recognition."""
        self.recognition_active = False
    
    def is_voice_available(self) -> bool:
        """Check if voice system is available and working."""
        try:
            # Test TTS
            test_text = "Testing voice system"
            self.tts_engine.say(test_text)
            self.tts_engine.runAndWait()
            
            # Test microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
            return True
        except Exception as e:
            print(f"Voice system not available: {e}")
            return False
    
    def get_voice_info(self) -> dict:
        """Get information about available voices."""
        try:
            voices = self.tts_engine.getProperty('voices')
            current_voice = self.tts_engine.getProperty('voice')
            
            voice_info = {
                'current_voice': current_voice,
                'available_voices': [{'id': v.id, 'name': v.name} for v in voices],
                'rate': self.tts_engine.getProperty('rate'),
                'volume': self.tts_engine.getProperty('volume')
            }
            
            return voice_info
        except Exception as e:
            print(f"Error getting voice info: {e}")
            return {}
    
    def set_voice_settings(self, rate: int = None, volume: float = None, voice_id: str = None):
        """
        Adjust voice settings.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice ID to use
        """
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
            
            if volume is not None:
                self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            
            if voice_id is not None:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if voice.id == voice_id:
                        self.tts_engine.setProperty('voice', voice_id)
                        break
                        
        except Exception as e:
            print(f"Error setting voice properties: {e}")