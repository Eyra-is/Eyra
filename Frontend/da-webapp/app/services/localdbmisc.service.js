// handles local forage actions regarding instructor, speaker and device setting

// stores speakers thusly: speakers/username = {'gender':gender, 'dob':dob, 'height':height}

'use strict';

angular.module('daApp')
  .factory('localDbMiscService', localDbMiscService);

localDbMiscService.$inject = ['$localForage', '$q', 'logger', 'utilityService'];

function localDbMiscService($localForage, $q, logger, utilityService) {
  var dbHandler = {};
  var util = utilityService;

  dbHandler.setSpeaker = setSpeaker;
  dbHandler.speakerExist = speakerExist;

  var speakersPrefix = 'speakers/';

  return dbHandler;

  //////////

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
          speakerPromise.reject('Speaker doesn\t exist.');
        }
      },
      function error(data){
        speakerPromise.reject(data);
      }
    );
    return speakerPromise.promise;
  }
}