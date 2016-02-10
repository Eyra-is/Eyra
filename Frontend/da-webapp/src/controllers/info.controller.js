(function () {
'use strict';

angular.module('daApp')
.controller('InfoController', InfoController);

InfoController.$inject = ['$scope', '$rootScope'];

function InfoController($scope, $rootScope) {
  var infoCtrl = this;

  $scope.msg = '';

  $rootScope.isLoaded = true;
  
  //////////

}
}());
