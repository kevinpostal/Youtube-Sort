from django.db import models
from youtube_auth.models import YoutubeCredential
from django.utils.html import mark_safe

class YoutubePlaylist(models.Model):
    youtube_credential = models.ForeignKey(YoutubeCredential, on_delete=models.CASCADE)
    yt_playlist_id = models.CharField(max_length=255, unique=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=255, blank=True, null=True)


class YoutubeVideo(models.Model):
    youtube_credential = models.ForeignKey(YoutubeCredential, on_delete=models.CASCADE)
    playlist = models.ForeignKey(YoutubePlaylist, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, null=True)
    track = models.CharField(max_length=255, blank=True, null=True)
    yid = models.CharField(max_length=255, unique=False)
    image_url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def url(self) -> str:
        """Return Youtube url.

        Returns:
            str: Youtube Url.

        """
        return "https://www.youtube.com/watch?v={0}".format(self.yid)
