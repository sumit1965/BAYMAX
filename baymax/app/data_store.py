import csv
import json
import os
import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class DataStore:
    """Manages users, schedules, and logs on the filesystem."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "data")
        self.faces_dir = os.path.join(self.data_dir, "faces")
        self.models_dir = os.path.join(self.data_dir, "models")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.logs_file = os.path.join(self.data_dir, "logs.csv")
        os.makedirs(self.faces_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump({"users": []}, f, indent=2)
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "user_id", "user_name", "time", "medicine", "status"])  # status: confirmed/missed
        self._lock = threading.RLock()

    # Users
    def _load_users_doc(self) -> Dict:
        with self._lock:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_users_doc(self, doc: Dict) -> None:
        with self._lock:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2)

    def add_user(self, name: str, schedule: List[Dict[str, str]]) -> Dict:
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        user_record = {
            "id": user_id,
            "name": name,
            "schedule": schedule,  # list of {"time": "HH:MM", "label": "Medicine Name"}
            "created_at": created_at,
        }
        doc = self._load_users_doc()
        doc["users"].append(user_record)
        self._save_users_doc(doc)
        os.makedirs(self.get_user_faces_dir(user_id), exist_ok=True)
        return user_record

    def update_user_schedule(self, user_id: str, schedule: List[Dict[str, str]]) -> None:
        doc = self._load_users_doc()
        for u in doc["users"]:
            if u["id"] == user_id:
                u["schedule"] = schedule
                break
        self._save_users_doc(doc)

    def list_users(self) -> List[Dict]:
        doc = self._load_users_doc()
        return list(doc.get("users", []))

    def get_user(self, user_id: str) -> Optional[Dict]:
        for u in self.list_users():
            if u["id"] == user_id:
                return u
        return None

    def get_user_by_name(self, name: str) -> Optional[Dict]:
        for u in self.list_users():
            if u["name"].strip().lower() == name.strip().lower():
                return u
        return None

    def get_user_faces_dir(self, user_id: str) -> str:
        return os.path.join(self.faces_dir, user_id)

    # Logs
    def log_dose(self, user_id: str, time_str: str, medicine_label: str, status: str) -> None:
        user = self.get_user(user_id)
        user_name = user["name"] if user else "?"
        with self._lock:
            with open(self.logs_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    user_id,
                    user_name,
                    time_str,
                    medicine_label,
                    status,
                ])

    # Labels mapping for face model
    def labels_mapping_file(self) -> str:
        return os.path.join(self.models_dir, "labels.json")

    def face_model_file(self) -> str:
        return os.path.join(self.models_dir, "face_lbph.yml")