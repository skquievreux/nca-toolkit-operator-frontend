import feedparser
import logging

logger = logging.getLogger(__name__)

RSS_URL = "https://acidmonk.unlock-your-song.de/api/rss/racket-voice"

def get_rss_items(limit=10):
    """
    Parses the RSS feed and returns a list of items.
    """
    try:
        feed = feedparser.parse(RSS_URL)
        items = []
        for entry in feed.entries[:limit]:
            audio_url = None
            if hasattr(entry, 'enclosures'):
                for enc in entry.enclosures:
                    if enc.type == 'audio/mpeg' or enc.url.endswith('.mp3'):
                        audio_url = enc.url
                        break
            
            image_url = None
            if hasattr(entry, 'media_content'):
                image_url = entry.media_content[0]['url']
            
            if not image_url and 'description' in entry:
                import re
                img_match = re.search(r'<img src="(.*?)"', entry.description)
                if img_match:
                    image_url = img_match.group(1)

            items.append({
                "title": entry.title,
                "image_url": image_url,
                "audio_url": audio_url,
                "link": entry.link,
                "id": entry.id if hasattr(entry, 'id') else entry.link
            })
        return items
    except Exception as e:
        logger.error(f"Error parsing RSS items: {e}")
        return []

def get_latest_rss_item():
    """
    Parses the RSS feed and returns the latest item with image and audio URLs.
    """
    try:
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            return None
        
        latest = feed.entries[0]
        
        # Audio URL extraction (from enclosure)
        audio_url = None
        if hasattr(latest, 'enclosures'):
            for enc in latest.enclosures:
                if enc.type == 'audio/mpeg' or enc.url.endswith('.mp3'):
                    audio_url = enc.url
                    break
        
        # Image URL extraction (from media:content or description)
        image_url = None
        if hasattr(latest, 'media_content'):
            image_url = latest.media_content[0]['url']
        elif 'content' in latest: # Fallback for some parsers
             pass
        
        # description fallback for image if not in media_content
        if not image_url and 'description' in latest:
            import re
            img_match = re.search(r'<img src="(.*?)"', latest.description)
            if img_match:
                image_url = img_match.group(1)

        return {
            "title": latest.title,
            "image_url": image_url,
            "audio_url": audio_url,
            "link": latest.link
        }
    except Exception as e:
        logger.error(f"Error parsing RSS: {e}")
        return None

if __name__ == "__main__":
    # Quick CLI test
    item = get_latest_rss_item()
    print(item)
