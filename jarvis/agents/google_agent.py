from jarvis.integrations.google.calendar import GoogleCalendar
from jarvis.integrations.google.gmail import GoogleGmail
from jarvis.integrations.google.drive import GoogleDrive
from jarvis.integrations.google.auth import authenticate_google
from loguru import logger


class GoogleAgent:
    name = "google_agent"
    description = "Access Google Calendar, Gmail, and Drive"

    def __init__(self, credentials_path: str = "integrations/google/credentials.json"):
        self.calendar = None
        self.gmail = None
        self.drive = None
        self._authenticate(credentials_path)

    def _authenticate(self, credentials_path: str):
        try:
            creds = authenticate_google(credentials_path=credentials_path)
            if creds:
                self.calendar = GoogleCalendar(creds)
                self.gmail = GoogleGmail(creds)
                self.drive = GoogleDrive(creds)
                logger.info("Google Agent authenticated (Calendar, Gmail, Drive)")
            else:
                logger.warning("Google authentication failed")
        except Exception as e:
            logger.warning(f"Google Agent disabled: {e}")

    def get_calendar_events(self, days: int = 3) -> str:
        if not self.calendar:
            return "Google Calendar not configured"
        return self.calendar.get_todays_events()

    def get_unread_emails(self) -> str:
        if not self.gmail:
            return "Gmail not configured"
        return self.gmail.get_unread_summary()

    def send_email(self, to: str, subject: str, body: str) -> str:
        if not self.gmail:
            return "Gmail not configured"
        return self.gmail.send_email(to, subject, body)

    def search_emails(self, query: str) -> str:
        if not self.gmail:
            return "Gmail not configured"
        emails = self.gmail.search_emails(query)
        if not emails:
            return f"No emails found matching '{query}'"
        parts = []
        for e in emails:
            parts.append(f"From {e['from']}: {e['subject']}")
        return "Found emails: " + "; ".join(parts)

    def list_drive_files(self) -> str:
        if not self.drive:
            return "Google Drive not configured"
        return self.drive.get_recent_summary()

    def create_folder(self, folder_name: str) -> str:
        if not self.drive:
            return "Google Drive not configured"
        return self.drive.create_folder(folder_name)

    def share_file(self, file_id: str, email: str, role: str = "writer") -> str:
        if not self.drive:
            return "Google Drive not configured"
        return self.drive.share_file(file_id, email, role)

    def reply_to_email(self, message_id: str, reply_body: str) -> str:
        if not self.gmail:
            return "Gmail not configured"
        return self.gmail.reply_to_email(message_id, reply_body)

    def create_draft(self, to: str, subject: str, body: str) -> str:
        if not self.gmail:
            return "Gmail not configured"
        return self.gmail.create_draft(to, subject, body)

    def find_free_slot(self, duration_minutes: int = 60) -> str:
        if not self.calendar:
            return "Google Calendar not configured"
        return self.calendar.find_free_slot(duration_minutes)

    def cancel_event(self, event_id: str) -> str:
        if not self.calendar:
            return "Google Calendar not configured"
        return self.calendar.cancel_event(event_id)
