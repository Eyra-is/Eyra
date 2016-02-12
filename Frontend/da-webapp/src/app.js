(function () {
'use strict';

// app 'options'
var BACKENDTYPE = 'default';
var BACKENDOPTS = {
                    'default':'/backend',
                    'localhost':'//localhost:5000',
                    'localtunnel':'//bakendi.localtunnel.me',
                    'off':'/nonpostablelink'
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
      when('/info', {
        templateUrl: 'views/info.html',
        controller: 'InfoController',
        controllerAs: 'infoCtrl',
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          }
        }
      }).
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
