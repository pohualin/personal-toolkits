import sys
from pytube import Channel, YouTube
from src.config.logging_config import setup_logging

logger = setup_logging()

if len(sys.argv) < 2:
    logger.error("Usage: python get_by_channel.py <CHANNEL_NAME>")
    sys.exit(1)

channel_name = sys.argv[1]
channel_url = f"https://www.youtube.com/c/{channel_name}"
channel = Channel(channel_url)

logger.info(f"Fetching videos from channel: {channel.channel_name} ({channel_url})")
logger.info(f"Channel ID: {channel.channel_id}")
logger.info(f"Channel name: {channel.channel_name}")
logger.info(f"Channel URL: {channel_url}")
logger.info(f"Channel video URLs: {list(channel.videos_url)}")

# Get the last 10 video URLs
latest_videos = list(channel.videos_url)[:10]

logger.info(f"Last 10 videos from channel '{channel_name}':")
logger.info(f"Total videos found: {len(channel.videos_url)}")
for idx, video_url in enumerate(latest_videos, 1):
    yt = YouTube(video_url)
    title = yt.title
    publish_date = yt.publish_date.strftime("%Y-%m-%d %H:%M:%S") if yt.publish_date else "Unknown"
    logger.info(f"{idx}: {title} | Published: {publish_date} | URL: {video_url}")