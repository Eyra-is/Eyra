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

evaluationService.$inject = [ '$q',
                              'deliveryService',
                              'localDbMiscService',
                              'logger',
                              'utilityService'];

function evaluationService($q, deliveryService, localDbMiscService, logger, utilityService) {
  var evalHandler = {};
  var delService = deliveryService;
  var localDb = localDbMiscService;
  var util = utilityService;

  evalHandler.initSet = initSet;
  evalHandler.getNext = getNext;
  evalHandler.getProgress = getProgress;
  evalHandler.setInfoReadyCallback = angular.noop; // for unit tests, make placeholder
  evalHandler.undo = undo;

  var evalBufferSize = util.getConstant('evalBufferSize');
  var evalSubmitFreq = util.getConstant('evalSubmitFreq');
  var currentSetLabel = 'No set.';
  var currentUser = 'No user.';
  // contains at most 2 x evalBufferSize active elements (rest are undefined)
  // starts at 0 and then changes those elements to undefined after they have been used
  //         | -- active elements --  |
  // [ ud ud [stuff], [stuff], ..     ]
  //          ^                 
  //     setProgress   
  // format: [stuff] == [recLink, prompt]
  var currentSet = [];
  var setProgress = 0;
  var setCount = '?'; // total number of elements in set, updated through $http call

  // format as in "submitEvaluation" in client-server API or
  /*  [
        {
            "evaluator": "daphne",
            "sessionId": 5,
            "recordingFilename": "asdf_2016-03-05T11:11:09.287Z.wav",
            "grade": 2,
            "comments": "Bad pronunciation",
            "skipped": false
        },
        ..
      ]*/
  var evaluation = [];

  // keep a copy of the last utterance graded to allow for an undo.
  var lastUtterance = ['error_no_rec.wav', 'Not a real prompt.'];
  var undoFlag = false; // true if an undo utterance is the current one (used to prevent consecutive undos)

  return evalHandler;

  //////////

  function addToBuffer() {
    /*
    Adds evalBufferSize elements to currentSet.
    */
    return deliveryService.getFromSet(currentSetLabel, currentSet.length, evalBufferSize).then(
      function(response){
        currentSet = currentSet.concat(response.data);
        //console.log(response);
      }
    );
  }

  function initSet(set, user, setInfoReadyCallback, setCompleteCallback) {
    /*
    Code using this service must call initSet with the set name before
    trying to use that set.

    Parameters:
        set                   the set in question (a string)
        user                  a string representing the user doing the evaluation
        setInfoReadyCallback  call with info from server after receiving info about set
        setCompleteCallback   call after user has evaluated the entire set
    */
    evalHandler.setInfoReadyCallback = setInfoReadyCallback || evalHandler.setInfoReadyCallback;
    evalHandler.setCompleteCallback = setCompleteCallback || evalHandler.setCompleteCallback;
    if (currentUser !== user) {
      currentUser = user;
    }
    if (currentSetLabel !== set) {
      currentSetLabel = set;
      currentSet = [];
      setProgress = 0;
      delService.getSetInfo(set).then(function(response){
        evalHandler.setInfoReadyCallback(response);
        setCount = response.data.count;
      }, util.stdErrCallback);
      // get progress from server and then grab evalBufferSize from set from server
      return $q.when()
        .then(function(){
          return getProgressFromServer();
        })
        .then(function(){
          return addToBuffer();
        });
    }
  }

  function getNext(grade, comments) {
    /*
    Gets next link to recording and prompt.

    Parameters:
      grade     the grade for the current prompt (1-4), if undefined, 
                means the prompt was skipped. If grade === 'initial', means this
                is the initial grab of a prompt, meaning we want neither
                an evaluation or to mark it as skipped.

    If we have reached the end of the specified set, notify the controller.

    returns [recLink, prompt]
    */
    if (grade === 'initial') {
      return currentSet[setProgress];
    }

    updateEvaluation(grade, comments); // add the results for current recording received from evalCtrl
    // additional - 1 in (setProgress + 1 - 1) % evalSubmitFreq === 0 to account for the one we
    // retain for undo purposes.
    if ((setProgress + 1 - 1) % evalSubmitFreq === 0
        || setProgress === setCount - 1) {
      // submit the current evaluation if our progress is a multiple of the frequency
      // or if we have reached the end of the set
      submitEvaluation();
    }

    if (setProgress === setCount - 1) {
      evalHandler.setCompleteCallback();
      return ['', ''];
    }

    var next = currentSet[setProgress + 1];
    lastUtterance = currentSet[setProgress];
    currentSet[setProgress] = undefined;
    setProgress++;

    // when we are half # utts into the most recent buffer, add to the buffer (server call)
    if ((currentSet.length - setProgress) < (evalBufferSize / 2)) {
      addToBuffer();
    }

    undoFlag = false;
    return next;
  }

  function getProgress() {
    return setProgress;
  }

  function getProgressFromServer() {
    return delService.getUserProgress(currentUser, currentSetLabel).then(function(response){
      setProgress = response.data.progress || setProgress;
      if (setProgress > 0) {
        currentSet[setProgress - 1] = undefined;
      }
    });
  }

  function submitEvaluation() {
    /*
    Submits evaluation to server. Sends everything except the most recent grade (for 
    undo purposes). (unless we have reached the end of the set, in which case send everything)

    Takes a copy, and then deletes what it sent on a successful send.
    */
    var evalCopy = setProgress === setCount - 1 ? 
                      JSON.parse(JSON.stringify(evaluation)) :
                      JSON.parse(JSON.stringify(evaluation.slice(0, evaluation.length - 1)));
    var count = evalCopy.length;
    var progress = setProgress;

    if (count === 0) {
      return;
    }

    delService.submitEvaluation(currentSetLabel, evalCopy).then(
      function success(response) {
        deleteFromEvaluation(count);
      }, function error(response) {
        logger.error('Error sending to server, saving evaluation in local db.');
        // save our failed send copy locally, but abandon trying to send if we
        // get any of the errors currently submitted after handling by server.
        // currently only: 400 and 500
        if (response.status === 400 || response.status === 500) {
          localDb.saveEvaluation(currentUser, currentSetLabel, evalCopy).then(
            function success(response) {
              deleteFromEvaluation(count);
            }, util.stdErrCallback
          );
        } else {
          localDb.saveEvaluation(currentUser, currentSetLabel, evalCopy).then(
            angular.noop, util.stdErrCallback);
        }
      }
    );

    function deleteFromEvaluation(count) {
      /*
      Delete elements 0 to count-1 from evaluation array.
      */
      evaluation.splice(0, count);
    }
  }

  function undo() {
    /*
    Undo the last grade to be able to grade again. Can only be used on the last grade, no more!

    Returns element on same format as "getNext", i.e. [recLink, prompt]
    */
    if (undoFlag) {
      logger.error('Undo called while undo going on. Shouldn\'t happen.');
      return;
    }
    undoFlag = true;

    currentSet[setProgress - 1] = lastUtterance;
    evaluation.pop(); // delete last grade from evaluation
    setProgress--;

    return lastUtterance;
  }

  function updateEvaluation(grade, comments) {
    /*
    Grabs relevant info from e.g. currentSet[setProgress], grade, currentUser
    and adds it to our evaluation array containing the results for current recording.

    Returns nothing.
    */
    // extract sessionId and recordingFilename from our recLink in currentSet[setProgress]
    var recLink = currentSet[setProgress][0];
    var sessionIdMatch = recLink.match(/session_(\d+)/);
    var sessionId = sessionIdMatch ? Number(sessionIdMatch[1]) : -1; // fallback session is -1
    var recNameMatch = recLink.match(/session_\d+\/(.*)$/);
    var recName = recNameMatch ? recNameMatch[1] : 'error_no_rec.wav';

    var uttEval = {};
    uttEval.evaluator = currentUser;
    uttEval.sessionId = sessionId;
    uttEval.recordingFilename = recName;
    uttEval.grade = grade || -1;
    uttEval.comments = comments || 'No comments.';
    uttEval.skipped = grade ? false : true;

    evaluation.push(uttEval);
  }
}
}());
