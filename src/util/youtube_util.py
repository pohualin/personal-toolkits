import os
import requests
import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv


ytt_api = YouTubeTranscriptApi()

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Set this in your .env file

if not YOUTUBE_API_KEY:
    raise EnvironmentError("YOUTUBE_API_KEY is not set. Please add it to your .env file.")

def search_youtube(handle, max_results=5):
    # Get channel ID from handle
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={YOUTUBE_API_KEY}"
    print(f"Requesting channel ID with URL: {url}")
    resp = requests.get(url)
    data = resp.json()
    if not data.get("items"):
        raise ValueError(f"Channel not found for handle: {handle}")
    channel_id = data["items"][0]["id"]

    # Get videos from channel
    publish_after = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Publishing after: {publish_after}")
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"key={YOUTUBE_API_KEY}&channelId={channel_id}&part=snippet,id&order=date"
        f"&publishedAfter={publish_after}"
    )
    resp = requests.get(search_url)
    videos = resp.json().get("items", [])
    print(f"Found {len(videos)} videos in the last 7 days.")
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