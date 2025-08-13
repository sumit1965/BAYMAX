from datetime import datetime, time as dtime
from typing import Callable, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tzlocal import get_localzone_name


class MedicineScheduler:
    def __init__(self):
        self._scheduler = BackgroundScheduler(timezone=get_localzone_name())
        self._scheduler.start()
        self._jobs_index: Dict[str, str] = {}

    def _job_id(self, user_id: str, time_str: str) -> str:
        return f"{user_id}-{time_str}"

    def schedule_user(self, user: Dict, callback: Callable[[Dict, Dict], None]) -> None:
        name = user["name"]
        user_id = user["id"]
        for sched in user.get("schedule", []):
            time_str = sched.get("time")
            label = sched.get("label", "Medicine")
            hh, mm = time_str.split(":")
            job_id = self._job_id(user_id, time_str)
            if job_id in self._jobs_index:
                try:
                    self._scheduler.remove_job(job_id)
                except Exception:
                    pass
            trigger = CronTrigger(hour=int(hh), minute=int(mm), timezone=self._scheduler.timezone)
            self._scheduler.add_job(lambda u=user, s=sched: callback(u, s), trigger=trigger, id=job_id, replace_existing=True)
            self._jobs_index[job_id] = name

    def unschedule_user(self, user_id: str) -> None:
        for key in list(self._jobs_index.keys()):
            if key.startswith(user_id + "-"):
                try:
                    self._scheduler.remove_job(key)
                except Exception:
                    pass
                self._jobs_index.pop(key, None)

    def shutdown(self) -> None:
        try:
            self._scheduler.shutdown(wait=False)
        except Exception:
            pass