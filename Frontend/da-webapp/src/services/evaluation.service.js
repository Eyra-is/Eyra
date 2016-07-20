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

// service to query and process prompts and recordings from server for evaluation

(function () {

'use strict';

angular.module('daApp')
  .factory('evaluationService', evaluationService);

evaluationService.$inject = [ '$http',
                              'BACKENDURL',
                              'utilityService'];

function evaluationService($http, BACKENDURL, utilityService) {
  var evaluationHandler = {};
  var util = utilityService;

  evaluationHandler.initSet = initSet;
  evaluationHandler.getNext = getNext;

  var evalBufferSize = util.getConstant('evalBufferSize');
  var currentSetLabel = 'No set.';
  // contains at most 2 x evalBufferSize active elements (rest are undefined)
  // starts at 0 and then changes those elements to undefined after they have been used
  //         | -- active elements --  |
  // [ ud ud [stuff], [stuff], ..     ]
  //         ^                 
  //    setProgress   
  // format: [stuff] == [recLink, prompt]
  var currentSet = [];
  var setProgress = 0;

  return evaluationHandler;

  //////////

  function addToBuffer() {
    /*
    Adds evalBufferSize elements to currentSet.
    */
    return $http.get( BACKENDURL + '/evaluation/set/' + currentSetLabel 
                      + '/progress/' + currentSet.length
                      + '/count/' + evalBufferSize).then(function(response){
      currentSet = currentSet.concat(response.data);
      //console.log(response);
    });
  }

  function initSet(set) {
    /*
    Code using this service must call initSet with the set name before
    trying to use that set.
    */
    if (currentSetLabel !== set) {
      currentSetLabel = set;
      currentSet = [];
      setProgress = 0;
      // grab evalBufferSize set from server
      return addToBuffer();
    }    
  }

  function getNext() {
    /*
    Gets next link to recording and prompt.

    returns [recLink, prompt]
    */
    var next = currentSet[setProgress];
    currentSet[setProgress] = undefined;
    setProgress++;

    // when we are half # utts into the most recent buffer, add to the buffer (server call)
    if ((currentSet.length - setProgress) < (evalBufferSize / 2)) {
      addToBuffer();
    }

    return next;
  }

}
}());
