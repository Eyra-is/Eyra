// service to query and process tokens from server

'use strict';

angular.module('daApp')
  .factory('tokenService', tokenService);

tokenService.$inject = ['$localForage', 
                        '$q',
                        'deliveryService',
                        'logger',
                        'utilityService'];

function tokenService($localForage, $q, deliveryService, logger, utilityService) {
  var tokenHandler = {};
  var delService = deliveryService;
  var util = utilityService;

  tokenHandler.getTokens = getTokens;
  tokenHandler.nextToken = nextToken;

  return tokenHandler;

  //////////

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
          logger.error('Tokens from server not on right format or empty.');
        }
      },
      util.stdErrCallback
    );
    return tokensPromise.promise;
  }

  function nextToken() {
    var next = $q.defer();
    $localForage.getItem('minFreeTokenIdx').then(function(value) {
      logger.log('Local db index: ' + value);

      var minFreeIdx = value === -1 ? 0 : (value || 0);
      $localForage.getItem('tokens/' + minFreeIdx).then(function(value){
        if (value) {
          next.resolve(value);
        } else {
          next.resolve({'id':0, 'token':'No more tokens. Hit \'Get tokens\' for more.'});
        }

        // update our minFreeIdx
        if (minFreeIdx > -1) minFreeIdx--;
        $localForage.setItem('minFreeTokenIdx', minFreeIdx).then(function(value){
          // don't delete token until we have updated the index, then if
          // user exits browser after get but before update of index,
          // at least it will still show the last token.
          $localForage.removeItem('tokens/' + (minFreeIdx+1))
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
    $localForage.getItem('minFreeTokenIdx').then(function(value) {
      var minFreeIdx = value === -1 ? 0 : (value || 0);
      var oldMinFreeIdx = minFreeIdx;

      var finishedPromises = []; // promises to wait for until we can say this saveTokens is finished
      for (var i = 0; i < tokens.length; i++) {
        finishedPromises.push(
          $localForage.setItem('tokens/' + minFreeIdx, tokens[i])
        );
        minFreeIdx++;
      }

      // update our minFreeIdx to reflect newly input tokens, 0 counts as 1, so only add length-1
      finishedPromises.push(
        $localForage.setItem('minFreeTokenIdx', oldMinFreeIdx + (tokens.length - 1))
      );

      $q.all(finishedPromises).then(function(val){
        tokensPromise.resolve(tokens);
      },
      util.stdErrCallback);
    },
    util.stdErrCallback);
  }
}