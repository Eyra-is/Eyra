'use strict';

angular.module('daApp')
.controller('MoreController', MoreController);

MoreController.$inject = ['$location', '$scope'];

function MoreController($location, $scope) {
  var moreCtrl = this;
  
  moreCtrl.addSpeaker = addSpeaker;
  moreCtrl.setInstructor = setInstructor;
  moreCtrl.registerDevice = registerDevice;

  $scope.isLoaded = true;

  
  //////////

  function addSpeaker() {
    $location.path('/start');
  }

  function setInstructor() {
    $location.path('/set-instructor');
  }

  function registerDevice() {
    $location.path('/register-device');
  }
}
