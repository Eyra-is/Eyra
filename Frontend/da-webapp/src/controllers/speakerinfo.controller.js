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
.controller('SpeakerInfoController', SpeakerInfoController);

SpeakerInfoController.$inject = ['$http', '$location', '$rootScope', '$scope', 'dataService', 'logger', 'localDbMiscService', 'utilityService'];

function SpeakerInfoController($http, $location, $rootScope, $scope, dataService, logger, localDbMiscService, utilityService) {
  var sinfoCtrl = this;
  var util = utilityService;
  var dbService = localDbMiscService;
  
  sinfoCtrl.submit = submit;
  $scope.msg = '';

  var speakerName = dataService.get('speakerName'); // speakerName should be set from start.html
  if (!speakerName || speakerName === '') {
    logger.error('No speaker name. Setting default.');
    speakerName = util.getConstant('defaultSpeakerName');
  }

  var SPEAKERINFOFORMATURL = 'json/speaker-info-format.json';
  $scope.attributes = [];
  $http.get(SPEAKERINFOFORMATURL).then(
    function success(infoFormat) {
      $scope.attributes = infoFormat.data;

      $rootScope.isLoaded = true;
    },
    function error(response) {
      $scope.msg = 'Error rendering page.';

      logger.error(response);
    }
  );

  //////////

  function submit() {
    // set info used by recording
    // input validation could come here
    var speakerInfo = {};
    for (var i = 0; i < $scope.attributes.length; i++) {
      var attr = $scope.attributes[i].attribute;
      // populate speakerInfo object with keys as attribute
      //   and values as the entered values from the template
      speakerInfo[attr] = sinfoCtrl[attr] || '';
    }
    speakerInfo.name = speakerName;
    if (util.getConstant('RECAGREEMENT')) {
      var fullName = dataService.get('fullName');
      var email = dataService.get('email');
      if (!fullName || !email) {
        $scope.msg = 'Something is wrong, did you accept the participant agreement?';
      }
      speakerInfo.fullName = fullName;
      speakerInfo.email = email;
      speakerInfo.agreementId = dataService.get('agreementId') || '1';
    }

    dataService.set('speakerInfo', speakerInfo); // set in ram

    // set user in local db async
    dbService.setSpeaker(speakerName, speakerInfo).then(
      function success(info){
        // on success, set the info in dataservice, with now updated speakerInfo['deviceImei']
        if (info) dataService.set('speakerInfo', info);
      },
      function error(value) {
        logger.error( 'Failed setting speaker in local db, speakerName: ' + speakerName + 
                      ', speakerInfo: ' + JSON.stringify(speakerInfo) + ', with error: ' + value);
      }
    );

    $location.path('/recording');
  }
}
}());
