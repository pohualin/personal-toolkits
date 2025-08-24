import os
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from src.config.auth import get_gmail_creds

def send(subject, body, to):
    """
    Send an email using Gmail API.

    Args:
        subject (str): Email subject
        body (str): Email body
        to (str): Recipient email address
        creds_path (str): Path to OAuth token.json
    """
    creds = get_gmail_creds()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_message = (
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
    )
    return send_message

# Example usage:
# send("Test Subject", "Hello from Gmail API!", "recipient@example.com")