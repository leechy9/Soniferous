import os.path
import re

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View

from music_player.models import Song, Album, Artist, json_list

# Left in scope here so that it is compiled at module load time.
byte_range_re = re.compile(r'bytes=(\d+)-(\d+)?')
# Used by multiple functions/methods below.
song_order = ('album__artist__artist', 'album__album', 'track_number')

def file_range_generator(field_file, block_size, start, stop):
  '''
  A generator capable of returning a portion of a fieldfile.
  Args:
   field_file - fieldfile, the file to read data from
   block_size - int, the size of the buffer to serve
   start - int, the first byte served
   stop - int, the last byte served
  Yield: The current chunk of bytes to serve
  '''
  field_file.seek(start)
  remaining = stop - start + 1
  while remaining > 0:
    if remaining < block_size:
      block_size = remaining
    yield field_file.read(block_size)
    remaining -= block_size

# Misc Views
@login_required
def player(request):
  '''Displays a basic music player view with controls.'''
  songs = Song.objects.select_related().all().order_by(*song_order)
  return render(request, 'soniferous/player.html', {'songs':songs})

# Songs 
class SongView(View):
  '''
  Provides a REST interface for accessing songs.
  '''
  @method_decorator(login_required)
  def get(self, request, pk=None):
    '''
    Displays a single song in json format if pk is provided.
    Otherwise, displays a json listing of all songs.
    '''
    if pk:
      song = get_object_or_404(Song.objects.select_related(), pk=pk)
      return JsonResponse(song.json_format())
    else:
      songs = Song.objects.select_related().all().order_by(*song_order)
      return JsonResponse(json_list('songs', songs))

  @method_decorator(staff_member_required)
  def delete(self, request, pk):
    '''
    Deletes the given song. Any associated artists or albums that are no
    longer used by any other model are automatically deleted. Requires
    that the user be classified as staff.
    '''
    if not pk:
      return HttpResponse(status=404)
    song = get_object_or_404(Song, pk=pk)
    song.delete()
    return HttpResponse()

  @login_required
  def audio(request, pk):
    '''
    Serves a song's file to the user. Supports HTTP range requests so that
    partial files can be sent to the user instead of a bulk transfer.
    '''
    block_size = 4096
    song = get_object_or_404(Song, pk=pk)
    song.music_file.open()
    # Attempt to serve partial ranges if necessary
    if 'HTTP_RANGE' in request.META:
      match = byte_range_re.match(request.META['HTTP_RANGE'])
      if not match:
        return HttpResponse(status=416)
      ranges = match.groups()
      start_range = int(ranges[0])
      if ranges[1]:
        stop_range = int(ranges[1])
      else:
        stop_range = song.music_file.size - 1
      # Valid ranges get data served
      if len(ranges) == 2 and (0 <= stop_range < song.music_file.size):
        file_wrapper = file_range_generator(\
         song.music_file, block_size, start_range, stop_range)
        response = HttpResponse(file_wrapper, status=206)
        response['Content-Length'] = str(stop_range - start_range + 1)
        response['Content-Range'] = 'bytes {0}-{1}/{2}'.format(\
        start_range, stop_range, song.music_file.size)
      # Immediately exit on invalid range
      else:
        return HttpResponse(status=416)
    # Standard file serving
    else:
      file_wrapper = iter(lambda: song.music_file.read(block_size), b'')
      response = HttpResponse(file_wrapper)
      response['Content-Length'] = str(song.music_file.size)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Type'] = 'audio/mpeg'
    response['Content-Disposition'] = \
     'attachment; filename="{}"'.format(os.path.basename(song.music_file.name))
    return response


# Albums
class AlbumView(View):
  '''Provides REST interface for retrieving album info.'''
  @method_decorator(login_required)
  def get(self, request, pk=None):
    '''
    If pk is provided, look up a specific album's songs.
    Otherwise, provide a listing of all albums.
    '''
    if pk:
      songs = Song.objects.select_related()\
       .filter(album=pk).order_by(*song_order)
      return JsonResponse(json_list('songs', songs))
    else:
      albums = Album.objects.select_related()\
       .all().order_by('artist__artist', 'album')
      return JsonResponse(json_list('albums', albums))

# Artists
class ArtistView(View):
  '''Provides REST interface for retrieving artist info.'''
  @method_decorator(login_required)
  def get(self, request, pk=None):
    '''
    If pk is provided, displays a listing of all songs for the given Artist.
    Otherwise, displays a json listing of all artists.
    '''
    if pk:
      songs = Song.objects.select_related()\
       .filter(album__artist=pk).order_by(*song_order)
      return JsonResponse(json_list('songs', songs))
    else:
      artists = Artist.objects.all().order_by('artist')
      return JsonResponse(json_list('artists', artists))

