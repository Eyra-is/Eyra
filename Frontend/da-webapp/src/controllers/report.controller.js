(function () {
'use strict';

angular.module('daApp')
.controller('ReportController', ReportController);

ReportController.$inject = ['$location', '$rootScope', '$scope', 'qcService'];

function ReportController($location, $rootScope, $scope, qcService) {
  var reportCtrl = this;
  
  reportCtrl.submit = submit;

  $scope.msg = '';

  $rootScope.isLoaded = true;

  //////////

  function submit() {
    $location.path('/recording');
  }
}
}());
