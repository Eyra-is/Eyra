/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

(function () {
// handles 
//   route errors in route resolves,
//   login reroutes,

'use strict';

angular.module('daApp')
  .factory('routeService', routeService);

routeService.$inject = ['$location', '$q', '$rootScope', 'authenticationService', 'dataService', 'logger'];

function routeService($location, $q, $rootScope, authenticationService, dataService, logger) {
  var routeHandler = {};
  var authService = authenticationService;

  // handle rejected promises in route resolves
  $rootScope.$on("$routeChangeError", routeError);

  routeHandler.appInitialized = appInitialized;
  routeHandler.loggedIn = loggedIn;
  routeHandler.evalReady = evalReady;

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
    if (data.loadedTemplateUrl.indexOf('evaluation') > -1 && !$rootScope.evalReady) {
      logger.log('No info about user submitted for evaluation, redirecting to login.');
      $location.path('/evaluation-login');
      return;
    }
    // for some reason, couldn't find for example the rejection messages in the eventInfo or the data...
    if (!$rootScope.appInitialized) {
      logger.log('App not initialized, going back to main page.');
      $location.path('/main');
    } else if (!authService.loggedIn()) {
      logger.log('Access denied, no one logged in, going to login page.');
      $location.path('/login');
    }
  }

  function evalReady() {
    /*
    Returns truthy if evaluation is ready (meaning it is okay to navigate to evaluation.html).
    E.g. user has typed in credentials.
    */
    if ($rootScope.evalReady) {
      return $q.when(true);
    } else {
      return $q.reject('Error, no info about user submitted.');
    }
  }
}
}());
