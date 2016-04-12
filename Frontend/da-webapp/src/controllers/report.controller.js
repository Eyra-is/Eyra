(function () {
'use strict';

angular.module('daApp')
.controller('ReportController', ReportController);

ReportController.$inject = ['$location', '$rootScope', '$sce', '$scope', 'dataService'];

function ReportController($location, $rootScope, $sce, $scope, dataService) {
  var reportCtrl = this;

  $scope.msg = '';
  // https://docs.angularjs.org/api/ngSanitize/service/$sanitize
  $scope.QCReport = function() {
    console.log('scoping QCReport')
    console.log($sce.trustAsHtml(dataService.get('QCReport')));
    return $sce.trustAsHtml(dataService.get('QCReport') || '<p>Nothing to report.</p>');
  }

  $rootScope.isLoaded = true;

  //////////

  
}
}());
