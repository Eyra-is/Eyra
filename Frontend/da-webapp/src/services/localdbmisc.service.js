(function () {
// handles local forage actions regarding instructor, speaker and device setting
// along with other misc stuff

// see Client-server API for format, but something like this:
// stores speakers thusly: speakers/username = {'name':name, 'gender':gender, 'dob':dob, 'height':height [, 'deviceImei':imei]}
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
  dbHandler.getRecsSaved = getRecsSaved;
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

  function getRecsSaved() {
    /*
      Looks through local database for saved recordings, returns count of those as a promise.

      Consider doing this differently by incrementing saved sessions number 
      each time dbService.saveSession is successful. (this is easier)
    */
    var cntPromise = $q.defer();
    lfService.keys().then(
      function success(lfKeys) {
        if (lfKeys) {
          var cnt = 0;
          for (var i = 0; i < lfKeys.length; i++) {
            // quick reject of keys shorter than possible
            var curKey = lfKeys[i];
            if (curKey.length < 26) {
              // 26 is length of 'localDb/sessions/X/blobs/X'
              continue;
            }
            if (curKey.match(new RegExp('localDb/sessions/.*/blobs/.*'))) {
              cnt++;
            }
          }
          cntPromise.resolve(cnt);
        } else {
          cntPromise.reject('Error grabbing keys from local db.');
        }
      },
      function error(error) {
        cntPromise.reject(error);
      }
    );
    return cntPromise.promise;
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
          res.resolve(
            lfService.setItem(speakersPrefix + speakerName, speakerInfo)
          );
        },
        function error(response) {
          // still resolve, just without device imei
          res.resolve(
            lfService.setItem(speakersPrefix + speakerName, speakerInfo)
          );
          logger.error(response);
        }
      );
      return res.promise;
    }
  }
}
}());
