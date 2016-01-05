// service to log errors/console output. Also saves it to localForage, with key 'logs' as one big string.

'use strict';

angular.module('daApp')
  .factory('utilityService', utilityService);

utilityService.$inject = ['logger'];

function utilityService(logger) {
  var utilityHandler = {};
  // CONSTANTS
  var constants = { 
    // sentinel value for invalid recordings
    'invalidTitle' : 'no_data.wav' 
  };

  utilityHandler.getConstant = getConstant;
  utilityHandler.stdErrCallback = stdErrCallback;

  return utilityHandler;

  //////////

  function getConstant(constant) {
    return constants[constant];
  }

  // standard error function to put as callback for rejected promises
  function stdErrCallback(arg) {
    logger.error(arg);
  }
}