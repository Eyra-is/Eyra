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
.controller('RegisterDeviceController', RegisterDeviceController);

RegisterDeviceController.$inject = ['$location', 
                                    '$rootScope',
                                    '$scope', 
                                    'dataService',
                                    'deliveryService', 
                                    'localDbMiscService', 
                                    'logger', 
                                    'utilityService'];

function RegisterDeviceController($location, $rootScope, $scope, dataService, deliveryService, localDbMiscService, logger, utilityService) {
  var regdCtrl = this;
  var delService = deliveryService;
  var dbService = localDbMiscService;
  var util = utilityService;
  
  regdCtrl.submit = submit;

  regdCtrl.imei = ''; // device hardcoded ID, btw many phones can display this by dialing *#06#
  $rootScope.isLoaded = true;

  $scope.deviceIdLabel = util.getConstant('IMEIDEVICETEXT');
  
  //////////

  function submit() {
    if (regdCtrl.imei.length > 0) {
      // lets not worry about sanitizing userAgent client side even though it can be spoofed. 
      var device =  {
                      'userAgent':navigator.userAgent,
                      'imei':regdCtrl.imei
                    };
      dataService.set('device', device);
      delService.submitDevice(device).then(
        function success(response) {

          alert(util.getConstant('DEVICEINFOALERT'));

          $location.path('/main');
        },
        function error(response) {
          $scope.msg = util.getConstant('DEVICESUBMITERRORMSG');
          logger.error(response);
        }
      );
      dbService.setDevice(device)
        .then(angular.noop, util.stdErrCallback);
    } else {
      logger.error('Error, no imei typed.');
    }
  }
}
}());
