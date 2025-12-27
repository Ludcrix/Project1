# youtube/collector.py

from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY


def get_video_info(video_id):
    """
    Récupère les infos principales d'une vidéo YouTube
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY manquante dans config.py")

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    )

    response = request.execute()

    if not response["items"]:
        return None

    item = response["items"][0]

    return {
        "video_id": video_id,
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "published_at": item["snippet"]["publishedAt"],
        "duration": item["contentDetails"]["duration"],
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "comments": int(item["statistics"].get("commentCount", 0)),
    }


def get_channel_id_by_name(channel_name):
    """
    Trouve l'ID d'une chaîne à partir de son nom
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )

    response = request.execute()

    items = response.get("items", [])
    if not items:
        return None

    return items[0]["id"]["channelId"]

def get_channel_videos(channel_id, max_results=10):
    """
    Récupère les dernières vidéos d'une chaîne YouTube
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY manquante dans config.py")

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )

    response = request.execute()

    video_ids = []
    for item in response.get("items", []):
        video_ids.append(item["id"]["videoId"])

    return video_ids

