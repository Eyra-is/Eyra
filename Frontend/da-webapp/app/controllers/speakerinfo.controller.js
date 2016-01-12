'use strict';

angular.module('daApp')
.controller('SpeakerInfoController', SpeakerInfoController);

SpeakerInfoController.$inject = ['$location', '$scope', 'dataService', 'localDbMiscService', 'utilityService'];

function SpeakerInfoController($location, $scope, dataService, localDbMiscService, utilityService) {
  var sinfoCtrl = this;
  var util = utilityService;
  var dbService = localDbMiscService;
  
  sinfoCtrl.go = go;

  $scope.isLoaded = true;
  sinfoCtrl.gender = '';
  sinfoCtrl.dob = '';
  sinfoCtrl.height = '';
  var speakerName = dataService.get('speakerName'); // speakerName should be set from start.html
  if (!speakerName || speakerName === '') {
    logger.error('No speaker name. Setting default.');
    speakerName = util.getConstant('defaultSpeakerName');
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
    // these are all dropdown lists, so only need to check for empty fields.
    if (sinfoCtrl.gender === '' || sinfoCtrl.dob === '' || sinfoCtrl.height === '') {
      $scope.msg = 'Please fill out all entries.';
    } else {
      var speakerInfo = { 'gender':sinfoCtrl.gender,
                          'dob':sinfoCtrl.dob,
                          'height':sinfoCtrl.height};
      var setData = dataService.set('speakerInfo', speakerInfo); // set in ram
      if (!setData) logger.error('Failed setting speaker info. This shouldn\'t happen.');

      // set user in local db async
      dbService.setSpeaker(speakerName, speakerInfo).then(
        angular.noop,
        function error(value) {
          logger.error( 'Failed setting speaker in local db, speakerName: ' + speakerName + 
                        ', speakerInfo: ' + JSON.stringify(speakerInfo) + ', with error: ' + value);
        }
      );

      $location.path('/recording');
    }
  }
}
