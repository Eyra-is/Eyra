(function () {
'use strict';

angular.module('daApp')
.controller('ReportController', ReportController);

ReportController.$inject = ['$location', '$rootScope', '$scope', 'dataService'];

function ReportController($location, $rootScope, $scope, dataService) {
  var reportCtrl = this;
  
  reportCtrl.submit = submit;

  $scope.msg = '';
  $scope.QCReport = dataService.get('QCReport');

  $rootScope.isLoaded = true;

  //////////

  function submit() {
    $location.path('/recording');
  }
}
}());
