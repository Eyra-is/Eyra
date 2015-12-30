// handles local forage actions, saves recordings to local db

// stores indices of session objects in 'localDb/sessionIdxs'
// for example localDb/sessionIdxs = ['localDb/sessions/0', etc.]
// then 'localDb/sessions/0 = { metadata, recordings }'

'use strict';

angular.module('daApp')
  .factory('localDbService', localDbService);

localDbService.$inject = ['$localForage'];

function localDbService($localForage) {
  var dbHandler = {};
  var lfPrefix = 'localDb/'; // local forage prefix, stuff stored at 'localDb/stuff'
  var sessionIdxsPath = lfPrefix + 'sessionIdxs';
  var sessionsPath = lfPrefix + 'sessions/';

  dbHandler.saveRecording = saveRecording;


  return dbHandler;

  //////////

  // adds new session to local db, and updates sessionIdxs
  function addNewSession(sessionData, recording, sessionIdxs) {
    var idx = 0;
    if (sessionIdxs.length > 0) {
      // we have some sessions already, set our idx as last idx + 1
      var tokens = sessionIdxs[sessionIdxs.length - 1].split('/');
      idx = parseInt(tokens[tokens.length - 1]) + 1;
    }
    // now add our session
    var session = { 'metadata' : sessionData, 'recordings' : [recording] };
    $localForage.setItem(sessionsPath + idx, session).then(function(value){
      // and update sessionIdxs
      sessionIdxs.push(sessionsPath + idx);
      $localForage.setItem(sessionIdxsPath, sessionIdxs);
    });
  }

  function isSameSession(sessionData, prevSessionData) {
    var data = sessionData['data'];
    var prevData = prevSessionData['data'];
    return  data['speakerId'] === prevData['speakerId'] && 
            data['instructorId'] === prevData['instructorId'] &&
            data['deviceId'] === prevData['deviceId'] &&
            data['location'] === prevData['location'] &&
            data['start'] === prevData['start'];
  }

  // sessionData is on format in Client-Server API
  function saveRecording(sessionData, recording) {
    console.log('Saving rec locally.');
    // first check if this recording is part of a previous session, only need to
    // look at the newest session.
    $localForage.getItem(sessionIdxsPath).then(function(value){
      var sessionIdxs;
      if (value === null) {
        sessionIdxs = [];
      } else {
        sessionIdxs = value;
      }

      if (sessionIdxs.length > 0) {
        // we have a previous session
        var prevSessionIdx = sessionIdxs.length - 1;
        $localForage.getItem(sessionIdxs[prevSessionIdx]).then(function(value){
          if (value === null) {
            // error, must have not deleted session idx from sessionIdxs, for now,
            // ignore this error, and just give up on saving this recording
            // delete the index though
            sessionIdxs.pop();
            $localForage.setItem(sessionIdxsPath, sessionIdxs);
            return;
          }
          // compare previous session with this session
          var prevSessionData = value['metadata'];
          if (isSameSession(sessionData, prevSessionData)) {
            // we have seen this session before, simply replace that session metadata (updated end-time) 
            // and add the recording
            value['metadata'] = sessionData;
            value['recordings'].push(recording);
            $localForage.setItem(sessionIdxs[prevSessionIdx], value);
          } else {
            // haven't seen this session before, need to add a session
            addNewSession(sessionData, recording, sessionIdxs);
          }
        });
      } else {
        // no previous session, in fact, no session at all stored
        addNewSession(sessionData, recording, sessionIdxs);
      }
    });
  }
}