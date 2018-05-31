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

(function () {
'use strict';

angular.module('daApp')
.controller('EvaluationController', EvaluationController);

EvaluationController.$inject = ['$document',
                                '$http',
                                '$q',
                                '$rootScope',
                                '$scope',
                                '$timeout',
                                'dataService',
                                'evaluationService',
                                'logger',
                                'utilityService'];

function EvaluationController($document, $http, $q, $rootScope, $scope, $timeout, dataService, evaluationService, logger, utilityService) {
  var evalCtrl = this;
  var evalService = evaluationService;
  var util = utilityService;

  evalCtrl.action = action;
  evalCtrl.skip = skip;
  evalCtrl.undo = undo;

  $scope.msg = ''; // single information msg
  $rootScope.isLoaded = false;

  evalCtrl.actionBtnDisabled = false;
  evalCtrl.skipBtnDisabled = false;
  evalCtrl.undoBtnDisabled = true;

  $scope.grade = util.getConstant('GRADETEXT');
  $scope.comment = util.getConstant('COMMENTTEXT');
  $scope.skip = util.getConstant('SKIPTEXT');
  $scope.undo = util.getConstant('UNDOTEXT');
  $scope.autoplay = util.getConstant('AUTOPLAYTEXT');
  $scope.uttGraded = util.getConstant('UTTGRADEDTEXT');
  $scope.user = util.getConstant('USERTEXT');
  $scope.set = util.getConstant('SETTEXTMIN');

  var actionType = 'play'; // current state

  var PLAYTEXT = util.getConstant('PLAYTEXT'); // text under the buttons
  var PAUSETEXT = util.getConstant('PAUSETEXT');
  var PLAYGLYPH = 'glyphicon-play'; // bootstrap glyph class
  var PAUSEGLYPH = 'glyphicon-pause';
  evalCtrl.actionText = PLAYTEXT;
  evalCtrl.actionGlyph = PLAYGLYPH;


  //var EVALUATIONCOMMENTSURL = 'json/evaluation-comments.json'; //uncomment for English
  var EVALUATIONCOMMENTSURL = 'json/evaluation-comments-isl.json'; //comment out for English
  evalCtrl.commentOpts = [];

  evalCtrl.currentUser = dataService.get('currentUser');
  evalCtrl.currentSet = dataService.get('currentSet');
  var isSetComplete = false;
  var undoFlag = false; // true if an undo utterance is the current one (used to circumvent needing to listen for grading)

  // save reference to the audio element on the page, for play/pause
  // thanks, Shushanth Pallegar, http://stackoverflow.com/a/30899643/5272567
  // TODO: would probably be nicer to make a directive
  var audioPlayback = $document.find("#audio-playback")[0];
  if (audioPlayback) {
    audioPlayback.addEventListener('ended', audioEnded);
  } else {
    $scope.msg = util.getConstant('PLAYBACKERRORMSG');
  }

  activate();

  ////////// 
  
  function activate() {
    evalCtrl.displayToken = util.getConstant('NOTOKENTEXT');
    evalCtrl.uttsGraded = 0;
    evalCtrl.setCount = '?';
    evalCtrl.comments = '';
    evalCtrl.autoplay = false;

    evalCtrl.grade = undefined; // initially unchecked
    $scope.$watch(function(){ return evalCtrl.grade; }, watchGrade);

    var promise = initSet(evalCtrl.currentSet, evalCtrl.currentUser);
    if (promise) {
      promise.then(
        function success(data){
          evalCtrl.uttsGraded = evalService.getProgress();
          // grab initial prompt/utterance
          return next('initial').then(
            function success(response) {
              logger.log('Ready for evaluation.');
            },
            function error(error) {
              $scope.msg = util.getConstant('SOMETINGWRONGERRORMSG');
              logger.error(error);
            });
        }, 
        function error(response){
          $scope.msg = util.getConstant('SOMETINGWRONGERRORMSG');
          logger.error(response);
        }
      )
      // grab comments from server
      .then(
        function success(data){
          return $http.get(EVALUATIONCOMMENTSURL).then(
            function success(response) {
              evalCtrl.commentOpts = response.data;
            },
            function error(response) {
              $scope.msg = util.getConstant('FETCHCOMMENTERRORMSG');
              logger.error(response);
            }
          );
        },
        function error(response){
          $scope.msg = util.getConstant('SOMETINGWRONGERRORMSG');
          logger.error(response);
        }
      )
      // now page is loaded
      .then(
        function success(data){
          $rootScope.isLoaded = true;
        }, util.stdErrCallback
      );
    }
  }

  function action() {
    /*
    Signifies the combined rec/pause button
    */
    evalCtrl.actionBtnDisabled = true;
    if (actionType === 'play') {
      play();
    } else if (actionType === 'pause') {
      pause();
    }
    toggleActionBtn();
    evalCtrl.actionBtnDisabled = false;
  }

  function audioEnded() {
    /*
    Automatically hit pause on our custom controls on reaching audio playback end.
    */
    if (actionType === 'pause') {
      action();
      $scope.$apply();
    }
  }

  function disableAllControls() {
    /*
    Disable most user interaction on page.
    */
    evalCtrl.actionBtnDisabled = true;
    evalCtrl.skipBtnDisabled = true;
    evalCtrl.undoBtnDisabled = true;
  }

  function initSet(set, user) {
    /*
    Returns promise resolved when evalService has init'd set.
    */
    return evalService.initSet(set, user, setInfoReadyCallback, setCompleteCallback);
  }

  function next(grade, comments) {
    /*
    Sets next recording and prompt.

    Parameters:
      grade     the grade for the current prompt (1-4), if undefined, 
                means the prompt was skipped

    Return: promise which is resolved when the audio playback is ready to go.
    */
    var recNPrompt = evalService.getNext(grade, comments);
    return handleRecNPrompt(recNPrompt);
  }

  function handleRecNPrompt(recNPrompt) {
    /*
    Update the current recording/prompt pair.
    
    Parameters:
      recNPrompt    format [recLink, prompt]

    Return: promise when playback is ready to go.
    */
    evalCtrl.grade = undefined; // reset grade
    evalCtrl.recording = recNPrompt[0];
    evalCtrl.displayToken = recNPrompt[1];

    var playbackReady = $q.defer();

    // thanks QuasarDonkey, http://stackoverflow.com/a/24600597/5272567 for the Mobi test quote
    if (/Mobi/i.test(navigator.userAgent)) {
      // workaround for mobile playback, where it didn't work on chrome/android.
      // fetch blob at url using xhr, and use url generated from that blob.
      // see issue: https://code.google.com/p/chromium/issues/detail?id=227476
      // thanks, gbrlg
      $http.get(evalCtrl.recording, {'responseType':'blob'}).then(
        function success(response) {
          var reBlob = response.data;
          if (reBlob) {
            evalCtrl.recording = (window.URL || window.webkitURL).createObjectURL(reBlob);
          }
          playbackReady.resolve(true);
        }, 
        function error(error) {
          logger.error(error);
          $scope.msg = util.getConstant('SOMETINGWRONGERRORMSG');
          playbackReady.reject(false);
        }
      );
    } else {
      return $q.resolve(true);
    }

    return playbackReady.promise;
  }

  function play() {
    /*
    Start playback on audio.
    */
    audioPlayback.play();
  }

  function skip() {
    evalCtrl.skipBtnDisabled = true;
    if (actionType === 'pause') {
      toggleActionBtn();
    }
    next(undefined).then(function(){
      evalCtrl.skipBtnDisabled = false;
    }, util.stdErrCallback);
  }

  function pause() {
    audioPlayback.pause();
  }

  function setCompleteCallback() {
    $scope.msg = util.getConstant('GRADECOMPLETETEXT');
    isSetComplete = true;
    disableAllControls();
  }

  function setInfoReadyCallback(info) {
    /*
    Function supplied to evaluation.service as a callback for when it has received
    info about the set (currently only count).
    */
    evalCtrl.setCount = info.data.count;
  }

  function toggleActionBtn() {
    if (actionType === 'play') {
      actionType = 'pause';
      evalCtrl.actionText = PAUSETEXT;
      evalCtrl.actionGlyph = PAUSEGLYPH;
    } else if (actionType === 'pause') {
      actionType = 'play';
      evalCtrl.actionText = PLAYTEXT;
      evalCtrl.actionGlyph = PLAYGLYPH;
    }
  }

  function undo() {
    /*
    Undo last grade and grade again. Can only be used to go back one grade.
    */
    evalCtrl.undoBtnDisabled = true;
    undoFlag = true;

    var recNPrompt = evalService.undo();
    evalCtrl.uttsGraded--;
    handleRecNPrompt(recNPrompt).then(function(){
      if (actionType === 'pause') {
        toggleActionBtn();
      }
    }, util.stdErrCallback);
  }

  function watchGrade() {
    /*
    Passed as a function into $scope.$watch.

    Notifies us when a grade radio button has been ticked,
    and in doing so saves the choice and triggeres the next recording.
    */
    // if valid grade has been clicked
    // thanks, Gumbo, http://stackoverflow.com/a/4728164/5272567
    if (['1','2','3','4'].indexOf(evalCtrl.grade) > -1 && !isSetComplete) {
      logger.log('Grade: '+evalCtrl.grade+', and comment: '+evalCtrl.comments+
                 ', detected for prompt: '+evalCtrl.displayToken);

      $scope.msg = '';
      evalCtrl.skipBtnDisabled = true;

      // if grade is low (2 or lower) make comment mandatory
      if (evalCtrl.comments === '' && evalCtrl.grade <= 2) {
        $scope.msg = util.getConstant('COMMENTMISSINGMSG');
        evalCtrl.grade = undefined;
        return;
      }
      // make evaluator at least have started listening
      if (audioPlayback.currentTime === 0 && !undoFlag) {
        $scope.msg = util.getConstant('LISTENMSG');
        evalCtrl.grade = undefined;
        return;
      }

      evalCtrl.uttsGraded++;

      next(evalCtrl.grade, evalCtrl.comments).then(
        finishWatchGrade,
        util.stdErrCallback
      );
    }

    function finishWatchGrade() {
      if (actionType === 'pause') {
        toggleActionBtn();
      }
      evalCtrl.comments = '';
      evalCtrl.skipBtnDisabled = isSetComplete ? true : false;
      evalCtrl.undoBtnDisabled = isSetComplete ? true : false;
      undoFlag = false;

      if (evalCtrl.autoplay) {
        // just writing action() here didn't seem to work.
        // not sure about this. Perhaps the angular digest has
        // to finish before this can be called?
        // real messy. If the rest of the digest takes longer
        // than X ms, the autoplay might break.
        // TODO: fix this
        $timeout(function(){ action(); }, 100);
      }
    }
  }
}
}());
