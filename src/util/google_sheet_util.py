import os
from src.config.logging_config import setup_logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

logger = setup_logging()

def get_sheet_service():
    """
    Returns an authenticated Google Sheets API service.
    """
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    
    if os.path.exists('sheet-token.json'):
        creds = Credentials.from_authorized_user_file('sheet-token.json', SCOPES)
        logger.info("Using existing sheet-token.json")
    else:
        creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "gmail_credentials.json")
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        logger.info("Saving new credentials to sheet-token.json")
        with open('sheet-token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build("sheets", "v4", credentials=creds)
    return service

def read_sheet(spreadsheet_id, range_name):
    """
    Reads values from a Google Sheet.
    """
    service = get_sheet_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return result.get("values", [])

def write_sheet(spreadsheet_id, range_name, values, creds_path="service_account.json"):
    """
    Writes values to a Google Sheet.
    """
    service = get_sheet_service(creds_path)
    body = {"values": values}
    sheet = service.spreadsheets()
    result = sheet.values().update(
        spreadsheetId=spreadsheet_id, range=range_name, valueInputOption="RAW", body=body
    ).execute()
    return result

# Example usage:
# rows = read_sheet("your_spreadsheet_id", "Sheet1!A1:C10")
# write_sheet("your_spreadsheet_id", "Sheet1!A1", [["Hello", "World"]])