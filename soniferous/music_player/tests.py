from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

import music_player.models as m

def create_test_songs():
  '''
  Provides a list of songs for testing
  '''
  song_info = [
   # First Artist
   ('Title1', '1:11', 1, 'Album1', 'Artist1', None),
   ('Title2', '2:22', 2, 'Album1', 'Artist1', None),
   ('Title1', '1:11', 1, 'Album2', 'Artist1', None),
   ('Title1', '2:22', 2, 'Album2', 'Artist1', None),
   # Second Artist
   ('Title1', '1:11', 1, 'Album1', 'Artist2', None),
   ('Title2', '2:22', 2, 'Album1', 'Artist2', None),
   ('Title1', '1:11', 1, 'Album2', 'Artist2', None),
   ('Title1', '2:22', 2, 'Album2', 'Artist2', None),
  ]
  songs = []
  for info in song_info:
    songs.append(m.create_song(*info))
  return songs

class GeneralTests(TestCase):
  
  def test_mutagen_import(self):
    '''Ensures Mutagen library is installed for ID3 support'''
    from mutagen.mp3 import EasyMP3


class ViewTests(TestCase):

  def user_page_contains(self, page_name, status, strings, kwargs={}):
    '''
    Checks if the page given has a specific status and contains values.
    Args:
     page_name - str, the page name to fetch and check against
     status - int, the page status response code
     strings - list(str), the list of strings to look for in the response
     kwargs - dict, the parameters to send with the response
    '''
    client = Client()
    client.login(username=self.user_credentials[0],\
     password=self.user_credentials[1])
    response = client.get(reverse(page_name, kwargs=kwargs))
    error = 'Page {0} failed tests.'.format(page_name)
    self.assertEqual(response.status_code, status, msg=error)
    for string in strings:
      self.assertTrue(string.encode() in response.content, msg=error)
  
  def setUp(self):
    '''Creates a basic user for testing'''
    self.user_credentials = ('user1', 'pass1')
    self.admin_credentials = ('admin', 'doge')
    User.objects.create_superuser(self.admin_credentials[0],\
     'admin@nobody.nowhere', self.admin_credentials[1])
    User.objects.create_user(self.user_credentials[0],\
     'user1@nobody.nowhere', self.user_credentials[1])
    create_test_songs()
  
  def test_pages(self):
    '''Ensures that each page is rendering the appropriate data'''
    page_params = [
     ('soniferous:player', 200, ['Soniferous']),
     ('soniferous:songs', 200, ['Title1', 'Album1', 'Artist1', 'Title2']),
     ('soniferous:songs', 200, ['Title1', 'Album1', 'Artist1'], {'pk':1}),
     ('soniferous:albums', 200, ['Album1', 'Album2']),
     ('soniferous:albums', 200, ['Title1', 'Album1'], {'pk':1}),
     ('soniferous:artists', 200, ['Artist1', 'Artist2']),
     ('soniferous:artists', 200, ['Title1', 'Artist1'], {'pk':1}),
    ]
    for params in page_params:
      self.user_page_contains(*params)

  def song_upload(self):
    '''
    Ensure that MP3 files uploaded can have their tags read and are served.
    If no tag data is present, "Unknown" is provided as the tag info.
    '''
    import os.path
    client = Client()
    client.login(username=self.admin_credentials[0],\
     password=self.admin_credentials[1])
    test_files = [
     ('test-data/FrankerZ.mp3', 'FrankerZ'),
     ('test-data/Kappa.mp3', 'Unknown'),
    ]
    for file_name, test_word in test_files:
      test_file = \
       os.path.join(os.path.dirname(__file__), file_name)
      with open(test_file, 'rb') as file_:
        response = client.post('/admin/music_player/song/add/',\
         {'music_file': file_}, follow=True)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(test_word.encode() in response.content,\
       msg='Song {0} info missing.'.format(file_name))
      self.user_page_contains('soniferous:songs', 200, [test_word])

  def song_files(self):
    '''
    Checks if the songs uploaded have corresponding files that are deleted
    along with the Song model.
    '''
    import os.path
    titles = ['FrankerZ', 'Unknown']
    for title in titles:
      new_song = m.Song.objects.get(title=title)
      url = new_song.music_file.url
      self.assertTrue(os.path.isfile(url), \
       msg='Song file {0} was not saved.'.format(url))
      new_song.delete()
      self.assertFalse(os.path.isfile(url), \
       msg='Song file {0} was not deleted.'.format(url))

  def test_song_upload_and_files(self):
    '''
    Tests song uploading and files in the specified order.
    '''
    self.song_upload()
    self.song_files()
    


class ModelTests(TestCase):

  def test_create_song_function(self):
    '''
    Ensures the create_song function adds the song to the appropriate artist
    and album model.
    '''
    songs = create_test_songs()
    # Check that songs were added to correct albums
    for i in range(0, 8, 2):
      self.assertEqual(songs[i].album, songs[i+1].album)
    for i in range(0, 4):
      self.assertNotEqual(songs[i].album, songs[i+4].album)
    # Check that songs were added to correct artists
    for i in range(1, 4):
      self.assertEqual(songs[0].album.artist, songs[i].album.artist)
      self.assertNotEqual(songs[0].album.artist, songs[i+4].album.artist)

  def test_json_formats(self):
    '''Ensure all models have correct fields when represented as JSON'''
    song = m.create_song('Title1', '1:11', 1, 'Album1', 'Artist1', None)
    # Artist
    for field in ('id', 'artist'):
      self.assertIn(field, song.album.artist.json_format())
    # Album
    for field in ('id', 'album', 'artist'):
      self.assertIn(field, song.album.json_format())
    # Song
    for field in ('id', 'title', 'artist', 'album', 'track_number', 'time'):
      self.assertIn(field, song.json_format())
    # Check json_list function
    obj = m.json_list('songs', [song,])
    self.assertEqual(obj['songs'][0], song.json_format())

  def test_delete_signals(self):
    '''
    Check that the signals to clean up database entries are active.
    An Album with no Songs should be deleted.
    An Artist with no Albums should be deleted.
    '''
    songs = create_test_songs()
    # Album cleanup
    self.assertEqual(m.Album.objects.count(), 4)
    songs[0].delete()
    self.assertEqual(m.Album.objects.count(), 4)
    songs[1].delete()
    self.assertEqual(m.Album.objects.count(), 3)
    # Artist cleanup
    self.assertEqual(m.Artist.objects.count(), 2)
    songs[2].delete()
    songs[3].delete()
    self.assertEqual(m.Artist.objects.count(), 1)

