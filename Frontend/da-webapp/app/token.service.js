// service to query and process tokens from server

'use strict';

angular.module('daApp')
  .factory('tokenService', tokenService);

tokenService.$inject = ['$localForage', 
                        '$q',
                        'deliveryService',
                        'logger'];

function tokenService($localForage, $q, deliveryService, logger) {
  var tokenHandler = {};
  var delService = deliveryService;

  tokenHandler.clearLocalDb = clearLocalDb;
  tokenHandler.getTokens = getTokens;
  tokenHandler.nextToken = nextToken;

  return tokenHandler;

  //////////

  // dev function, clear the entire local forage database
  function clearLocalDb() {
    logger.log('Deleting entire local database...');
    $localForage.clear();
  }

  function getTokens(numTokens) {
    // query server for tokens
    delService.getTokens(numTokens)
    .then(
      function success(response) {
        // seems like response is automatically parsed as JSON for us

        // some validation of 'data' perhaps here
        saveTokens(response.data); // save to local forage
      }, 
      function error(response) {
        logger.log(response);
      }
    );
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
          $localForage.removeItem('tokens/' + (minFreeIdx+1));
        });
      });
    });
    return next.promise;
  }

  // save tokens locally. tokens should be on format depicted in getTokens in client-server API
  function saveTokens(tokens) {
    $localForage.getItem('minFreeTokenIdx').then(function(value) {
      var minFreeIdx = value === -1 ? 0 : (value || 0);
      var oldMinFreeIdx = minFreeIdx;

      for (var i = 0; i < tokens.length; i++) {
        $localForage.setItem('tokens/' + minFreeIdx, tokens[i]);
        minFreeIdx++;
      }

      // update our minFreeIdx to reflect newly input tokens, 0 counts as 1, so only add length-1
      $localForage.setItem('minFreeTokenIdx', oldMinFreeIdx + (tokens.length - 1));
    });
  }
}