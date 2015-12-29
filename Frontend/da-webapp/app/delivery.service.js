// handles http post and get requests to server
// "implements" the Client-Server API

'use strict';

angular.module('daApp')
  .factory('deliveryService', deliveryService);

deliveryService.$inject = ['$http', '$q'];

function deliveryService($http, $q) {
  var reqHandler = {};

  reqHandler.getTokens = getTokens;
  reqHandler.submitRecordings = submitRecordings;
  reqHandler.testServerGet = testServerGet;

  return reqHandler;

  //////////

  function getTokens(numTokens) {

  }

  // invalid title is just a sentinel value for a 'no_data' wav recording.
  function submitRecordings(jsonData, recordings, invalidTitle) {
    var fd = new FormData();
    for (var i = 0; i < recordings.length; i++) {
      // send our recording/s, and metadata as json, so long as it is valid
      var rec = recordings[i];
      var tokenId = jsonData["data"]["recordingsInfo"][rec.title]["tokenId"];
      if (rec.title !== invalidTitle || tokenId !== 0) {
        fd.append('rec' + i, rec.blob, rec.title);
        fd.append('json', JSON.stringify(jsonData));
      }
    }
    return $http.post('http://'+BACKENDURL+'/submit/session', fd, {
      // this is so angular sets the correct headers/info itself
      transformRequest: angular.identity,
      headers: {'Content-Type': undefined}
    });
  }

  // send a simple get request to the server, just to see if we have connection
  function testServerGet() {
    return $http({
      method: 'GET',
      url: '//'+BACKENDURL+'/submit/session'
    });
  }
}