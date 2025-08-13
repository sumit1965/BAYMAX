import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd

class UserManager:
    """
    User management system for BAYMAX healthcare assistant.
    Handles user registration, profiles, and medicine schedules integration.
    """
    
    def __init__(self, data_dir: str = "/workspace/data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "baymax_users.db")
        self.users_file = os.path.join(data_dir, "users.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load users from JSON (for compatibility)
        self.users_data = self._load_users_json()
    
    def _init_database(self):
        """Initialize SQLite database for user management."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    age INTEGER,
                    email TEXT,
                    phone TEXT,
                    emergency_contact TEXT,
                    medical_conditions TEXT,
                    allergies TEXT,
                    face_registered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Medicine schedules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicine_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    medicine_name TEXT NOT NULL,
                    dosage TEXT,
                    times TEXT NOT NULL,  -- JSON array of times
                    days TEXT NOT NULL,   -- JSON array of days
                    notes TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User sessions table (for tracking interactions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_type TEXT NOT NULL,  -- 'medicine_reminder', 'registration', etc.
                    status TEXT NOT NULL,        -- 'started', 'completed', 'failed'
                    details TEXT,                -- JSON details
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def _load_users_json(self) -> Dict:
        """Load users from JSON file for compatibility."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading users JSON: {e}")
            return {}
    
    def _save_users_json(self):
        """Save users to JSON file for compatibility."""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving users JSON: {e}")
    
    def register_user(self, user_name: str, full_name: str = None, 
                     age: int = None, email: str = None, phone: str = None,
                     emergency_contact: str = None, medical_conditions: str = None,
                     allergies: str = None) -> bool:
        """
        Register a new user in the system.
        
        Args:
            user_name: Unique username
            full_name: Full name of the user
            age: Age of the user
            email: Email address
            phone: Phone number
            emergency_contact: Emergency contact information
            medical_conditions: Medical conditions
            allergies: Known allergies
            
        Returns:
            bool: True if registration successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE user_name = ?", (user_name,))
            if cursor.fetchone():
                print(f"User {user_name} already exists")
                conn.close()
                return False
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (user_name, full_name, age, email, phone, 
                                 emergency_contact, medical_conditions, allergies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_name, full_name, age, email, phone, 
                  emergency_contact, medical_conditions, allergies))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Update JSON for compatibility
            self.users_data[user_name] = {
                'user_id': user_id,
                'full_name': full_name,
                'age': age,
                'email': email,
                'phone': phone,
                'emergency_contact': emergency_contact,
                'medical_conditions': medical_conditions,
                'allergies': allergies,
                'face_registered': False,
                'created_at': datetime.now().isoformat()
            }
            self._save_users_json()
            
            print(f"User {user_name} registered successfully with ID {user_id}")
            return True
            
        except Exception as e:
            print(f"Error registering user {user_name}: {e}")
            return False
    
    def get_user(self, user_name: str) -> Optional[Dict]:
        """
        Get user information by username.
        
        Args:
            user_name: Username to lookup
            
        Returns:
            Dict: User information or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_name, full_name, age, email, phone, 
                       emergency_contact, medical_conditions, allergies, 
                       face_registered, created_at, updated_at
                FROM users WHERE user_name = ?
            ''', (user_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[0],
                    'user_name': row[1],
                    'full_name': row[2],
                    'age': row[3],
                    'email': row[4],
                    'phone': row[5],
                    'emergency_contact': row[6],
                    'medical_conditions': row[7],
                    'allergies': row[8],
                    'face_registered': bool(row[9]),
                    'created_at': row[10],
                    'updated_at': row[11]
                }
            return None
            
        except Exception as e:
            print(f"Error getting user {user_name}: {e}")
            return None
    
    def update_user(self, user_name: str, **kwargs) -> bool:
        """
        Update user information.
        
        Args:
            user_name: Username to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if update successful
        """
        try:
            user = self.get_user(user_name)
            if not user:
                print(f"User {user_name} not found")
                return False
            
            # Build update query
            valid_fields = ['full_name', 'age', 'email', 'phone', 'emergency_contact',
                          'medical_conditions', 'allergies', 'face_registered']
            
            update_fields = []
            update_values = []
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                print("No valid fields to update")
                return False
            
            update_values.append(datetime.now().isoformat())
            update_values.append(user_name)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f'''
                UPDATE users 
                SET {', '.join(update_fields)}, updated_at = ?
                WHERE user_name = ?
            '''
            
            cursor.execute(query, update_values)
            conn.commit()
            conn.close()
            
            # Update JSON
            if user_name in self.users_data:
                self.users_data[user_name].update(kwargs)
                self.users_data[user_name]['updated_at'] = datetime.now().isoformat()
                self._save_users_json()
            
            print(f"User {user_name} updated successfully")
            return True
            
        except Exception as e:
            print(f"Error updating user {user_name}: {e}")
            return False
    
    def mark_face_registered(self, user_name: str) -> bool:
        """Mark user as having face registered."""
        return self.update_user(user_name, face_registered=True)
    
    def get_all_users(self) -> List[Dict]:
        """Get all registered users."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_name, full_name, age, email, phone, 
                       emergency_contact, medical_conditions, allergies, 
                       face_registered, created_at, updated_at
                FROM users ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append({
                    'user_id': row[0],
                    'user_name': row[1],
                    'full_name': row[2],
                    'age': row[3],
                    'email': row[4],
                    'phone': row[5],
                    'emergency_contact': row[6],
                    'medical_conditions': row[7],
                    'allergies': row[8],
                    'face_registered': bool(row[9]),
                    'created_at': row[10],
                    'updated_at': row[11]
                })
            
            return users
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def delete_user(self, user_name: str) -> bool:
        """
        Delete a user from the system.
        
        Args:
            user_name: Username to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            user = self.get_user(user_name)
            if not user:
                print(f"User {user_name} not found")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_id = user['user_id']
            
            # Delete user sessions
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            
            # Delete medicine schedules
            cursor.execute("DELETE FROM medicine_schedules WHERE user_id = ?", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from JSON
            if user_name in self.users_data:
                del self.users_data[user_name]
                self._save_users_json()
            
            print(f"User {user_name} deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting user {user_name}: {e}")
            return False
    
    def add_medicine_schedule(self, user_name: str, medicine_name: str, 
                            dosage: str, times: List[str], days: List[str],
                            notes: str = "") -> bool:
        """
        Add medicine schedule for a user.
        
        Args:
            user_name: Username
            medicine_name: Name of the medicine
            dosage: Dosage information
            times: List of times (HH:MM format)
            days: List of days
            notes: Additional notes
            
        Returns:
            bool: True if successful
        """
        try:
            user = self.get_user(user_name)
            if not user:
                print(f"User {user_name} not found")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO medicine_schedules (user_id, medicine_name, dosage, 
                                              times, days, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user['user_id'], medicine_name, dosage, 
                  json.dumps(times), json.dumps(days), notes))
            
            conn.commit()
            conn.close()
            
            print(f"Medicine schedule added for {user_name}: {medicine_name}")
            return True
            
        except Exception as e:
            print(f"Error adding medicine schedule: {e}")
            return False
    
    def get_user_medicine_schedules(self, user_name: str) -> List[Dict]:
        """Get all medicine schedules for a user."""
        try:
            user = self.get_user(user_name)
            if not user:
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, medicine_name, dosage, times, days, notes, active, created_at
                FROM medicine_schedules 
                WHERE user_id = ? AND active = TRUE
                ORDER BY created_at DESC
            ''', (user['user_id'],))
            
            rows = cursor.fetchall()
            conn.close()
            
            schedules = []
            for row in rows:
                schedules.append({
                    'schedule_id': row[0],
                    'medicine_name': row[1],
                    'dosage': row[2],
                    'times': json.loads(row[3]),
                    'days': json.loads(row[4]),
                    'notes': row[5],
                    'active': bool(row[6]),
                    'created_at': row[7]
                })
            
            return schedules
            
        except Exception as e:
            print(f"Error getting medicine schedules for {user_name}: {e}")
            return []
    
    def log_user_session(self, user_name: str, session_type: str, 
                        status: str, details: Dict = None):
        """
        Log user session/interaction.
        
        Args:
            user_name: Username
            session_type: Type of session
            status: Session status
            details: Additional details
        """
        try:
            user = self.get_user(user_name)
            if not user:
                print(f"User {user_name} not found for session logging")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_type, status, details)
                VALUES (?, ?, ?, ?)
            ''', (user['user_id'], session_type, status, 
                  json.dumps(details) if details else None))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging user session: {e}")
    
    def get_user_sessions(self, user_name: str, days: int = 7) -> List[Dict]:
        """Get user sessions from the last N days."""
        try:
            user = self.get_user(user_name)
            if not user:
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_type, status, details, timestamp
                FROM user_sessions 
                WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days), (user['user_id'],))
            
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                sessions.append({
                    'session_type': row[0],
                    'status': row[1],
                    'details': json.loads(row[2]) if row[2] else None,
                    'timestamp': row[3]
                })
            
            return sessions
            
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    def get_users_with_face_registration(self) -> List[str]:
        """Get list of users who have face registration."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_name FROM users WHERE face_registered = TRUE")
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            print(f"Error getting users with face registration: {e}")
            return []
    
    def export_user_data(self, output_file: str = None) -> str:
        """
        Export all user data to CSV.
        
        Args:
            output_file: Output file path
            
        Returns:
            str: Path to exported file
        """
        try:
            if output_file is None:
                output_file = os.path.join(self.data_dir, f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            users = self.get_all_users()
            
            if users:
                df = pd.DataFrame(users)
                df.to_csv(output_file, index=False)
                print(f"User data exported to {output_file}")
                return output_file
            else:
                print("No users to export")
                return ""
                
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return ""
    
    def import_users_from_csv(self, csv_file: str) -> bool:
        """
        Import users from CSV file.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            bool: True if import successful
        """
        try:
            df = pd.read_csv(csv_file)
            
            required_columns = ['user_name']
            if not all(col in df.columns for col in required_columns):
                print(f"CSV must contain at least: {required_columns}")
                return False
            
            success_count = 0
            for _, row in df.iterrows():
                user_data = {
                    'user_name': row['user_name'],
                    'full_name': row.get('full_name'),
                    'age': row.get('age'),
                    'email': row.get('email'),
                    'phone': row.get('phone'),
                    'emergency_contact': row.get('emergency_contact'),
                    'medical_conditions': row.get('medical_conditions'),
                    'allergies': row.get('allergies')
                }
                
                # Remove None values
                user_data = {k: v for k, v in user_data.items() if pd.notna(v)}
                
                if self.register_user(**user_data):
                    success_count += 1
            
            print(f"Successfully imported {success_count} users from {csv_file}")
            return success_count > 0
            
        except Exception as e:
            print(f"Error importing users from CSV: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Count users with face registration
            cursor.execute("SELECT COUNT(*) FROM users WHERE face_registered = TRUE")
            face_registered_users = cursor.fetchone()[0]
            
            # Count medicine schedules
            cursor.execute("SELECT COUNT(*) FROM medicine_schedules WHERE active = TRUE")
            active_schedules = cursor.fetchone()[0]
            
            # Count sessions
            cursor.execute("SELECT COUNT(*) FROM user_sessions")
            total_sessions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_users': total_users,
                'face_registered_users': face_registered_users,
                'active_medicine_schedules': active_schedules,
                'total_sessions': total_sessions,
                'database_path': self.db_path
            }
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}