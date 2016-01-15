(function () {
'use strict';

angular.module('daApp')
.controller('MoreController', MoreController);

MoreController.$inject = ['$location', '$scope', 'authenticationService', 'localDbService', 'logger', 'tokenService', 'utilityService'];

function MoreController($location, $scope, authenticationService, localDbService, logger, tokenService, utilityService) {
  var moreCtrl = this;
  var authService = authenticationService;
  var dbService = localDbService;
  var util = utilityService;
  
  moreCtrl.addSpeaker = addSpeaker;
  moreCtrl.clearLocalDb = clearLocalDb;
  moreCtrl.getTokens = getTokens;
  moreCtrl.registerDevice = registerDevice;
  moreCtrl.setInstructor = setInstructor;
  moreCtrl.test = test;

  moreCtrl.logout = logout;

  $scope.isLoaded = true;

  
  //////////

  function addSpeaker() {
    $location.path('/start');
  }

  function logout() {
    authService.logout();
    alert('Logged out successfully!');
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
      moreCtrl.msg = 'Clearing entire local db...';
      dbService.clearLocalDb()
        .then(function(val){
          alert('Database cleared!');
          moreCtrl.msg = 'Database cleared.';
        }, util.stdErrCallback);
    }
  }
  
  function getTokens() {
    moreCtrl.msg = 'Getting tokens...';

    tokenService.getTokens(25).then(function(tokens){
      alert('Tokens acquired!');
      moreCtrl.msg = 'Tokens acquired.';
    },
    util.stdErrCallback);
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
      '//' + BACKENDURL + '/submit/session'
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
