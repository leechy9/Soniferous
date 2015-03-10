from django import forms
from django.core.exceptions import ValidationError
from music_player.models import Artist, Album, Song

class CreateSongForm(forms.ModelForm):
  '''
  Attempts to create a new song from the uploaded file by reading the ID3
  info embedded in it.
  '''
  class Meta:
    fields = ['music_file', 'title',]
    exclude = ['title',]
    model = Song

  def validate_id3_info(self):
    '''
    Raises a validation error if the information retreived from the file
    does not fit within the model constraints.
    '''
    if len(self.cleaned_data['title']) > \
     Song._meta.get_field('title').max_length:
      raise ValidationError('Invalid MP3. Title field too long.')
    if len(self.cleaned_data['album']) > \
     Album._meta.get_field('album').max_length:
      raise ValidationError('Invalid MP3. Album field too long.')
    if len(self.cleaned_data['artist']) > \
     Artist._meta.get_field('artist').max_length:
      raise ValidationError('Invalid MP3. Artist field too long.')
      

  def clean(self):
    '''
    Checks to see if the file provided has clean input.
    '''
    import re
    from mutagen.mp3 import EasyMP3
    from math import ceil
    super(CreateSongForm, self).clean()
    # Attempt to read id3 tag info
    try:
      # Read tags
      mp3_file = EasyMP3(self.files['music_file'].file.name)
      self.cleaned_data['title'] = 'Unknown'
      self.cleaned_data['album'] = 'Unknown'
      self.cleaned_data['artist'] = 'Unknown'
      self.cleaned_data['track_number'] = 0
      if mp3_file.tags:
        if 'title' in mp3_file.tags:
          self.cleaned_data['title'] = mp3_file.tags['title'][0]
        if 'album' in mp3_file.tags:
          self.cleaned_data['album'] = mp3_file.tags['album'][0]
        if 'artist' in mp3_file.tags:
          self.cleaned_data['artist'] = mp3_file.tags['artist'][0]
        if 'tracknumber' in mp3_file.tags:
          str_track = mp3_file.tags['tracknumber'][0]
          self.cleaned_data['track_number'] = \
           int(re.match(r'(\d+)', str_track).groups(0)[0])
      # Calculate time string
      seconds = ceil(mp3_file.info.length)
      self.cleaned_data['time'] = \
       '{0:d}:{1:02d}'.format(seconds // 60, seconds % 60)
    # Invalid file
    except Exception as ex:
      raise ValidationError(\
       'Invalid File. The file provided does not appear to be an MP3.')
    self.validate_id3_info()
    return self.cleaned_data

  def save(self, commit=True):
    '''
    Saves the model to the database.
    Creates additional an Artist and Album if necessary.
    '''
    db_art, created = Artist.objects.get_or_create(\
     artist=self.cleaned_data['artist'])
    db_alb, created = Album.objects.get_or_create(\
     artist=db_art, album=self.cleaned_data['album'])
    self.instance.album = db_alb
    self.instance.track_number = self.cleaned_data['track_number']
    self.instance.title = self.cleaned_data['title']
    self.instance.time = self.cleaned_data['time']
    self.instance.full_clean()
    self.instance.save()
    return super(CreateSongForm, self).save(commit=commit)


class ModifySongForm(forms.ModelForm):
  '''
  Allows for the modification of a Song. Hides the database structure from the
  user by presenting proxy text fields instead of foreign keys.
  '''
  album_name = forms.CharField(label='Album', max_length=128, required=True)
  artist_name = forms.CharField(label='Artist', max_length=128, required=True)

  class Meta:
    fields = ['title', 'album_name', 'artist_name', 'track_number',]
    model = Song

  def __init__(self, *args, **kwargs):
    '''
    Sets the initial values for the proxy text fields.
    '''
    super(ModifySongForm, self).__init__(*args, **kwargs)
    if self.instance.pk:
      self.fields['album_name'].initial = self.instance.album.album
      self.fields['artist_name'].initial = self.instance.album.artist.artist

  def save(self, commit=True):
    '''
    Saves the model to the database.
    Creates additional an Artist and Album if necessary.
    '''
    if self.instance.pk:
      album = self.cleaned_data['album_name']
      artist = self.cleaned_data['artist_name']
    db_art, created = Artist.objects.get_or_create(artist=artist)
    db_alb, created = Album.objects.get_or_create(artist=db_art, album=album)
    self.instance.album = db_alb
    self.instance.save()
    return super(ModifySongForm, self).save(commit=commit)

