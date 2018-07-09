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
.controller('EvaluationLoginController', EvaluationLoginController);

EvaluationLoginController.$inject = [ '$location',
                                      '$rootScope',
                                      '$scope',
                                      'dataService',
                                      'deliveryService',
                                      'logger',
                                      'utilityService'];

function EvaluationLoginController($location, $rootScope, $scope, dataService, deliveryService, logger, utilityService) {
  var evalLoginCtrl = this;
  var delService = deliveryService;
  var util = utilityService;

  evalLoginCtrl.submit = submit;

  $scope.msg = '';// single information msg
  $scope.username = util.getConstant('USERNAMETEXT');
  $scope.set =  util.getConstant('SETTEXT');
  $scope.enterInfo =  util.getConstant('ENTERINFO');
  $scope.namePlaceholder =  util.getConstant('NAMEPLACEHOLDERTEXT');
  evalLoginCtrl.currentUser = '';
  evalLoginCtrl.currentSet = '';

  evalLoginCtrl.possibleSets = [];
  delService.getPossibleSets().then(
    function success(response){
      evalLoginCtrl.possibleSets = response.data;
    },
    function error(error){
      $scope.msg = util.getConstant('FETCHERRORMSG');
      logger.error(error);
    }
  )
  .then(
    function success(data){
      $rootScope.isLoaded = true;
    }, util.stdErrCallback
  );

  ////////// 

  function submit() {
    /*
    Called when user hits submit button for his info.
    */
    if (evalLoginCtrl.currentUser && evalLoginCtrl.currentSet) {
      dataService.set('currentUser', evalLoginCtrl.currentUser);
      dataService.set('currentSet', evalLoginCtrl.currentSet);
      $rootScope.evalReady = true;
      $location.path('/evaluation');
    } else {
      if (!evalLoginCtrl.currentUser) {
        $scope.msg = util.getConstant('USERNAMEERRORMSG');
      } else if (!evalLoginCtrl.currentSet) {
        $scope.msg = util.getConstant('SETERRORMSG');
      }
      if (!evalLoginCtrl.currentUser && !evalLoginCtrl.currentSet) {
        $scope.msg = util.getConstant('USERSETERRORMSG');
      }
    }
  }
}
}());
