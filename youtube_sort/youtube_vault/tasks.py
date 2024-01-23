from django.contrib.auth import get_user_model
from google.auth.transport.requests import Request as GoogleAuthTransportRequest

# from google.oauth2.credentials import Credentials as GoogleOauth2Credentials
from googleapiclient.discovery import build as googleapiclient_discovery_build
from youtube_vault.models import YoutubePlaylist, YoutubeVideo
from youtube_auth.models import YoutubeCredential

User = get_user_model()

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def import_youtube_playlists(youtube_credential_id):
    """import_youtube_playlists.

    Args:
        user_id (_type_): _description_.

    """

    youtube_credential_obj = YoutubeCredential.objects.get(id=youtube_credential_id)
    youtube = googleapiclient_discovery_build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=youtube_credential_obj.get_credentials,
    )
    # import ipdb; ipdb.set_trace()
    try:
        results = youtube.playlists().list(mine=True, part="snippet").execute()
    except Exception:
        request = GoogleAuthTransportRequest()
        youtube_credential_obj.credentials.refresh(request)
        youtube = googleapiclient_discovery_build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=youtube_credential_obj,
        )
        results = youtube.playlists().list(mine=True, part="snippet").execute()

    return_data = []


        
    for item in results["items"]:
        title = item.get("snippet", {}).get("title")
        playlist_id = item.get("id")
        description = item.get("snippet", {}).get("description")
        image_url = (
            item.get("snippet", {})
            .get("thumbnails", {})
            .get("default", {})
            .get("url", "")
        )
        obj_dict = {
            "title": title,
            "description": description,
            "youtube_credential": youtube_credential_obj,
            "image_url": image_url,
        }
        obj, created = YoutubePlaylist.objects.update_or_create(
            youtube_credential=youtube_credential_obj,
            yt_playlist_id=playlist_id,
            defaults=obj_dict,
        )
        return_data.append((obj.id, created))

    obj_dict = {
        "title": "Liked Videos",
        "description": "Liked Videos",
        "youtube_credential": youtube_credential_obj,
        "image_url": "BLANK",
    }
    obj, created = YoutubePlaylist.objects.update_or_create(
        yt_playlist_id="LL",
        youtube_credential=youtube_credential_obj,
        defaults=obj_dict,
    )
    return_data.append((obj.id, created))

    return return_data


def import_youtube_playlist_videos(playlist_pk):
    """_summary_

    Args:
        playlist_pk (_type_): _description_

    Returns:
        _type_: _description_
    """
    playlist_obj = YoutubePlaylist.objects.get(pk=playlist_pk)
    
    youtube = googleapiclient_discovery_build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=playlist_obj.youtube_credential.get_credentials,
    )
    
    
    try:
        results = youtube.playlistItems().list(
            playlistId=playlist_obj.yt_playlist_id,
            part="snippet",
        ).execute()
    except Exception:
        request = GoogleAuthTransportRequest()
        playlist_obj.credentials.refresh(request)
        youtube = googleapiclient_discovery_build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=playlist_obj.youtube_credential.get_credentials,
        )
        results = youtube.playlistItems().list(
            playlistId=playlist_obj.yt_playlist_id,
            part="snippet",
            maxResults=50,
        ).execute()
    
    token = results.get("nextPageToken")
    return_data = []
    
    while token is not None:
        for item in results["items"]:
            yid = item.get("snippet", {}).get("resourceId", {}).get("videoId")
            title = item.get("snippet", {}).get("title")
            image_url = item.get("snippet", {}).get("thumbnails", {}).get("default",
                                                                          {}).get("url", "")
            obj_dict = {
                "title": title,
                "youtube_credential": playlist_obj.youtube_credential,
                "playlist": playlist_obj,
                "image_url": image_url,
            }
            obj, created = YoutubeVideo.objects.update_or_create(
                yid=yid,
                youtube_credential=playlist_obj.youtube_credential,
                defaults=obj_dict,
            )
            return_data.append((obj.yid, created))

        results = youtube.playlistItems().list(
            playlistId=playlist_obj.yt_playlist_id, part="snippet", maxResults=50, pageToken=token
        ).execute()
        token = results.get("nextPageToken", None)
        
    return return_data