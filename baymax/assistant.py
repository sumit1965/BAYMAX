import os
import threading
import time
from datetime import datetime
from typing import Optional

from baymax.gui import BaymaxGUI
from baymax.voice import VoiceEngine
from baymax.face import FaceService
from baymax.storage import Storage


class Assistant:
    def __init__(self, gui: BaymaxGUI, voice: VoiceEngine, face: FaceService, storage: Storage) -> None:
        self.gui = gui
        self.voice = voice
        self.face = face
        self.storage = storage
        self._wake_listener_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pending_confirmation = threading.Event()

        self.gui.on_confirm(self._on_confirm_clicked)

    def _on_confirm_clicked(self) -> None:
        self._pending_confirmation.set()

    def register_user_flow(self) -> None:
        # Simple blocking prompts using Tkinter dialogs
        import tkinter.simpledialog as sd
        import tkinter.messagebox as mb

        name = sd.askstring("Register User", "Enter user's name:")
        if not name:
            return
        # Create user or fetch existing
        existing = self.storage.get_user_by_name(name)
        if existing:
            user_id = existing[0]
        else:
            user_id = self.storage.add_user(name)

        mb.showinfo("Capture Faces", "We will capture ~20 face images. Press 'q' to stop early.")
        self.face.capture_user_faces(user_id=user_id, num_samples=20)
        self.face.train_model()

        times_str = sd.askstring("Schedules", "Enter daily times (HH:MM) separated by commas:")
        if times_str:
            for t in [s.strip() for s in times_str.split(",") if s.strip()]:
                self.storage.add_schedule(user_id=user_id, time_str=t)
        # Scheduler will be reloaded on next app start; for simplicity we won't hot-reload here
        mb.showinfo("Done", f"Registered {name} with schedules: {times_str or 'none'}.")

    def handle_medicine_reminder(self, user_id: int, schedule_id: Optional[int] = None) -> None:
        user = self.storage.get_user(user_id)
        user_name = user[1] if user else "User"
        self.gui.set_status(f"Reminder for {user_name}")
        self.gui.set_expression_alert()

        # Attempt recognition
        recognized = self.face.recognize(timeout_seconds=10)
        if recognized is None or recognized[0] != user_id:
            # Not recognized; allow wake word or manual confirm
            pass

        # Speak and wait for confirmation with retries
        attempts = 0
        confirmed = False
        while attempts < 3 and not confirmed:
            if attempts == 0:
                self.gui.set_expression_talking()
                self.voice.speak_greeting()
            else:
                self.gui.set_expression_alert()
                self.voice.speak_retry()
            self.gui.set_status(f"Waiting for confirmation... (attempt {attempts + 1}/3)")

            self._pending_confirmation.clear()
            start_time = time.time()
            while time.time() - start_time < 20:
                if self._pending_confirmation.is_set():
                    confirmed = True
                    break
                time.sleep(0.2)
            attempts += 1

        if confirmed:
            self.gui.set_expression_talking()
            self.voice.speak_confirm()
            self.gui.set_status("Medicine confirmed")
        else:
            self.gui.set_expression_sad()
            self.voice.speak_missed()
            self.gui.set_status("Missed dose logged")
            self.storage.log_missed(user_id=user_id, schedule_id=schedule_id, reason="no confirmation")

        self.gui.set_expression_idle()
        self.gui.set_status("Idle")

    def wake_flow_manual(self) -> None:
        self.gui.set_status("Manual wake")
        self.gui.set_expression_talking()
        self.voice.speak("How can I assist you?")
        self.gui.set_expression_idle()
        self.gui.set_status("Idle")

    def start_wake_word_listener(self) -> None:
        if self._wake_listener_thread is not None:
            return
        self._stop_event.clear()
        self._wake_listener_thread = threading.Thread(target=self._wake_listener_loop, daemon=True)
        self._wake_listener_thread.start()

    def _wake_listener_loop(self) -> None:
        model_path = os.environ.get("VOSK_MODEL_PATH")
        try:
            import json
            import queue
            import sounddevice as sd
            from vosk import Model, KaldiRecognizer
        except Exception:
            return
        if not model_path:
            # Try default
            default_dir = os.path.join("models", "vosk-model-small-en-us-0.15")
            if os.path.isdir(default_dir):
                model_path = default_dir
            else:
                return
        try:
            model = Model(model_path)
            recognizer = KaldiRecognizer(model, 16000)
        except Exception:
            return

        q: "queue.Queue[bytes]" = queue.Queue()

        def callback(indata, frames, time_info, status):  # type: ignore[no-redef]
            q.put(bytes(indata))

        def matches_confirmation(text: str) -> bool:
            phrases = [
                "i took my medicine",
                "i have taken my medicine",
                "i took my pills",
                "i have taken my pills",
                "confirm medicine",
                "medicine taken",
            ]
            return any(p in text for p in phrases)

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
                while not self._stop_event.is_set():
                    try:
                        data = q.get(timeout=0.2)
                    except Exception:
                        continue
                    if recognizer.AcceptWaveform(data):
                        res = recognizer.Result()
                        try:
                            j = json.loads(res)
                            text = j.get("text", "").lower().strip()
                            if any(kw in text for kw in ["hello baymax", "hey baymax"]):
                                self.wake_flow_manual()
                            if matches_confirmation(text):
                                self._pending_confirmation.set()
                        except Exception:
                            pass
        except Exception:
            return

    def shutdown(self) -> None:
        self._stop_event.set()
        if self._wake_listener_thread and self._wake_listener_thread.is_alive():
            self._wake_listener_thread.join(timeout=1.0)