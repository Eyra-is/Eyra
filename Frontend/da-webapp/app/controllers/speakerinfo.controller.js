'use strict';

angular.module('daApp')
.controller('SpeakerInfoController', SpeakerInfoController);

SpeakerInfoController.$inject = ['$location', '$scope'];

function SpeakerInfoController($location, $scope) {
  var sinfoCtrl = this;
  
  sinfoCtrl.go = go;

  $scope.isLoaded = true;
  sinfoCtrl.gender = '';
  sinfoCtrl.dob = '';
  sinfoCtrl.height = '';

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
    $location.path('/recording');
  }
}
