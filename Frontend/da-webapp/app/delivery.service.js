// handles http post and get requests to server
// "implements" the Client-Server API and also handles sending recs from local db when syncing

'use strict';

angular.module('daApp')
  .factory('deliveryService', deliveryService);

deliveryService.$inject = ['$http', '$q', 'logger', 'localDbService', 'utilityService'];

function deliveryService($http, $q, logger, localDbService, utilityService) {
  var reqHandler = {};
  var dbService = localDbService;
  var util = utilityService;

  reqHandler.getTokens = getTokens;
  reqHandler.sendLocalSessions = sendLocalSessions;
  reqHandler.submitRecordings = submitRecordings;
  reqHandler.testServerGet = testServerGet;

  var TOKENURL = '/submit/gettokens';
  var invalidTitle = util.getConstant('invalidTitle');
  var failedSessionSends = 0;

  return reqHandler;

  ////////// local db functions

  function deliverSession(session) {
    submitRecordings(session.metadata, session.recordings)
    .then(
      function success(response) {
        logger.log('Sent session.');
        logger.log(response.data); // DEBUG

        sendLocalSession(null); // send next session
      },
      function error(response) {
        logger.log('Failed sending session, trying again.');

        failedSessionSends++;
        sendLocalSession(session); // failed to send, try again to send same session

        util.stdErrCallback(response);
      }
    );
  }

  // send session from localdb to server
  // lastSession, is the session failed to send from last sendLocalSession, null otherwise
  // recursive function, calls itself as long as there are sessions in localdb
  // aborts after 5 failed sends.
  function sendLocalSession(lastSession) {
    if (failedSessionSends > 4) {
      logger.log('Failed sending session too many times. Aborting sync...');
      failedSessionSends = 0;
      // we failed at sending session, save it to the database again.
      dbService.saveSession(lastSession).then(function(successfulSave){
        reqHandler.syncDoneCallback(false);
      },
      util.stdErrCallback);
      return;
    }
    // if we have a lastSession, it means last transmission was a failure, attempt to send again
    if (lastSession) {
      deliverSession(lastSession); // recursively calls sendLocalSession
      return;
    }
    dbService.countAvailableSessions().then(function(availSessions){
      if (availSessions > 0) {
        logger.log('Sending session as part of sync...');
        dbService.pullSession().then(function(session){
          deliverSession(session); // recursively calls sendLocalSession
        },
        util.stdErrCallback);
      } else {
        alert('All synced up!');
        failedSessionSends = 0;
        reqHandler.syncDoneCallback(true);
      }
    },
    util.stdErrCallback);
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
    var validSubmit = false;
    try {
      fd.append('json', JSON.stringify(sessionData));

      for (var i = 0; i < recordings.length; i++) {
        // send our recording/s, and metadata as json, so long as it is valid
        var rec = recordings[i];
        var tokenId = sessionData["data"]["recordingsInfo"][rec.title]["tokenId"];
        if (rec.title !== invalidTitle && tokenId !== 0) {
          fd.append('rec' + i, rec.blob, rec.title);
          validSubmit = true;
        }
      }
    } catch (e) {
      util.stdErrCallback(e);
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