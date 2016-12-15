from django.conf.urls import include, url
import django.contrib.auth.views as django_auth

from music_player import views

urlpatterns = [
    # Misc
    url(r'^$', views.player, name='player'),
    # Login 
    url(r'^login$', django_auth.login,
     {'template_name':'soniferous/login.html'}, name='login'),
    # Password
    url(r'^password$', django_auth.password_change, {
      'template_name':'soniferous/password.html',
      'post_change_redirect':'soniferous:logout'
     }, name='password'),
    # Logout
    url(r'^logout$', django_auth.logout_then_login, name='logout'),
    # Songs
    url(r'^song(?:/(?P<pk>\d+))?/?$', views.SongView.as_view(), name='songs'),
    url(r'^song/(?P<pk>\d+)/audio$', views.SongView.audio),
    # Albums
    url(r'^album(?:/(?P<pk>\d+))?/?$',
     views.AlbumView.as_view(), name='albums'),
    # Artists
    url(r'^artist(?:/(?P<pk>\d+))?/?$',
     views.ArtistView.as_view(), name='artists'),
]
