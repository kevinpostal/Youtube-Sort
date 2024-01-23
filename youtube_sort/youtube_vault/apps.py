from django.apps import AppConfig


class YoutubeVaultConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "youtube_vault"

    def ready(self):
        import youtube_vault.signals