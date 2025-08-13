import cv2
import face_recognition
import numpy as np
import pickle
import os
import json
from typing import List, Tuple, Optional, Dict

class FaceRecognizer:
    """
    Face recognition system for BAYMAX healthcare assistant.
    Handles face detection, encoding, and recognition for user authentication.
    """
    
    def __init__(self, data_dir: str = "/workspace/data"):
        self.data_dir = data_dir
        self.face_encodings_file = os.path.join(data_dir, "face_encodings.pkl")
        self.user_data_file = os.path.join(data_dir, "users.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing face encodings and user data
        self.known_face_encodings = []
        self.known_face_names = []
        self.user_data = {}
        
        self.load_face_data()
        
        # Camera settings
        self.camera = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def load_face_data(self):
        """Load saved face encodings and user data from files."""
        try:
            if os.path.exists(self.face_encodings_file):
                with open(self.face_encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
            
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r') as f:
                    self.user_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading face data: {e}")
            self.known_face_encodings = []
            self.known_face_names = []
            self.user_data = {}
    
    def save_face_data(self):
        """Save face encodings and user data to files."""
        try:
            # Save face encodings
            with open(self.face_encodings_file, 'wb') as f:
                pickle.dump({
                    'encodings': self.known_face_encodings,
                    'names': self.known_face_names
                }, f)
            
            # Save user data
            with open(self.user_data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving face data: {e}")
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Initialize the camera for face detection."""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def release_camera(self):
        """Release the camera resource."""
        if self.camera:
            self.camera.release()
            cv2.destroyAllWindows()
    
    def capture_face_for_registration(self, user_name: str, num_samples: int = 5) -> bool:
        """
        Capture multiple face samples for user registration.
        
        Args:
            user_name: Name of the user to register
            num_samples: Number of face samples to capture
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        if not self.camera:
            if not self.initialize_camera():
                return False
        
        print(f"Registering user: {user_name}")
        print(f"Please look at the camera. Capturing {num_samples} samples...")
        
        face_encodings = []
        samples_captured = 0
        
        while samples_captured < num_samples:
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Could not read from camera")
                continue
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if face_locations:
                # Get face encoding for the first face found
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                face_encodings.append(face_encoding)
                samples_captured += 1
                
                # Draw rectangle around face
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Sample {samples_captured}/{num_samples}", 
                           (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                print(f"Captured sample {samples_captured}/{num_samples}")
            else:
                cv2.putText(frame, "No face detected", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('Face Registration', frame)
            
            # Break if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        
        if len(face_encodings) >= num_samples:
            # Average the face encodings for better accuracy
            avg_encoding = np.mean(face_encodings, axis=0)
            
            # Add to known faces
            self.known_face_encodings.append(avg_encoding)
            self.known_face_names.append(user_name)
            
            # Save the data
            self.save_face_data()
            
            print(f"Successfully registered user: {user_name}")
            return True
        else:
            print(f"Failed to capture enough samples for {user_name}")
            return False
    
    def recognize_face(self, frame: np.ndarray = None, tolerance: float = 0.6) -> Optional[str]:
        """
        Recognize a face in the given frame or capture from camera.
        
        Args:
            frame: Image frame to analyze (optional)
            tolerance: Face recognition tolerance (lower = more strict)
            
        Returns:
            str: Name of recognized user, None if no match
        """
        if frame is None:
            if not self.camera:
                if not self.initialize_camera():
                    return None
            
            ret, frame = self.camera.read()
            if not ret:
                return None
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces and face encodings in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, tolerance=tolerance
            )
            
            if True in matches:
                # Find the best match
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    return self.known_face_names[best_match_index]
        
        return None
    
    def detect_face_in_frame(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a frame and return their locations.
        
        Args:
            frame: Image frame to analyze
            
        Returns:
            List of face locations as (top, right, bottom, left) tuples
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return face_recognition.face_locations(rgb_frame)
    
    def is_face_present(self) -> bool:
        """
        Check if any face is present in the current camera feed.
        
        Returns:
            bool: True if face detected, False otherwise
        """
        if not self.camera:
            if not self.initialize_camera():
                return False
        
        ret, frame = self.camera.read()
        if not ret:
            return False
        
        face_locations = self.detect_face_in_frame(frame)
        return len(face_locations) > 0
    
    def get_registered_users(self) -> List[str]:
        """Get list of all registered users."""
        return self.known_face_names.copy()
    
    def remove_user(self, user_name: str) -> bool:
        """
        Remove a user from the face recognition system.
        
        Args:
            user_name: Name of user to remove
            
        Returns:
            bool: True if user removed successfully
        """
        try:
            if user_name in self.known_face_names:
                index = self.known_face_names.index(user_name)
                self.known_face_names.pop(index)
                self.known_face_encodings.pop(index)
                
                # Remove from user data
                if user_name in self.user_data:
                    del self.user_data[user_name]
                
                self.save_face_data()
                print(f"User {user_name} removed successfully")
                return True
            else:
                print(f"User {user_name} not found")
                return False
        except Exception as e:
            print(f"Error removing user {user_name}: {e}")
            return False
    
    def continuous_recognition(self, callback_func=None, timeout: int = 30) -> Optional[str]:
        """
        Continuously monitor camera for face recognition.
        
        Args:
            callback_func: Function to call when face is recognized
            timeout: Timeout in seconds
            
        Returns:
            str: Name of recognized user, None if timeout or no recognition
        """
        if not self.camera:
            if not self.initialize_camera():
                return None
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            recognized_user = self.recognize_face(frame)
            
            if recognized_user:
                if callback_func:
                    callback_func(recognized_user)
                return recognized_user
            
            # Optional: Display the frame
            cv2.imshow('BAYMAX Face Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        return None