"""
BAYMAX Utility Functions
Helper functions for logging, validation, and system operations
"""

import logging
import os
import json
import csv
from datetime import datetime
import re
from typing import List, Dict, Any, Optional

def setup_logging(log_file: str = 'baymax.log', level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration for BAYMAX"""
    logger = logging.getLogger('BAYMAX')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def validate_time_format(time_str: str) -> bool:
    """Validate time format (HH:MM)"""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))

def validate_medicine_name(medicine_name: str) -> bool:
    """Validate medicine name (basic validation)"""
    return len(medicine_name.strip()) > 0 and len(medicine_name) <= 100

def validate_user_name(user_name: str) -> bool:
    """Validate user name (basic validation)"""
    return len(user_name.strip()) > 0 and len(user_name) <= 50

def save_data_to_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to JSON file with error handling"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving data to {file_path}: {e}")
        return False

def load_data_from_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file with error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

def log_missed_dose_to_csv(user_name: str, medicine_name: str, 
                          scheduled_time: str, file_path: str = 'missed_doses.csv') -> bool:
    """Log missed medicine dose to CSV file"""
    try:
        missed_data = {
            'user_name': user_name,
            'medicine_name': medicine_name,
            'scheduled_time': scheduled_time,
            'logged_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'missed'
        }
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(file_path)
        
        with open(file_path, 'a', newline='') as f:
            fieldnames = ['user_name', 'medicine_name', 'scheduled_time', 'logged_time', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(missed_data)
        
        return True
    except Exception as e:
        logging.error(f"Error logging missed dose to CSV: {e}")
        return False

def get_current_time_str() -> str:
    """Get current time in HH:MM format"""
    return datetime.now().strftime("%H:%M")

def get_current_datetime_str() -> str:
    """Get current date and time in full format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_medicine_due(scheduled_time: str, current_time: str = None) -> bool:
    """Check if medicine is due at current time"""
    if current_time is None:
        current_time = get_current_time_str()
    return scheduled_time == current_time

def format_time_for_display(time_str: str) -> str:
    """Format time for display (e.g., 14:30 -> 2:30 PM)"""
    try:
        hour, minute = map(int, time_str.split(':'))
        if hour == 0:
            return f"12:{minute:02d} AM"
        elif hour < 12:
            return f"{hour}:{minute:02d} AM"
        elif hour == 12:
            return f"12:{minute:02d} PM"
        else:
            return f"{hour-12}:{minute:02d} PM"
    except:
        return time_str

def create_backup_file(file_path: str) -> str:
    """Create a backup of a file"""
    if not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        return backup_path
    except Exception as e:
        logging.error(f"Error creating backup of {file_path}: {e}")
        return None

def cleanup_old_backups(directory: str = '.', max_backups: int = 5) -> None:
    """Clean up old backup files, keeping only the most recent ones"""
    try:
        backup_files = [f for f in os.listdir(directory) if f.endswith('.backup_')]
        backup_files.sort(reverse=True)  # Sort by name (timestamp)
        
        # Remove old backups
        for old_backup in backup_files[max_backups:]:
            os.remove(os.path.join(directory, old_backup))
            logging.info(f"Removed old backup: {old_backup}")
    except Exception as e:
        logging.error(f"Error cleaning up backups: {e}")

def get_system_info() -> Dict[str, str]:
    """Get system information for debugging"""
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture()[0],
        'processor': platform.processor()
    }

def check_dependencies() -> Dict[str, bool]:
    """Check if all required dependencies are available"""
    dependencies = {
        'opencv': False,
        'face_recognition': False,
        'pyttsx3': False,
        'tkinter': False,
        'numpy': False,
        'pandas': False,
        'schedule': False,
        'speech_recognition': False,
        'pygame': False
    }
    
    try:
        import cv2
        dependencies['opencv'] = True
    except ImportError:
        pass
    
    try:
        import face_recognition
        dependencies['face_recognition'] = True
    except ImportError:
        pass
    
    try:
        import pyttsx3
        dependencies['pyttsx3'] = True
    except ImportError:
        pass
    
    try:
        import tkinter
        dependencies['tkinter'] = True
    except ImportError:
        pass
    
    try:
        import numpy
        dependencies['numpy'] = True
    except ImportError:
        pass
    
    try:
        import pandas
        dependencies['pandas'] = True
    except ImportError:
        pass
    
    try:
        import schedule
        dependencies['schedule'] = True
    except ImportError:
        pass
    
    try:
        import speech_recognition
        dependencies['speech_recognition'] = True
    except ImportError:
        pass
    
    try:
        import pygame
        dependencies['pygame'] = True
    except ImportError:
        pass
    
    return dependencies

def print_system_status() -> None:
    """Print system status and dependency information"""
    print("=" * 50)
    print("BAYMAX System Status")
    print("=" * 50)
    
    # System info
    system_info = get_system_info()
    print(f"Platform: {system_info['platform']}")
    print(f"Python Version: {system_info['python_version']}")
    print(f"Architecture: {system_info['architecture']}")
    
    # Dependencies
    print("\nDependencies:")
    dependencies = check_dependencies()
    for dep, available in dependencies.items():
        status = "✓" if available else "✗"
        print(f"  {dep}: {status}")
    
    # Files
    print("\nData Files:")
    files = ['users.json', 'medicine_schedule.json', 'missed_doses.csv']
    for file in files:
        exists = "✓" if os.path.exists(file) else "✗"
        print(f"  {file}: {exists}")
    
    print("=" * 50)