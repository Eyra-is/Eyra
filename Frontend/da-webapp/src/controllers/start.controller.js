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
.controller('StartController', StartController);

StartController.$inject = ['$location', '$rootScope', '$scope', 'dataService', 'localDbMiscService', 'logger', 'utilityService'];

function StartController($location, $rootScope, $scope, dataService, localDbMiscService, logger, utilityService) {
  var startCtrl = this;
  var util = utilityService;
  var dbService = localDbMiscService;
  
  startCtrl.submit = submit;

  startCtrl.speakerName = '';
  startCtrl.comments = '';
  startCtrl.doneBefore = false;
  $scope.startHeadingText = util.getConstant('STARTHEADINGTEXT');
  $scope.usernameText = util.getConstant('USERNAMETEXT');
  $scope.doneBeforeText = util.getConstant('DONEBEFORETEXT');
  $scope.namePlaceholder = util.getConstant('NAMEPLACEHOLDERTEXT');

  $scope.msg = '';

  $rootScope.isLoaded = true;

  //////////

  function submit() {
    // validate inputs here if needed
    if (startCtrl.speakerName === '') {
      $scope.msg = util.getConstant('USERNAMEERRORMSG');
      return;
    }
    if (startCtrl.comments === '') {
      startCtrl.comments = 'No comments.';
    }
    // set these values for use by next page
    dataService.set('speakerName', startCtrl.speakerName);
    dataService.set('comments', startCtrl.comments);
    dataService.set('doneBefore', startCtrl.doneBefore);

    // this might be a little bit slow for a submit button, consider pulling up all previous users on app load
    // and store in memory so this would be faster (can save info async, but navigate straight away)
    dbService.getSpeaker(startCtrl.speakerName).then(
      function success(speakerInfo){
        if (speakerInfo) {
          dataService.set('speakerInfo', speakerInfo);

          if (startCtrl.doneBefore) {
            // speaker has done this before, and is in db, go record!
            $location.path('/recording');
          } else {
            $scope.msg = util.getConstant('SPEAKEREXISTSERRORMSG');
          }
        } else {
          // speaker doesn't exist
          $location.path('/speaker-info');
        }
      },
      function error(value){
        $scope.msg = util.getConstant('SOMETINGWRONGERRORMSG');
        logger.error(value);
      }
    );
  }
}
}());
