/**
 * Start the music player application after the page has loaded.
 */
$(document).ready(function(){

  /**
   * Handles displaying a single song on screen and listens for events.
   */
  Soniferous.SongView = Backbone.View.extend({
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
      this.model.trigger('select', this.model);
    },
    remove: function(){
      this.el.parentNode.removeChild(this.el);
    },
  });

  /**
   * Handles displaying a single album on screen.
   */
  Soniferous.AlbumView = Backbone.View.extend({
    tagName: 'li',
    template: _.template($('#album-template').html()),
    events: {
      'add': 'render',
      'click': 'select',
    },
    render: function(){
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },
    select: function(){
      this.model.trigger('select', this.model);
    },
  });

  /**
   * Handles displaying a single artist on screen.
   */
  Soniferous.ArtistView = Backbone.View.extend({
    tagName: 'li',
    template: _.template($('#artist-template').html()),
    events: {
      'add': 'render',
      'click': 'select',
    },
    render: function(){
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },
    select: function(){
      this.model.trigger('select', this.model);
    },
  });
  
  
  /**
   * Handles the main user interface and is the driver for the music player.
   */
  Soniferous.MusicPlayerView = Backbone.View.extend({
    el: $('#audio-nav'),
    events: {
      'click #view-songs': 'displayAllSongs',
      'click #view-albums': 'viewAlbums',
      'click #view-artists': 'viewArtists',
      'click #play-button': 'togglePause',
      'click #next-button': 'playNextSong',
      'click #previous-button': 'playPreviousSong',
      'input #search-bar': 'displaySearchSongs',
      'focus #search-bar': 'clearSearch',
    },
  
    /**
     * Handle what to do during the launch of the application.
     */
    initialize: function(){
      this.currentSong = -1;
      this.audioPlayer = $('#audio-player').get(0);
      this.searchBar = $('#search-bar');
      // Play the next song in the list when the current playing song ends.
      this.audioPlayer.addEventListener('ended',
       _.bind(this.playNextSong, this));
      // The lists of all information used in the music player
      this.albumList = new Soniferous.AlbumList();
      this.artistList = new Soniferous.ArtistList();
      this.songList = new Soniferous.SongList();
      // The current playlist of songs to loop through
      this.playList = null;
      // The songs to display in the current view
      this.displayList = new Soniferous.SongList();
      // Fetch songs
      this.songList.fetch({
        // Performed after the list of songs has been fetched
        success: _.bind(function(collection){
          this.listenTo(this.displayList, 'reset', this.displaySongs);
          this.listenTo(this.displayList, 'select', this.selectSong);
          this.displayList.reset(collection.models);
          this.playList = collection.clone();
        }, this)
      });
      // Fetch albums
      this.albumList.fetch({
        success: _.bind(function(collection){
          this.listenTo(this.albumList, 'reset', this.displayAlbums);
          this.listenTo(this.albumList, 'select', this.selectAlbum);
          this.albumList.reset(collection.models);
        }, this)
      });
      // Fetch artists
      this.artistList.fetch({
        success: _.bind(function(collection){
          this.listenTo(this.artistList, 'reset', this.displayArtists);
          this.listenTo(this.artistList, 'select', this.selectArtist);
          this.artistList.reset(collection.models);
        }, this)
      });
    },

    /**
     * Clears the text in the search bar.
     */
    clearSearch: function(){
      this.searchBar.val('');
    },

    /**
     * Displays the songs associated with the given artist.
     */
    selectArtist: function(artist){
      this.displayList.reset(
        this.songList.where({ 'artist_id': artist.id }));
      this.viewSongs();
    },

    /**
     * Displays the songs associated with the given album.
     */
    selectAlbum: function(album){
      this.displayList.reset(
        this.songList.where({ 'album_id': album.id }));
      this.viewSongs();
    },

    /**
     * Plays the selected song after updating the playlist.
     */
    selectSong: function(song){
      if(this.currentSong != -1){
        this.playList.at(this.currentSong).set('isPlaying', false);
      }
      this.playList.reset(this.displayList.models);
      this.playSong(song);
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
      this.playList.at(this.currentSong).set('isPlaying', false);
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
      this.playList.at(this.currentSong).set('isPlaying', false);
      this.playSong(this.playList.at(nextSong));
    },
  
    /**
     * Plays the given song after setting the previous song to not-playing.
     */
    playSong: function(song){
      this.currentSong = this.playList.indexOf(song);
      this.audioPlayer.pause();
      // Set the new song to playing
      this.audioPlayer.setAttribute('src',
       Soniferous.songUrlBase + song.id + '/audio');
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
        var songView = new Soniferous.SongView({model: songList[i]});
        fragment.appendChild(songView.render().el);
      }
      $('#song-list').empty();
      $('#song-list').append(fragment);
    },

    /**
     * Render multiple albums with only one document reflow.
     */
    displayAlbums: function(albumCollection){
      var albumList = albumCollection.models;
      var fragment = document.createDocumentFragment();
      for(var i=0; i<albumList.length; ++i){
        var albumView = new Soniferous.AlbumView({model: albumList[i]});
        fragment.appendChild(albumView.render().el);
      }
      $('#album-list').empty();
      $('#album-list').append(fragment);
    },

    /**
     * Render multiple artists with only one document reflow.
     */
    displayArtists: function(artistCollection){
      var artistList = artistCollection.models;
      var fragment = document.createDocumentFragment();
      for(var i=0; i<artistList.length; ++i){
        var artistView = new Soniferous.ArtistView({model: artistList[i]});
        fragment.appendChild(artistView.render().el);
      }
      $('#artist-list').empty();
      $('#artist-list').append(fragment);
    },

    /**
     * Displays all songs that were loaded during the start of the application.
     */
    displayAllSongs: function(){
      this.displayList.reset(this.songList.models);
      this.viewSongs();
    },

    /**
     * Displays a listing of songs that match the search. Only updates
     * after input has completed.
     */
    displaySearchSongs: _.debounce(function(){
      var query = this.searchBar.val().toLocaleLowerCase();
      this.displayList.reset(
        this.songList.filter(function(song){
          if(song.get('title').toLocaleLowerCase().indexOf(query) != -1)
            return true;
          if(song.get('album').toLocaleLowerCase().indexOf(query) != -1)
            return true;
          if(song.get('artist').toLocaleLowerCase().indexOf(query) != -1)
            return true;
          else
            return false;
        })
      );
      this.viewSongs();
    }, 300),
  
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
  var musicPlayer = new Soniferous.MusicPlayerView();
});
