import threading
from loguru import logger

from jarvis.config import settings
from jarvis.integrations.telegram_bot import TelegramBot
from jarvis.integrations.whatsapp import WhatsAppAutomation


class MessagingAgent:
    name = "messaging_agent"
    description = "Send messages via Telegram and WhatsApp"

    def __init__(self, llm=None):
        self.telegram = None
        self.whatsapp = None
        self._telegram_thread = None
        self._init_telegram(llm)
        self._init_whatsapp()

    def _init_telegram(self, llm):
        if settings.telegram_bot_token:
            self.telegram = TelegramBot(llm=llm)
            self._telegram_thread = threading.Thread(target=self.telegram.start_polling, daemon=True)
            self._telegram_thread.start()
            logger.info("Telegram bot started in background")
        else:
            logger.warning("Telegram bot token not set, Telegram disabled")

    def _init_whatsapp(self):
        self.whatsapp = WhatsAppAutomation(headless=False)

    def send_telegram(self, chat_id: int, message: str) -> str:
        if not self.telegram:
            return "Telegram not configured"
        try:
            self.telegram.send_message(chat_id, message)
            return f"Telegram message sent to chat {chat_id}"
        except Exception as e:
            return f"Telegram send failed: {e}"

    def send_whatsapp(self, contact_name: str, message: str) -> str:
        if not self.whatsapp:
            return "WhatsApp not configured"
        return self.whatsapp.send_message(contact_name, message)

    def send_whatsapp_media(self, contact_name: str, file_path: str, caption: str = "") -> str:
        if not self.whatsapp:
            return "WhatsApp not configured"
        return self.whatsapp.send_media(contact_name, file_path, caption)

    def send_telegram_media(self, chat_id: int, file_path: str, caption: str = "", media_type: str = "photo") -> str:
        if not self.telegram:
            return "Telegram not configured"
        try:
            self.telegram.send_media(chat_id, file_path, caption, media_type)
            return f"Telegram {media_type} sent to chat {chat_id}"
        except Exception as e:
            return f"Telegram media send failed: {e}"
