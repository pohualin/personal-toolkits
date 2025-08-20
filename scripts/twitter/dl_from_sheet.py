import sys
from src.config.logging_config import setup_logging
from src.util.twitter_downloader import download_twitter_video
from src.util.google_sheet_util import read_sheet

logger = setup_logging()

def main():
    # if len(sys.argv) < 3:
    #     logger.error("Usage: python dl_from_sheet.py <spreadsheet_id> <range>")
    #     sys.exit(1)

    # spreadsheet_id = sys.argv[1]
    # range_name = sys.argv[2]

    try:
        urls = read_sheet("1h0K5yDn0oPijTr7axw__LYzZoHhGt4FE2PE4M5h2WJs", 'Sheet1!A1:A10')  # Replace with actual spreadsheet_id and range_name
    except Exception as e:
        logger.error(f"Failed to read sheet: {e}")
        sys.exit(1)

    for row in urls:
        if row:
            url = row[0]
            logger.info(f"Downloading video from: {url}")
            download_twitter_video(url)

if __name__ == "__main__":
    main()