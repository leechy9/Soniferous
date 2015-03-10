from django.db import models

class Artist(models.Model):
  '''Represents a musical artist'''
  artist = models.CharField(max_length=128, unique=True, db_index=True)
  def __str__(self):
    return str(self.pk) + ' - ' + self.artist
  def json_format(self):
    '''
    Converts the Artist to a dictionary that includes important information.
    Return: The dictionary containing this Artist's information.
     { artists: [{ id: int, artist: str }, ...] }
    '''
    return { 'id': self.pk, 'artist': self.artist, }


class Album(models.Model):
  '''Represents an album that belongs to an artist '''
  album = models.CharField(max_length=128, db_index=True)
  artist = models.ForeignKey(Artist, db_index=True, null=False)
  def __str__(self):
    return ' - '.join((str(self.pk), self.album, self.artist.artist))
  class Meta:
    unique_together = ('album', 'artist')
  def json_format(self):
    '''
    Converts the Album to a dictionary that includes important information.
    Includes some information from foreign key fields.
    Return: The dictionary containing this Album's information.
     { albums: [{ id: int, album: str, artist: str }, ...] }
    '''
    album = {
     'id': self.pk,
     'album': self.album,
     'artist': self.artist.artist,
    }
    return album


class Song(models.Model):
  '''Represents a song's info and its file.'''
  title = models.CharField(max_length=128, db_index=True)
  track_number = models.IntegerField(db_index=True)
  album = models.ForeignKey(Album, db_index=True, null=False)
  time = models.CharField(max_length=16)
  music_file = models.FileField(upload_to='uploaded_music')
  def __str__(self):
    return ' - '.join(\
     (str(self.pk), self.title, self.album.album, self.album.artist.artist))
  def json_format(self):
    '''
    Converts a single Song model to a dictionary with foreign key info added.
    Args: song - Song, the Song model to convert.
    Return: dict, the dict representing the song.
     { artists: [{ id: int, title: str, track_number: int,
      time: str, album: str, artist: str }, ...] }
    '''
    song = {
     'id': self.pk,
     'title': self.title,
     'track_number': self.track_number,
     'time': self.time,
     'album': self.album.album,
     'artist': self.album.artist.artist,
    }
    return song


def json_list(label, models):
  '''
  Converts models to json-objects (dictionaries) using the json_format method,
  and stores them in a list with the specified label.
  Args:
   label - string, the name to assign to the list.
   models - resultset, the models to convert.
  Return: list(dict), the list of dictionary-formatted models.
  '''
  results = []
  for model in models:
    results.append(model.json_format())
  return { label: results }

def create_song(title, time, track_number, album, artist, music_file):
  '''
  Creates a song in the database. Ensures that all dependencies are met
  first (i.e. artist and album) if they do not already exist.
  Args:
   title - str, title of the song.
   time - str, length of song duration. MM:SS format.
   track_number - int, the track number of the song.
   album - str, the name of the album this song belongs to.
   artist - str, the name of the artist this song belongs to.
   music_file - file, the file containing the song.
  '''
  db_art, created = Artist.objects.get_or_create(artist=artist)
  db_alb, created = Album.objects.get_or_create(album=album, artist=db_art)
  # Create song
  song = Song(\
   title=title,\
   track_number=track_number,\
   album=db_alb,\
   time=time,\
   music_file=music_file,\
  )
  song.save()
  return song

