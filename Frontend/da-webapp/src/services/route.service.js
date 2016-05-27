/*
Copyright 2016 Matthias Petursson
Apache 2.0
*/

(function () {
// handles 
//   route errors in route resolves,
//   login reroutes,

'use strict';

angular.module('daApp')
  .factory('routeService', routeService);

routeService.$inject = ['$location', '$q', '$rootScope', 'authenticationService', 'logger'];

function routeService($location, $q, $rootScope, authenticationService, logger) {
  var routeHandler = {};
  var authService = authenticationService;

  // handle rejected promises in route resolves
  $rootScope.$on("$routeChangeError", routeError);

  routeHandler.appInitialized = appInitialized;
  routeHandler.loggedIn = loggedIn;

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

  function loggedIn() {
    if (authService.loggedIn()) {
      return $q.when(true);
    } else {
      return $q.reject('Access denied, no one logged in.');
    }
  }

  // fired when for example app isn't initialized and we try to access another page manually
  function routeError(eventInfo, data) {
    // for some reason, couldn't find for example the rejection messages in the eventInfo or the data...
    if (!$rootScope.appInitialized) {
      logger.log('App not initialized, going back to main page.');
      $location.path('/main');
    } else if (!authService.loggedIn()) {
      logger.log('Access denied, no one logged in, going to login page.');
      $location.path('/login');
    }
  }
}
}());
