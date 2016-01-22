(function () {
// service to handle some session logic, 
// info about start of session
// and logic to assemble the session (from speaker, instructor, device, rec, token and all that info)
//   and create the json object needed to send to server according to client server API.

'use strict';

angular.module('daApp')
  .factory('sessionService', sessionService);

sessionService.$inject = ['$q', 'dataService', 'localDbMiscService', 'logger'];

function sessionService($q, dataService, localDbMiscService, logger) {
  var sessionHandler = {};
  var dbService = localDbMiscService;

  var start_time;

  sessionHandler.setStartTime = setStartTime;
  sessionHandler.assembleSessionData = assembleSessionData;

  return sessionHandler;

  //////////

  // put together session json data needed for client server API comms
  // need the recording object as it is in recordingService and the id of the respective token
  // this is called by the recording controller on a single rec/token send.
  function assembleSessionData(rec, tokenId) {
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
                    [rec.title] = { 'tokenId' : tokenId };

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
    getGeneralInfo('deviceInfo', deviceInfoPromise, dbService.getDevice, undefined);

    return $q.all(dataPromises);
  }

  function setStartTime(time) {
    start_time = time;
  }
}
}());
