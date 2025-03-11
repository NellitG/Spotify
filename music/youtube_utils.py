from googleapiclient.discovery import build

# Replace this with your actual API Key
YOUTUBE_API_KEY = "Youtube API Key"

def search_youtube(song_name):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        q=song_name,
        part="id,snippet",
        maxResults=1,
        type="video"
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        video_id = response["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    return None

# Example Usage
print(search_youtube("shape of you by ed sheeran"))
