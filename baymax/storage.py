import os
import csv
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Tuple, Dict


class Storage:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def init(self) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    time_str TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS face_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS missed_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    schedule_id INTEGER,
                    timestamp TEXT NOT NULL,
                    reason TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY(schedule_id) REFERENCES schedules(id) ON DELETE SET NULL
                )
                """
            )
            conn.commit()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    # Users
    def add_user(self, name: str) -> int:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users(name) VALUES(?)", (name,))
            conn.commit()
            return cur.lastrowid

    def get_user_by_name(self, name: str) -> Optional[Tuple[int, str]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users WHERE name=?", (name,))
            return cur.fetchone()

    def get_user(self, user_id: int) -> Optional[Tuple[int, str]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users WHERE id=?", (user_id,))
            return cur.fetchone()

    def list_users(self) -> List[Tuple[int, str]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users ORDER BY name")
            return cur.fetchall()

    # Schedules
    def add_schedule(self, user_id: int, time_str: str) -> int:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO schedules(user_id, time_str) VALUES(?, ?)",
                (user_id, time_str),
            )
            conn.commit()
            return cur.lastrowid

    def list_schedules(self) -> List[Tuple[int, int, str]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, user_id, time_str FROM schedules")
            return cur.fetchall()

    def list_user_schedules(self, user_id: int) -> List[Tuple[int, int, str]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, user_id, time_str FROM schedules WHERE user_id=?",
                (user_id,),
            )
            return cur.fetchall()

    # Face samples
    def add_face_sample(self, user_id: int, file_path: str) -> int:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO face_samples(user_id, file_path) VALUES(?, ?)",
                (user_id, file_path),
            )
            conn.commit()
            return cur.lastrowid

    def get_all_face_samples(self) -> List[Tuple[int, int, str]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, user_id, file_path FROM face_samples")
            return cur.fetchall()

    # Missed logs
    def log_missed(self, user_id: int, schedule_id: Optional[int], reason: str) -> None:
        timestamp = datetime.now().isoformat()
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO missed_logs(user_id, schedule_id, timestamp, reason) VALUES(?, ?, ?, ?)",
                (user_id, schedule_id, timestamp, reason),
            )
            conn.commit()
        # Also append to CSV for ease of inspection
        os.makedirs("data", exist_ok=True)
        csv_path = os.path.join("data", "missed.csv")
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "user_id", "schedule_id", "reason"]) 
            writer.writerow([timestamp, user_id, schedule_id if schedule_id else "", reason])