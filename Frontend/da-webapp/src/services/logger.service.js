/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

(function () {
// service to log errors/console output. Also saves it to localForage, with key 'logs' as one big string.

'use strict';

angular.module('daApp')
  .factory('logger', logger);

logger.$inject = ['myLocalForageService'];

function logger(myLocalForageService) {
  var logHandler = {};
  var lfService = myLocalForageService;

  logHandler.error = error;
  logHandler.getLogs = getLogs; // not the wood kind
  logHandler.log = log;
  
  var LOGKEY = 'logs';

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
    save(arg);
  }

  function error(arg) {
    if (typeof arg === 'object') {
      if (arg.message) {
        // probably a javascript thrown error
        console.log(arg);
        save('Error: ' + arg.message + ', Stack: ' + arg.stack);
        return;
      }
      try {
        arg = JSON.stringify(arg, null, 4);
      } catch (e) { angluar.noop(); }
    }
    var msg = 'Error: ';
    console.log(msg + arg);
    save(msg + arg);
  }

  // returns promise of logs
  function getLogs() {
    return lfService.getItem(LOGKEY);
  }

  // save to local db
  function save(arg) {
    lfService.getItem(LOGKEY).then(function(logs){
      lfService.setItem(LOGKEY, logs + arg + '\n');
    });
  }
}
}());
