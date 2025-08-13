import json
import os
import threading
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


class FaceDatasetManager:
    def __init__(self, faces_dir: str):
        self.faces_dir = faces_dir
        os.makedirs(self.faces_dir, exist_ok=True)
        self._haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def _detect_face(self, gray_frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        faces = self._haar_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            return None
        # pick largest face
        x, y, w, h = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)[0]
        return x, y, w, h

    def collect_samples_from_camera(self, user_id: str, num_samples: int = 30, camera_index: int = 0) -> int:
        os.makedirs(os.path.join(self.faces_dir, user_id), exist_ok=True)
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise RuntimeError("Cannot open camera for face capture")
        saved = 0
        try:
            while saved < num_samples:
                ret, frame = cap.read()
                if not ret:
                    continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detected = self._detect_face(gray)
                if detected is None:
                    cv2.imshow("Capture Face - Align your face", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue
                x, y, w, h = detected
                face_roi = gray[y : y + h, x : x + w]
                face_resized = cv2.resize(face_roi, (200, 200))
                save_path = os.path.join(self.faces_dir, user_id, f"img_{saved:03d}.jpg")
                cv2.imwrite(save_path, face_resized)
                saved += 1
                # Draw rectangle for visual feedback
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Saved {saved}/{num_samples}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Capture Face - Align your face", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
        return saved


class FaceRecognizer:
    def __init__(self, model_file: str, labels_file: str, dataset_dir: str):
        self.model_file = model_file
        self.labels_file = labels_file
        self.dataset_dir = dataset_dir
        self._recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
        self._haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self._threshold = 70.0  # lower is better; tune this threshold per environment
        self._lock = threading.RLock()
        self._labels_to_user: Dict[int, str] = {}
        self._user_to_labels: Dict[str, int] = {}
        self._load_labels()
        self._maybe_load_model()

    def _load_labels(self) -> None:
        if os.path.exists(self.labels_file):
            with open(self.labels_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                self._labels_to_user = {int(k): v for k, v in content.get("labels_to_user", {}).items()}
                self._user_to_labels = {v: int(k) for k, v in self._labels_to_user.items()}
        else:
            self._labels_to_user = {}
            self._user_to_labels = {}

    def _save_labels(self) -> None:
        payload = {"labels_to_user": {str(k): v for k, v in self._labels_to_user.items()}}
        with open(self.labels_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def _maybe_load_model(self) -> None:
        if os.path.exists(self.model_file):
            try:
                self._recognizer.read(self.model_file)
            except Exception:
                pass

    def _next_label(self) -> int:
        if not self._labels_to_user:
            return 1
        return max(self._labels_to_user.keys()) + 1

    def _iter_dataset(self) -> Tuple[List[np.ndarray], List[int]]:
        images: List[np.ndarray] = []
        labels: List[int] = []
        for user_id in os.listdir(self.dataset_dir):
            user_dir = os.path.join(self.dataset_dir, user_id)
            if not os.path.isdir(user_dir):
                continue
            label = self._user_to_labels.get(user_id)
            if label is None:
                label = self._next_label()
                self._labels_to_user[label] = user_id
                self._user_to_labels[user_id] = label
            for img_name in os.listdir(user_dir):
                if not img_name.lower().endswith((".jpg", ".png", ".jpeg")):
                    continue
                path = os.path.join(user_dir, img_name)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                try:
                    resized = cv2.resize(img, (200, 200))
                    images.append(resized)
                    labels.append(label)
                except Exception:
                    continue
        return images, labels

    def train_from_dataset(self) -> int:
        with self._lock:
            images, labels = self._iter_dataset()
            if len(images) < 2 or len(set(labels)) < 1:
                # Require at least some data
                return 0
            self._recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
            self._recognizer.train(images, np.array(labels))
            os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
            self._recognizer.write(self.model_file)
            self._save_labels()
            return len(set(labels))

    def recognize_best(self, frame_bgr) -> Tuple[Optional[str], float]:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self._haar_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            return None, 9999.0
        x, y, w, h = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)[0]
        roi = gray[y : y + h, x : x + w]
        roi_resized = cv2.resize(roi, (200, 200))
        with self._lock:
            try:
                label_id, distance = self._recognizer.predict(roi_resized)
            except cv2.error:
                return None, 9999.0
        user_id = self._labels_to_user.get(int(label_id))
        if user_id is None:
            return None, distance
        if distance <= self._threshold:
            return user_id, distance
        return None, distance