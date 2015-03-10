from django.db.models import signals, Q
from django.dispatch.dispatcher import receiver

from music_player.models import Song, Album, Artist

# Signals

@receiver(signals.post_delete, sender=Song)
def delete_file_from_disk(sender, instance, **kwargs):
  '''Cleans up a music file after it has been deleted from the database'''
  instance.music_file.delete(False)

@receiver(signals.post_delete, sender=Album)
@receiver(signals.post_save, sender=Album)
def clean_unused_artists(sender, instance, **kwargs):
  '''Used as a trigger to clean up artists with no albums.'''
  used_artists = Album.objects.all().values('artist')
  Artist.objects.filter(~Q(pk__in=used_artists)).delete()

@receiver(signals.post_delete, sender=Song)
@receiver(signals.post_save, sender=Song)
def clean_unused_albums(sender, instance, **kwargs):
  '''Used as a trigger to clean up albums with no songs.'''
  used_albums = Song.objects.all().values('album')
  Album.objects.filter(~Q(pk__in=used_albums)).delete()
