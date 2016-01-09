'use strict';

angular.module('daApp')
.controller('StartController', StartController);

StartController.$inject = ['$location', '$scope', 'dataService', 'localDbMiscService', 'logger', 'utilityService'];

function StartController($location, $scope, dataService, localDbMiscService, logger, utilityService) {
  var startCtrl = this;
  var util = utilityService;
  var dbService = localDbMiscService;
  
  startCtrl.go = go;

  startCtrl.speakerName = '';
  startCtrl.doneBefore = false;

  $scope.isLoaded = true;

  //////////

  function go() {
    // sanitize speakerName input here if needed
    if (startCtrl.speakerName === '') {
      logger.log('No speaker name set, using default.');
      startCtrl.speakerName = util.getConstant('defaultSpeakerName');
    }
    // set these values for use by next page
    var setData = dataService.set('speakerName', startCtrl.speakerName);
    if (!setData) logger.error('Error writing speaker name: ' + startCtrl.speakerName);

    setData = dataService.set('comments', startCtrl.comments);
    if (!setData) logger.error('Error writing comments: ' + startCtrl.comments);

    setData = dataService.set('doneBefore', startCtrl.doneBefore);
    if (!setData) logger.error('Error writing doneBefore: ' + startCtrl.doneBefore);


    dbService.speakerExist(startCtrl.speakerName).then(
      function exists(speaker){
        var speakerInfo = { 'gender':speaker.gender,
                            'dob':speaker.dob,
                            'height':speaker.height};
        dataService.set('speakerInfo', speakerInfo);

        if (startCtrl.doneBefore) {
          // speaker has done this before, and is in db, go record!
          $location.path('/recording');
        } else {
          $scope.msg = 'Speaker already in database. Choose a different name, unless you have done this before on this device, then tick the box.';
        }
      },
      function notExists(value){
        $location.path('/speaker-info');
      }
    );
  }
}
