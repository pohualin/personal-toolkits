import os
import requests
import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from src.config.auth import get_youtube_creds
from src.config.logging_config import setup_logging

log = setup_logging()
ytt_api = YouTubeTranscriptApi()

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Set this in your .env file

if not YOUTUBE_API_KEY:
    raise EnvironmentError("YOUTUBE_API_KEY is not set. Please add it to your .env file.")

def videos_by_channel_id(channel_id, last_x_days=7):
    """
    Returns a list of videos published by the channel in the last_x_days.
    """
    publish_after = (datetime.datetime.utcnow() - datetime.timedelta(days=last_x_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"key={YOUTUBE_API_KEY}&channelId={channel_id}&part=snippet,id&order=date"
        f"&publishedAfter={publish_after}"
    )
    resp = requests.get(search_url)
    videos = resp.json().get("items", [])
    recent_videos = []
    for v in videos:
        if v["id"]["kind"] != "youtube#video":
            continue
        published = v["snippet"]["publishedAt"]
        recent_videos.append({
            "title": v["snippet"]["title"],
            "video_id": v["id"]["videoId"],
            "published": published,
        })
    return recent_videos

def videos_by_handle(handle, last_x_days=7):
    # Get channel ID from handle
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={YOUTUBE_API_KEY}"
    log.info(f"Requesting channel ID with URL: {url}")
    resp = requests.get(url)
    data = resp.json()
    if not data.get("items"):
        raise ValueError(f"Channel not found for handle: {handle}")
    channel_id = data["items"][0]["id"]
    return videos_by_channel_id(channel_id, last_x_days)

def get_transcript(video_id):
    """
    Fetches the transcript for a given YouTube video ID using youtube-transcript-api.
    Returns the transcript text as a single string, or None if unavailable.
    """
    try:
        transcript = ytt_api.fetch(video_id)
        return " ".join(snippet.text for snippet in transcript)
    except Exception as e:
        print(f"Transcript not available for video {video_id}: {e}")
        return

def get_subscribed_channels():
    """
    Returns a list of channels the user is subscribed to.
    Requires OAuth token with YouTube scope.
    """
    creds = get_youtube_creds()
    service = build("youtube", "v3", credentials=creds)

    channels = []
    request = service.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response.get("items", []):
            channel_title = item["snippet"]["title"]
            channel_id = item["snippet"]["resourceId"]["channelId"]
            last_video = get_last_video(channel_id)
            last_published = last_video["published"] if last_video else None
            channels.append({
                "title": channel_title,
                "id": channel_id,
                "last_published": last_published
            })
        request = service.subscriptions().list_next(request, response)
    return channels


def get_last_video(channel_id):
    videos = videos_by_channel_id(channel_id, 365)
    if not videos:
        return None
    return videos[0]