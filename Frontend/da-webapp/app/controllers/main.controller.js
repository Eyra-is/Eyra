'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$location', '$scope', 'recordingService', 'tokenService', 'utilityService'];

function MainController($location, $scope, recordingService, tokenService, utilityService) {
  var mainCtrl = this;
  var recService = recordingService;
  var tokService = tokenService;
  var util = utilityService;
  
  mainCtrl.start = start;
  mainCtrl.more = more;

  $scope.isLoaded = false;

  activate();

  //////////

  function activate() {
    recService.init(recServiceInitDoneCallback);
    getTokensIfNeeded();
  }

  function getTokensIfNeeded() {
    tokenService.countAvailableTokens().then(function(numTokens){
      if (numTokens < 50) {
        tokenService.getTokens(100);
      }
    },
    util.stdErrCallback);
  }

  function recServiceInitDoneCallback(result) {
    $scope.isLoaded = true;
  }

  // NAVIGATION //

  function start() {
    $location.path('/start');
  }

  function more() {
    $location.path('/more')
  }
}
