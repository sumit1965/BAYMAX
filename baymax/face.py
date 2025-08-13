import os
from typing import Optional, Tuple, List

import cv2
import numpy as np

from baymax.storage import Storage


class FaceService:
    def __init__(self, storage: Storage, model_path: str = "data/recognizer_lbph.yml") -> None:
        self.storage = storage
        self.model_path = model_path
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_loaded = False
        self._load_model_if_exists()

    def _load_model_if_exists(self) -> None:
        if os.path.exists(self.model_path):
            try:
                self.recognizer.read(self.model_path)
                self.model_loaded = True
            except Exception:
                self.model_loaded = False

    def capture_user_faces(self, user_id: int, num_samples: int = 20, camera_index: int = 0) -> List[str]:
        os.makedirs(f"data/faces/{user_id}", exist_ok=True)
        cap = cv2.VideoCapture(camera_index)
        saved_paths: List[str] = []
        count = 0
        while count < num_samples:
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face_img = gray[y : y + h, x : x + w]
                file_path = f"data/faces/{user_id}/img_{count}.png"
                cv2.imwrite(file_path, face_img)
                self.storage.add_face_sample(user_id, file_path)
                saved_paths.append(file_path)
                count += 1
                break
            cv2.imshow("Capture Faces - Press q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
        return saved_paths

    def train_model(self) -> None:
        samples = self.storage.get_all_face_samples()
        if not samples:
            self.model_loaded = False
            return
        images: List[np.ndarray] = []
        labels: List[int] = []
        for _, user_id, file_path in samples:
            if not os.path.exists(file_path):
                continue
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(user_id)
        if not images:
            self.model_loaded = False
            return
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.train(images, np.array(labels))
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.recognizer.write(self.model_path)
        self.model_loaded = True

    def recognize(self, camera_index: int = 0, timeout_seconds: int = 15) -> Optional[Tuple[int, float]]:
        if not self.model_loaded:
            return None
        cap = cv2.VideoCapture(camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        start = cv2.getTickCount()
        freq = cv2.getTickFrequency()
        result: Optional[Tuple[int, float]] = None
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face_img = gray[y : y + h, x : x + w]
                try:
                    label, confidence = self.recognizer.predict(face_img)
                except Exception:
                    label, confidence = -1, 999.0
                # Lower confidence is better in LBPH; typical threshold around 70-90
                if confidence < 85:
                    result = (label, confidence)
                    break
            cv2.imshow("Recognition - Press q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            elapsed = (cv2.getTickCount() - start) / freq
            if result is not None or elapsed > timeout_seconds:
                break
        cap.release()
        cv2.destroyAllWindows()
        return result