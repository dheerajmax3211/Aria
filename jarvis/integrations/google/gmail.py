import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from loguru import logger


class GoogleGmail:
    def __init__(self, creds):
        self.service = build("gmail", "v1", credentials=creds)

    def get_unread_emails(self, max_results: int = 10) -> list[dict]:
        results = self.service.users().messages().list(
            userId="me",
            q="is:unread",
            maxResults=max_results,
        ).execute()
        messages = results.get("messages", [])
        emails = []
        for msg in messages:
            message = self.service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
            emails.append({
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "No subject"),
                "date": headers.get("Date", "Unknown"),
            })
        return emails

    def send_email(self, to: str, subject: str, body: str) -> str:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.service.users().messages().send(userId="me", body={"raw": raw}).execute()
        logger.info(f"Email sent to {to}: {subject}")
        return f"Email sent to {to} with subject: {subject}"

    def search_emails(self, query: str, max_results: int = 5) -> list[dict]:
        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results,
        ).execute()
        messages = results.get("messages", [])
        emails = []
        for msg in messages:
            message = self.service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
            emails.append({
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "No subject"),
                "date": headers.get("Date", "Unknown"),
            })
        return emails

    def get_unread_summary(self) -> str:
        emails = self.get_unread_emails(max_results=5)
        if not emails:
            return "No unread emails"
        parts = []
        for email in emails:
            parts.append(f"From {email['from']}: {email['subject']}")
        return f"You have unread emails: {'; '.join(parts)}"

    def reply_to_email(self, message_id: str, reply_body: str) -> str:
        try:
            original = self.service.users().messages().get(userId="me", id=message_id, format="metadata", metadataHeaders=["From", "Subject", "Message-ID"]).execute()
            headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
            subject = headers.get("Subject", "Re: ")
            if not subject.startswith("Re: "):
                subject = f"Re: {subject}"
            message = MIMEText(reply_body)
            message["to"] = headers.get("From", "")
            message["subject"] = subject
            message["In-Reply-To"] = headers.get("Message-ID", "")
            message["References"] = headers.get("Message-ID", "")
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(userId="me", body={"raw": raw, "threadId": original.get("threadId", "")}).execute()
            logger.info(f"Replied to email {message_id}")
            return f"Replied to email: {subject}"
        except Exception as e:
            return f"Failed to reply: {e}"

    def create_draft(self, to: str, subject: str, body: str) -> str:
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            draft = self.service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
            logger.info(f"Draft created for {to}: {subject}")
            return f"Draft created: '{subject}' to {to}. Review before sending."
        except Exception as e:
            return f"Failed to create draft: {e}"
