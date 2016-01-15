'use strict';

angular.module('daApp')
.controller('MoreController', MoreController);

MoreController.$inject = ['$location', '$scope', 'authenticationService', 'localDbService', 'logger', 'tokenService', 'utilityService'];

function MoreController($location, $scope, authenticationService, localDbService, logger, tokenService, utilityService) {
  var moreCtrl = this;
  var authService = authenticationService;
  var dbService = localDbService;
  var util = utilityService;
  
  moreCtrl.addSpeaker = addSpeaker;
  moreCtrl.setInstructor = setInstructor;
  moreCtrl.registerDevice = registerDevice;

  moreCtrl.logout = logout;

  $scope.isLoaded = true;

  
  //////////

  function addSpeaker() {
    $location.path('/start');
  }

  function logout() {
    authService.logout();
    alert('Logged out successfully!');
  }

  function setInstructor() {
    $location.path('/set-instructor');
  }

  function registerDevice() {
    $location.path('/register-device');
  }
}
