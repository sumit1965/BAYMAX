import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from .data_store import DataStore
from .face_recog import FaceDatasetManager, FaceRecognizer
from .gui import BaymaxGUI
from .scheduler import MedicineScheduler
from .voice import BaymaxTTS, VoskRecognizer


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class ConfirmationState:
    def __init__(self):
        self._event = threading.Event()

    def confirm(self):
        self._event.set()

    def wait(self, timeout: float) -> bool:
        return self._event.wait(timeout)

    def reset(self):
        self._event.clear()


class BaymaxApp:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.data_store = DataStore(base_dir)
        self.face_dataset = FaceDatasetManager(self.data_store.faces_dir)
        self.face_recognizer = FaceRecognizer(
            model_file=self.data_store.face_model_file(),
            labels_file=self.data_store.labels_mapping_file(),
            dataset_dir=self.data_store.faces_dir,
        )
        self.tts = BaymaxTTS()
        self.asr = VoskRecognizer(models_base_dir=os.path.join(self.base_dir, "models"))
        self.scheduler = MedicineScheduler()

        self.confirmation_state = ConfirmationState()

        self.gui = BaymaxGUI(
            on_register=self._on_register_user,
            on_capture_faces=self._on_capture_faces,
            on_confirm_taken=self._on_confirm_taken,
        )
        self.gui.set_users(self.data_store.list_users())

        # Start background wake phrase listener
        self._wake_thread = threading.Thread(target=self._wake_phrase_loop, daemon=True)
        self._wake_thread.start()

        # Schedule existing users
        for u in self.data_store.list_users():
            self.scheduler.schedule_user(u, self._on_medicine_time)

    # GUI Callbacks
    def _on_register_user(self, name: str, schedule: List[Dict[str, str]]) -> Dict:
        user = self.data_store.add_user(name, schedule)
        # update UI list
        self.gui.set_users(self.data_store.list_users())
        # schedule
        self.scheduler.schedule_user(user, self._on_medicine_time)
        return user

    def _on_capture_faces(self, user_id_short: str) -> None:
        # map short id to full
        target = None
        for u in self.data_store.list_users():
            if u["id"].startswith(user_id_short):
                target = u
                break
        if target is None:
            self.gui.set_message("Could not resolve selected user.")
            return
        self.gui.set_message(f"Capturing faces for {target['name']} - a camera window will open. Press 'q' to stop early.")
        try:
            count = self.face_dataset.collect_samples_from_camera(target["id"], num_samples=30)
            self.gui.set_message(f"Collected {count} samples for {target['name']}. Training model...")
            persons = self.face_recognizer.train_from_dataset()
            self.gui.set_message(f"Face model trained for {persons} person(s).")
        except Exception as e:
            self.gui.set_message(f"Error capturing faces: {e}")

    def _on_confirm_taken(self) -> None:
        self.confirmation_state.confirm()

    # Wake phrase loop
    def _wake_phrase_loop(self) -> None:
        while True:
            try:
                phrase = self.asr.listen_for_keywords(["hello baymax", "hey baymax"], timeout_sec=5.0)
                if phrase:
                    self.gui.set_expression("alert")
                    self.gui.set_message("Hello. I am your personal healthcare companion. How can I assist you?")
                    self.tts.speak("Hello. I am your personal healthcare companion. How can I assist you?")
                    time.sleep(5)
                    self.gui.set_expression("idle")
            except Exception:
                time.sleep(5)

    # Medicine event
    def _on_medicine_time(self, user: Dict, sched: Dict) -> None:
        # Run in a separate thread to avoid blocking scheduler
        threading.Thread(target=self._handle_medicine_flow, args=(user, sched), daemon=True).start()

    def _handle_medicine_flow(self, user: Dict, sched: Dict) -> None:
        user_id = user["id"]
        user_name = user["name"]
        time_str = sched.get("time", "")
        label = sched.get("label", "Medicine")

        # Wake and greet
        self.gui.set_expression("alert")
        greeting = (
            f"Hello. My name is Baymax, your personal healthcare companion. It is time for your {label}. Please take it now."
        )
        self.gui.set_message(greeting)
        self.tts.speak(greeting)

        # Attempt face authentication
        auth_ok = self._attempt_face_auth(user_id, timeout_sec=60.0)
        if not auth_ok:
            # Emergency voice fallback: require name confirmation
            self.tts.speak("If you cannot show your face, please say 'Hello Baymax'.")
            phrase = self.asr.listen_for_keywords(["hello baymax", "hey baymax"], timeout_sec=20.0)
            if phrase:
                self.tts.speak("Please say your name.")
                # naive name capture
                recognized_name = self.asr.listen_for_keywords([user_name.lower()], timeout_sec=8.0)
                if recognized_name:
                    auth_ok = True

        # Ask for medicine taken confirmation with retries
        confirmed = False
        self.confirmation_state.reset()
        for attempt in range(3):
            if attempt > 0:
                self.tts.speak("Reminder. Please confirm you have taken your medicine.")
                self.gui.set_message("Reminder. Please confirm you have taken your medicine.")
            # parallel: listen for speech confirmation and button
            spoke = False
            def asr_waiter(res_holder: List[bool]):
                try:
                    res_holder[0] = self.asr.listen_for_confirmation(timeout_sec=8.0)
                except Exception:
                    res_holder[0] = False
            res = [False]
            t = threading.Thread(target=asr_waiter, args=(res,), daemon=True)
            t.start()
            button = self.confirmation_state.wait(timeout=10.0)
            t.join(timeout=0.1)
            spoke = res[0]
            if button or spoke:
                confirmed = True
                break
            if attempt < 2:
                time.sleep(20)
        if confirmed:
            self.data_store.log_dose(user_id, time_str, label, status="confirmed")
            self.gui.set_message("Thank you. I have recorded that you have taken your medicine.")
            self.tts.speak("Thank you. I have recorded that you have taken your medicine.")
            self.gui.set_expression("talking")
            time.sleep(3)
        else:
            self.data_store.log_dose(user_id, time_str, label, status="missed")
            self.gui.set_message("I did not receive a confirmation. I will log a missed dose.")
            self.tts.speak("I did not receive a confirmation. I will log a missed dose.")
            self.gui.set_expression("sad")
            time.sleep(3)
        self.gui.set_expression("idle")

    def _attempt_face_auth(self, user_id: str, timeout_sec: float) -> bool:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False
        deadline = time.time() + timeout_sec
        ok = False
        try:
            while time.time() < deadline:
                ret, frame = cap.read()
                if not ret:
                    continue
                recognized_user_id, distance = self.face_recognizer.recognize_best(frame)
                if recognized_user_id == user_id:
                    ok = True
                    break
                # tiny sleep to avoid busy loop
                time.sleep(0.05)
        finally:
            cap.release()
        return ok

    def run(self) -> None:
        self.gui.mainloop()


def main():
    app = BaymaxApp(base_dir=BASE_DIR)
    app.run()


if __name__ == "__main__":
    main()