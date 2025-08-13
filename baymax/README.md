# BAYMAX - Personal Healthcare Companion (Inspired)

Important: This project uses a Baymax-inspired synthetic voice. It does not clone or impersonate any real person's voice.

## Features
- Animated GUI with Baymax-like face (Tkinter)
- Multi-user registration (name, face data, daily medicine schedule)
- Face recognition using OpenCV LBPH
- Wake phrase and speech recognition via Vosk ("hello baymax", "taken")
- Voice prompts via offline TTS (pyttsx3)
- Medicine reminders with retries and missed-dose logging

## Requirements
- Python 3.10+
- Camera and microphone
- Linux: you may need system libraries for audio (e.g., `libportaudio2`).

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If microphone access fails on Linux, install PortAudio runtime:
```bash
sudo apt-get update && sudo apt-get install -y libportaudio2
```

## Run
```bash
cd baymax
source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -m app.main
```

First, register a user from the GUI, then capture face samples. Add medicine times as HH:MM (24h), comma-separated. Example: `08:00:Vitamin C, 20:30:Blood Pressure`

## Data & Models
- Users: `data/users.json`
- Face images: `data/faces/<user_id>/img_*.jpg`
- Face model: `data/models/face_lbph.yml`
- Label mapping: `data/models/labels.json`
- Logs: `data/logs.csv`
- Vosk model auto-downloads to `models/vosk-model-small-en-us-0.15`

## Notes
- Face recognition threshold may need tuning based on lighting and camera.
- The assistant retries reminders twice (20s apart). If still unconfirmed, the dose is logged as missed.
- Voice model is a generic, calm synthetic voice configured via TTS rate and volume.