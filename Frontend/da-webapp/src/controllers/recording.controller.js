(function () {
'use strict';

angular.module('daApp')
.controller('RecordingController', RecordingController);

RecordingController.$inject = [ '$rootScope',
                                '$scope',  
                                'dataService',
                                'deliveryService',
                                'localDbService',
                                'logger',
                                'recordingService',
                                'sessionService',
                                'tokenService',
                                'utilityService',
                                'volumeMeterService'];

function RecordingController($rootScope, $scope, dataService, deliveryService, localDbService, logger, recordingService, sessionService, tokenService, utilityService, volumeMeterService) {
  var recCtrl = this;
  var recService = recordingService;
  var delService = deliveryService;
  var dbService = localDbService;
  var util = utilityService;
  var volService = volumeMeterService;

  recCtrl.action = action;
  recCtrl.skip = skip;

  $scope.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.actionBtnDisabled = false;
  recCtrl.skipBtnDisabled = true;

  $scope.tokensRead = 0; // simple counter

  var actionType = 'record'; // current state

  var RECTEXT = 'Next'; // text under the buttons
  var STOPTEXT = 'Stop';
  var RECGLYPH = 'glyphicon-record'; // bootstrap glyph class
  var STOPGLYPH = 'glyphicon-stop';
  $scope.actionText = RECTEXT;
  $scope.actionGlyph = RECGLYPH;

  var currentToken = {'id':0, 'token':'No token yet. Hit \'Next\' for next token.'};
  recCtrl.displayToken = currentToken['token'];

  sessionService.setStartTime(new Date().toISOString());
  var invalidTitle = util.getConstant('invalidTitle');

  activate();

  //////////

  function activate() {
    recService.setupCallbacks(recordingCompleteCallback);
    var res = volService.init(recService.getAudioContext(), recService.getStreamSource());
    if (!res) logger.log('Volume meter failed to initialize.');
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

  function toggleActionBtn() {
    if (actionType === 'record') {
      actionType = 'stop';
      $scope.actionText = STOPTEXT;
      $scope.actionGlyph = STOPGLYPH;
    } else if (actionType === 'stop') {
      actionType = 'record';
      $scope.actionText = RECTEXT;
      $scope.actionGlyph = RECGLYPH;
    }
  }

  function record() {
    $scope.msg = 'Recording now...';

    recCtrl.skipBtnDisabled = false;
    if (actionType === 'record') {
      toggleActionBtn();
    }
    recCtrl.actionBtnDisabled = false;

    recService.record();

    currentToken = {'id':0, 'token':'Waiting for new token...'};
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
    sessionService.assembleSessionData(oldCurRec, currentToken['id']).then(
      function success(sessionData) {
        send(sessionData, oldCurRec)
        .then(
          function success(response) {
            logger.log(response); // DEBUG

            var oldSessionId = dataService.get('sessionId');
            var sessionId;

            // if no error, save sessionId to RAM to be used to identify session
            //   in later requests (e.g. QC reports)
            try {
              sessionId = response.data.sessionId;
              if (sessionId) {
                dataService.set('sessionId', sessionId); // set it in ram
              } else {
                $scope.msg = 'Something went wrong.';
              }
            } catch (e) {
              logger.error(e);
            }

            // query for QC report with last used session (should be same probably)
            //   and if non-existant, use the one we got now, and if non-existant don't move.
            var sessionIdToUse = oldSessionId || sessionId;
            if (sessionIdToUse) {
              delService.queryQC(sessionIdToUse)
              .then(function (response){
                logger.log(response);
              },
              util.stdErrCallback)
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
    // test CORS is working
    delService.testServerGet()
    .then(
      function success(response) {
        logger.log(response);
      }, 
      function error(response) {
        logger.log(response);
      }
    );

    // plump out the recording!
    return delService.submitRecordings(sessionData, [oldCurRec]);
  }

  function skip() {
    $scope.msg = 'Token skipped.';

    if (currentToken.id !== 0) {
      stop(false);
    }
    record();
  }

  function stop(valid) {
    $scope.msg = 'Stopped.';

    recCtrl.actionBtnDisabled = true;
    recCtrl.skipBtnDisabled = true;
    
    recService.stop(valid);

    // whenever stopped is pressed from gui, it should mean a valid token read.
    if (valid) {
      $scope.tokensRead++;
    }
  }
}
}());
