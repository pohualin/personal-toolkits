import sys
from src.config.logging_config import setup_logging
from src.util.twitter_downloader import download_twitter_video

logger = setup_logging()

if len(sys.argv) < 2:
    logger.error(
        "Please provide the Twitter video URL as a command line argument.\nEg: python twitter_downloader.py <URL>"
    )
else:
    url = sys.argv[1]
    if url:
        download_twitter_video(url)
    else:
        logger.error("Invalid Twitter video URL provided.")
