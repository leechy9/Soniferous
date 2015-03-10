
/**
 * Creates a new music player instance.
 * The music player listens for button presses on its controls and plays
 * music accordingly.
 * @return
 *  MusicPlayer, The music player instance.
 */
function createMusicPlayer() {
  var ns = {};
  var $ = function(q){ return document.querySelector(q); };

 /**
  * Sets the current song information to the info from the li given.
  */
  ns.updateSongDisplay = function(){
    if(ns.currentSong){
      var temp = ns.currentSong.children;
      $('#current-song').textContent = temp[0].textContent;
      $('#current-album').textContent = temp[1].textContent;
      $('#current-artist').textContent = temp[2].textContent;
    }
  };

  /**
   * Sets the current song to the li given.
   */
  ns.updateCurrentSong = function(li){
    var song_id;
    if(li){
      song_id = li.getAttribute('data-song_id');
      ns.currentSong.classList.remove('selected-song');
      ns.currentSong = li;
      ns.updateSongDisplay();
      ns.setPlayerSource(song_id);
      ns.setPlaying(false);
      ns.currentSong.classList.add('selected-song');
    }
  };

  /**
   * Sets the player's source to the specified song.
   * @param song_id
   *  The string song_id for the player to play.
   */
  ns.setPlayerSource = function(song_id){
    var audioPlayer = $('#audio-player');
    audioPlayer.src = 'song/' + song_id + '/audio';
  };

  /**
   * Selects the next song in the list. Loops back to beginning.
   */
  ns.nextSong = function(){
    if(ns.currentSong){
      ns.currentSong.classList.remove('selected-song');
      ns.currentSong = ns.currentSong.nextElementSibling;
      if(!ns.currentSong) ns.currentSong = $('#song-list').firstElementChild;
      ns.currentSong.classList.add('selected-song');
    }
  };

  /**
   * Selects the previous song in the list. Loops back to end.
   */
  ns.previousSong = function(){
    if(ns.currentSong){
      ns.currentSong.classList.remove('selected-song');
      ns.currentSong = ns.currentSong.previousElementSibling;
      if(!ns.currentSong) ns.currentSong = $('#song-list').lastElementChild;
      ns.currentSong.classList.add('selected-song');
    }
  };

  /**
   * Plays the next song in the song-list.
   */
  ns.nextPressed = function(){
    var audioPlayer = $('#audio-player');
    audioPlayer.pause();
    ns.nextSong();
    ns.updateSongDisplay();
    ns.setPlayerSource(ns.currentSong.getAttribute('data-song_id'));
    if(ns.isPlaying) audioPlayer.play();
  };

  /**
   * Plays the previous song in the song-list.
   */
  ns.previousPressed = function(){
    var audioPlayer = $('#audio-player');
    audioPlayer.pause();
    ns.previousSong();
    ns.updateSongDisplay();
    ns.setPlayerSource(ns.currentSong.getAttribute('data-song_id'));
    if(ns.isPlaying) audioPlayer.play();
  };

  /**
   * Sets the player's state to playing music.
   * @param state
   *  The state that the player should be put into.
   */
  ns.setPlaying = function(state){
    if(state){
      ns.isPlaying = true;
      $('#audio-player').play();
      $('#play-button').style.backgroundImage = "url('static/soniferous/images/pause.svg')";
    }
    else{
      ns.isPlaying = false;
      $('#audio-player').pause();
      $('#play-button').style.backgroundImage = "url('static/soniferous/images/play.svg')";
    }
  };

  /**
   * Toggles the play/pause state of the music player on button press.
   */
  ns.playPressed = function(){
    ns.setPlaying(!ns.isPlaying);
  };

  /**
   * Handles the selection of a new song when the current song ends.
   */
  ns.songEnded = function(){
    ns.nextPressed();
  };

  /**
   * Initializes the music player.
   */
  ns.init = function(){
    var audioPlayer = $('#audio-player');
    ns.isPlaying = false;
    ns.currentSong = null;
    ns.currentSong = $('#song-list').firstElementChild;
    if(ns.currentSong){
      ns.currentSong.classList.add('selected-song');
      ns.updateSongDisplay();
      audioPlayer.addEventListener('ended', ns.songEnded);
      ns.setPlayerSource(ns.currentSong.getAttribute('data-song_id'));
      $('#play-button').addEventListener('click', ns.playPressed);
      $('#previous-button').addEventListener('click', ns.previousPressed);
      $('#next-button').addEventListener('click', ns.nextPressed);
    }
  };

  return ns;
};

