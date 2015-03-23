from django.contrib import admin
from music_player.forms import CreateSongForm, ModifySongForm
from music_player.models import Album, Artist, Song

class SongAdmin(admin.ModelAdmin):
  '''
  New model: Displays an upload field for MP3 files.
  Change model: Displays text fields to modify existing data.
  '''
  list_display = ('title', 'album_', 'artist_',)
  ordering = ('album__artist__artist', 'album__album', 'track_number', 'title',)
  def album_(self, song):
    return song.album.album
  def artist_(self, song):
    return song.album.artist.artist
  def get_form(self, request, obj=None, **kwargs):
    if obj:
      self.form = ModifySongForm
    else:
      self.form = CreateSongForm 
    return super(SongAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Song, SongAdmin)
