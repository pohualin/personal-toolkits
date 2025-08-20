import os
import re
import requests
import bs4

from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
from config.logging_config import setup_logging

logger = setup_logging()
load_dotenv()
TWITTER_DOWNLOAD_DIR=os.environ.get("TWITTER_DOWNLOAD_DIR")
if not TWITTER_DOWNLOAD_DIR:
    raise ValueError("TWITTER_DOWNLOAD_DIR environment variable is not set or empty.")

def download_video(url, channel_id, file_name) -> None:
    """Download a video from a URL into a filename.

    Args:
        url (str): The video URL to download
        file_name (str): The file name or path to save the video to.
    """

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    download_path = os.path.join(os.path.expanduser(TWITTER_DOWNLOAD_DIR), channel_id, file_name)
    os.makedirs(os.path.dirname(download_path), exist_ok=True)

    logger.info(f"Downloading video: {file_name}")
    with open(download_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()
    logger.info(f"Video downloaded successfully to {download_path}")


def download_twitter_video(url):
    """Extract the highest quality video url to download into a file

    Args:
        url (str): The twitter post URL to download from
    """

    api_url = f"https://twmate.com"
    response = requests.post(api_url, data={"page": url})
    data = bs4.BeautifulSoup(response.text, "html.parser")

    # Find the download link
    download_link_tag = data.find("a", class_="btn-dl")
    if not download_link_tag or not download_link_tag.get("href"):
        logger.error("Could not find download link on the page.")
        return

    highest_quality_url = download_link_tag.get("href")

    # Extract file name (fallback to default if not found)
    match = re.search(r"x\.com/([^/]+)/status/(\d+)", url)
    if match:
        channel_id = match.group(1)
        post_id = match.group(2)
        file_name = f"{channel_id}-{post_id}.mp4"
    else:
        logger.error("Could not extract file name from the Twitter URL.")
        return
    
    download_video(highest_quality_url, channel_id, file_name)