from django.contrib import admin
from django.urls import path
from youtube_vault.models import YoutubePlaylist, YoutubeVideo
from youtube_vault.tasks import import_youtube_playlists
from django.utils.html import format_html


class YoutubeVideoAdmin(admin.ModelAdmin):
    list_display = ["thumbnail", "title",]
    search_fields = ["title", "artist", "track", "title"]
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 130px; \
                           height: 100px"/>'.format(obj.image_url))
        return ""



class YoutubePlaylistAdmin(admin.ModelAdmin):
    list_display = ["yt_playlist_id", "title", "description", "youtube_credential"]
    change_list_template = "admin/youtube_vault/YoutubePlaylist/change_list.html"

    def get_urls(self):
        urls = super(YoutubePlaylistAdmin, self).get_urls()
        my_urls = [
            path(
                r"^import_youtube_playlists/$",
                self.import_youtube_playlists,
                name="import_youtube_playlists",
            )
        ]
        return my_urls + urls

    # def changelist_view(self, request, extra_context=None):
    #     # import ipdb; ipdb.set_trace()

    #     return super().changelist_view(
    #         request,
    #         extra_context=extra_context,
    #     )

    def import_youtube_playlists(self, request):
        import_youtube_playlists(request.user.id)
        return super().changelist_view(request)


admin.site.register(YoutubeVideo, YoutubeVideoAdmin)
admin.site.register(YoutubePlaylist, YoutubePlaylistAdmin)
