// handles local forage actions regarding instructor, speaker and device setting

// stores speakers thusly: speakers/username = {'gender':gender, 'dob':dob, 'height':height}

'use strict';

angular.module('daApp')
  .factory('localDbMiscService', localDbMiscService);

localDbMiscService.$inject = ['$localForage', '$q', 'logger', 'utilityService'];

function localDbMiscService($localForage, $q, logger, utilityService) {
  var dbHandler = {};
  var util = utilityService;

  dbHandler.userExist = userExist;

  var speakersPrefix = 'speakers/';

  return dbHandler;

  //////////

  // returns user info if he exists, otherwise rejects promise
  function userExist(username) {
    var user = $q.defer();
    $localForage.getItem(speakersPrefix + username).then(
      function success(speaker){
        if (speaker) {
          user.resolve(speaker);
        } else {
          user.reject('Speaker doesn\t exist.');
        }
      },
      function error(data){
        user.reject(data);
      }
    );
    return user.promise;
  }
}