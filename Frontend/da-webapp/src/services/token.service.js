(function () {
// service to query and process tokens from server

'use strict';

angular.module('daApp')
  .factory('tokenService', tokenService);

tokenService.$inject = ['$q',
                        'deliveryService',
                        'logger',
                        'myLocalForageService',
                        'utilityService'];

function tokenService($q, deliveryService, logger, myLocalForageService, utilityService) {
  var tokenHandler = {};
  var delService = deliveryService;
  var lfService = myLocalForageService;
  var util = utilityService;

  tokenHandler.countAvailableTokens = countAvailableTokens;
  tokenHandler.getTokens = getTokens;
  tokenHandler.nextToken = nextToken;

  return tokenHandler;

  //////////

  // returns promise, number of tokens in local db, 0 if no tokens
  function countAvailableTokens() {
    var isAvail = $q.defer();
    lfService.getItem('minFreeTokenIdx').then(
      function success(idx){
        if (idx && idx >= 0) {
          isAvail.resolve(idx + 1);
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

  // returns promise, 
  function getTokens(numTokens) {
    var tokensPromise = $q.defer();
    // query server for tokens
    delService.getTokens(numTokens)
    .then(
      function success(response) {
        // seems like response is automatically parsed as JSON for us

        // some validation of 'data'
        var tokens = response.data;
        if (tokens && tokens.length > 0) {
          saveTokens(tokens, tokensPromise); // save to local forage
        } else {
          tokensPromise.reject('Tokens from server not on right format or empty.');
        }
      },
      function error(data) {
        tokensPromise.reject(data);
      }
    );
    return tokensPromise.promise;
  }

  function nextToken() {
    var next = $q.defer();
    lfService.getItem('minFreeTokenIdx').then(function(value) {
      logger.log('Local db index: ' + value);

      var minFreeIdx = value === -1 ? 0 : (value || 0);
      lfService.getItem('tokens/' + minFreeIdx).then(function(value){
        if (value) {
          next.resolve(value);
        } else {
          next.resolve({'id':0, 'token':'No more tokens. Hit \'Get tokens\' for more.'});
        }

        // update our minFreeIdx
        if (minFreeIdx > -1) minFreeIdx--;
        lfService.setItem('minFreeTokenIdx', minFreeIdx).then(function(value){
          // don't delete token until we have updated the index, then if
          // user exits browser after get but before update of index,
          // at least it will still show the last token.
          lfService.removeItem('tokens/' + (minFreeIdx+1))
            .then(angular.noop, util.stdErrCallback);
        },
        util.stdErrCallback);
      },
      util.stdErrCallback);
    },
    util.stdErrCallback);
    return next.promise;
  }

  // save tokens locally. tokens should be on format depicted in getTokens in client-server API
  // should not be called with tokens.length===0
  // tokensPromise is an angular q.defer(), resolved with tokens on completion of save
  function saveTokens(tokens, tokensPromise) {
    lfService.getItem('minFreeTokenIdx').then(function(value) {
      var minFreeIdx = value === -1 ? 0 : (value || 0);
      var oldMinFreeIdx = minFreeIdx;

      var finishedPromises = []; // promises to wait for until we can say this saveTokens is finished
      for (var i = 0; i < tokens.length; i++) {
        finishedPromises.push(
          lfService.setItem('tokens/' + minFreeIdx, tokens[i])
        );
        minFreeIdx++;
      }

      // update our minFreeIdx to reflect newly input tokens, 0 counts as 1, so only add length-1
      finishedPromises.push(
        lfService.setItem('minFreeTokenIdx', oldMinFreeIdx + (tokens.length - 1))
      );

      $q.all(finishedPromises).then(function(val){
        tokensPromise.resolve(tokens);
      },
      function error(data){
        tokensPromise.reject(data);
      });
    },
    function error(data){
        tokensPromise.reject(data);
    });
  }
}
}());
