'use strict';

angular.module('daApp')
.controller('StartController', StartController);

StartController.$inject = ['$location', '$scope'];

function StartController($location, $scope) {
  var startCtrl = this;
  
  startCtrl.go = go;

  $scope.isLoaded = true;

  
  //////////

  function go() {
    $location.path('/recording');
  }
}
