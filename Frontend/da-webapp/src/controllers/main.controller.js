/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
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

function MainController($location, 
                        $q, 
                        $rootScope, 
                        $scope, 
                        $window, 
                        androidRecordingService, 
                        locationService, 
                        logger, 
                        myLocalForageService, 
                        recordingService, 
                        routeService, 
                        tokenService, 
                        utilityService) {
  var mainCtrl = this;
  var locService = locationService;
  var lfService = myLocalForageService;
  var recService = recordingService;
  var tokService = tokenService;
  var util = utilityService;
  $scope.info = util.getConstant('INFO');

  $scope.startText = util.getConstant('STARTTEXT');

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
      $scope.msg = util.getConstant('APPINITIALIZATIONFAILMSG');
      logger.error(data);
    });
    $scope.startText = util.getConstant('STARTTEXT');
  }

  function getTokensIfNeeded() {
    tokenService.countAvailableTokens().then(function(numTokens){
      if (numTokens < util.getConstant('tokenThreshold')) {
        $rootScope.loading_msg = util.getConstant('GETPROMPTSMSGTEXT');
        logger.log('Getting tokens..');
        tokenService.getTokens(util.getConstant('tokenGetCount')).then(function(tokens){
          tokensPromise.resolve(true);
          logger.log('Got tokens.');
          $rootScope.loading_msg = util.getConstant('WAITINGTEXT');
        },
        function error(data){
          tokensPromise.reject(data);
          logger.log('Failed getting tokens.');
          $rootScope.loading_msg = util.getConstant('FAILEDTOGETTOKENS');
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
    if (util.getConstant('RECAGREEMENT') && !$rootScope.agreementSigned) {
      $location.path('/recording-agreement');
    } else {
      $location.path('/start');
    }
  }
}
}());
