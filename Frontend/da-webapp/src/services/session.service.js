/*
Copyright 2016 Matthias Petursson
Apache 2.0
*/

(function () {
// service to handle some session logic, 
// info about start of session
// and logic to assemble the session (from speaker, instructor, device, rec, token and all that info)
//   and create the json object needed to send to server according to client server API.

'use strict';

angular.module('daApp')
  .factory('sessionService', sessionService);

sessionService.$inject = ['$q', '$rootScope', 'dataService', 'localDbMiscService', 'logger', 'utilityService'];

function sessionService($q, $rootScope, dataService, localDbMiscService, logger, utilityService) {
  var sessionHandler = {};
  var dbService = localDbMiscService;
  var util = utilityService;

  var start_time;

  sessionHandler.assembleSessionData = assembleSessionData;
  sessionHandler.handleSessionResponse = handleSessionResponse;
  sessionHandler.setStartTime = setStartTime;

  return sessionHandler;

  //////////

  // put together session json data needed for client server API comms
  // need the recording object as it is in recordingService and the respective token
  // this is called by the recording controller on a single rec/token send.
  // token is on format: { 'id':id, 'token':token }
  function assembleSessionData(rec, token) {
    var sessionData = $q.defer();
    // start by getting the info that might take local db access (async)
    // i.e. speakerInfo, instructorId and deviceInfo
    getPossiblyAsyncData().then(
      function success(data) {
        var end_time = new Date().toISOString();
        var speakerInfoFallback = {
          'name':'No user.',
          'gender':'Other',
          'height':'1337',
          'dob':'19 B.C.',
          'deviceImei':''
        };
        var instructorIdFallback = 1; 
        var deviceInfoFallback = {
          'userAgent':navigator.userAgent,
          'imei':''
        };
        if (!data.deviceInfo && $rootScope.isWebView) {
          deviceInfoFallback['imei'] = AndroidConstants.getImei();
        }
        // fix if speaker is created before device is registered, add speaker deviceImei here
        if (data.deviceInfo && data.deviceInfo['imei'] && data.deviceInfo['imei'] !== '') {
          if (data.speakerInfo) {
            data.speakerInfo['deviceImei'] = data.deviceInfo['imei'];
          }
        }
        // special case for speakerInfo, remove tokensRead attribute
        data.speakerInfo = speakerInfoCorrection(data.speakerInfo);

        var tempSessionData = {                                                                  
                                "type":'session', 
                                "data":
                                {
                                  "speakerInfo"    : (data.speakerInfo || speakerInfoFallback),
                                  "instructorId"   : (data.instructorId || instructorIdFallback),
                                  "deviceInfo"     : (data.deviceInfo || deviceInfoFallback),
                                  "location"       : (dataService.get('location') || 'Unknown.'),
                                  "start"          : (start_time || 'No start time set. (error)'),
                                  "end"            : end_time,
                                  "comments"       : (dataService.get('comments') || 'No comments.'),
                                  "recordingsInfo" : {}
                                }
                              };
        tempSessionData['data']['recordingsInfo']
                    [rec.title] = { 'tokenId' : token['id'], 'tokenText' : token['token'] };

        sessionData.resolve(tempSessionData);
      },
      function error(response) {
        sessionData.reject(response);
      }
    );

    return sessionData.promise;
  }

  // attempts first to get the info specified by key from dataService
  // if it fails, it tries to get it from localDb and returns a promise
  // which resolves to falsy on failure, and the info on success
  //
  // dbServiceArg is an optional argument to the dbServiceFunction, keep it undefined if not used
  //
  // example usage: 
  //   getGeneralInfo('speakerInfo', $q.defer(), dbService.getSpeaker, 'josh9')
  // would resolve returnPromise with either data from dataService or localDb
  function getGeneralInfo(key, returnPromise, dbServiceFunction, dbServiceArg) {
    // start by checking if we have key-data in memory
    var keyInfo = dataService.get(key);
    if (keyInfo) {
      returnPromise.resolve(keyInfo);
    } else {
      // next try to get it from local db
      dbServiceFunction(dbServiceArg).then(
        function success(info){
          returnPromise.resolve(info);
        },
        function error(response){
          // we didn't get any info, so return falsy
          // fallback info will be used in assembleSessionData
          // important we don't want any rejections in $q.all return value
          // og getPossiblyAsyncData function
          returnPromise.resolve(undefined);
          logger.error(response);
        }
      );
    }
  }

  // called from assembleSessionData
  // gets the info that might take local db access (async)
  // i.e. speakerInfo, instructorId and deviceInfo
  // returns object of promises, dataPromises = 
  //    { 'speakerInfo':speakerInfo, 
  //      'instructorId':instructorId, 
  //      'deviceInfo':deviceInfo }
  function getPossiblyAsyncData() {
    var speakerInfoPromise = $q.defer();
    var instructorIdPromise = $q.defer();
    var deviceInfoPromise = $q.defer();
    var dataPromises = 
      {
        'speakerInfo'  : speakerInfoPromise.promise,
        'instructorId' : instructorIdPromise.promise,
        'deviceInfo'   : deviceInfoPromise.promise
      };
    var speakerName = dataService.get('speakerName');
    if (!speakerName) speakerName = undefined; // make sure it's undefined for our getGeneralInfo call
    // the infoPromises will be changed after the function calls
    getGeneralInfo('speakerInfo', speakerInfoPromise, dbService.getSpeaker, speakerName);
    getGeneralInfo('instructorId', instructorIdPromise, dbService.getInstructorId, undefined);
    getGeneralInfo('device', deviceInfoPromise, dbService.getDevice, undefined);

    return $q.all(dataPromises);
  }

  function handleSessionResponse(response) {
    /*
      Handles response from server after sending a session, either through 
      delService.submitRecordings or delService.sendLocalSession.

      parameters:
        response    http response from server, should contain response.data as e.g.
                    { 'sessionId' : int, 'speakerId': int, 'deviceId' : int, 'recsDelivered' : int }

      return:
                    returns recsDelivered
    */

    // we may have gotten a deviceId and speakerId from server, in which case
    //   we handle that by setting it in RAM and local database, if it is different
    //   from the id's there.
    var speakerId = response.data.speakerId;
    var deviceId = response.data.deviceId;
    if (deviceId) updateDevice(deviceId); 
    if (speakerId) updateSpeakerInfo(speakerId);

    // update how many prompt recordings have actually arrived at server
    var recsDelivered = dataService.get('recsDelivered') || 0;
    var delivered = response.data.recsDelivered;
    if (delivered) {
      recsDelivered = delivered;
      dataService.set('recsDelivered', recsDelivered);
      var sInfo = dataService.get('speakerInfo');
      if (sInfo) {
        sInfo.recsDelivered = recsDelivered;
        dataService.set('speakerInfo', sInfo);
        dbService.setSpeaker(sInfo.name, sInfo)
          .then(angular.noop, util.stdErrCallback);
      }
      // TODO
      // else get from ldb and update recsDelivered. speakerInfo should be set though, according to start.controller
    }
    return recsDelivered;
  }

  function setStartTime(time) {
    start_time = time;
  }

  function speakerInfoCorrection(oldSpeakerInfo) {
    // function creates new speakerInfo object without tokensRead and recsDelivered

    var newSpeakerInfo = JSON.parse(JSON.stringify(oldSpeakerInfo)); // copy object
    delete newSpeakerInfo.tokensRead;
    delete newSpeakerInfo.recsDelivered;
    return newSpeakerInfo;
  }

  // updates device or speakerInfo by checking for an id, and adding
  //   it. Both in RAM and local database.
  // id is the id supplied from the backend
  // updateDevice() and updateSpeakerInfo() aren't DRY unfortunately
  //   due to the need for speakerName in the latter case (could be fixed)
  function updateDevice(id) {
    var device = dataService.get('device');
    if (device) {
      // either device.deviceId is undefined, in which case we add it
      // or it is different from our id, in which case we update it
      // otherwise, we assume we don't need to change anything
      if (device.deviceId !== id) {
        device.deviceId = id;
        dataService.set('device', device); // this line might be redundant
        dbService.setDevice(device)
          .then(angular.noop, util.stdErrCallback);
      }
    } else {
      // no device in ram, check in local db
      dbService.getDevice().then(
        function success(device) {
          if (device) {
            device.deviceId = id;
          } else {
            device = {
              'userAgent' : navigator.userAgent,
              'deviceId' : id
            };
          }
          if (!device.imei && $rootScope.isWebView) {
            device['imei'] = AndroidConstants.getImei();
          }
          dataService.set('device', device);
          dbService.setDevice(device)
            .then(angular.noop, util.stdErrCallback);
        },
        util.stdErrCallback
      );
    }
  }

  function updateSpeakerInfo(id) {
    var speakerName = dataService.get('speakerName'); // this is the only thing we are guaranteed is in RAM
    var speakerInfo = dataService.get('speakerInfo');
    if (speakerInfo) {
      // either speakerInfo.speakerId is undefined, in which case we add it
      // or it is different from our id, in which case we update it
      // otherwise, we assume we don't need to change anything
      if (speakerInfo.speakerId !== id) {
        speakerInfo.speakerId = id;
        dataService.set('speakerInfo', speakerInfo); // this line might be redundant
        dbService.setSpeaker(speakerName, speakerInfo)
          .then(angular.noop, util.stdErrCallback);
      }
    } else {
      // no speakerInfo in ram, check in local db
      dbService.getSpeaker(speakerName).then(
        function success(speakerInfo) {
          if (speakerInfo) {
            speakerInfo.speakerId = id;
            dataService.set('speakerInfo', speakerInfo);
            dbService.setSpeaker(speakerName, speakerInfo)
              .then(angular.noop, util.stdErrCallback);
          } else {
            logger.error('Speaker not in database, ' + speakerName + '.');
          }
        },
        util.stdErrCallback
      );
    }
  }
}
}());
