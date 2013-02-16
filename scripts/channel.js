var state = {
    game_key: '{{ game_key }}',
    me: '{{ me }}'
  };

  sendMessage = function(path, opt_param) {
    path += '?g=' + state.game_key;
    if (opt_param) {
      path += '&' + opt_param;
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', path, true);
    xhr.send();
  };

  onOpened = function() {
    sendMessage('/opened');
  };
  
  onMessage = function(m) {
    newState = JSON.parse(m.data);
    state.board = newState.board || state.board;
    state.userX = newState.userX || state.userX;
    state.userO = newState.userO || state.userO;
    state.moveX = newState.moveX;
    state.winner = newState.winner || "";
    state.winningBoard = newState.winningBoard || "";
    updateGame();
  }
  
  openChannel = function() {
    var token = '{{ token }}';
    var channel = new goog.appengine.Channel(token);
    var handler = {
      'onopen': onOpened,
      'onmessage': onMessage,
      'onerror': function() {},
      'onclose': function() {}
    };
    var socket = channel.open(handler);
    socket.onopen = onOpened;
    socket.onmessage = onMessage;
  }
  
  initialize = function() {
    openChannel();
    onMessage({data: '{{ initial_message }}'});
  }      

  setTimeout(initialize, 100);