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
// service to handle GPS location, basically a wrapper around navigator.geolocation

'use strict';

angular.module('daApp')
  .factory('locationService', locationService);

locationService.$inject = ['$q', 'dataService', 'logger'];

function locationService($q, dataService, logger) {
  var locHandler = {};

  locHandler.init = init;
  locHandler.setLocation = setLocation;

  // used simply to avoid calling those callbacks in setPosition
  //   when called later.
  var serviceInitialized = false;

  return locHandler;

  //////////

  function init(initCompleteCallback) {
    locHandler.initCompleteCallback = initCompleteCallback;

    // start by setting location as the default.
    dataService.set('location', 'Unknown.');

    if (navigator && navigator.geolocation) {
      setLocation(); // calls initCompleteCallback appropriately
    } else {
      logger.log('Geolocation is not supported.');
      serviceInitialized = true;
      initCompleteCallback(false);
    }
  }

  // takes in position object from navigator.geolocation.getCurrentPosition
  //   and returns a string representing the location
  //
  // format:
  //   'lat:'+lat+',lon:'+lon+',acc:'+acc 
  //    [+'\nalt:'+alt+'\naacc:'+altAcc+'\nhead:'+head+'\nspd:'+spd+'\ntime:'+time]
  //
  // where lat is latitude, lon is longitude, acc is accuracy of lat and lon,
  //   alt is altitude, altAcc is altitude accuracy, head is heading and spd is speed.
  //   alt, altAcc, head, spd and time are optional depending on device capabilities.
  //   
  // see Geolocation html5 API for more info on meaning of these values.
  function processPosition(position) {
    var coords = position.coords;
    var template = 'lat:'+coords.latitude+',lon:'+coords.longitude+',acc:'+coords.accuracy;
    if (coords.altitude) {
      template += '\nalt:'+coords.altitude;
    }
    if (coords.altitudeAccuracy) {
      template += '\naacc:'+coords.altitudeAccuracy;
    }
    if (coords.heading) {
      template += '\nhead:'+coords.heading;
    }
    if (coords.speed) {
      template += '\nspd:'+coords.speed;
    }
    if (position.timestamp) {
      template += '\ntime:'+position.timestamp;
    }
    return template;
  }

  // get location and put it in dataService (ram)
  // assumes navigator.geolocation defined
  // calls initCompleteCallback after finishing if serviceInitialized is false
  function setLocation() {
    navigator.geolocation.getCurrentPosition(
      function(position) {
        dataService.set('location', processPosition(position));

        if (!serviceInitialized) {
          serviceInitialized = true;
          locHandler.initCompleteCallback(true);
        }
      },
      function (err) {
        logger.error(err);
        if (!serviceInitialized) {
          serviceInitialized = true;          
          locHandler.initCompleteCallback(false);
        }
      }
    );
  }
}
}());
