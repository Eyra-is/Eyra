'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$location', 
                          '$q', 
                          '$rootScope', 
                          '$scope', 
                          'logger', 
                          'recordingService', 
                          'tokenService', 
                          'utilityService'];

function MainController($location, $q, $rootScope, $scope, logger, recordingService, tokenService, utilityService) {
  var mainCtrl = this;
  var recService = recordingService;
  var tokService = tokenService;
  var util = utilityService;

  mainCtrl.start = start;
  mainCtrl.more = more;

  $scope.isLoaded = false;
  $scope.msg = 'Loading...';

  // promises for everything that needs to be done for app to count as initialized
  var recorderPromise = $q.defer();
  var tokensPromise = $q.defer();
  var initPromises = {'recorder' : recorderPromise.promise, 
                      'tokens'   : tokensPromise.promise};

  activate();

  //////////

  function activate() {
    recService.init(recServiceInitDoneCallback);
    getTokensIfNeeded();

    $q.all(initPromises).then(function(tasksComplete){
      $rootScope.appInitialized = true;
      logger.log('App initialized.asd');

      $scope.isLoaded = true;
    },
    // this means our app didn't initialize.. we should probably do something if that happens
    function error(data){
      $scope.msg = 'App failed to initialize. Try refreshing the page and check your connection.';
      util.stdErrCallback(data);
    });
  }

  function getTokensIfNeeded() {
    tokenService.countAvailableTokens().then(function(numTokens){
      if (numTokens < 50) {
        tokenService.getTokens(100).then(function(tokens){
          tokensPromise.resolve(true);
        },
        function error(data){
          tokensPromise.reject(data);
        });
      } else {
        // we are still okay, just didn't get any tokens, so resolve not reject here.
        tokensPromise.resolve(false);
      }
    }, function error(data){
      tokensPromise.reject(data);
    });
  }

  function recServiceInitDoneCallback(result) {
    if (result)
      recorderPromise.resolve(true);
    else
      recorderPromise.reject('Recorder not initialized.');
  }

  // NAVIGATION //

  function start() {
    $location.path('/start');
  }

  function more() {
    $location.path('/more');
  }
}
