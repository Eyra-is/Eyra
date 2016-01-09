'use strict';

angular.module('daApp')
.controller('SpeakerInfoController', SpeakerInfoController);

SpeakerInfoController.$inject = ['$location', '$scope', 'dataService', 'utilityService'];

function SpeakerInfoController($location, $scope, dataService, utilityService) {
  var sinfoCtrl = this;
  var util = utilityService;
  
  sinfoCtrl.go = go;

  $scope.isLoaded = true;
  sinfoCtrl.gender = '';
  sinfoCtrl.dob = '';
  sinfoCtrl.height = '';
  var username = dataService.get('username'); // username should be set from start.html
  if (!username || username === '') {
    logger.error('No username. Setting default.');
    username = util.getConstant('defaultUsername');
  }

  sinfoCtrl.genders = ['Male', 'Female', 'Other'];
  
  sinfoCtrl.dobs = []
  var year = new Date().getFullYear();
  var interval = 5;
  for (var i = year - interval; i >= 1950; i -= interval) {
    sinfoCtrl.dobs.push(i + '-' + (i + interval - 1));
  }
  sinfoCtrl.dobs.push('< 1950');

  sinfoCtrl.heights = ['> 200']
  interval = 10;
  for (var i = 200 - interval; i >= 140; i -= interval) {
    sinfoCtrl.heights.push(i + '-' + (i + interval - 1));
  }
  sinfoCtrl.heights.push('< 140');  

  //////////

  function go() {
    // set info used by recording
    // these are all dropdown lists, so no need for sanitation here.
    var speakerInfo = { 'gender':sinfoCtrl.gender,
                        'dob':sinfoCtrl.dob,
                        'height':sinfoCtrl.height};
    var setData = dataService.set('speakerInfo', speakerInfo);
    if (!setData) {
      logger.error('Failed setting speaker info: ' + JSON.stringify(speakerInfo));
    }

    $location.path('/recording');
  }
}
