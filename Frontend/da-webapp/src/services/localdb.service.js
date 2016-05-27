/*
Copyright 2016 Matthias Petursson
Apache 2.0
*/

(function () {
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

localDbService.$inject = ['$q', 'logger', 'myLocalForageService', 'utilityService'];

function localDbService($q, logger, myLocalForageService, utilityService) {
  var dbHandler = {};
  var lfService = myLocalForageService;
  var util = utilityService;

  dbHandler.clearLocalDb = clearLocalDb;
  dbHandler.countAvailableSessions = countAvailableSessions;
  dbHandler.pullSession = pullSession;
  dbHandler.saveRecording = saveRecording;
  dbHandler.saveSession = saveSession;
  
  var lfPrefix = 'localDb/'; // local forage prefix, stuff stored at 'localDb/stuff'
  var sessionIdxsPath = lfPrefix + 'sessionIdxs';
  var sessionsPath = lfPrefix + 'sessions/';
  var blobsPrefix = 'blobs/';

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
      blobIdx = util.getIdxFromPath(recordings[recordings.length - 1].blobPath) + 1;
    }
    var blobPath = sessionsPath + sessionIdx + '/' + blobsPrefix + blobIdx;
    recordings.push({ 'blobPath' : blobPath, 'title' : recording.title });

    // finally save blob object to our blobPath
    lfService.setItem(blobPath, recording.blob)
      .then(angular.noop, util.stdErrCallback);

    return { 'metadata' : newSessionData, 'recordings' : recordings };
  }

  // adds new session to local db, and updates sessionIdxs
  function addNewSession(sessionData, recording, sessionIdxs) {
    var idx = 0;
    if (sessionIdxs.length > 0) {
      // we have some sessions already, set our idx as last idx + 1
      idx = util.getIdxFromPath(sessionIdxs[sessionIdxs.length - 1]) + 1;
    }
    // now add our session
    var sessionObject = addRecording(null, sessionData, idx, [], recording);
    lfService.setItem(sessionsPath + idx, sessionObject).then(function(value){
      // and update sessionIdxs
      sessionIdxs.push(sessionsPath + idx);
      lfService.setItem(sessionIdxsPath, sessionIdxs)
        .then(angular.noop, util.stdErrCallback);
    },
    util.stdErrCallback);
  }

  // dev function, clear the entire local forage database
  function clearLocalDb() {
    logger.log('Deleting entire local database...');
    return lfService.clear();
  }

  // returns promise, number of sessions in local db, 0 if no session data
  function countAvailableSessions() {
    var isAvail = $q.defer();
    lfService.getItem(sessionIdxsPath).then(
      function success(value){
        if (value && value.length > 0) {
          isAvail.resolve(value.length);
        } else {
          isAvail.resolve(0);
        }
      }, 
      function error(response){
        isAvail.reject(response);
      }
    );
    return isAvail.promise;
  }

  function isSameSession(sessionData, prevSessionData) {
    try {
      var data = sessionData['data'];
      var prevData = prevSessionData['data'];
      return  data['speakerId'] === prevData['speakerId'] && 
              data['instructorId'] === prevData['instructorId'] &&
              data['deviceId'] === prevData['deviceId'] &&
              data['location'] === prevData['location'] &&
              data['start'] === prevData['start'];
    } catch (e) {
      logger.error('Invalid format of sessionData or prevSessionData');
      util.stdErrCallback(e);
      return false;
    }
  }

  // writes sessionIdxs to sessionIdxsPath with 1 element popped
  // used when sessionIdxs has at least one invalid index at the top
  function popSessionIdxs(sessionIdxs) {
    logger.error('Invalid session idx: ' + sessionIdxs[sessionIdxs.length - 1] + ', deleting index.');
    return lfService.setItem(sessionIdxsPath, sessionIdxs.slice(0, sessionIdxs.length - 1));
  }

  // gets recCount recs/data from session pair from local db and deletes them.
  // returns { 'metadata' : sessionData, 'recordings' : [ {'blob':blob, 'title':title}, ...]}
  // There should be some session data before calling this function, that's what 'countAvailableSessionsData()' is for.
  function pullSession(recCount) {
    logger.log('Getting session data...');
    var pulledSession = $q.defer();
    lfService.getItem(sessionIdxsPath).then(function(sessionIdxs){
      // get newest session
      var sessionIdxPath = sessionIdxs[sessionIdxs.length - 1];
      lfService.getItem(sessionIdxPath).then(function(session){
        if (!session) {
          // must have been a leftover index, not pointing to a session, lets delete it
          popSessionIdxs(sessionIdxs)
            .then(angular.noop, failedPullCallback);
          return;
        }

        if (session.recordings.length <= recCount) {
          // we have less than recCount recs left to send, so send entire rest of session, and delete it.

          // update our sessionIdxs in db
          lfService.setItem(sessionIdxsPath, sessionIdxs.slice(0, sessionIdxs.length - 1))
          .then(function(sessionIdxs){
            // and async delete the session data (in case it doesn't work, it will just get overwritten)
            lfService.removeItem(sessionIdxPath)
              .then(angular.noop, util.stdErrCallback);
            processCurrentSession(session);
          }, failedPullCallback);
        } else {
          // we only want to send part of the session, do that.

          // only use recCount recordings as our new recordings and send those, 
          // make sure to delete them afterwards from local db as well
          var recordings = [];
          var recordingsInfo = {};
          for (var i = 0; i < recCount; i++) {
            if (session.recordings.length <= 0) 
              break;
            var rec = session.recordings.pop();
            recordings.push(rec);
            recordingsInfo[rec.title] = session.metadata.data.recordingsInfo[rec.title];
            delete session.metadata.data.recordingsInfo[rec.title];
          }

          // update our session in ldb with recCount recs removed, then attempt the "pull"
          lfService.setItem(sessionIdxPath, session).then(function(remainingSession){
            session.metadata.data.recordingsInfo = recordingsInfo;
            session.recordings = recordings;
            processCurrentSession(session);
          },
          failedPullCallback);
        }        
      }, failedPullCallback);
    }, failedPullCallback);

    return pulledSession.promise;

    // local callback, for errors in this function
    function failedPullCallback(response) {
      pulledSession.reject(response);
    }

    // sends session just like it is. Assumes session was modified if need be in previous code.
    function processCurrentSession(session) {
      // now we just have to replace recordings[i].blobPath:blobPath with blob:blob
      var recordings = session.recordings;
      var blobPromises = []; // an array of blob promises
      // get all blobs for this session from our local db
      for (var i = 0; i < recordings.length; i++) {
        blobPromises.push(lfService.getItem(recordings[i].blobPath));
      }
      // q.all waits on all blobs to resolve, or one to reject
      $q.all(blobPromises).then(function(blobs){
        for (var i = 0; i < blobs.length; i++) {
          // delete blob from local db, don't fail on a failure here, 
          // if a single blob doesn't get deleted, we don't care too much
          // it will get overwritten later most likely.
          lfService.removeItem(recordings[i].blobPath)
            .then(angular.noop, util.stdErrCallback); 
          delete recordings[i].blobPath;
          recordings[i].blob = blobs[i];
        }
        // finally we have our updated session to return!
        pulledSession.resolve(session);
      },
      failedPullCallback);
    }
  }

  // sessionData is on format in Client-Server API
  function saveRecording(sessionData, recording) {
    logger.log('Saving rec locally.');
    // first check if this recording is part of a previous session, only need to
    // look at the newest session.
    lfService.getItem(sessionIdxsPath).then(function(value){
      var sessionIdxs;
      if (!value) {
        sessionIdxs = [];
      } else {
        sessionIdxs = value;
      }

      if (sessionIdxs.length > 0) {
        // we have a previous session
        var prevSessionIdx = sessionIdxs.length - 1;
        lfService.getItem(sessionIdxs[prevSessionIdx]).then(function(session){
          if (!session) {
            // error, must have not deleted session idx from sessionIdxs, for now
            // give up on saving this recording, delete the index though
            popSessionIdxs(sessionIdxs)
              .then(angular.noop, util.stdErrCallback);
            return;
          }
          // compare previous session with this session
          var prevSessionData = session['metadata'];
          if (isSameSession(sessionData, prevSessionData)) {
            // we have seen this session before, simply replace that session metadata (updated end-time) 
            // and add the recording
            var sessionIdx = util.getIdxFromPath(sessionIdxs[prevSessionIdx]);
            var sessionObject = addRecording(prevSessionData, sessionData, sessionIdx, session['recordings'], recording);
            lfService.setItem(sessionIdxs[prevSessionIdx], sessionObject)
              .then(angular.noop, util.stdErrCallback);
          } else {
            // haven't seen this session before, need to add a session
            addNewSession(sessionData, recording, sessionIdxs);
          }
        }, util.stdErrCallback);
      } else {
        // no previous session, in fact, no session at all stored
        addNewSession(sessionData, recording, sessionIdxs);
      }
    }, util.stdErrCallback);
  }

  // takes in session obejct: { 'metadata':sessionData, 'recordings':{'blob':blob, 'title':title} }
  // and saves it to local db
  // returns promise, resolved as true on save completion, otherwise rejected
  // (will resolve as true even if saving the blob fails (addRecording))
  function saveSession(session) {
    var successfulSave = $q.defer();
    lfService.getItem(sessionIdxsPath).then(function(sessionIdxs){
      // get next new index for our session
      var sessionIdx;
      if (sessionIdxs && sessionIdxs.length > 0) {
        sessionIdx = util.getIdxFromPath(sessionIdxs[sessionIdxs.length - 1]) + 1;
      } else {
        sessionIdx = 0;
      }
      // save all our recordings as blobs by using addRecording function.
      var newRecs = [];
      var newSession;
      var recs = session.recordings;
      for (var i = 0; i < recs.length; i++) {
        newSession = addRecording(null, null, sessionIdx, newRecs, recs[i]);
        newRecs = newSession.recordings;
      }
      // finally we can save our session knowing the blobs/paths are now correct
      var sessionPath = sessionsPath + sessionIdx;
      lfService.setItem(sessionPath, { 'metadata':session.metadata, 'recordings':newRecs }).then(function(value){
        sessionIdxs.push(sessionPath);
        lfService.setItem(sessionIdxsPath, sessionIdxs)
        .then(
          function success(sessionIdxs){
            successfulSave.resolve(true);
          }, 
          failedSaveCallback);
      }, failedSaveCallback);
    }, failedSaveCallback);

    return successfulSave.promise;

    // local callback, for errors in this function
    function failedSaveCallback(response) {
      successfulSave.reject(response);
    }
  }
}
}());
