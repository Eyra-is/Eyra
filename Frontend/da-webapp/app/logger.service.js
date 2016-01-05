// service to log errors/console output. Also saves it to localForage, with key 'logs' as one big string.

'use strict';

angular.module('daApp')
  .factory('logger', logger);

logger.$inject = ['$localForage'];

function logger($localForage) {
  var logHandler = {};
  var LOGKEY = 'logs';

  logHandler.error = error;
  logHandler.getLogs = getLogs; // not the wood kind
  logHandler.log = log;

  return logHandler;

  //////////

  function log(arg) {
    if (typeof arg === 'object') {
      try {
        // JSON.stringify(arg, null, 4) for nice indented output, http://stackoverflow.com/a/4293047/5272567
        arg = JSON.stringify(arg, null, 4);
      } catch (e) { angluar.noop(); }
    }
    console.log(arg);
    $localForage.getItem(LOGKEY).then(function(logs){
      $localForage.setItem(LOGKEY, logs + arg + '\n');
    });
  }

  function error(arg) {
    if (typeof arg === 'object') {
      try {
        arg = JSON.stringify(arg, null, 4);
      } catch (e) { angluar.noop(); }
    }
    var msg = 'Error: ';
    console.log(msg + arg);
    $localForage.getItem(LOGKEY).then(function(logs){
      $localForage.setItem(LOGKEY, logs + msg + arg + '\n');
    });
  }

  // returns promise of logs
  function getLogs() {
    return $localForage.getItem(LOGKEY);
  }
}