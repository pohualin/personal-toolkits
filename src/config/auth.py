import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GSHEET_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def refresh_creds_if_needed(creds, token_path, scopes, creds_path):
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        elif not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    except RefreshError:
        # Handle invalid_grant by forcing a new OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_gmail_creds():
    creds_path = "gmail_credentials.json"
    token_path = "token.json"
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)
    creds = refresh_creds_if_needed(creds, token_path, GMAIL_SCOPES, creds_path)
    return creds

def get_gsheet_creds():
    creds_path = "gmail_credentials.json"
    token_path = "sheet-token.json"
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GSHEET_SCOPES)
    creds = refresh_creds_if_needed(creds, token_path, GSHEET_SCOPES, creds_path)
    return creds

def get_youtube_creds():
    creds_path = "gmail_credentials.json"
    token_path = "youtube-token.json"
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, YOUTUBE_SCOPES)
    creds = refresh_creds_if_needed(creds, token_path, YOUTUBE_SCOPES, creds_path)
    return creds