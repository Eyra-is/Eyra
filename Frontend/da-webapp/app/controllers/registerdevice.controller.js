'use strict';

angular.module('daApp')
.controller('RegisterDeviceController', RegisterDeviceController);

RegisterDeviceController.$inject = ['$location', '$scope'];

function RegisterDeviceController($location, $scope) {
  var regdCtrl = this;
  
  regdCtrl.go = go;

  $scope.isLoaded = true;

  
  //////////

  function go() {
    $location.path('/main');
  }
}
