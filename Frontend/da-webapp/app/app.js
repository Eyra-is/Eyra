// **************************************************************************************** //

//                                         TODO                                             //

// sanitize user input for speakerId, etc. (maybe no need, only stored in database)
// CONSIDER moving logic in recordingsCallback() to a service or something, 
//   and out of main controller 
// Think about if we want to have a limit on how many sessions are sent in "sync"

// ***************************************************************************************** //

'use strict';

var putOnline = false;
var BACKENDURL = putOnline ? 'bakendi.localtunnel.me' : '127.0.0.1:5000';

angular.module('daApp', ['ngRoute', 'LocalForageModule'])

// make sure Angular doesn't prepend "unsafe:" to the blob: url
.config( [
  '$compileProvider',
  function( $compileProvider )
  {   
      $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|blob):/);
  }
])

.config([
  '$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/recording', {
        templateUrl: 'views/recording.html',
        controller: 'RecordingController'
      }).
      otherwise({
        redirectTo: '/recording'
      });
  }
])

// fix some angular issue with <audio ng-src="{{var}}"></audio>
// http://stackoverflow.com/questions/20049261/sce-trustasresourceurl-globally
.filter("trustUrl", ['$sce', function ($sce) {
  return function (url) {
    return $sce.trustAsResourceUrl(url);
  };
}]);




