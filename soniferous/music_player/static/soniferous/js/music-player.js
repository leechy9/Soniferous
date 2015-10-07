/**
 * Begin the music player application after the page has loaded all resources.
 * Wrap in a namespace to prevent global namespace conflicts.
 */
$(document).ready(function(){

  var songUrlBase = 'song/';

  /**
   * Song model. Used to represent a track that can be played
   * within the music player.
   */
  var Song = Backbone.Model.extend({
    defaults: function(){
      return {
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
  var SongList = Backbone.Collection.extend({
    url: songUrlBase,
    model: Song,
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
   * Handles displaying a single song on screen and listens for events.
   */
  var SongView = Backbone.View.extend({
    tagName: 'li',
    template: _.template($('#song-template').html()),
    events: {
      'add': 'render',
      'click': 'select',
    },
    initialize: function(){
      this.listenTo(this.model, 'change:isPlaying',
       _.bind(this.updatePlaying, this));
    },
    render: function(){
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },
    updatePlaying: function(song, isPlaying){
      if(isPlaying) this.$el.addClass('selected-song');
      else this.$el.removeClass('selected-song');
    },
    select: function(){
      this.model.trigger('play', this.model);
    },
    remove: function(){
      this.el.parentNode.removeChild(this.el);
    },
  });

  
  /**
   * Handles the main user interface and is the driver for the music player.
   */
  var MusicPlayerView = Backbone.View.extend({
    el: $('#audio-nav'),
    events: {
      'click #view-songs': 'viewSongs',
      'click #view-albums': 'viewAlbums',
      'click #view-artists': 'viewArtists',
      'click #play-button': 'togglePause',
      'click #next-button': 'playNextSong',
      'click #previous-button': 'playPreviousSong',
    },

    /**
     * Handle what to do during the launch of the application.
     */
    initialize: function(){
      this.currentSong = -1;
      this.audioPlayer = $('#audio-player').get(0);
      // Play the next song in the list when the current playing song ends.
      this.audioPlayer.addEventListener('ended',
       _.bind(this.playNextSong, this));
      // The listing of all songs.
      this.songList = new SongList();
      // The current playlist of songs to loop through
      this.playList = null;
      // The songs to display in the current view
      this.displayList = new SongList();
      // Performed after the list of songs has been fetched.
      var successCallback = _.bind(function(collection){
        this.listenTo(this.displayList, 'reset', this.displaySongs);
        this.displayList.reset(collection.models);
        this.playList = collection.clone();
        this.listenTo(this.playList, 'play', this.playSong);
      }, this);
      // Fetch the list of songs.
      this.songList.fetch({success: successCallback});
    },

    /**
     * Pauses the audio if already playing and plays audio if already paused.
     * Has a special case to handle when first song has been played.
     */
    togglePause: function(){
      if(this.currentSong == -1){
        this.currentSong = 0;
        this.playSong(this.playList.at(this.currentSong));
      }
      else if(this.audioPlayer.paused)
        this.audioPlayer.play();
      else
        this.audioPlayer.pause();
      this.updatePlayButton();
    },

    /**
     * Sets the play button to match the status of the audio player.
     */
    updatePlayButton: function(){
      if(this.audioPlayer.paused)
        $('#play-button').removeClass('pause-button');
      else
        $('#play-button').addClass('pause-button');
    },

    /**
     * Plays the previous song in the playlist.
     * Wraps around to last song if at start of list when this is called.
     */
    playPreviousSong: function(){
      // Handle calls before any song has been queued.
      if(this.currentSong == -1)
        return
      var previousSong = this.currentSong - 1;
      if(previousSong < 0)
        previousSong = this.playList.length - 1;
      this.playSong(this.playList.at(previousSong));
    },

    /**
     * Plays the next song in the playlist.
     * Wraps around to first song if at end of list when this is called.
     */
    playNextSong: function(){
      // Handle calls before any song has been queued.
      if(this.currentSong == -1)
        return
      var nextSong = this.currentSong + 1;
      if(nextSong >= this.playList.length)
        nextSong = 0;
      this.playSong(this.playList.at(nextSong));
    },

    /**
     * Plays the given song after setting the previous song to not-playing.
     */
    playSong: function(song){
      // Set the former song to not-playing.
      this.playList.at(this.currentSong).set('isPlaying', false);
      this.currentSong = this.playList.indexOf(song);
      this.audioPlayer.pause();
      // Set the new song to playing
      this.audioPlayer.setAttribute('src', songUrlBase + song.id + '/audio');
      song.set('isPlaying', true);
      this.audioPlayer.play();
      this.displaySongInfo(song);
      this.updatePlayButton();
    },

    /**
     * Displays the current song's info in the player.
     */
    displaySongInfo: function(song){
      $('#current-song').text(song.get('title'));
      $('#current-album').text(song.get('album'));
      $('#current-artist').text(song.get('artist'));
    },
    
    /**
     * Render multiple songs with only one document reflow.
     */
    displaySongs: function(songCollection){
      var songList = songCollection.models;
      var fragment = document.createDocumentFragment();
      for(var i=0; i<songList.length; ++i){
        var songView = new SongView({model: songList[i]});
        fragment.appendChild(songView.render().el);
      }
      $('#song-list').empty();
      $('#song-list').append(fragment);
    },

    /**
     * Display the main listing of songs.
     */
    viewSongs: function(){
      $('#album-list').addClass('hidden');
      $('#artist-list').addClass('hidden');
      $('#song-list').removeClass('hidden');
    },

    /**
     * Display the list of artists.
     */
    viewArtists: function(){
      $('#album-list').addClass('hidden');
      $('#song-list').addClass('hidden');
      $('#artist-list').removeClass('hidden');
    },

    /**
     * Display the list of albums.
     */
    viewAlbums: function(){
      $('#artist-list').addClass('hidden');
      $('#song-list').addClass('hidden');
      $('#album-list').removeClass('hidden');
    },
  });

  // Create a new music player and start the application.
  var musicPlayer = new MusicPlayerView();
});
