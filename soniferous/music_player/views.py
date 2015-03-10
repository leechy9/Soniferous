import os.path
import re

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from music_player.models import Song, Album, Artist, json_list

########################
# Utilities
########################
song_order = ('album__artist__artist', 'album__album', 'track_number')

byte_range_re = re.compile(r'bytes=(\d+)-(\d+)?')

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
  position = start
  while(start <= position <= stop):
    if position + block_size <= stop:
      chunk_size = block_size
    else:
      chunk_size = stop - position + 1
    position += chunk_size
    yield field_file.read(chunk_size)

########################
# Misc Views
########################

@login_required
def player(request):
  '''Displays a basic music player view with controls.'''
  songs = Song.objects.select_related().all().order_by(*song_order)
  return render(request, 'soniferous/player.html', {'songs':songs})

@login_required
def search_all(request, query):
  '''
  Displays a json listing of all songs, artists, and albums that contain the
  provided query string.
  '''
  songs = Song.objects.select_related().filter(\
   Q(title__icontains=query) |\
   Q(album__album__icontains=query) |\
   Q(album__artist__artist__icontains=query)\
  ).order_by(*song_order)
  return JsonResponse(json_list('songs', songs))

########################
# Songs 
########################

@login_required
def song_info(request, pk):
  '''Displays a single song in json format'''
  song = get_object_or_404(Song.objects.select_related(), pk=pk)
  return JsonResponse(song.json_format())

@login_required
def song_list(request):
  '''Displays a json listing of all songs.'''
  songs = Song.objects.select_related().all().order_by(*song_order)
  return JsonResponse(json_list('songs', songs))

@login_required
def song_serve(request, pk):
  '''Serves a song's file to the user.'''
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

@staff_member_required
def song_delete(request, pk):
  song = get_object_or_404(Song, pk=pk)
  song.delete()
  return HttpResponse()

@login_required
def song_search(request, query):
  '''Searches for songs with titles that contain query. Case-insensitive.'''
  songs = Song.objects.select_related()\
   .filter(title__icontains=query).order_by(*song_order)
  return JsonResponse(json_list('songs', songs))

########################
# Albums
########################
@login_required
def album_list(request):
  '''Displays a json listing of all albums.'''
  albums = Album.objects.select_related()\
   .all().order_by('artist__artist', 'album')
  return JsonResponse(json_list('albums', albums))

@login_required
def album_songs(request, pk):
  '''Displays a json listing of all songs in the specified Album.'''
  songs = Song.objects.select_related()\
   .filter(album=pk).order_by(*song_order)
  return JsonResponse(json_list('songs', songs))

@login_required
def album_search(request, query):
  '''Searches for albums with names that contain query. Case-insensitive.'''
  albums = Album.objects.select_related()\
   .filter(album__icontains=query).order_by('artist__artist', 'album')
  return JsonResponse(json_list('albums', albums))

########################
# Artists
########################
@login_required
def artist_list(request):
  '''Displays a json listing of all artists.'''
  artists = Artist.objects.all().order_by('artist')
  return JsonResponse(json_list('artists', artists))

@login_required
def artist_songs(request, pk):
  '''Displays a json listing of all songs for the specified Artist.'''
  songs = Song.objects.select_related()\
   .filter(album__artist=pk).order_by(*song_order)
  return JsonResponse(json_list('songs', songs))

@login_required
def artist_albums(request, pk):
  '''Displays a json listing of all albums for the specified Artist.'''
  albums = Album.objects.select_related()\
   .filter(artist=pk).order_by('artist__artist', 'album')
  return JsonResponse(json_list('albums', albums))

@login_required
def artist_search(request, query):
  '''Searches for artists with names that contain query. Case-insensitive.'''
  artists = Artist.objects.filter(artist__icontains=query).order_by('artist')
  return JsonResponse(json_list('artists', artists))


  
