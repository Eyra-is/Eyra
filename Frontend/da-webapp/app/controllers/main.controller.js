'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$location', 
                          '$q', 
                          '$rootScope', 
                          '$scope', 
                          '$window',
                          'logger',
                          'myLocalForageService', 
                          'recordingService', 
                          'routeService',
                          'tokenService', 
                          'utilityService'];

function MainController($location, $q, $rootScope, $scope, $window, logger, myLocalForageService, recordingService, routeService, tokenService, utilityService) {
  var mainCtrl = this;
  var lfService = myLocalForageService;
  var recService = recordingService;
  var tokService = tokenService;
  var util = utilityService;

  mainCtrl.start = start;
  mainCtrl.more = more;

  $scope.msg = 'Loading...';
  $scope.isLoaded = false;

  var recorderPromise, tokensPromise, initPromises;
  if (!$rootScope.appInitialized) {
    // promises for everything async that needs to be done for app to count as initialized
    recorderPromise = $q.defer();
    tokensPromise = $q.defer();
    initPromises = {  'recorder' : recorderPromise.promise, 
                      'tokens'   : tokensPromise.promise};

    init();
  } else {
    $scope.isLoaded = true;
  }

  //////////

  function init() {
    // synchronous things
    // make sure user gets warning on navigate away from page if local db operations are going on still
    $window.addEventListener('beforeunload', function(e){
      if (lfService.inProgress()) {
        var msg =   'Are you sure you want to navigate away?\n\
                     There is still possibly important processing going on in the app.';

        // https://developer.mozilla.org/en-US/docs/Web/Events/beforeunload
        // browsers still seem to ignore this message, at least some..
        //   at least they show a warning
        (e || $window.event).returnValue = msg;
        return msg;
      }
    });

    // async things
    recService.init(recServiceInitDoneCallback);
    getTokensIfNeeded();

    $q.all(initPromises).then(function(tasksComplete){
      $rootScope.appInitialized = true;
      logger.log('App initialized.');

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
        logger.log('Getting tokens..');
        tokenService.getTokens(100).then(function(tokens){
          tokensPromise.resolve(true);
          logger.log('Got tokens.');
        },
        function error(data){
          tokensPromise.reject(data);
          logger.log('Failed getting tokens.');
          logger.error(data);
        });
      } else {
        // we are still okay, just didn't get any tokens, so resolve not reject here.
        tokensPromise.resolve(false);
      }
    }, function error(data){
      tokensPromise.reject(data);
      logger.error(data);
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
