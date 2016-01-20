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

  $rootScope.isLoaded = true;

  //////////

  function submit() {
    // validate inputs here if needed
    if (startCtrl.speakerName === '') {
      logger.log('No speaker name set, using default.');
      startCtrl.speakerName = util.getConstant('defaultSpeakerName');
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
}());
