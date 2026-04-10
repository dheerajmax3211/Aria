import os
import time
from playwright.sync_api import sync_playwright
from loguru import logger


class WhatsAppAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self._pw = None
        self._logged_in = False

    def _launch(self):
        if self.browser:
            return
        self._pw = sync_playwright().start()
        user_data_dir = os.path.join("data", "whatsapp_session")
        os.makedirs(user_data_dir, exist_ok=True)
        self.browser = self._pw.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=self.headless,
        )
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()

    def login(self):
        self._launch()
        self.page.goto("https://web.whatsapp.com", wait_until="networkidle")
        if "web.whatsapp.com" in self.page.url:
            try:
                self.page.wait_for_selector("div[role='main']", timeout=5000)
                self._logged_in = True
                logger.info("WhatsApp Web already logged in")
            except Exception:
                logger.info("WhatsApp Web requires QR code scan. Check browser window.")
                self.page.wait_for_selector("div[role='main']", timeout=120000)
                self._logged_in = True
                logger.info("WhatsApp Web logged in via QR code")

    def send_message(self, contact_name: str, message: str) -> str:
        try:
            self._launch()
            if not self._logged_in:
                self.login()

            search_box = self.page.wait_for_selector("div[contenteditable='true'][data-tab='3']", timeout=10000)
            search_box.click()
            search_box.fill(contact_name)
            self.page.wait_for_timeout(2000)

            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(1000)

            input_box = self.page.wait_for_selector("div[contenteditable='true'][data-tab='10']", timeout=10000)
            input_box.click()
            input_box.fill(message)
            self.page.keyboard.press("Enter")

            logger.info(f"WhatsApp message sent to {contact_name}")
            return f"Message sent to {contact_name}"
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return f"Failed to send message: {e}"

    def send_media(self, contact_name: str, file_path: str, caption: str = "") -> str:
        try:
            self._launch()
            if not self._logged_in:
                self.login()

            search_box = self.page.wait_for_selector("div[contenteditable='true'][data-tab='3']", timeout=10000)
            search_box.click()
            search_box.fill(contact_name)
            self.page.wait_for_timeout(2000)

            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(1000)

            attach_button = self.page.wait_for_selector("div[title='Attach']", timeout=10000)
            attach_button.click()
            self.page.wait_for_timeout(500)

            file_input = self.page.wait_for_selector("input[type='file']", timeout=10000)
            file_input.set_input_files(file_path)
            self.page.wait_for_timeout(2000)

            if caption:
                caption_box = self.page.wait_for_selector("div[contenteditable='true'][data-tab='10']", timeout=10000)
                caption_box.fill(caption)

            send_button = self.page.wait_for_selector("button[data-testid='compose-btn-send']", timeout=10000)
            send_button.click()

            logger.info(f"WhatsApp media sent to {contact_name}")
            return f"Media sent to {contact_name}"
        except Exception as e:
            logger.error(f"WhatsApp media send failed: {e}")
            return f"Failed to send media: {e}"

    def close(self):
        if self.browser:
            self.browser.close()
        if self._pw:
            self._pw.stop()
        logger.info("WhatsApp session closed")
