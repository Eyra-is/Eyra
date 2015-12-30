// handles http post and get requests to server
// "implements" the Client-Server API

'use strict';

angular.module('daApp')
  .factory('deliveryService', deliveryService);

deliveryService.$inject = ['$http', '$q'];

function deliveryService($http, $q) {
  var reqHandler = {};
  var TOKENURL = '/submit/gettokens';

  reqHandler.getTokens = getTokens;
  reqHandler.submitRecordings = submitRecordings;
  reqHandler.testServerGet = testServerGet;

  return reqHandler;

  //////////

  function getTokens(numTokens) {
    return $http({
        method: 'GET',
        url: '//'+BACKENDURL+TOKENURL+'/'+numTokens
      });
  }

  // invalid title is just a sentinel value for a 'no_data' wav recording.
  function submitRecordings(sessionData, recordings, invalidTitle) {
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
      return $http.post('http://'+BACKENDURL+'/submit/session', fd, {
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