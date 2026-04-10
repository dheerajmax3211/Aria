import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger

from jarvis.config import settings


class TelegramBot:
    def __init__(self, tts=None, stt=None, llm=None):
        self.app = None
        self.tts = tts
        self.stt = stt
        self.llm = llm
        self._init_bot()

    def _init_bot(self):
        if not settings.telegram_bot_token:
            logger.warning("Telegram bot token not set, Telegram integration disabled")
            return
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        logger.info("Telegram bot handlers registered")

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"Hello! I'm {settings.jarvis_name}. Send me a message and I'll process it on your PC."
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Send me any text message. I'll process it through ARIA on your PC and respond here."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        logger.info(f"Telegram message from {update.message.chat_id}: '{user_message}'")

        if self.llm:
            response = self.llm.chat(user_message)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("ARIA brain not connected yet.")

    def start_polling(self):
        if self.app:
            logger.info("Starting Telegram bot polling...")
            self.app.run_polling(drop_pending_updates=True)

    def send_message(self, chat_id: int, text: str):
        if self.app:
            asyncio.run(self.app.bot.send_message(chat_id=chat_id, text=text))
            logger.info(f"Sent Telegram message to {chat_id}")

    def send_media(self, chat_id: int, file_path: str, caption: str = "", media_type: str = "photo"):
        if self.app:
            if media_type == "photo":
                asyncio.run(self.app.bot.send_photo(chat_id=chat_id, photo=open(file_path, "rb"), caption=caption))
            elif media_type == "document":
                asyncio.run(self.app.bot.send_document(chat_id=chat_id, document=open(file_path, "rb"), caption=caption))
            elif media_type == "audio":
                asyncio.run(self.app.bot.send_audio(chat_id=chat_id, audio=open(file_path, "rb"), caption=caption))
            elif media_type == "video":
                asyncio.run(self.app.bot.send_video(chat_id=chat_id, video=open(file_path, "rb"), caption=caption))
            logger.info(f"Sent Telegram {media_type} to {chat_id}")
