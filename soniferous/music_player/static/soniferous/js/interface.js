/**
 * Handles mouse clicks concerning the various lists in the interface.
 */
function createInterfaceHandler(musicPlayer){
  var ns = {};
  var $ = function(q){ return document.querySelector(q); };
  ns.musicPlayer = musicPlayer;

  /**
   * Hides all lists and only displays the list given.
   * @param listID 
   *  The list to display.
   */
  ns.displaySections = function(listID){
    // Hide all views but the one provided.
    $('#album-list').classList.add('hidden');
    $('#artist-list').classList.add('hidden');
    $('#song-list').classList.add('hidden');
    $(listID).classList.remove('hidden');
  }

  /**
   * Displays the given list of songs.
   * @param json
   *  The json request of song objects to display.
   */
  ns.displaySongs = function(json){
    var i, li, span, songs;
    var list = $('#song-list');
    songs = json['songs'];
    while(list.firstChild){
      list.removeChild(list.firstChild);
    }
    for(i=0;i<songs.length;++i){
      li = document.createElement('li');
      span = document.createElement('span');
      span.textContent = songs[i]['title'];
      li.appendChild(span);
      span = document.createElement('span');
      span.textContent = songs[i]['album'];
      li.appendChild(span);
      span = document.createElement('span');
      span.textContent = songs[i]['artist'];
      li.appendChild(span);
      span = document.createElement('span');
      span.textContent = songs[i]['time'];
      li.appendChild(span);
      li.setAttribute('data-song_id', songs[i]['id']);
      list.appendChild(li);
    }
    ns.musicPlayer.updateCurrentSong(list.firstElementChild);
  };

  /**
   * Displays the given list of albums.
   * @param json
   *  The json request of album objects to display.
   */
  ns.displayAlbums = function(json){
    var i, li, span, albums;
    var list = $('#album-list');
    albums = json['albums'];
    while(list.firstChild){
      list.removeChild(list.firstChild);
    }
    for(i=0;i<albums.length;++i){
      li = document.createElement('li');
      span = document.createElement('span');
      span.textContent = albums[i]['album'];
      li.appendChild(span);
      span = document.createElement('span');
      span.textContent = albums[i]['artist'];
      li.appendChild(span);
      li.setAttribute('data-album_id', albums[i]['id']);
      list.appendChild(li);
    }
  };

  /**
   * Displays the given list of artists.
   * @param json
   *  The json request of album objects to display.
   */
  ns.displayArtists = function(json){
    var i, li, span, artists;
    var list = $('#artist-list');
    artists = json['artists'];
    while(list.firstChild){
      list.removeChild(list.firstChild);
    }
    for(i=0;i<artists.length;++i){
      li = document.createElement('li');
      span = document.createElement('span');
      span.textContent = artists[i]['artist'];
      li.appendChild(span);
      li.setAttribute('data-artist_id', artists[i]['id']);
      list.appendChild(li);
    }
  };

  /**
   * Send an XHR to the url, parse the json, and pass it as a
   * parameter to the callback function.
   * @param url
   *  The url to fetch json from.
   * @param callback
   *  The function to execute and pass the json objects to.
   */
  ns.jsonQuery = function(url, callback){
    var req = new XMLHttpRequest();
    req.open('get', url, true);
    req.onload = function(){
      callback(JSON.parse(this.responseText));
    };
    req.send();
  }

  /**
   * Adds listeners for clicks on each item in a list.
   * @param root
   *  The list to listen for clicks on.
   * @param eventType
   *  The type of event to listen for (click/dblclick).
   * @param func
   *  The function to call when the root element is clicked.
   */
  ns.addListListener = function(root, eventType, func){
    root.addEventListener(eventType, function(event){
      if(event.target.tagName == 'LI'){
        func(event.target);
      }
      else if(event.target.tagName == 'SPAN'){
        func(event.target.parentElement);
      }
    });
  };

  /**
   * Sets up the search bar to perform queries.
   */
  ns.initSearchBar = function(){
    var searchBar = $('#search-bar');
    searchBar.addEventListener('keypress', function(e){
      if(e.keyCode === 13){
        if(searchBar.value === '')
          ns.jsonQuery('song/', ns.displaySongs);
        else
          ns.jsonQuery('search/' + searchBar.value, ns.displaySongs);
        ns.displaySections('#song-list');
      }
    });
    searchBar.addEventListener('blur', function(e){
      searchBar.value = '';
    });
  };

  /**
   * Sets up the interface with appropriate action listeners.
   */
  ns.init = function(){
    // Handle clicks on view selector buttons.
    $('#view-artists').addEventListener('click', function(){
      ns.jsonQuery('artist/', ns.displayArtists);
      ns.displaySections('#artist-list');
    });
    $('#view-albums').addEventListener('click', function(){
      ns.jsonQuery('album/', ns.displayAlbums);
      ns.displaySections('#album-list');
    });
    $('#view-songs').addEventListener('click', function(){
      ns.jsonQuery('song/', ns.displaySongs);
      ns.displaySections('#song-list');
    });
    // Handle clicks in each list.
    ns.addListListener($('#song-list'), 'click', function(li){
      ns.musicPlayer.updateCurrentSong(li);
      ns.musicPlayer.setPlaying(true);
    });
    ns.addListListener($('#album-list'), 'click', function(li){
      var url = 'album/' + li.getAttribute('data-album_id') + '/songs';
      ns.jsonQuery(url, ns.displaySongs);
      ns.displaySections('#song-list');
    });
    ns.addListListener($('#artist-list'), 'click', function(li){
      var url = 'artist/' + li.getAttribute('data-artist_id') + '/songs';
      ns.jsonQuery(url, ns.displaySongs);
      ns.displaySections('#song-list');
    });
    // Add search bar functionality
    ns.initSearchBar();
  };

  return ns;
};

/* Initializes the entire interface and player. */
window.onload = function(){
  var musicPlayer = createMusicPlayer();
  musicPlayer.init();
  var interfaceHandler = createInterfaceHandler(musicPlayer);
  interfaceHandler.init();
};
