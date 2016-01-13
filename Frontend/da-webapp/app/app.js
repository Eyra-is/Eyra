// **************************************************************************************** //

//                                         TODO                                             //

// sanitize user input for speakerId, etc. (maybe no need, only stored in database)
// CONSIDER moving logic in recordingsCallback() to a service or something, 
//   and out of main controller 
// Think about if we want to have a limit on how many sessions are sent in "sync"
// Think about adding underscore for service private functions
// Think about sending the token itself instead of the id (in case the id's get mixed up later in the db)
// Add (function(){}) around every js code to avoid putting stuff in global scope

// in production, the logger.error should NOT LOG ANYTHING

// ***************************************************************************************** //

'use strict';

var putOnline = false;
var BACKENDURL = putOnline ? 'bakendi.localtunnel.me' : '127.0.0.1:5000';

angular.module('daApp', ['ngRoute', 'LocalForageModule', 'satellizer'])

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
  '$authProvider',
  function($authProvider) {
    $authProvider.loginUrl = '//' + BACKENDURL + '/auth/login';
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



