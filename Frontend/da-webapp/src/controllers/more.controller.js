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
  moreCtrl.logs = logs;

  moreCtrl.logout = logout;

  $rootScope.isLoaded = true;
  
  $scope.addSpeaker = util.getConstant('ADDSPEAKERTEXT');
  $scope.setInstructor = util.getConstant('SETINSTRUCTORTEXT');
  $scope.registerDevice = util.getConstant('REGISTERDEVICETEXT');
  $scope.sync = util.getConstant('SYNCTEXT');
  $scope.logout = util.getConstant('LOGOUTTEXT');
  $scope.getTokens = util.getConstant('GETTOKENTEXT');
  $scope.clearDb = util.getConstant('CLEARDBTEXT');
  $scope.clearTokens = util.getConstant('CLEARTOKENSDBTEXT');
  $scope.printLogs = util.getConstant('PRINTLOGSTEXT');

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
    if (confirm(util.getConstant('CONFIRMMSG'))) {
      $scope.msg = util.getConstant('CLEARINGDBMSG');
      dbService.clearLocalDb()
        .then(function(val){
          alert(util.getConstant('DBCLEAREDALERT'));
          $scope.msg = util.getConstant('DBCLEAREDMSG');
        }, util.stdErrCallback);
    }
  }

  // dev function, clear all tokens
  function clearTokens() {
    $scope.msg = util.getConstant('CLEARINGTOKENSMSG');
    tokenService.clearTokens().then(
      function success(res) {
        alert(util.getConstant('TOKENSCLEARSALERT'));
        $scope.msg = util.getConstant('TOKENSCLEARSMSG');
      },
      util.stdErrCallback
    );
  }
  
  function getTokens() {
    $scope.msg = util.getConstant('GETTINGTOKENSMSG');

    tokenService.getTokens(1000).then(function(tokens){
      alert(util.getConstant('TOKENSACQUIREDALERT'));
      $scope.msg = util.getConstant('TOKENSACQUIREDMSG');
    },
    util.stdErrCallback);
  }

  // sends all available sessions from local db to server, one session at a time
  // assumes internet connection
  function sync() {
    $scope.msg = util.getConstant('SYNCINGMSG');

    delService.sendLocalSessions(syncDoneCallback, angular.noop);
  }

  // result is true if sync completed successfully
  function syncDoneCallback(result) {
    $scope.msg = result ? util.getConstant('SYNCCOMPLETEMSG') : util.getConstant('SYNCFAILEDMSG');
  }

  function logs() {
    logger.getLogs().then(function(logs){
      console.log(logs);
      $scope.msg = logs;
    });
  }
}
}());
