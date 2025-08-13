import os
import queue
import threading
import time
from typing import Iterable, List, Optional

import pyttsx3


class BaymaxTTS:
    """Offline TTS configured to a calm, monotone style. This is an inspired voice, not a clone.

    If the system TTS engine is unavailable, this class degrades gracefully to a no-op logger.
    """

    def __init__(self):
        self._engine = None
        self._enabled = True
        try:
            self._engine = pyttsx3.init()
            try:
                self._engine.setProperty('rate', 135)
                self._engine.setProperty('volume', 0.9)
            except Exception:
                pass
        except Exception:
            # Fallback to disabled engine (no-op)
            self._engine = None
            self._enabled = False
        self._lock = threading.RLock()
        self._speak_thread: Optional[threading.Thread] = None
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._stop_event = threading.Event()
        self._start_worker()

    def _start_worker(self) -> None:
        if self._engine is None:
            return
        def worker():
            while not self._stop_event.is_set():
                try:
                    text = self._queue.get(timeout=0.2)
                except queue.Empty:
                    continue
                try:
                    with self._lock:
                        self._engine.say(text)
                        self._engine.runAndWait()
                except Exception:
                    pass
        self._speak_thread = threading.Thread(target=worker, daemon=True)
        self._speak_thread.start()

    def speak(self, text: str) -> None:
        if self._engine is None or not self._enabled:
            # graceful degrade: print to stdout
            print(f"[TTS disabled] {text}")
            return
        self._queue.put(text)

    def stop(self) -> None:
        self._stop_event.set()
        try:
            if self._engine is not None:
                self._engine.stop()
        except Exception:
            pass


# Optional STT via Vosk
try:
    import json
    import sounddevice as sd
    from vosk import KaldiRecognizer, Model
except Exception:  # pragma: no cover - optional
    sd = None
    Model = None
    KaldiRecognizer = None


class VoskRecognizer:
    def __init__(self, models_base_dir: str):
        self.models_base_dir = models_base_dir
        self.model_dir = os.path.join(self.models_base_dir, "vosk-model-small-en-us-0.15")
        self._model = None
        self._rec = None
        self._lock = threading.RLock()

    def ensure_model(self) -> None:
        if os.environ.get("BAYMAX_DISABLE_STT") == "1":
            return
        if os.path.isdir(self.model_dir) and os.path.exists(os.path.join(self.model_dir, "am")):
            return
        # Lazy download
        import zipfile
        import requests
        from tqdm import tqdm

        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        os.makedirs(self.models_base_dir, exist_ok=True)
        zip_path = os.path.join(self.models_base_dir, "vosk_en_small.zip")
        if not os.path.exists(zip_path):
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                with open(zip_path, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True, desc='Downloading Vosk') as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(self.models_base_dir)

    def _ensure_recognizer(self) -> None:
        if os.environ.get("BAYMAX_DISABLE_STT") == "1":
            raise RuntimeError("STT disabled by environment variable BAYMAX_DISABLE_STT=1")
        if sd is None or Model is None:
            raise RuntimeError("Speech recognition dependencies not available")
        with self._lock:
            if self._model is None:
                self.ensure_model()
                self._model = Model(self.model_dir)

    def listen_for_keywords(self, keywords: List[str], timeout_sec: float = 10.0) -> Optional[str]:
        if os.environ.get("BAYMAX_DISABLE_STT") == "1":
            return None
        if sd is None or Model is None or KaldiRecognizer is None:
            return None
        self._ensure_recognizer()
        samplerate = 16000
        with self._lock:
            rec = KaldiRecognizer(self._model, samplerate)
        result_text = ""
        keywords_lc = [k.lower() for k in keywords]
        deadline = time.time() + timeout_sec
        q: "queue.Queue[bytes]" = queue.Queue()

        def audio_callback(indata, frames, time_info, status):  # type: ignore
            q.put(bytes(indata))
            return None

        try:
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=1, callback=audio_callback):
                while time.time() < deadline:
                    try:
                        data = q.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    if rec.AcceptWaveform(data):
                        res = rec.Result()
                        try:
                            j = json.loads(res)
                            text = j.get("text", "").lower()
                            result_text += " " + text
                            for kw in keywords_lc:
                                if kw in text:
                                    return kw
                        except Exception:
                            pass
        except Exception:
            return None
        return None

    def listen_for_confirmation(self, timeout_sec: float = 8.0) -> bool:
        if os.environ.get("BAYMAX_DISABLE_STT") == "1":
            return False
        phrase = self.listen_for_keywords(["taken", "yes", "i have taken it", "i took it"], timeout_sec=timeout_sec)
        return phrase is not None