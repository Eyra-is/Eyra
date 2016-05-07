(function () {
'use strict';

angular.module('daApp')
.controller('MoreController', MoreController);

MoreController.$inject = ['$location', 
                          '$rootScope', 
                          '$scope', 
                          'dataService',
                          'authenticationService', 
                          'deliveryService', 
                          'localDbService', 
                          'logger', 
                          'tokenService', 
                          'utilityService'];

function MoreController($location, $rootScope, $scope, dataService, authenticationService, deliveryService, localDbService, logger, tokenService, utilityService) {
  var moreCtrl = this;
  var authService = authenticationService;
  var dbService = localDbService;
  var delService = deliveryService;
  var util = utilityService;
  
  moreCtrl.addSpeaker = addSpeaker;
  moreCtrl.clearLocalDb = clearLocalDb;
  moreCtrl.clearTokens = clearTokens;
  moreCtrl.getTokens = getTokens;
  moreCtrl.registerDevice = registerDevice;
  moreCtrl.setInstructor = setInstructor;
  moreCtrl.sync = sync;
  moreCtrl.test = test;

  moreCtrl.logout = logout;

  $rootScope.isLoaded = true;
  $scope.hide_recording = true;
  $scope.hide_sync = false;
  $scope.hide_start = true;
  $scope.hide_login_msg = true;
  $scope.hide_wifi_msg = true;
  
  //////////

  function addSpeaker() {
    $location.path('/start');
  }

  function logout() {
    authService.logout();
    $location.path('/main');
  }

  function setInstructor() {
    $location.path('/set-instructor');
  }

  function registerDevice() {
    $location.path('/register-device');
  }

  // DEV FUNCTIONS

  // dev function, clear the entire local forage database
  function clearLocalDb() {
    if (confirm('Are you sure?\nThis will delete the entire local db, including tokens and recordings.')) {
      $scope.msg = 'Clearing entire local db...';
      dbService.clearLocalDb()
        .then(function(val){
          alert('Database cleared!');
          $scope.msg = 'Database cleared.';
        }, util.stdErrCallback);
    }
  }

  // dev function, clear all tokens
  function clearTokens() {
    $scope.msg = 'Clearing tokens...';
    tokenService.clearTokens().then(
      function success(res) {
        alert('All tokens gone!');
        $scope.msg = 'Tokens deleted.';
      },
      util.stdErrCallback
    );
  }
  
  function getTokens() {
    $scope.msg = 'Getting tokens...';

    tokenService.getTokens(1000).then(function(tokens){
      alert('Tokens acquired!');
      $scope.msg = 'Tokens acquired.';
    },
    util.stdErrCallback);
  }

  // sends all available sessions from local db to server, one session at a time
  // assumes internet connection
  function sync() {
    $scope.hide_sync = true;

    $scope.msg = 'Syncing - please wait';

    delService.sendLocalSessions(syncDoneCallback);
  }

  // result is true if sync completed successfully
  function syncDoneCallback(result) {
    $scope.msg = result ? 'Sync complete.' : 'Sync failed.';
    $scope.hide_sync = false;
    if (!result){
      $scope.wifi_msg = 'Please connect device to wifi or ethernet.'
      $scope.hide_wifi_msg = false
    } else {
      $scope.hide_wifi_msg = true
    }
  }

  function test() {
    /*dbService.countAvailableSessions().then(function(value){
      if (value > 0)
        logger.log('Aw yeah, '+value);
      else
        logger.log('Nope');
    });*/

    logger.getLogs().then(function(logs){
      console.log(logs);
    });

    /*$http.post(
      BACKENDURL + '/submit/session'
    ).then(function(response){
      console.log(response);
    },
    util.stdErrCallback);*/

    tokenService.countAvailableTokens().then(function(n){
      console.log(n);
    });
  }
}
}());
