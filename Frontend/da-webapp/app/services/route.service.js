// right now only handles route errors in route resolves

'use strict';

angular.module('daApp')
  .factory('routeService', routeService);

routeService.$inject = ['$location', '$q', '$rootScope', 'logger'];

function routeService($location, $q, $rootScope, logger) {
  var routeHandler = {};

  // handle rejected promises in route resolves
  $rootScope.$on("$routeChangeError", routeError);

  routeHandler.appInitialized = appInitialized;

  return routeHandler;

  //////////

  // used for routing back to main page if other pages are accessed manually (before app can be initialized)
  // returns a promise, true/false
  function appInitialized() {
    if ($rootScope.appInitialized) {
      return $q.when(true);
    } else {
      return $q.reject('App is not initialized.');
    }
  }

  // fired when for example app isn't initialized and we try to access another page manually
  function routeError(event, data) {
    logger.log("App not initialized, going back to main page.");
    $location.path('/main');
  }
}