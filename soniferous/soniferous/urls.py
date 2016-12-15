from django.conf.urls import include, url
from django.contrib import admin

from music_player.urls import urlpatterns as music_player_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(music_player_urls, namespace='soniferous')),
]
