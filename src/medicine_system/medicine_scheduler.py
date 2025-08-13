import schedule
import time
import threading
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Callable
import pandas as pd

class MedicineScheduler:
    """
    Medicine scheduling and reminder system for BAYMAX healthcare assistant.
    Handles medicine schedules, reminders, and intake logging.
    """
    
    def __init__(self, data_dir: str = "/workspace/data"):
        self.data_dir = data_dir
        self.schedules_file = os.path.join(data_dir, "medicine_schedules.json")
        self.log_file = os.path.join(data_dir, "medicine_log.csv")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Medicine schedules: {user_name: [schedule_items]}
        self.medicine_schedules = {}
        
        # Active reminders and their status
        self.active_reminders = {}
        
        # Callback functions for different events
        self.reminder_callback = None
        self.missed_callback = None
        
        # Scheduler settings
        self.reminder_interval = 20  # seconds between reminders
        self.max_reminders = 3  # maximum number of reminders
        
        # Threading
        self.scheduler_thread = None
        self.scheduler_active = False
        self.stop_event = threading.Event()
        
        # Load existing schedules
        self.load_schedules()
        
        # Initialize medicine log
        self.init_medicine_log()
    
    def load_schedules(self):
        """Load medicine schedules from file."""
        try:
            if os.path.exists(self.schedules_file):
                with open(self.schedules_file, 'r') as f:
                    self.medicine_schedules = json.load(f)
                print(f"Loaded schedules for {len(self.medicine_schedules)} users")
            else:
                self.medicine_schedules = {}
                print("No existing schedules found")
        except Exception as e:
            print(f"Error loading schedules: {e}")
            self.medicine_schedules = {}
    
    def save_schedules(self):
        """Save medicine schedules to file."""
        try:
            with open(self.schedules_file, 'w') as f:
                json.dump(self.medicine_schedules, f, indent=2, default=str)
            print("Schedules saved successfully")
        except Exception as e:
            print(f"Error saving schedules: {e}")
    
    def init_medicine_log(self):
        """Initialize medicine log CSV file."""
        try:
            if not os.path.exists(self.log_file):
                # Create CSV with headers
                with open(self.log_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'user_name', 'medicine_name', 
                        'scheduled_time', 'actual_time', 'status', 'method'
                    ])
                print("Medicine log initialized")
        except Exception as e:
            print(f"Error initializing medicine log: {e}")
    
    def add_user_schedule(self, user_name: str, medicine_name: str, times: List[str], 
                         days: List[str] = None, notes: str = ""):
        """
        Add medicine schedule for a user.
        
        Args:
            user_name: Name of the user
            medicine_name: Name of the medicine
            times: List of times in HH:MM format (e.g., ["08:00", "20:00"])
            days: List of days (e.g., ["monday", "tuesday"]) or None for daily
            notes: Additional notes about the medicine
        """
        if user_name not in self.medicine_schedules:
            self.medicine_schedules[user_name] = []
        
        schedule_item = {
            'medicine_name': medicine_name,
            'times': times,
            'days': days if days else ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
            'notes': notes,
            'active': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.medicine_schedules[user_name].append(schedule_item)
        self.save_schedules()
        
        print(f"Added schedule for {user_name}: {medicine_name} at {times}")
        
        # Reschedule jobs
        self.setup_scheduled_jobs()
    
    def remove_user_schedule(self, user_name: str, medicine_name: str = None):
        """
        Remove medicine schedule for a user.
        
        Args:
            user_name: Name of the user
            medicine_name: Name of specific medicine to remove (None to remove all)
        """
        if user_name not in self.medicine_schedules:
            print(f"No schedules found for user: {user_name}")
            return False
        
        if medicine_name:
            # Remove specific medicine
            original_count = len(self.medicine_schedules[user_name])
            self.medicine_schedules[user_name] = [
                item for item in self.medicine_schedules[user_name] 
                if item['medicine_name'] != medicine_name
            ]
            removed = original_count - len(self.medicine_schedules[user_name])
            
            if removed > 0:
                print(f"Removed {removed} schedule(s) for {medicine_name}")
                self.save_schedules()
                self.setup_scheduled_jobs()
                return True
        else:
            # Remove all schedules for user
            del self.medicine_schedules[user_name]
            print(f"Removed all schedules for user: {user_name}")
            self.save_schedules()
            self.setup_scheduled_jobs()
            return True
        
        return False
    
    def get_user_schedules(self, user_name: str) -> List[Dict]:
        """Get all medicine schedules for a user."""
        return self.medicine_schedules.get(user_name, [])
    
    def get_all_users(self) -> List[str]:
        """Get list of all users with schedules."""
        return list(self.medicine_schedules.keys())
    
    def setup_scheduled_jobs(self):
        """Setup scheduled jobs for all medicine reminders."""
        # Clear existing schedule
        schedule.clear()
        
        for user_name, schedules in self.medicine_schedules.items():
            for schedule_item in schedules:
                if not schedule_item.get('active', True):
                    continue
                
                medicine_name = schedule_item['medicine_name']
                times = schedule_item['times']
                days = schedule_item['days']
                
                for time_str in times:
                    for day in days:
                        # Create job for each day and time
                        job = getattr(schedule.every(), day.lower()).at(time_str)
                        job.do(self._trigger_medicine_reminder, user_name, medicine_name, time_str)
        
        print(f"Setup {len(schedule.jobs)} scheduled medicine reminders")
    
    def _trigger_medicine_reminder(self, user_name: str, medicine_name: str, scheduled_time: str):
        """Trigger medicine reminder for a user."""
        reminder_id = f"{user_name}_{medicine_name}_{scheduled_time}_{datetime.now().strftime('%Y%m%d')}"
        
        # Check if reminder already active for today
        if reminder_id in self.active_reminders:
            print(f"Reminder already active for {user_name} - {medicine_name}")
            return
        
        print(f"Triggering medicine reminder: {user_name} - {medicine_name} at {scheduled_time}")
        
        # Create active reminder
        self.active_reminders[reminder_id] = {
            'user_name': user_name,
            'medicine_name': medicine_name,
            'scheduled_time': scheduled_time,
            'reminder_count': 0,
            'status': 'pending',
            'created_at': datetime.now(),
            'last_reminder': None
        }
        
        # Trigger callback if set
        if self.reminder_callback:
            try:
                self.reminder_callback(user_name, medicine_name, scheduled_time, reminder_id)
            except Exception as e:
                print(f"Error in reminder callback: {e}")
    
    def confirm_medicine_taken(self, user_name: str, medicine_name: str, 
                              method: str = "face", actual_time: str = None) -> bool:
        """
        Confirm that medicine has been taken.
        
        Args:
            user_name: Name of the user
            medicine_name: Name of the medicine
            method: Method of confirmation ("face", "voice", "manual")
            actual_time: Time when medicine was actually taken
            
        Returns:
            bool: True if confirmation successful
        """
        current_time = datetime.now()
        actual_time = actual_time or current_time.strftime('%H:%M')
        
        # Find active reminder
        reminder_id = None
        for rid, reminder in self.active_reminders.items():
            if (reminder['user_name'] == user_name and 
                reminder['medicine_name'] == medicine_name and
                reminder['status'] == 'pending'):
                reminder_id = rid
                break
        
        if reminder_id:
            # Update reminder status
            self.active_reminders[reminder_id]['status'] = 'taken'
            self.active_reminders[reminder_id]['actual_time'] = actual_time
            self.active_reminders[reminder_id]['method'] = method
            scheduled_time = self.active_reminders[reminder_id]['scheduled_time']
        else:
            # No active reminder found, but still log it
            scheduled_time = "unknown"
        
        # Log medicine intake
        self.log_medicine_intake(
            user_name=user_name,
            medicine_name=medicine_name,
            scheduled_time=scheduled_time,
            actual_time=actual_time,
            status='taken',
            method=method
        )
        
        print(f"Medicine confirmed taken: {user_name} - {medicine_name} via {method}")
        return True
    
    def mark_medicine_missed(self, user_name: str, medicine_name: str, scheduled_time: str):
        """Mark medicine as missed after maximum reminders."""
        # Find and update active reminder
        reminder_id = None
        for rid, reminder in self.active_reminders.items():
            if (reminder['user_name'] == user_name and 
                reminder['medicine_name'] == medicine_name and
                reminder['scheduled_time'] == scheduled_time and
                reminder['status'] == 'pending'):
                reminder_id = rid
                break
        
        if reminder_id:
            self.active_reminders[reminder_id]['status'] = 'missed'
        
        # Log missed medicine
        self.log_medicine_intake(
            user_name=user_name,
            medicine_name=medicine_name,
            scheduled_time=scheduled_time,
            actual_time=None,
            status='missed',
            method='system'
        )
        
        print(f"Medicine marked as missed: {user_name} - {medicine_name} at {scheduled_time}")
        
        # Trigger missed callback if set
        if self.missed_callback:
            try:
                self.missed_callback(user_name, medicine_name, scheduled_time)
            except Exception as e:
                print(f"Error in missed callback: {e}")
    
    def log_medicine_intake(self, user_name: str, medicine_name: str, 
                           scheduled_time: str, actual_time: str, 
                           status: str, method: str):
        """Log medicine intake to CSV file."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, user_name, medicine_name, 
                    scheduled_time, actual_time, status, method
                ])
        except Exception as e:
            print(f"Error logging medicine intake: {e}")
    
    def get_medicine_log(self, user_name: str = None, days: int = 7) -> pd.DataFrame:
        """
        Get medicine log as pandas DataFrame.
        
        Args:
            user_name: Filter by specific user (None for all users)
            days: Number of days to look back
            
        Returns:
            pandas.DataFrame: Medicine log data
        """
        try:
            if not os.path.exists(self.log_file):
                return pd.DataFrame()
            
            df = pd.read_csv(self.log_file)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['timestamp'] >= cutoff_date]
            
            # Filter by user if specified
            if user_name:
                df = df[df['user_name'] == user_name]
            
            return df.sort_values('timestamp', ascending=False)
            
        except Exception as e:
            print(f"Error reading medicine log: {e}")
            return pd.DataFrame()
    
    def get_missed_medicines(self, user_name: str = None, days: int = 7) -> List[Dict]:
        """Get list of missed medicines."""
        df = self.get_medicine_log(user_name, days)
        
        if df.empty:
            return []
        
        missed_df = df[df['status'] == 'missed']
        return missed_df.to_dict('records')
    
    def get_adherence_rate(self, user_name: str, days: int = 7) -> float:
        """
        Calculate medicine adherence rate for a user.
        
        Args:
            user_name: Name of the user
            days: Number of days to calculate for
            
        Returns:
            float: Adherence rate as percentage (0-100)
        """
        df = self.get_medicine_log(user_name, days)
        
        if df.empty:
            return 0.0
        
        total_medicines = len(df)
        taken_medicines = len(df[df['status'] == 'taken'])
        
        return (taken_medicines / total_medicines) * 100 if total_medicines > 0 else 0.0
    
    def get_next_medicine_time(self, user_name: str) -> Optional[Tuple[str, str]]:
        """
        Get the next scheduled medicine time for a user.
        
        Args:
            user_name: Name of the user
            
        Returns:
            Tuple: (medicine_name, time_string) or None
        """
        if user_name not in self.medicine_schedules:
            return None
        
        current_time = datetime.now()
        current_day = current_time.strftime('%A').lower()
        current_time_str = current_time.strftime('%H:%M')
        
        next_medicines = []
        
        for schedule_item in self.medicine_schedules[user_name]:
            if not schedule_item.get('active', True):
                continue
            
            medicine_name = schedule_item['medicine_name']
            times = schedule_item['times']
            days = schedule_item['days']
            
            # Check today's remaining times
            if current_day in days:
                for time_str in times:
                    if time_str > current_time_str:
                        time_obj = datetime.strptime(time_str, '%H:%M').time()
                        next_datetime = datetime.combine(current_time.date(), time_obj)
                        next_medicines.append((medicine_name, time_str, next_datetime))
            
            # Check tomorrow's times if no more today
            tomorrow = (current_time + timedelta(days=1))
            tomorrow_day = tomorrow.strftime('%A').lower()
            
            if tomorrow_day in days:
                for time_str in times:
                    time_obj = datetime.strptime(time_str, '%H:%M').time()
                    next_datetime = datetime.combine(tomorrow.date(), time_obj)
                    next_medicines.append((medicine_name, time_str, next_datetime))
        
        if next_medicines:
            # Sort by datetime and return the earliest
            next_medicines.sort(key=lambda x: x[2])
            return next_medicines[0][0], next_medicines[0][1]
        
        return None
    
    def set_reminder_callback(self, callback: Callable):
        """Set callback function for medicine reminders."""
        self.reminder_callback = callback
    
    def set_missed_callback(self, callback: Callable):
        """Set callback function for missed medicines."""
        self.missed_callback = callback
    
    def start_scheduler(self):
        """Start the medicine scheduler in a background thread."""
        if self.scheduler_active:
            print("Scheduler already running")
            return
        
        self.scheduler_active = True
        self.stop_event.clear()
        
        def run_scheduler():
            print("Medicine scheduler started")
            while self.scheduler_active and not self.stop_event.is_set():
                try:
                    schedule.run_pending()
                    self._check_reminder_timeouts()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error in scheduler: {e}")
                    time.sleep(5)
            print("Medicine scheduler stopped")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Setup scheduled jobs
        self.setup_scheduled_jobs()
    
    def stop_scheduler(self):
        """Stop the medicine scheduler."""
        self.scheduler_active = False
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
    
    def _check_reminder_timeouts(self):
        """Check for reminders that need follow-up or timeout."""
        current_time = datetime.now()
        
        for reminder_id, reminder in list(self.active_reminders.items()):
            if reminder['status'] != 'pending':
                continue
            
            time_since_created = (current_time - reminder['created_at']).total_seconds()
            
            # Check if it's time for another reminder
            if (reminder['last_reminder'] is None or 
                (current_time - reminder['last_reminder']).total_seconds() >= self.reminder_interval):
                
                if reminder['reminder_count'] < self.max_reminders:
                    # Send another reminder
                    reminder['reminder_count'] += 1
                    reminder['last_reminder'] = current_time
                    
                    print(f"Sending reminder #{reminder['reminder_count']} for {reminder['user_name']} - {reminder['medicine_name']}")
                    
                    # Trigger callback for reminder
                    if self.reminder_callback:
                        try:
                            self.reminder_callback(
                                reminder['user_name'], 
                                reminder['medicine_name'], 
                                reminder['scheduled_time'], 
                                reminder_id,
                                reminder['reminder_count']
                            )
                        except Exception as e:
                            print(f"Error in reminder callback: {e}")
                
                else:
                    # Maximum reminders reached, mark as missed
                    self.mark_medicine_missed(
                        reminder['user_name'], 
                        reminder['medicine_name'], 
                        reminder['scheduled_time']
                    )
    
    def get_active_reminders(self) -> Dict:
        """Get all active reminders."""
        return {k: v for k, v in self.active_reminders.items() if v['status'] == 'pending'}
    
    def load_schedules_from_csv(self, csv_file: str) -> bool:
        """
        Load medicine schedules from CSV file.
        
        CSV format: user_name, medicine_name, times (semicolon separated), days (semicolon separated), notes
        Example: John Doe, Aspirin, 08:00;20:00, monday;tuesday;wednesday, Take with food
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    user_name = row['user_name'].strip()
                    medicine_name = row['medicine_name'].strip()
                    times = [t.strip() for t in row['times'].split(';')]
                    days = [d.strip() for d in row['days'].split(';')] if row['days'].strip() else None
                    notes = row.get('notes', '').strip()
                    
                    self.add_user_schedule(user_name, medicine_name, times, days, notes)
            
            print(f"Successfully loaded schedules from {csv_file}")
            return True
            
        except Exception as e:
            print(f"Error loading schedules from CSV: {e}")
            return False