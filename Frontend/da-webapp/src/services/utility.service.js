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
// service with utility functions for the app

'use strict';

angular.module('daApp')
  .factory('utilityService', utilityService);

utilityService.$inject = ['logger'];

function utilityService(logger) {
  var utilityHandler = {};

  utilityHandler.getConstant = getConstant;
  utilityHandler.getIdxFromPath = getIdxFromPath;
  utilityHandler.generateUUID = generateUUID;
  utilityHandler.percentage = percentage;
  utilityHandler.stdErrCallback = stdErrCallback;

  var CONSTANTS = { 
    'invalidTitle' : 'no_data.wav', // sentinel value for invalid recordings
    'tokenThreshold' : 600, 
    'tokenGetCount' : 1500, 
    'QCAccThreshold' : 0.2,
    'QCFrequency' : 5, // per sessions sent
    'QCInitRecThreshold' : 10, // recording count before QC can report, adjustment period for speaker
    'tokenAnnouncementFreq' : 500,
    'tokenCountGoal' : 500,
    'syncRecCountPerSend' : 5, // recs to send each transmission to server during a Sync operation,
    'evalBufferSize' : 5, // number of prompts and/or recs to fetch and keep in memory during evaluation
    'evalSubmitFreq' : 5, // per utterance graded, after X send to server
    'RECAGREEMENT' : true // include the recording participant agreement
  };
  

  return utilityHandler;

  //////////

  function getConstant(constant) {
    return CONSTANTS[constant];
  }

  // e.g if path === 'localDb/sessions/blob/5'
  // this will return 5
  // returns -1 on error
  function getIdxFromPath(path) {
    var idx = -1;
    try {
      var tokens = path.split('/');
      idx = parseInt(tokens[tokens.length - 1]);
      if (!idx && idx !== 0) idx = -1; // allow 0 as index
    } catch (e) {
      logger.error(e);
    }
    return idx;
  }

  function generateUUID() {
    // Thanks, broofa, http://stackoverflow.com/a/2117523/5272567
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
      return v.toString(16);
    });
  }

  // part=3, whole=9, accuracy=2 would result in 33.33
  function percentage(part, whole, accuracy) {
    return Math.round(part/whole*100 * Math.pow(10, accuracy)) / Math.pow(10, accuracy);
  }

  // standard error function to put as callback for rejected promises
  function stdErrCallback(arg) {
    logger.error(arg);
  }
}
}());
