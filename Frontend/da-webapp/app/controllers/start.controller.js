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

    // this is a little bit slow for a go button, consider pulling up all previous users on app load
    // and store in memory so this would be faster (can save info async, but navigate straight away)
    dbService.getSpeaker(startCtrl.speakerName).then(
      function success(speakerInfo){
        if (speakerInfo) {
          dataService.set('speakerInfo', speakerInfo);

          if (startCtrl.doneBefore) {
            // speaker has done this before, and is in db, go record!
            $location.path('/recording');
          } else {
            $scope.msg = 'Speaker already in database. Choose a different name, unless you have done this before on this device, then tick the box.';
          }
        } else {
          // speaker doesn't exist
          $location.path('/speaker-info');
        }
      },
      function error(value){
        $scope.msg = 'Something went wrong.';
        logger.error(value);
      }
    );
  }
}
