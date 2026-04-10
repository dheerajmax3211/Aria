import asyncio
import os
import re
import tempfile
import edge_tts
from elevenlabs import ElevenLabs
from loguru import logger
import threading

from jarvis.config import settings
from jarvis.output.speaker import Speaker


class TextToSpeech:
    def __init__(self):
        self.elevenlabs_client = None
        self.speaker = Speaker()
        self._stop_event = threading.Event()
        self.voice = settings.tts_voice
        self._init_primary()

    def _init_primary(self):
        if settings.elevenlabs_configured:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=settings.elevenlabs_api_key)
                logger.info(f"ElevenLabs TTS initialized (premium, voice: {settings.elevenlabs_voice_id})")
            except Exception as e:
                logger.warning(f"ElevenLabs init failed: {e}, using Edge TTS")
                self.elevenlabs_client = None
        else:
            logger.info(f"Edge TTS neural voice: {self.voice} (free, no API key)")

    def speak(self, text: str, tone: str = "neutral"):
        self._stop_event.clear()
        natural_text = self._make_natural(text)
        audio_bytes = self._generate(natural_text, tone)
        if audio_bytes and not self._stop_event.is_set():
            self.speaker.play(audio_bytes)
        elif self._stop_event.is_set():
            logger.info("TTS interrupted")
        else:
            logger.error("All TTS engines failed")

    def _make_natural(self, text: str) -> str:
        text = re.sub(r'\b(\d+)\b', lambda m: self._number_to_words(int(m.group(1))), text)
        text = text.replace('°C', ' degrees Celsius').replace('°F', ' degrees Fahrenheit')
        text = text.replace('%', ' percent')
        text = text.replace('&', ' and ')
        text = text.replace('/', ' or ')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _number_to_words(self, n: int) -> str:
        ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        if n < 0:
            return f"negative {self._number_to_words(-n)}"
        if n < 10:
            return ones[n]
        if n < 20:
            return teens[n - 10]
        if n < 100:
            return f"{tens[n // 10]} {ones[n % 10]}".strip()
        if n < 1000:
            return f"{ones[n // 100]} hundred {self._number_to_words(n % 100)}".strip()
        if n < 1000000:
            return f"{self._number_to_words(n // 1000)} thousand {self._number_to_words(n % 1000)}".strip()
        return str(n)

    def _generate(self, text: str, tone: str = "neutral") -> bytes | None:
        if self.elevenlabs_client:
            try:
                style_map = {
                    "calm": {"stability": 0.7, "similarity_boost": 0.8},
                    "urgent": {"stability": 0.3, "similarity_boost": 0.9},
                    "happy": {"stability": 0.5, "similarity_boost": 0.7},
                    "serious": {"stability": 0.9, "similarity_boost": 0.9},
                    "neutral": {"stability": 0.5, "similarity_boost": 0.75},
                }
                style = style_map.get(tone, style_map["neutral"])
                audio = self.elevenlabs_client.generate(
                    text=text,
                    voice=settings.elevenlabs_voice_id,
                    model="eleven_monolingual_v1",
                    voice_settings=style,
                )
                audio_bytes = b"".join(chunk for chunk in audio)
                logger.info(f"ElevenLabs generated {len(audio_bytes)} bytes (tone: {tone})")
                return audio_bytes
            except Exception as e:
                logger.warning(f"ElevenLabs generation failed: {e}, falling back to Edge TTS")

        return self._edge_tts(text, tone)

    def _edge_tts(self, text: str, tone: str = "neutral") -> bytes | None:
        try:
            rate_map = {
                "calm": "+5%",
                "urgent": "+25%",
                "happy": "+18%",
                "serious": "+2%",
                "neutral": "+15%",
            }
            pitch_map = {
                "calm": "-3Hz",
                "urgent": "+4Hz",
                "happy": "+6Hz",
                "serious": "-6Hz",
                "neutral": "+0Hz",
            }
            rate = rate_map.get(tone, settings.tts_rate)
            pitch = pitch_map.get(tone, settings.tts_pitch)
            audio_bytes = asyncio.run(self._run_edge_tts(text, rate, pitch))
            if audio_bytes:
                logger.info(f"Edge TTS generated {len(audio_bytes)} bytes (tone: {tone})")
            return audio_bytes
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            return None

    async def _run_edge_tts(self, text: str, rate: str, pitch: str) -> bytes | None:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        communicate = edge_tts.Communicate(text, self.voice, rate=rate, pitch=pitch)
        await communicate.save(tmp_path)

        with open(tmp_path, "rb") as f:
            mp3_data = f.read()

        try:
            os.unlink(tmp_path)
        except PermissionError:
            pass

        return mp3_data

    def stop(self):
        self._stop_event.set()
        self.speaker.stop()

    def interrupt(self):
        self.stop()
        logger.info("TTS interrupted by user")
