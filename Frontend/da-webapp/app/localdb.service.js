// handles local forage actions, saves recordings to local db

// stores indices of session objects in 'localDb/sessionIdxs'
// for example localDb/sessionIdxs = ['localDb/sessions/0', etc.]
// then sessionObject: 
//          'localDb/sessions/0 = { 'metadata' : sessionData, 
//                                  'recordings' : [{'blobPath' : blobPath, 'title' : wavTitle.wav },...] }'
// where blobPath is the localForage index of the stored blob (it seems like you can only store 
// blobs as single blobs and not as part of an object when you store them through localForage)
//   see issue: https://github.com/mozilla/localForage/issues/380
// blobPath = 'localDb/sessions/0/blobs/0' where blob id is same as recording index in array recordings

'use strict';

angular.module('daApp')
  .factory('localDbService', localDbService);

localDbService.$inject = ['$localForage'];

function localDbService($localForage) {
  var dbHandler = {};
  var lfPrefix = 'localDb/'; // local forage prefix, stuff stored at 'localDb/stuff'
  var sessionIdxsPath = lfPrefix + 'sessionIdxs';
  var sessionsPath = lfPrefix + 'sessions/';
  var blobsPrefix = 'blobs/';

  dbHandler.saveRecording = saveRecording;


  return dbHandler;

  //////////

  // adds recording to local database, and returns
  // ready to store sessionObject, containing sessionData updated with recording info
  // and blob reference.
  // where: prev/sessionData is as in Client Server API (prevSessionData is falsy if no previous session data)
  //        sessionIdx is the numerical index of the session to add recording to 
  //          e.g. if session is at 'localDb/sessions/5', sessionIdx = 5
  //        recordings is the recordings array associated with the session
  //        recording is the recording itself, with attribute blob and title.
  function addRecording(prevSessionData, sessionData, sessionIdx, recordings, recording) {
    // firstly, add this recording data to sessionData['data']['recordingsInfo']
    var newSessionData;
    if (prevSessionData) {
      // we have some previous session data
      prevSessionData['data']['recordingsInfo'][recording.title] =
        sessionData['data']['recordingsInfo'][recording.title];

      newSessionData = prevSessionData;
    } else {
      newSessionData = sessionData;
    }

    // secondly add blobPath & title to our sessionObject['recordings'] array
    var blobIdx = 0;
    if (!recordings || recordings.length === 0) {
      recordings = [];
      blobIdx = 0;
    } else {
      // we have some recordings already, set our idx as last idx + 1
      blobIdx = getIdxFromPath(recordings[recordings.length - 1].blobPath) + 1;
    }
    var blobPath = sessionsPath + sessionIdx + '/' + blobsPrefix + blobIdx;
    recordings.push({ 'blobPath' : blobPath, 'title' : recording.title });

    // finally save blob object to our blobPath
    $localForage.setItem(blobPath, recording.blob);

    return { 'metadata' : newSessionData, 'recordings' : recordings };
  }

  // adds new session to local db, and updates sessionIdxs
  function addNewSession(sessionData, recording, sessionIdxs) {
    var idx = 0;
    if (sessionIdxs.length > 0) {
      // we have some sessions already, set our idx as last idx + 1
      idx = getIdxFromPath(sessionIdxs[sessionIdxs.length - 1]) + 1;
    }
    // now add our session
    var sessionObject = addRecording(null, sessionData, idx, [], recording);
    $localForage.setItem(sessionsPath + idx, sessionObject).then(function(value){
      // and update sessionIdxs
      sessionIdxs.push(sessionsPath + idx);
      $localForage.setItem(sessionIdxsPath, sessionIdxs);
    });
  }

  // e.g if path === 'localDb/sessions/blob/5'
  // this will return 5
  function getIdxFromPath(path) {
    var tokens = path.split('/');
    var idx = parseInt(tokens[tokens.length - 1]);
    return idx;
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
      if (!value) {
        sessionIdxs = [];
      } else {
        sessionIdxs = value;
      }

      if (sessionIdxs.length > 0) {
        // we have a previous session
        var prevSessionIdx = sessionIdxs.length - 1;
        $localForage.getItem(sessionIdxs[prevSessionIdx]).then(function(value){
          if (!value) {
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
            var sessionIdx = getIdxFromPath(sessionIdxs[prevSessionIdx]);
            var sessionObject = addRecording(prevSessionData, sessionData, sessionIdx, value['recordings'], recording);
            $localForage.setItem(sessionIdxs[prevSessionIdx], sessionObject);
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