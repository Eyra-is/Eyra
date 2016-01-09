'use strict';

angular.module('daApp')
.controller('StartController', StartController);

StartController.$inject = ['$location', '$scope', 'dataService', 'localDbMiscService', 'logger', 'utilityService'];

function StartController($location, $scope, dataService, localDbMiscService, logger, utilityService) {
  var startCtrl = this;
  var util = utilityService;
  var dbService = localDbMiscService;
  
  startCtrl.go = go;

  startCtrl.username = '';
  startCtrl.doneBefore = false;

  $scope.isLoaded = true;

  //////////

  function go() {
    // sanitize username input here if needed
    if (startCtrl.username === '') {
      logger.log('No username set, using default.');
      startCtrl.username = util.getConstant('defaultUsername');
    }
    // set these values for use by next page
    var setData = dataService.set('username', startCtrl.username);
    if (!setData) logger.error('Error writing username: ' + startCtrl.username);

    setData = dataService.set('doneBefore', startCtrl.doneBefore);
    if (!setData) logger.error('Error writing doneBefore: ' + startCtrl.doneBefore);

    dbService.userExist(startCtrl.username).then(
      function exists(user){
        var speakerInfo = { 'gender':user.gender,
                            'dob':user.dob,
                            'height':user.height};
        dataService.set('speakerInfo', speakerInfo);

        if (startCtrl.doneBefore) {
          // speaker has done this before, and is in db, go record!
          $location.path('/recording');
        } else {
          $scope.msg = 'User already in database. Choose a different username, unless you have done this before on this device, then tick the box.';
        }
      },
      function notExists(value){
        $location.path('/speaker-info');
      }
    );
  }
}
