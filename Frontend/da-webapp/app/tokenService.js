// service to query and process tokens from server

'use strict';

angular.module('daApp')
  .factory('tokenService', ['$http', '$localForage', '$q', function ($http, $localForage, $q) {
    var tokenHandler = {};
    var TOKENURL = '/submit/gettokens';

    tokenHandler.getTokens = getTokens;
    tokenHandler.nextToken = nextToken;

    return tokenHandler;

    //////////

    function getTokens(numTokens) {
      // query server for tokens
      $http({
        method: 'GET',
        url: '//'+BACKENDURL+TOKENURL+'/'+numTokens
      })
      .success(function (data) {
        // seems like data is automatically parsed as JSON for us

        // some validation of 'data' perhaps here
        saveTokens(data); // save to local forage
      })
      .error(function (data, status) {
        console.log(data);
        console.log(status);
      });
    }

    function nextToken() {
      var next = $q.defer();
      $localForage.getItem('minFreeTokenIdx').then(function(value) {
        console.log(value);

        var minFreeIdx = value || 0;
        $localForage.pull('tokens/' + minFreeIdx).then(function(value){
          if (value) {
            next.resolve(value);
          } else {
            next.reject({'id':0, 'token':'No more tokens.'});
          }

          // update our minFreeIdx
          if (minFreeIdx > 0) minFreeIdx--;
          $localForage.setItem('minFreeTokenIdx', minFreeIdx);
        });
      });
      return next.promise;
    }

    // save tokens locally. tokens should be on format depicted in getTokens in client-server API
    function saveTokens(tokens) {
      $localForage.getItem('minFreeTokenIdx').then(function(value) {
        var minFreeIdx = value || 0;
        var oldMinFreeIdx = minFreeIdx;

        for (var i = 0; i < tokens.length; i++) {
          $localForage.setItem('tokens/' + minFreeIdx, tokens[i]);
          minFreeIdx++;
        }

        // update our minFreeIdx to reflect newly input tokens
        $localForage.setItem('minFreeTokenIdx', oldMinFreeIdx + tokens.length);
      });
    }
  }]);