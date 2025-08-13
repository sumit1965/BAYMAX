import os
import threading
from datetime import datetime

from baymax.gui import BaymaxGUI
from baymax.voice import VoiceEngine
from baymax.face import FaceService
from baymax.storage import Storage
from baymax.scheduler import ReminderScheduler
from baymax.assistant import Assistant


def ensure_directories() -> None:
    os.makedirs("data/faces", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)


def main() -> int:
    ensure_directories()

    storage = Storage(db_path="data/db.sqlite3")
    storage.init()

    voice = VoiceEngine()
    face = FaceService(storage=storage)

    gui = BaymaxGUI()

    assistant = Assistant(gui=gui, voice=voice, face=face, storage=storage)

    scheduler = ReminderScheduler(storage=storage, assistant=assistant)
    scheduler.start()

    # Wire GUI buttons
    gui.on_register(lambda: assistant.register_user_flow())
    gui.on_wake(lambda: assistant.wake_flow_manual())

    # Start optional wake word listener in a thread
    assistant.start_wake_word_listener()

    gui.run()
    scheduler.shutdown()
    assistant.shutdown()
    return 0