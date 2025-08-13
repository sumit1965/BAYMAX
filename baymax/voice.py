import os
import tempfile
from typing import Optional

import pyttsx3
from pydub import AudioSegment
import numpy as np
import sounddevice as sd


class VoiceEngine:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        # Configure a calm, gentle, clinical profile
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("volume", 1.0)
        # Choose a neutral voice if available
        voices = self.engine.getProperty("voices") or []
        for v in voices:
            if "en" in (v.languages[0] if v.languages else "en"):
                self.engine.setProperty("voice", v.id)
                break
        # Mild pitch lowering will be applied post-TTS via resampling
        self.pitch_semitones = -2

    def speak(self, text: str, style: Optional[str] = None) -> None:
        # Save TTS to a temp WAV, then pitch-shift and play
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, "tts.wav")
            self.engine.save_to_file(text, wav_path)
            self.engine.runAndWait()

            audio = AudioSegment.from_wav(wav_path)
            if self.pitch_semitones != 0:
                new_sample_rate = int(audio.frame_rate * (2.0 ** (self.pitch_semitones / 12.0)))
                pitched = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate}).set_frame_rate(audio.frame_rate)
            else:
                pitched = audio

            samples = np.frombuffer(pitched.raw_data, dtype=np.int16)
            channels = pitched.channels
            if channels > 1:
                samples = samples.reshape((-1, channels))
            sd.play(samples, pitched.frame_rate, blocking=True)

    def speak_greeting(self) -> None:
        self.speak("Hello. My name is your personal healthcare companion. It's time for your medicine. Please take it now.")

    def speak_retry(self) -> None:
        self.speak("Reminder. Please take your medicine now.")

    def speak_confirm(self) -> None:
        self.speak("Thank you. Confirmation received.")

    def speak_missed(self) -> None:
        self.speak("I am sorry. I will log this as a missed dose.")