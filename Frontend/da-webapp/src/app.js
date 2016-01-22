// **************************************************************************************** //

//                                         TODO                                             //

// sanitize user input for speakerId, etc. (maybe no need, only stored in database)
// Think about if we want to have a limit on how many sessions are sent in "sync"
// Think about adding underscore for service private functions
// Think about sending the token itself instead of the id (in case the id's get mixed up later in the db)

// in production, the logger.error should NOT LOG ANYTHING and CHANGE some ERRORS to LOGS for prod.
// remove all $q.defers (if possible) and use insead return values from .then callbacks
//   to promise chain, see: http://www.codelord.net/2015/09/24/$q-dot-defer-youre-doing-it-wrong/
// rename minFreeTokenIdx to highest used token idx
// make speaker and No comments. not show in start menu on default ok click
// remove alerts

// move bootstrap/jquery to local code, not through internet (because of offline capabilities)

// ***************************************************************************************** //

(function () {
'use strict';

// app 'options'
var BACKENDTYPE = 'localhost';
var BACKENDOPTS = {
                    'default':'/backend',
                    'localhost':'//localhost:5000',
                    'localtunnel':'//bakendi.localtunnel.me'
                  };
var BACKENDURL = BACKENDOPTS[BACKENDTYPE];

angular.module('daApp', ['ngRoute', 'LocalForageModule', 'satellizer'])

.constant('BACKENDURL', BACKENDURL)

// make sure Angular doesn't prepend "unsafe:" to the blob: url
.config([
  '$compileProvider',
  function($compileProvider) {   
      $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|blob):/);
  }
])

// fix some angular issue with <audio ng-src="{{var}}"></audio>
// http://stackoverflow.com/questions/20049261/sce-trustasresourceurl-globally
.filter("trustUrl", ['$sce', function ($sce) {
  return function (url) {
    return $sce.trustAsResourceUrl(url);
  };
}])

.config([
  '$authProvider', 'BACKENDURL',
  function($authProvider, BACKENDURL) {
    $authProvider.loginUrl = BACKENDURL + '/auth/login';
    $authProvider.tokenName = 'access_token'; // to accomodate for the Flask-JWT response token
    $authProvider.storageType = 'sessionStorage';
    $authProvider.authToken = 'JWT'; // sets the token prefix in requests, accomodate for Flask-JWT
  }
])

.config([
  '$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/login', {
        templateUrl: 'views/login.html',
        controller: 'LoginController',
        controllerAs: 'loginCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          }
        }
      }).
      when('/main', {
        templateUrl: 'views/main.html',
        controller: 'MainController',
        controllerAs: 'mainCtrl'
      }).
      when('/more', {
        templateUrl: 'views/more.html',
        controller: 'MoreController',
        controllerAs: 'moreCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          },
          loggedIn: function(routeService){
            return routeService.loggedIn();
          }
        }
      }).
      when('/recording', {
        templateUrl: 'views/recording.html',
        controller: 'RecordingController',
        controllerAs: 'recCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          }
        }
      }).
      when('/register-device', {
        templateUrl: 'views/register-device.html',
        controller: 'RegisterDeviceController',
        controllerAs: 'regdCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          },
          loggedIn: function(routeService){
            return routeService.loggedIn();
          }
        }
      }).
      when('/set-instructor', {
        templateUrl: 'views/set-instructor.html',
        controller: 'SetInstructorController',
        controllerAs: 'setiCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          },
          loggedIn: function(routeService){
            return routeService.loggedIn();
          }
        }
      }).
      when('/speaker-info', {
        templateUrl: 'views/speaker-info.html',
        controller: 'SpeakerInfoController',
        controllerAs: 'sinfoCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          }
        }
      }).
      when('/start', {
        templateUrl: 'views/start.html',
        controller: 'StartController',
        controllerAs: 'startCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          }
        }
      }).
      otherwise({
        redirectTo: '/main'
      });
  }
]);
}());
