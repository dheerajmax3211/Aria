import os
import tempfile
import numpy as np
import sounddevice as sd
import pygame
from loguru import logger


class Speaker:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self._stop_event = False
        pygame.mixer.init()

    def play(self, audio_bytes: bytes):
        self._stop_event = False
        try:
            if audio_bytes[:3] == b"ID3" or audio_bytes[:4] == b"\xff\xfb" or audio_bytes[:2] == b"\xff\xf3":
                self._play_mp3(audio_bytes)
            else:
                self._play_pcm(audio_bytes)
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")

    def _play_mp3(self, audio_bytes: bytes):
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() and not self._stop_event:
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            import time
            time.sleep(0.1)
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass

            logger.info("MP3 playback complete")
        except Exception as e:
            logger.error(f"MP3 playback failed: {e}")

    def _play_pcm(self, audio_bytes: bytes):
        try:
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            sd.play(audio_array, self.sample_rate)
            sd.wait()
        except Exception as e:
            logger.error(f"PCM playback failed: {e}")

    def stop(self):
        self._stop_event = True
        pygame.mixer.music.stop()
        sd.stop()
        logger.info("Audio playback stopped")

    @property
    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy() or (sd.get_stream() is not None and sd.get_stream().active)
