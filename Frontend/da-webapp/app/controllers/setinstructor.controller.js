'use strict';

angular.module('daApp')
.controller('SetInstructorController', SetInstructorController);

SetInstructorController.$inject = ['$location', '$scope'];

function SetInstructorController($location, $scope) {
  var setiCtrl = this;
  
  setiCtrl.go = go;

  $scope.isLoaded = true;

  
  //////////

  function go() {
    $location.path('/main');
  }
}
