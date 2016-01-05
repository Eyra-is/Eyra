// handles http post and get requests to server
// "implements" the Client-Server API and also handles sending recs from local db when syncing

'use strict';

angular.module('daApp')
  .factory('deliveryService', deliveryService);

deliveryService.$inject = ['$http', '$q', 'invalidTitle', 'localDbService'];

function deliveryService($http, $q, invalidTitle, localDbService) {
  var reqHandler = {};
  var dbService = localDbService;
  var TOKENURL = '/submit/gettokens';

  reqHandler.getTokens = getTokens;
  reqHandler.sendLocalSessions = sendLocalSessions;
  reqHandler.submitRecordings = submitRecordings;
  reqHandler.testServerGet = testServerGet;

  reqHandler.failedSessionSends = 0;

  return reqHandler;

  ////////// local db functions

  function deliverSession(session) {
    submitRecordings(session.metadata, session.recordings)
    .then(
      function success(response) {
        console.log(response);

        sendLocalSession(null); // send next session
      },
      function error(response) {
        console.log(response);

        reqHandler.failedSessionSends++;
        sendLocalSession(session); // failed to send, try again to send same session
      }
    );
  }

  // send session from localdb to server
  // lastSession, is the session failed to send from last sendLocalSession, null otherwise
  // recursive function, calls itself as long as there are sessions in localdb
  // aborts after 5 failed sends.
  function sendLocalSession(lastSession) {
    if (reqHandler.failedSessionSends > 4) {
      console.log('Failed sending session too many times. Aborting sync...');
      reqHandler.failedSessionSends = 0;
      // we failed at sending session, save it to the database again.
      // function doesn't work yet
      dbService.saveSession(lastSession);
      reqHandler.syncDoneCallback(false);
      return;
    }
    // if we have a lastSession, it means last transmission was a failure, attempt to send again
    if (lastSession) {
      deliverSession(lastSession); // recursively calls sendLocalSession
      return;
    }
    dbService.countAvailableSessions().then(function(availSessions){
      if (availSessions > 0) {
        console.log('Sending session as part of sync...');
        dbService.pullSession().then(function(session){
          deliverSession(session); // recursively calls sendLocalSession
        });
      } else {
        alert('All synced up!');
        reqHandler.failedSessionSends = 0;
        reqHandler.syncDoneCallback(true);
      }
    });
  }

  // callback is function to call when all local sessions have been sent or failed to send
  function sendLocalSessions(callback) {
    reqHandler.syncDoneCallback = callback;
    sendLocalSession(null); // recursive
  }

  ////////// client-server API functions

  function getTokens(numTokens) {
    return $http({
        method: 'GET',
        url: '//'+BACKENDURL+TOKENURL+'/'+numTokens
      });
  }

  // invalid title is just a sentinel value for a 'no_data' wav recording.
  // sessionData is on the json format depicted in client-server API.
  // recordings is an array with [{ 'blob':blob, 'title':title }, ...]
  function submitRecordings(sessionData, recordings) {
    var fd = new FormData();
    fd.append('json', JSON.stringify(sessionData));
    var validSubmit = false;
    for (var i = 0; i < recordings.length; i++) {
      // send our recording/s, and metadata as json, so long as it is valid
      var rec = recordings[i];
      var tokenId = sessionData["data"]["recordingsInfo"][rec.title]["tokenId"];
      if (rec.title !== invalidTitle && tokenId !== 0) {
        fd.append('rec' + i, rec.blob, rec.title);
        validSubmit = true;
      }
    }
    if (validSubmit) {
      return $http.post('//'+BACKENDURL+'/submit/session', fd, {
          // this is so angular sets the correct headers/info itself
          transformRequest: angular.identity,
          headers: {'Content-Type': undefined}
        });
    }
    return $q.reject('No valid recordings in submission, not sending anything.');
  }

  // send a simple get request to the server, just to see if we have connection
  function testServerGet() {
    return $http({
        method: 'GET',
        url: '//'+BACKENDURL+'/submit/session'
      });
  }
}