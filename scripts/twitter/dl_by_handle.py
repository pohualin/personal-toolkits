import snscrape.modules.twitter as sntwitter
from src.config.logging_config import setup_logging

logger = setup_logging()

def get_latest_media(handle, limit=10):
    media_urls = []
    for tweet in sntwitter.TwitterUserScraper(handle).get_items():
        if hasattr(tweet, "media") and tweet.media:
            for media in tweet.media:
                if hasattr(media, "fullUrl"):
                    media_urls.append(media.fullUrl)
        if len(media_urls) >= limit:
            break
    return media_urls

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logger.error("Usage: python dl_by_handle.py <twitter_handle>")
        sys.exit(1)
    handle = sys.argv[1]
    media = get_latest_media(handle)
    for url in media:
        logger.info(f"Media URL: {url}")