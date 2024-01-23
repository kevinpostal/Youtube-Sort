from django.dispatch import receiver
from django.db.models.signals import post_save
from youtube_vault.models import YoutubePlaylist
from youtube_vault.tasks import import_youtube_playlist_videos

@receiver(post_save, sender=YoutubePlaylist, dispatch_uid='YoutubePlaylist_post_save')
def import_youtube_playlist_videos_signal(instance, created, **kwargs):
    if created:
        import_youtube_playlist_videos(instance.id)
