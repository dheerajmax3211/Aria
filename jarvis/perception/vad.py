import numpy as np
import sounddevice as sd
from loguru import logger


class VoiceActivityDetector:
    def __init__(
        self,
        sample_rate: int = 16000,
        silence_threshold: float = 0.008,
        silence_duration: float = 1.2,
        min_speech_duration: float = 0.3,
        max_recording_duration: float = 30.0,
    ):
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        self.max_recording_duration = max_recording_duration
        self.silence_frames = int(silence_duration * sample_rate / 1024)
        self.chunk_size = 1024

    def is_silent(self, audio_chunk: np.ndarray) -> bool:
        rms = np.sqrt(np.mean(audio_chunk.astype(np.float32) ** 2))
        return rms < self.silence_threshold

    def record_until_silence(self) -> np.ndarray:
        logger.info("Listening... (speak now)")
        audio_buffer = []
        consecutive_silent_frames = 0
        total_frames = 0
        max_frames = int(self.max_recording_duration * self.sample_rate / self.chunk_size)
        min_frames = int(self.min_speech_duration * self.sample_rate / self.chunk_size)
        speech_started = False

        def callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            audio_buffer.append(indata.copy())

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            callback=callback,
        ):
            while True:
                sd.sleep(50)
                if not audio_buffer:
                    continue

                total_frames += 1

                if total_frames >= max_frames:
                    logger.info(f"Max recording duration reached ({self.max_recording_duration}s)")
                    break

                recent_chunks = audio_buffer[-20:]
                chunk = np.concatenate(recent_chunks)

                if self.is_silent(chunk):
                    consecutive_silent_frames += 1
                    if speech_started and consecutive_silent_frames >= self.silence_frames:
                        logger.info("Silence detected, stopping recording")
                        break
                else:
                    consecutive_silent_frames = 0
                    if total_frames >= min_frames:
                        speech_started = True

        if not audio_buffer:
            logger.info("No audio captured")
            return np.array([], dtype=np.float32)

        full_audio = np.concatenate(audio_buffer, axis=0)
        duration = len(full_audio) / self.sample_rate
        logger.info(f"Recorded {duration:.1f}s of audio (speech_detected={speech_started})")
        return full_audio.flatten()
