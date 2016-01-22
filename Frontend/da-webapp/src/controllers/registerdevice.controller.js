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

          alert('Device info submitted!');

          $location.path('/main');
        },
        function error(response) {
          regdCtrl.msg = 'Error submitting device.';
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
