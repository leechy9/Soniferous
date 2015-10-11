// Check if namespace exists. Create if not.
if(Soniferous === undefined)
  var Soniferous = {};

Soniferous.songUrlBase = 'song/';
Soniferous.artistUrlBase = 'artist/';
Soniferous.albumUrlBase = 'album/';

/**
 * Artist model. Represents a single musical artist.
 */
Soniferous.Artist = Backbone.Model.extend({
  defaults: function(){
    return {'artist': 'Unknown Artist'};
  },
});


/**
 * Album model. Represents a single album from a musical artist.
 */
Soniferous.Album = Backbone.Model.extend({
  defaults: function(){
    return {
      'album': 'Unknown Album',
      'artist': 'Unknown Artist',
      'artist_id': -1,
    };
  },
});


/**
 * Song model. Used to represent a track that can be played
 * within the music player.
 */
Soniferous.Song = Backbone.Model.extend({
  defaults: function(){
    return {
     'album_id': -1,
     'artist_id': -1,
     'isPlaying': false,
     'title': 'Unknown Title',
     'track_number': '0',
     'time': '0:00',
     'album': 'Unknown Album',
     'artist': 'Unknown Artist',
    };
  },
});

/**
 * A collection of songs with options to sort.
 */
Soniferous.SongList = Backbone.Collection.extend({
  url: Soniferous.songUrlBase,
  model: Soniferous.Song,
  parse: function(songObject) { return songObject.songs; },
  /**
   * Sorts songs by artist, album, track_number, and title.
   */
  comparator: function(song){
    return [
     song.get('artist'),
     song.get('album'),
     song.get('track_number'),
     song.get('title')
    ];
  },
});

/**
 * A collection of albums with options to sort.
 */
Soniferous.AlbumList = Backbone.Collection.extend({
  url: Soniferous.albumUrlBase,
  model: Soniferous.Album,
  parse: function(albumObject) { return albumObject.albums; },
  comparator: function(album){
    return [
      album.get('artist'),
      album.get('album'),
    ];
  },
});

/**
 * A collection of artists with options to sort.
 */
Soniferous.ArtistList = Backbone.Collection.extend({
  url: Soniferous.artistUrlBase,
  model: Soniferous.Artist,
  parse: function(artistObject) { return artistObject.artists; },
  comparator: 'artist',
});
