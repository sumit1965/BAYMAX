from datetime import datetime, time
from typing import List, Tuple

from apscheduler.schedulers.background import BackgroundScheduler

from baymax.storage import Storage
from baymax.assistant import Assistant


class ReminderScheduler:
    def __init__(self, storage: Storage, assistant: Assistant):
        self.storage = storage
        self.assistant = assistant
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        self.scheduler.start()
        self.reload_jobs()

    def reload_jobs(self) -> None:
        self.scheduler.remove_all_jobs()
        for sched_id, user_id, time_str in self.storage.list_schedules():
            try:
                hour, minute = map(int, time_str.split(":"))
            except Exception:
                continue
            self.scheduler.add_job(
                self.assistant.handle_medicine_reminder,
                trigger="cron",
                args=[user_id, sched_id],
                id=f"user_{user_id}_sched_{sched_id}",
                hour=hour,
                minute=minute,
                replace_existing=True,
            )

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)