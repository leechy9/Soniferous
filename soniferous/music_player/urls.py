from django.conf.urls import patterns, include, url

from music_player import views

urlpatterns = patterns('',
    # Misc
    url(r'^$', views.player, name='player'),
    # Login 
    url(r'^login$', 'django.contrib.auth.views.login', \
     {'template_name':'soniferous/login.html'}, name='login'),
    # Password
    url(r'^password$',
     'django.contrib.auth.views.password_change',\
     {
      'template_name':'soniferous/password.html',\
      'post_change_redirect':'soniferous:logout'
     },\
     name='password'),
    # Logout
    url(r'^logout$',\
     'django.contrib.auth.views.logout_then_login',\
     name='logout'),
    # Songs
    url(r'^song(?:/(?P<pk>\d+))?/?$', views.SongView.as_view(), name='songs'),
    url(r'^song/(?P<pk>\d+)/audio$', views.SongView.audio),
    # Albums
    url(r'^album(?:/(?P<pk>\d+))?/?$',
     views.AlbumView.as_view(), name='albums'),
    # Artists
    url(r'^artist(?:/(?P<pk>\d+))?/?$',
     views.ArtistView.as_view(), name='artists'),
)
