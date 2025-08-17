import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

def send_gmail(subject, body, to):
    """
    Send an email using Gmail API.

    Args:
        subject (str): Email subject
        body (str): Email body
        to (str): Recipient email address
        creds_path (str): Path to OAuth token.json
    """
    # Load credentials
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "gmail_credentials.json")
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # print(f"Loaded credentials: {creds.to_json()}")
    
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
# send_gmail("Test Subject", "Hello from Gmail API!", "recipient@example.com")