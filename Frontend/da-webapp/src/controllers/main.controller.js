/*
Copyright 2016 Matthias Petursson
Apache 2.0
*/

(function () {
'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$location', 
                          '$q', 
                          '$rootScope', 
                          '$scope', 
                          '$window',
                          'androidRecordingService',
                          'locationService',
                          'logger',
                          'myLocalForageService', 
                          'recordingService', 
                          'routeService',
                          'tokenService', 
                          'utilityService'];

function MainController($location, $q, $rootScope, $scope, $window, androidRecordingService, locationService, logger, myLocalForageService, recordingService, routeService, tokenService, utilityService) {
  var mainCtrl = this;
  var locService = locationService;
  var lfService = myLocalForageService;
  var recService = recordingService;
  var tokService = tokenService;
  var util = utilityService;

  // because of a 8k filtering issue, detect if we are in an the Android webview app fix
  //   in which case use a different recorder from the web audio API
  var ANDROID;
  try {
    // AndroidRecorder is interface from WebView
    ANDROID = AndroidRecorder;
  } catch (e) {
    // we are not in a webview here, pass
  }
  if (ANDROID) {
    $rootScope.isWebView = true;
    recService = androidRecordingService;
  } else {
    $rootScope.isWebView = false;
  }

  mainCtrl.start = start;

  $rootScope.isLoaded = false;

  var recorderPromise, tokensPromise, initPromises;
  if (!$rootScope.appInitialized) {
    // promises for everything async that needs to be done for app to count as initialized
    recorderPromise = $q.defer();
    tokensPromise = $q.defer();
    initPromises = {  'recorder' : recorderPromise.promise, 
                      'tokens'   : tokensPromise.promise};

    init();
  } else {
    $rootScope.isLoaded = true;
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
    locService.init(locServiceInitDoneCallback); // lets not require location
    recService.init(recServiceInitDoneCallback);
    getTokensIfNeeded();

    $q.all(initPromises).then(function(tasksComplete){
      $rootScope.appInitialized = true;
      logger.log('App initialized.');

      $rootScope.isLoaded = true;
    },
    // this means our app didn't initialize.. we should probably do something if that happens
    function error(data){
      $scope.msg = 'App failed to initialize. Try refreshing the page and check your connection.';
      logger.error(data);
    });
  }

  function getTokensIfNeeded() {
    tokenService.countAvailableTokens().then(function(numTokens){
      if (numTokens < util.getConstant('tokenThreshold')) {
        $rootScope.loading_msg = 'Getting prompts  - Please wait';
        logger.log('Getting tokens..');
        tokenService.getTokens(util.getConstant('tokenGetCount')).then(function(tokens){
          tokensPromise.resolve(true);
          logger.log('Got tokens.');
          $rootScope.loading_msg = 'Please wait';
        },
        function error(data){
          tokensPromise.reject(data);
          logger.log('Failed getting tokens.');
          $rootScope.loading_msg = 'Failed to get tokens';
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

  function locServiceInitDoneCallback(result) {
    if (result) {
      logger.log('Location successfully set.');
    } else {
      logger.log('No location set.');
    }
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
}
}());
