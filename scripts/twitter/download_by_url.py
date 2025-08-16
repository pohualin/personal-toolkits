import sys
import os
import re
import requests
import bs4
from tqdm import tqdm
from pathlib import Path
from src.config.logging_config import setup_logging

logger = setup_logging()

def download_video(url, file_name) -> None:
    """Download a video from a URL into a filename.

    Args:
        url (str): The video URL to download
        file_name (str): The file name or path to save the video to.
    """

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    download_path = os.path.join(Path.home(), "Downloads", file_name)

    with open(download_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()
    logger.info("Video downloaded successfully!")  # Use logger instead of print


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
    file_name_tag = data.find("div", class_="leading-tight")
    if file_name_tag:
        p_tag = file_name_tag.find("p", class_="m-2")
        if p_tag and p_tag.text:
            file_name = re.sub(r"[^a-zA-Z0-9]+", " ", p_tag.text).strip() + ".mp4"
        else:
            file_name = "twitter_video.mp4"
    else:
        file_name = "twitter_video.mp4"

    logger.info(f"Downloading video: {file_name} from {highest_quality_url}")
    # download_video(highest_quality_url, file_name)


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
