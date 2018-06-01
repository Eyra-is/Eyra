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
    Sveinn Ernstsson (asyncTokenRead, tokensRead)
*/

(function () {
'use strict';

angular.module('daApp')
.controller('RecordingController', RecordingController);

RecordingController.$inject = [ '$q',
                                '$uibModal',
                                '$rootScope',
                                '$scope', 
                                'androidRecordingService',
                                'dataService',
                                'deliveryService',
                                'localDbService',
                                'localDbMiscService',
                                'logger',
                                'notificationService',
                                'qcService',
                                'recordingService',
                                'sessionService',
                                'tokenService',
                                'utilityService',
                                'volumeMeterService',
                                'CACHEBROKEN_REPORT'];

function RecordingController($q, 
                             $uibModal, 
                             $rootScope, 
                             $scope, 
                             androidRecordingService, 
                             dataService, 
                             deliveryService, 
                             localDbService, 
                             localDbMiscService, 
                             logger, 
                             notificationService, 
                             qcService, 
                             recordingService, 
                             sessionService, 
                             tokenService, 
                             utilityService, 
                             volumeMeterService, 
                             CACHEBROKEN_REPORT) {
  var recCtrl = this;
  // fix for android audio filtering (8k) through browser recording, in case of webview (in our android app)
  //   use the native recorder through the app
  var recService = $rootScope.isWebView ? androidRecordingService : recordingService;
  var delService = deliveryService;
  var dbService = localDbService;
  var notifService = notificationService;
  var miscDbService = localDbMiscService;
  var util = utilityService;
  var volService = volumeMeterService;

  recCtrl.action = action;
  recCtrl.skip = skip;
  $scope.skipText = util.getConstant('SKIPTEXT');
  $scope.promptsReadText = util.getConstant('PROMPTSREADTEXT');
  $scope.utteranceQuality = util.getConstant('UTTQUALITYTEXT');
  $scope.utteranceUploaded = util.getConstant('UTTUPLOADEDTEXT');

  $scope.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.actionBtnDisabled = false;
  recCtrl.skipBtnDisabled = true;
  var speaker = dataService.get('speakerName');
  $scope.tokensRead = tokensRead(speaker); // fetch tokenRead for current speaker/user

  var actionType = 'record'; // current state

  var RECGLYPH = 'glyphicon-record'; // bootstrap glyph class
  var STOPGLYPH = 'glyphicon-stop';
  $scope.actionText = util.getConstant('RECTEXT');
  $scope.actionGlyph = RECGLYPH;
  $scope.hide_playback = true;

  var currentToken = {'id':0, 'token': util.getConstant('INITTOKENTEXT')};
  recCtrl.displayToken = currentToken['token'];

  sessionService.setStartTime(new Date().toISOString());
  var invalidTitle = util.getConstant('invalidTitle');

  // if this is true, on next stop click (when user is not in a recording)
  //   show report.
  var shouldDisplayReport = false;

  $scope.tokenCountGoal = util.getConstant('tokenCountGoal') || 300;

  recCtrl.accuracy = 1.0;
  recCtrl.lowThreshold = util.getConstant('QCAccThreshold') || 0.2;
  recCtrl.highThreshold = util.getConstant('QCHighThreshold') || 0.7;
  recCtrl.lowerUtt = '?';
  recCtrl.upperUtt = '?';

  $scope.recsDelivered = 0;

  activate();

  ////////// 

  function activate() {
    recService.setupCallbacks(recordingCompleteCallback);
    var res = volService.init(recService.getAudioContext(), recService.getStreamSource());
    if (!res) logger.log('Volume meter failed to initialize.');
    qcService.setupCallbacks(qcDataReady);

    // get recsDelivered, first check RAM, then ldb
    $scope.recsDelivered = dataService.get('recsDelivered') || 0;
    if ($scope.recsDelivered === 0) {
      miscDbService.getSpeaker(speaker).then(function(dbSpeaker){
        if (dbSpeaker && dbSpeaker.recsDelivered) {
          $scope.recsDelivered = dbSpeaker.recsDelivered;
        }
      }, util.stdErrCallback);
    }
    
    $rootScope.isLoaded = true; // is page loaded?  
  }

  // signifies the combined rec/stop button
  function action() {
    if (actionType === 'record') {
      record();
    } else if (actionType === 'stop') {
      stop(true);
    }
  }

  function asyncTokenRead(speaker, increment){
    // this functon handles getting and setting/incrementing of tokensRead in 
    // ldb speakerInfo
    // it also updates ram speakerInfo - syncs the ldb/ram speakerInfo

    var ramSpeakerInfo = dataService.get('speakerInfo');
    var tokensRead = 0;

    miscDbService.getSpeaker(speaker).then(
      function success(speakerInfo) {
        //console.info(speakerInfo);
        if (increment === 'return'){
          if (speakerInfo && speakerInfo['tokensRead']) {
            ramSpeakerInfo['tokensRead'] = speakerInfo['tokensRead'];
            tokensRead = ramSpeakerInfo['tokensRead'];
            // updating speakerInfo in ram
            dataService.set('speakerInfo', ramSpeakerInfo);
          }
        }

        if (typeof(increment) === 'number') {
          // the value of increment is taken from the $scope tokenRead
          // the $scope tokenRead is incremented
          speakerInfo['tokensRead'] = increment;
          // updating speakerInfo in ram
          dataService.set('speakerInfo', speakerInfo);

          miscDbService.setSpeaker(speaker, speakerInfo).then(
            angular.noop,
            function error(value){
              $scope.msg =  util.getConstant('SPEAKERINFOERRORMSG');
              logger.error(value);
            }
          );
        }

        if (increment === 'return') {
          return tokensRead;
        }
      },
      function error(value){
        $scope.msg =  util.getConstant('TOKENSREADERRORMSG');
        logger.error(value);
      }

    );
  }

  function displayReport() {
    $uibModal.open({
      // defined in app.js to simpliy gruntfile replace of rest of the views.
      templateUrl: CACHEBROKEN_REPORT, // e.g. 'views/report.2016-03-02-15-42.html'
      controller: 'ReportController',
      controllerAs: 'reportCtrl',
    }); 
  }

  // callback, called by qc service
  function qcDataReady(data) {
    recCtrl.accuracy = data.avgAcc;
    recCtrl.lowerUtt = data.lowerUtt;
    recCtrl.upperUtt = data.upperUtt;
  }

  function toggleActionBtn() {
    if (actionType === 'record') {
      actionType = 'stop';
      $scope.actionText = util.getConstant('STOPTEXT');
      $scope.actionGlyph = STOPGLYPH;
      $scope.hide_playback = true;
    } else if (actionType === 'stop') {
      actionType = 'record';
      $scope.hide_playback = false;
      $scope.actionText = util.getConstant('RECTEXT');
      $scope.actionGlyph = RECGLYPH;
    }
  }

  function record() {
    $scope.msg = util.getConstant('RECORDINGNOWTEXT');

    recCtrl.skipBtnDisabled = false;
    if (actionType === 'record') {
      toggleActionBtn();
    }
    recCtrl.actionBtnDisabled = false;

    recService.record();

    currentToken = {'id':0, 'token': util.getConstant('WAITINGFORTOKENTEXT')};    

    // show token on record/newToken button hit
    tokenService.nextToken().then(function(token){
      recCtrl.displayToken = token['token'];
      currentToken = token;
    },
    util.stdErrCallback);
  }

  

  // function passed to our recording service, notified when a recording has been finished
  function recordingCompleteCallback() {
    // attempt to send current recording
    // remember to take a copy of the reference to curRec, 
    //   because they might change when it is actually sent (this is async)
    //   or more likely when it is saved locally at least.
    var oldCurRec = recCtrl.curRec[0];

    // get the data for the session to be sent to the server or saved locally on failure
    // send token as new object so it is definitely not changed to the next token
    //   when accessed later in assembleSessionData
    sessionService.assembleSessionData(oldCurRec, {'id':currentToken.id, 'token':currentToken.token}).then(
      function success(sessionData) {
        send(sessionData, oldCurRec)
        .then(
          function success(response) {
            // TODO CLEAN THIS UP, maybe put in a service

            $scope.recsDelivered = sessionService.handleSessionResponse(response);

            var oldSessionId = dataService.get('sessionId');
            var sessionId;
            // if no error, save sessionId to RAM to be used to identify session
            //   in later requests (e.g. QC reports)
            try {
              sessionId = response.data.sessionId;
              if (sessionId) {
                dataService.set('sessionId', sessionId); // set it in ram
              } else {
                $scope.msg = util.getConstant('SOMETINGWRONGERRORMSG');
              }
            } catch (e) {
              logger.error(e);
            }

            // notify QC with last used session (should be same probably)
            //   and if non-existant, use the one we got now, and if non-existant don't move.
            var sessionIdToUse = oldSessionId || sessionId;
            if (sessionIdToUse) {
              qcService.notifySend( sessionIdToUse, 
                                    dataService.get('speakerInfo').tokensRead || 0);
            }

            var announcement = notifService.notifySend(dataService.get('speakerInfo').tokensRead || 0);
            if (announcement) {
              // so long as the user is not in a recording
              //   display report straight away
              // otherwise, queue it for next stop click.
              if (actionType === 'record') {
                displayReport();
              } else {
                shouldDisplayReport = true;
              }
            }
          },
          function error(response) {
            // on unsuccessful submit to server, save recordings locally, if they are valid (non-empty)
            var rec = oldCurRec;
            var tokenId = sessionData['data']['recordingsInfo'][rec.title]['tokenId'];
            if (rec.title !== invalidTitle && tokenId !== 0) {
              logger.log('Submitting recording to server was unsuccessful, saving locally...');
              // only need blob and title from recording
              dbService.saveRecording(sessionData, {'blob' : rec.blob, 'title' : rec.title });
            } else {
              logger.error('Invalid token in submission.');

              // no recording saved, do not count as token read
              $scope.tokensRead--; 
              // updating tokenRead in ldb and ram
              asyncTokenRead(speaker, $scope.tokensRead);
            }

            logger.error(response);
          }
        );
      },
      util.stdErrCallback
    );

    toggleActionBtn();
    recCtrl.actionBtnDisabled = false;
  }

  // oldCurRec is a reference to the possibly previous recCtrl.curRec, because
  //   it might have changed when it is sent (although almost impossible atm)
  function send(sessionData, oldCurRec) {
    logger.log('Sending recs...');

    // and send it to remote server
    // plump out the recording!
    return delService.submitRecordings(sessionData, [oldCurRec]);
  }

  function skip() {
    $scope.msg = util.getConstant('TOKENSKIPPEDTEXT');

    if (currentToken.id !== 0) {
      stop(false);
    }
    record();
  }

  function stop(valid) {
    $scope.msg = util.getConstant('STOPPEDTEXT');

    recCtrl.actionBtnDisabled = true;
    recCtrl.skipBtnDisabled = true;
    
    if (shouldDisplayReport) {
      displayReport();
      shouldDisplayReport = false;
    }

    recService.stop(valid);

    // whenever stopped is pressed from gui, it should mean a valid token read.
    if (valid) {
      $scope.tokensRead++; 
      // updating tokenRead in ldb and ram
      asyncTokenRead(speaker, $scope.tokensRead);
    }
  }

  function tokensRead(speaker) {
    // input is speaker fetched from ram

    var tokensRead;
    // get speakerInfo from ram
    var ramSpeakerInfo = dataService.get('speakerInfo') || {};

    // get speaker info in ram and check if info contains tokensRead
    if (ramSpeakerInfo['tokensRead']) {

      tokensRead = ramSpeakerInfo['tokensRead'];
 
    } else { 
    // if tokensRead is not in ram speakerInfo then it might be in ldb speakerInfo
    // in any case it will be either fetched or initialized in ldb.

      tokensRead = asyncTokenRead(speaker, 'return')
    };

    if (tokensRead){
        return tokensRead;
    } else {
        return 0;
    };    
  }
}
}());
