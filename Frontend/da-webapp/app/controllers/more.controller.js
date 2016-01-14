'use strict';

angular.module('daApp')
.controller('MoreController', MoreController);

MoreController.$inject = ['$location', '$scope', 'authenticationService'];

function MoreController($location, $scope, authenticationService) {
  var moreCtrl = this;
  var authService = authenticationService;
  
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
