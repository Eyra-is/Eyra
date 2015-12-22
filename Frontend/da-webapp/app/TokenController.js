// query, receive and display tokens

'use strict';

angular.module('daApp')
  .controller('TokenController', ['$http', '$scope', function($http, $scope) {
    var numTokens = 10;
    var TOKENURL = '/submit/gettokens';

    $scope.tokens = {'0':'no tokens yet'};

    // query server for tokens
    $http({
      method: 'GET',
      url: '//'+BACKENDURL+TOKENURL+'/'+numTokens
    })
    .success(function (data) {
      // seems like data is automatically parsed as JSON for us
      console.log(data);

      // some validation of 'data' perhaps here
      $scope.tokens = data;
    })
    .error(function (data, status) {
      console.log(data);
      console.log(status);
    });

    //////////

  }]);