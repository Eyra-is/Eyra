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

EvaluationController.$inject = ['$rootScope',
                                '$scope',
                                'evaluationService',
                                'logger',
                                'utilityService'];

function EvaluationController($rootScope, $scope, evaluationService, logger, utilityService) {
  var evalCtrl = this;
  var evalService = evaluationService;
  var util = utilityService;

  evalCtrl.play = play;
  evalCtrl.skip = skip;

  $scope.msg = ''; // single information msg

  evalCtrl.playBtnDisabled = false;
  evalCtrl.skipBtnDisabled = true;

  evalCtrl.hidePlayback = false;

  evalCtrl.commentOpts = [
    'yeye',
    'nono'
  ];

  var currentSet = 'malromur_3k';

  activate();

  ////////// 
  
  function activate() {
    evalCtrl.displayToken = 'sup';
    evalCtrl.uttsGraded = 0;
    evalCtrl.gradesDelivered = 0;

    evalCtrl.grade = undefined; // initially unchecked
    $scope.$watch(function(){ return evalCtrl.grade; }, watchGrade);

    initSet(currentSet).then(
      function success(data){
        $rootScope.isLoaded = true; // is page loaded?
      }, 
      function error(response){
        $scope.msg = 'Something went wrong.';

        logger.error(response);

        $rootScope.isLoaded = true;
      }
    );
  }

  function initSet(set) {
    /*
    Returns promise resolved when evalService has init'd set.
    */
    return evalService.initSet(set);
  }

  function next() {
    /*
    Sets next recording and prompt.
    */
    var recNPrompt = evalService.getNext();
    evalCtrl.recording = recNPrompt[0];
    evalCtrl.displayToken = recNPrompt[1];
  }

  function play() {
    evalCtrl.playBtnDisabled = true;
    evalCtrl.skipBtnDisabled = false;

    console.log(evalCtrl.grade);
    console.log(evalCtrl.comment);
  }

  function skip() {
    evalCtrl.skipBtnDisabled = true;
  }

  function watchGrade() {
    /*
    Passed as a function into $scope.$watch.

    Notifies us when a grade radio button has been ticked,
    and in doing so saves the choice and triggeres the next recording.
    */
    // if valid grade has been clicked
    // thanks, Gumbo, http://stackoverflow.com/a/4728164/5272567
    if (['1','2','3','4'].indexOf(evalCtrl.grade) > -1) {
      evalCtrl.uttsGraded++;
      next();
    }
  }
}
}());
