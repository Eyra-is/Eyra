'use strict';

angular.module('daApp')
.controller('InstructorLoginController', InstructorLoginController);

InstructorLoginController.$inject = ['$location', '$scope'];

function InstructorLoginController($location, $scope) {
  var iloginCtrl = this;
  
  iloginCtrl.go = go;

  $scope.isLoaded = true;

  
  //////////

  function go() {
    $location.path('/set-instructor');
  }
}
