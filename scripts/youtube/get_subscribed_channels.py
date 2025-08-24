from src.util.youtube_util import get_subscribed_channels
from src.config.logging_config import setup_logging

log = setup_logging()

def main():
    channels = get_subscribed_channels()
    log.info("Subscribed channels:")
    for ch in channels:
        log.info(f"{ch['title']} ({ch['id']}) - Last published: {ch.get('last_published', 'N/A')})")

if __name__ == "__main__":
    main()