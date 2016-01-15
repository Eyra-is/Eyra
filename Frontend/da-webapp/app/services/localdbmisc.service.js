// handles local forage actions regarding instructor, speaker and device setting

// stores speakers thusly: speakers/username = {'gender':gender, 'dob':dob, 'height':height}
// stores instructors as: instructorId = 13
// stores devices as: device = {'userAgent':'user agent string', 'imei':12363563456}

'use strict';

angular.module('daApp')
  .factory('localDbMiscService', localDbMiscService);

localDbMiscService.$inject = ['$q', 'dataService', 'logger', 'myLocalForageService', 'utilityService'];

function localDbMiscService($q, dataService, logger, myLocalForageService, utilityService) {
  var dbHandler = {};
  var lfService = myLocalForageService;
  var util = utilityService;

  dbHandler.getDevice = getDevice;
  dbHandler.setDevice = setDevice;
  dbHandler.getInstructorId = getInstructorId;
  dbHandler.setInstructorId = setInstructorId;
  dbHandler.getSpeaker = getSpeaker;
  dbHandler.setSpeaker = setSpeaker;

  var devicePath = 'device';
  var instructorIdPath = 'instructorId';
  var speakersPrefix = 'speakers/';

  return dbHandler;

  //////////

  function getDevice() {
    return lfService.getItem(devicePath);
  }

  // device on format as in client-server API
  function setDevice(device) {
    return lfService.setItem(devicePath, device);  
  }

  function getInstructorId() {
    return lfService.getItem(instructorIdPath);
  }

  function setInstructorId(instructorId) {
    return lfService.setItem(instructorIdPath, instructorId);
  }

  function getSpeaker(speakerName) {
    return lfService.getItem(speakersPrefix + speakerName);
  }

  // here speakerData does not necessarily contain the optional imei, therefore
  //   always check if we can get that and submit before we send.
  function setSpeaker(speakerName, speakerInfo) {
    var device = dataService.get('device');
    if (device && device['imei'] && device['imei'] !== '') {
      speakerInfo['deviceImei'] = device['imei'];
      return lfService.setItem(speakersPrefix + speakerName, speakerInfo);
    } else {
      var res = $q.defer();
      getDevice().then(
        function success(device){
          if (device && device['imei'] && device['imei'] !== '') {
            speakerInfo['deviceImei'] = device['imei'];
          }
          $q.resolve(
            lfService.setItem(speakersPrefix + speakerName, speakerInfo)
          );
        },
        function error(response) {
          // still resolve, just without device imei
          $q.resolve(
            lfService.setItem(speakersPrefix + speakerName, speakerInfo)
          );
          logger.error(response);
        }
      );
      return res.promise;
    }
  }
}