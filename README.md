# BAYMAX: Personal Healthcare Companion

An AI assistant inspired by Baymax that reminds patients to take medicine, verifies via face recognition, supports wake words, and provides a friendly animated GUI.

Important note: This project does not clone or reproduce the exact copyrighted Baymax movie voice. It uses a calm, gentle, clinical voice profile that evokes a similar vibe. You can plug in your own custom TTS model if you have usage rights.

## Features
- Animated always-on GUI with a friendly face and expression states (idle, talking, alert, sad)
- Multi-user registration with name, facial data, and medicine schedules
- Face detection and recognition via OpenCV (LBPH)
- Scheduled reminders with retries and missed-dose logging
- Optional wake-word/voice command support using Vosk ("hello baymax", "hey baymax")
- Local SQLite storage and CSV import/export helpers

## Quick Start
1. Python 3.10+ recommended. Ensure Tkinter is installed (Linux: `sudo apt install python3-tk`).
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Download a small Vosk model for wake word:
   - Visit `https://alphacephei.com/vosk/models` and download a small English model (e.g., `vosk-model-small-en-us-0.15`).
   - Extract to `models/vosk-model-small-en-us-0.15` and set `VOSK_MODEL_PATH` env var or place it under `./models`.
4. Run the app:
   ```bash
   python run.py
   ```

## Usage
- Use "Register User" to add a new person, capture ~20 face samples, and set one or more daily times (HH:MM, 24h).
- The assistant will wake at scheduled times, try to detect/recognize the user via the camera, speak a reminder, and wait for confirmation.
- If not confirmed, it retries twice (20 seconds apart). Otherwise, it logs a missed dose in `data/missed.csv` and SQLite.
- You can also trigger by voice ("hello baymax"), if Vosk model is available, or via the GUI "Wake" button.

## Voice
- Default is a calm, gentle TTS profile via `pyttsx3` with subtle pitch processing to evoke a Baymax-like tone.
- We do not ship a copyrighted movie-voice clone. If you have rights to a custom model, implement a `CustomVoiceBackend` by extending `baymax/voice.py` and point `VOICE_BACKEND=custom` in `.env`.

## Folders
- `baymax/`: app modules
- `data/`: database, models, face samples, logs
- `models/`: optional ASR models (e.g., Vosk)

## Troubleshooting
- If Tkinter is missing: `sudo apt install python3-tk`
- If microphone isn't working, check `sounddevice` default device or set `DEFAULT_AUDIO_DEVICE` in `.env`.
- If OpenCV LBPH is missing, ensure `opencv-contrib-python` is installed (not `opencv-python`).

## License
MIT