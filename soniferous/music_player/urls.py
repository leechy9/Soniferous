from django.conf.urls import patterns, include, url

from music_player import views

urlpatterns = patterns('',
    # Misc
    url(r'^$', views.player, name='player'),
    url(r'^search/(?P<query>.+)$', views.search_all, name='search'),
    # Authentication
    url(r'^login$', 'django.contrib.auth.views.login', \
     {'template_name':'soniferous/login.html'}, name='login'),
    url(r'^password$',
     'django.contrib.auth.views.password_change',\
     {
      'template_name':'soniferous/password.html',\
      'post_change_redirect':'soniferous:logout'
     },\
     name='password'),
    url(r'^logout$',\
      'django.contrib.auth.views.logout_then_login',\
      name='logout'),
    # Songs
    url(r'^song/$', views.song_list, name='song_list'),
    url(r'^song/(?P<pk>\d+)$', views.song_info, name='song_info'),
    url(r'^song/(?P<pk>\d+)/audio$', views.song_serve, name='song_serve'),
    url(r'^song/(?P<pk>\d+)/delete$', views.song_delete, name='song_delete'),
    url(r'^song/search/(?P<query>.+)$', views.song_search, name='song_search'),
    # Albums
    url(r'^album/$', views.album_list, name='album_list'),
    url(r'^album/(?P<pk>\d+)/songs$', views.album_songs, name='album_songs'),
    url(r'^album/search/(?P<query>.+)$', views.album_search, name='album_search'),
    # Artists
    url(r'^artist/$', views.artist_list, name='artist_list'),
    url(r'^artist/(?P<pk>\d+)/albums$', views.artist_albums, name='artist_albums'),
    url(r'^artist/(?P<pk>\d+)/songs$', views.artist_songs, name='artist_songs'),
    url(r'^artist/search/(?P<query>.+)$', views.artist_search, name='artist_search'),
)
