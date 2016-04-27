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
  utilityHandler.percentage = percentage;
  utilityHandler.stdErrCallback = stdErrCallback;

  var CONSTANTS = { 
    // sentinel value for invalid recordings
    'invalidTitle' : 'no_data.wav',
    'tokenThreshold' : 40,
    'tokenGetCount' : 520,
    'QCAccThreshold' : 0.2,
    'QCFrequency' : 5, // per sessions sent
    'QCInitRecThreshold' : 10, // recording count before QC can report, adjustment period for speaker
    'TokenAnnouncementFreq' : 50,
    'TokenCountGoal' : 500
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

  // part=3, whole=10, accuracy=2 would result in 33.33
  function percentage(part, whole, accuracy) {
    
    return Math.round(part/whole*100 * Math.pow(10, accuracy)) / Math.pow(10, accuracy);
  }

  // standard error function to put as callback for rejected promises
  function stdErrCallback(arg) {
    logger.error(arg);
  }
}
}());
