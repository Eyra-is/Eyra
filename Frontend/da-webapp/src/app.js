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

angular.module('daApp', ['ngRoute', 'LocalForageModule', 'satellizer', 'ui.bootstrap'])

.constant('BACKENDURL', BACKENDURL)
.constant('CACHEBROKEN_REPORT', 'views/report.html')

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
      when('/evaluation', {
        templateUrl: 'views/evaluation.html',
        controller: 'EvaluationController',
        controllerAs: 'evalCtrl',
        resolve: {
          evalReady: function(routeService){
            return routeService.evalReady();
          }
        }
      }).
      when('/evaluation-login', {
        templateUrl: 'views/evaluation-login.html',
        controller: 'EvaluationLoginController',
        controllerAs: 'evalLoginCtrl'
      }).
      when('/info', {
        templateUrl: 'views/info.html',
        controller: 'InfoController',
        controllerAs: 'infoCtrl'
      }).
      when('/login', {
        templateUrl: 'views/login.html',
        controller: 'LoginController',
        controllerAs: 'loginCtrl'
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
      when('/recording-agreement', {
        templateUrl: 'views/recording-agreement.html',
        controller: 'RecordingAgreementController',
        controllerAs: 'agrCtrl'/*,
        resolve: {
          appInitialized: function(routeService){
            return routeService.appInitialized();
          }
        }*/
      }).
      when('/register-device', {
        templateUrl: 'views/register-device.html',
        controller: 'RegisterDeviceController',
        controllerAs: 'regdCtrl',
        resolve: {
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
      when('/sync', {
        templateUrl: 'views/sync.html',
        controller: 'SyncController',
        controllerAs: 'syncCtrl'
      }).
      otherwise({
        redirectTo: '/main'
      });
  }
]);
}());
