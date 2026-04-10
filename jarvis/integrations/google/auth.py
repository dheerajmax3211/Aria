import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from loguru import logger

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive",
]


def authenticate_google(credentials_path: str = "integrations/google/credentials.json", token_path: str = "integrations/google/token.pickle"):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing Google credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                logger.error(f"Google credentials file not found at {credentials_path}")
                logger.info("Download credentials from: https://console.cloud.google.com/apis/credentials")
                return None
            logger.info("Opening browser for Google OAuth authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("Google OAuth completed")

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds
