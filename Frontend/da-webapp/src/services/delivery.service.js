(function () {
// handles http post and get requests to server
// "implements" the Client-Server API and also handles sending recs from local db when syncing

'use strict';

angular.module('daApp')
  .factory('deliveryService', deliveryService);

deliveryService.$inject = [
                            '$http', 
                            '$q',
                            '$rootScope',
                            'BACKENDURL', 
                            'dataService',
                            'logger', 
                            'localDbMiscService', 
                            'localDbService', 
                            'sessionService',
                            'utilityService'];

function deliveryService($http, $q, $rootScope, BACKENDURL, dataService, logger, localDbMiscService, localDbService, sessionService, utilityService) {
  var reqHandler = {};
  var dbService = localDbService;
  var dbMiscService = localDbMiscService;
  var util = utilityService;

  // LOCAL DB
  reqHandler.sendLocalSessions = sendLocalSessions;
  // API
  reqHandler.getTokens = getTokens;
  reqHandler.queryQC = queryQC;
  reqHandler.submitDevice = submitDevice;
  reqHandler.submitInstructor = submitInstructor;
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
        logger.log(response); // DEBUG

        // update recsDelivered
        dataService.set('recsDelivered', sessionService.handleSessionResponse(response));

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
  // aborts after 2 failed sends.
  function sendLocalSession(lastSession) {
    if (failedSessionSends > 1) {
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
        // sort of added hack, now pullSession sends only syncRecCountPerSend || 5 recordings per "session" send.
        dbService.pullSession(util.getConstant('syncRecCountPerSend') || 5).then(function(session){
          deliverSession(session); // recursively calls sendLocalSession
        },
        util.stdErrCallback);
      } else {
        //alert('All synced up!');
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
        url: BACKENDURL+TOKENURL+'/'+numTokens
      });
  }

  function queryQC(sessionId) {
    // function input is a sessionId
    // a async http get call is sent to backend w a string as input
    // the return value is a 
    return $http.get(BACKENDURL + '/qc/report/session/'+sessionId);
  }

  function submitDevice(device) {
    // make sure always to send the user agent string, even in case of some erraneous programming
    //   before this function call
    if (!device.userAgent) {
      device.userAgent = navigator.userAgent;
    }
    // same for imei if we are in webview
    if (!device.imei && $rootScope.isWebView) {
      device.imei = AndroidConstants.getImei();
    }
    return submitGeneralJson(device, '/submit/general/device');
  }

  function submitGeneralJson(jsonData, url) {
    var fd = new FormData();
    var validSubmit = false;
    try {
      fd.append('json', JSON.stringify(jsonData));
      validSubmit = true;
    } catch (e) {
      logger.error(e);
    }
    if (validSubmit) {
      return $http.post(BACKENDURL+url, fd, {
          // this is so angular sets the correct headers/info itself
          transformRequest: angular.identity,
          headers: {'Content-Type': undefined}
        });
    }
    return $q.reject('Error submitting data.');
  }

  function submitInstructor(instructorData) {
    return submitGeneralJson(instructorData, '/submit/general/instructor');
  }

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
      logger.error(e);
    }
    if (validSubmit) {
      return $http.post(BACKENDURL+'/submit/session', fd, {
          // this is so angular sets the correct headers/info itself
          transformRequest: angular.identity,
          headers: {'Content-Type': undefined}
        });
    }
    return $q.reject('No valid recordings in submission, not sending anything.');
  }

  // NOT USED, speaker data is sent with each session
  // here speakerData does not necessarily contain the optional imei, therefore
  //   always check if we can get that and submit before we send.
  /*function submitSpeaker(speakerData){
    var submission = $q.defer();
    dbMiscService.getDevice().then(
      function success(device){
        if (device && device['imei'] !== '') {
          speakerData['deviceImei'] = device['imei'];
        }
        $q.resolve(
          submitGeneralJson(speakerData, '/submit/general/speaker')
        );
      },
      function error(response) {
        // still resolve, just without device imei
        $q.resolve(
          submitGeneralJson(speakerData, '/submit/general/speaker')
        );
        logger.error(response);
      }
    );
    return submission.promise;
  }*/

  // send a simple get request to the server, just to see if we have connection
  function testServerGet() {
    return $http({
        method: 'GET',
        url: BACKENDURL+'/submit/session'
      });
  }
}
}());
