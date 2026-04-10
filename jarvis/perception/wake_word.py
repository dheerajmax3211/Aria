import os
import numpy as np
import sounddevice as sd
from loguru import logger

from jarvis.config import settings


class WakeWordDetector:
    def __init__(self, wake_word: str | None = None):
        self.wake_word = wake_word or settings.wake_word
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.stt = None
        self._use_keyword_mode = "aria" in self.wake_word.lower()

    def listen(self) -> bool:
        if self._use_keyword_mode:
            return self._listen_keyword()
        return self._listen_model()

    def _listen_keyword(self) -> bool:
        logger.info(f"Listening for keyword: '{self.wake_word}'")
        from jarvis.perception.stt import SpeechToText

        if self.stt is None:
            self.stt = SpeechToText()

        keyword = self.wake_word.lower().replace("hey ", "").strip()

        while True:
            try:
                audio_buffer = []
                samples_collected = 0
                max_samples = int(self.sample_rate * 3.0)

                def callback(indata, frames, time_info, status):
                    nonlocal samples_collected
                    audio_buffer.append(indata.copy())
                    samples_collected += frames

                with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    blocksize=1024,
                    dtype=np.int16,
                    callback=callback,
                ):
                    while samples_collected < max_samples:
                        sd.sleep(100)

                full_audio = np.concatenate(audio_buffer, axis=0).flatten().astype(np.float32) / 32768.0
                rms = np.sqrt(np.mean(full_audio ** 2))
                if rms < 0.01:
                    continue

                text = self.stt.transcribe(full_audio).lower().strip()
                if text and keyword in text:
                    logger.info(f"Wake word detected: '{text}'")
                    return True
            except Exception as e:
                logger.warning(f"Wake word detection error: {e}")
                sd.sleep(1000)
                continue

    def _listen_model(self) -> bool:
        try:
            import openwakeword
            oww_dir = os.path.dirname(openwakeword.__file__)
            model_dir = os.path.join(oww_dir, "resources", "models")

            model_files = [f for f in os.listdir(model_dir) if f.endswith(".onnx") and not f.startswith(("embedding", "melspectrogram", "silero"))]
            if not model_files:
                logger.warning("No ONNX wake word models found, downloading defaults")
                from openwakeword.utils import download_models
                download_models()
                model_files = [f for f in os.listdir(model_dir) if f.endswith(".onnx") and not f.startswith(("embedding", "melspectrogram", "silero"))]

            logger.info(f"Found {len(model_files)} ONNX wake word models")
            model_paths = [os.path.join(model_dir, f) for f in model_files]

            from openwakeword.model import Model
            oww_model = Model(
                wakeword_models=model_paths,
                inference_framework="onnx",
            )
            logger.info("openWakeWord models loaded successfully (ONNX)")

            logger.info(f"Listening for wake word: '{self.wake_word}'")

            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                audio_chunk = indata.copy().flatten()
                prediction = oww_model.predict(audio_chunk)
                for model_name, score in prediction.items():
                    if score > 0.5:
                        logger.info(f"Wake word detected: '{model_name}' (confidence: {score:.3f})")
                        raise WakeWordDetected()

            class WakeWordDetected(Exception):
                pass

            try:
                with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    blocksize=self.chunk_size,
                    dtype=np.int16,
                    callback=audio_callback,
                ):
                    while True:
                        sd.sleep(50)
            except WakeWordDetected:
                return True
        except Exception as e:
            logger.error(f"Failed to load openWakeWord: {e}")
            raise

    def record_after_wake(self, duration: float = 5.0) -> np.ndarray:
        logger.info(f"Recording for {duration}s after wake word detection")
        audio_buffer = []
        samples_needed = int(self.sample_rate * duration)
        samples_collected = 0

        def callback(indata, frames, time_info, status):
            nonlocal samples_collected
            if status:
                logger.warning(f"Audio callback status: {status}")
            audio_buffer.append(indata.copy().flatten())
            samples_collected += len(indata)

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            callback=callback,
        ):
            while samples_collected < samples_needed:
                sd.sleep(50)

        full_audio = np.concatenate(audio_buffer)
        audio_float32 = full_audio.astype(np.float32) / 32768.0
        logger.info(f"Recorded {len(audio_float32) / self.sample_rate:.1f}s of audio")
        return audio_float32
