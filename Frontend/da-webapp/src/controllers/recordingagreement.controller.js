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
.controller('RecordingAgreementController', RecordingAgreementController);

RecordingAgreementController.$inject = ['$location', '$scope', '$rootScope', 'logger'];

function RecordingAgreementController($location, $scope, $rootScope, logger) {
  var agrCtrl = this;

  agrCtrl.submit = submit;

  $scope.msg = '';

  $rootScope.isLoaded = true;
  
  //////////

  function submit(choice) {
    if (choice === 'accept') {
      logger.log('Agreement accepted.');
      $location.path('/start');
    } else {
      logger.log('Agreement declined, cannot record unless accepted.');
      $scope.msg = 'You have to accept the agreement to continue.';
    }
  }
}
}());
