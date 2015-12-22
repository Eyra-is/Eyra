// handler to query and process tokens from server

'use strict';

angular.module('daApp')
  .factory('tokenService', ['$http', function ($http) {
    var tokenHandler = {};
    tokenHandler.getTokens = getTokens;
    tokenHandler.nextToken = nextToken;

    var TOKENURL = '/submit/gettokens';
    var tokens = [];    

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
        console.log(data);

        // some validation of 'data' perhaps here
        tokens = data; // later just save to local storage here
      })
      .error(function (data, status) {
        console.log(data);
        console.log(status);
      });
    }

    function nextToken() {
      var next = tokens.pop();
      return next ? next['token'] : 'No more tokens.';
    }
  }]);