import numpy as np
import sounddevice as sd
from loguru import logger


class MuteDetector:
    def __init__(
        self,
        sample_rate: int = 16000,
        mute_threshold: float = 0.001,
        check_duration: float = 2.0,
    ):
        self.sample_rate = sample_rate
        self.mute_threshold = mute_threshold
        self.check_duration = check_duration
        self._is_muted = False
        self._last_check = None

    def check_mute(self) -> bool:
        logger.info("Checking microphone input level for mute detection")
        try:
            audio = sd.rec(
                int(self.sample_rate * self.check_duration),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
            )
            sd.wait()
            rms = np.sqrt(np.mean(audio ** 2))
            self._is_muted = rms < self.mute_threshold
            from datetime import datetime
            self._last_check = datetime.now()
            if self._is_muted:
                logger.info(f"Microphone appears muted (RMS: {rms:.6f})")
            else:
                logger.info(f"Microphone active (RMS: {rms:.6f})")
            return self._is_muted
        except Exception as e:
            logger.warning(f"Mute detection failed: {e}, assuming not muted")
            return False

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    def should_respond(self) -> bool:
        if not self._last_check:
            self.check_mute()
        from datetime import datetime, timedelta
        if self._last_check and datetime.now() - self._last_check > timedelta(minutes=5):
            self.check_mute()
        return not self._is_muted
