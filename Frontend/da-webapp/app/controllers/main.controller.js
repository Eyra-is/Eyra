'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$location', '$scope'];

function MainController($location, $scope) {
  var mainCtrl = this;
  
  mainCtrl.start = start;
  mainCtrl.more = more;

  $scope.isLoaded = true;

  //////////

  function start() {
    $location.path('/start');
  }

  function more() {
    $location.path('/more')
  }
}
