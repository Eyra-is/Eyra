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

  // promises for everything that needs to be done for app to count as initialized
  var initPromises = {'recorder' : $q.defer(), 
                      'tokens'   : $q.defer()};

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
    util.stdErrCallback);
  }

  function getTokensIfNeeded() {
    tokenService.countAvailableTokens().then(function(numTokens){
      if (numTokens < 50) {
        tokenService.getTokens(100).then(function(tokens){
          initPromises.tokens.resolve(true);
        },
        util.stdErrCallback);
      }
    }, util.stdErrCallback);
  }

  function recServiceInitDoneCallback(result) {
    if (result)
      initPromises.recorder.resolve(true);
    else
      initPromises.recorder.reject('Recorder not initialized.');
  }

  // NAVIGATION //

  function start() {
    $location.path('/start');
  }

  function more() {
    $location.path('/more')
  }
}
