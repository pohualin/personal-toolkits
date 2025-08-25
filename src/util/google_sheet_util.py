import os
from src.config.logging_config import setup_logging
from googleapiclient.discovery import build
from src.config.auth import get_gsheet_creds

logger = setup_logging()

def get_sheet_service():
    """
    Returns an authenticated Google Sheets API service.
    """
    creds = get_gsheet_creds()
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