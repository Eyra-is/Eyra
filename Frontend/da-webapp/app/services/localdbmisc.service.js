// handles local forage actions regarding instructor, speaker and device setting

// stores speakers thusly: speakers/username = {'gender':gender, 'dob':dob, 'height':height}
// stores instructors as: instructorId = 13
// stores devices as: device = {'userAgent':'user agent string', 'imei':12363563456}

'use strict';

angular.module('daApp')
  .factory('localDbMiscService', localDbMiscService);

localDbMiscService.$inject = ['$localForage', '$q', 'logger', 'utilityService'];

function localDbMiscService($localForage, $q, logger, utilityService) {
  var dbHandler = {};
  var util = utilityService;

  dbHandler.getDevice = getDevice;
  dbHandler.setDevice = setDevice;
  dbHandler.getInstructorId = getInstructorId;
  dbHandler.setInstructorId = setInstructorId;
  dbHandler.getSpeaker = getSpeaker;
  dbHandler.setSpeaker = setSpeaker;
  dbHandler.speakerExist = speakerExist;

  var devicePath = 'device';
  var instructorIdPath = 'instructorId';
  var speakersPrefix = 'speakers/';

  return dbHandler;

  //////////

  function getDevice() {
    return $localForage.getItem(devicePath);
  }

  // device on format as in client-server API
  function setDevice(device) {
    return $localForage.setItem(devicePath, device);  
  }

  function getInstructorId() {
    return $localForage.getItem(instructorIdPath);
  }

  function setInstructorId(instructorId) {
    return $localForage.setItem(instructorIdPath, instructorId);
  }

  function getSpeaker(speakerName) {
    return $localForage.getItem(speakersPrefix + speakerName);
  }

  function setSpeaker(speakerName, speakerInfo) {
    return $localForage.setItem(speakersPrefix + speakerName, speakerInfo);
  }

  // returns speaker info if he exists, otherwise rejects promise
  function speakerExist(speakerName) {
    var speakerPromise = $q.defer();
    $localForage.getItem(speakersPrefix + speakerName).then(
      function success(speaker){
        if (speaker) {
          speakerPromise.resolve(speaker);
        } else {
          speakerPromise.reject('Speaker doesn\'t exist.');
        }
      },
      function error(data){
        speakerPromise.reject(data);
      }
    );
    return speakerPromise.promise;
  }
}