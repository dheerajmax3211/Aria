import numpy as np
import noisereduce as nr
from faster_whisper import WhisperModel
from loguru import logger

from jarvis.config import settings


class SpeechToText:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        logger.info(f"Loading Whisper model: {settings.stt_model}")
        try:
            self.model = WhisperModel(
                settings.stt_model,
                device="cpu",
                compute_type="int8",
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        try:
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
            if rms < 0.005:
                return audio
            cleaned = nr.reduce_noise(y=audio, sr=16000, stationary=True, prop_decrease=0.50)
            return cleaned
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}, using raw audio")
            return audio

    def transcribe(self, audio: np.ndarray) -> str:
        if self.model is None:
            logger.error("Whisper model not loaded")
            return ""

        try:
            audio_cleaned = self._reduce_noise(audio)
            audio_float32 = audio_cleaned.astype(np.float32)
            segments, info = self.model.transcribe(
                audio_float32,
                beam_size=5,
                language=None,
            )
            text = " ".join(segment.text for segment in segments).strip()
            logger.info(f"Transcribed: '{text}' (lang: {info.language}, prob: {info.language_probability:.2f})")
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
