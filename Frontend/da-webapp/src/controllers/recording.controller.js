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
                                'qcService',
                                'recordingService',
                                'sessionService',
                                'tokenService',
                                'utilityService',
                                'volumeMeterService',
                                'CACHEBROKEN_REPORT'];

function RecordingController($q, $uibModal, $rootScope, $scope, androidRecordingService, dataService, deliveryService, localDbService, localDbMiscService, logger, qcService, recordingService, sessionService, tokenService, utilityService, volumeMeterService, CACHEBROKEN_REPORT) {
  var recCtrl = this;
  // fix for android audio filtering (8k) through browser recording, in case of webview (in our android app)
  //   use the native recorder through the app
  var recService = $rootScope.isWebView ? androidRecordingService : recordingService;
  var delService = deliveryService;
  var dbService = localDbService;
  var miscDbService = localDbMiscService;
  var util = utilityService;
  var volService = volumeMeterService;

  recCtrl.action = action;
  recCtrl.skip = skip;

  $scope.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.actionBtnDisabled = false;
  recCtrl.skipBtnDisabled = true;
  var speaker = dataService.get('speakerName');
  $scope.tokensRead = tokensRead(speaker); // fetch tokenRead for current speaker/user

  var actionType = 'record'; // current state

  var RECTEXT = 'Rec'; // text under the buttons
  var STOPTEXT = 'Stop';
  var RECGLYPH = 'glyphicon-record'; // bootstrap glyph class
  var STOPGLYPH = 'glyphicon-stop';
  $scope.actionText = RECTEXT;
  $scope.actionGlyph = RECGLYPH;
  $scope.hide_playback = true;

  var currentToken = {'id':0, 'token':'Hit \'Rec\' for prompt.'};
  recCtrl.displayToken = currentToken['token'];

  sessionService.setStartTime(new Date().toISOString());
  var invalidTitle = util.getConstant('invalidTitle');

  // if this is true, on next stop click (when user is not in a recording)
  //   show QC report.
  var displayReport = false;

  activate();

  ////////// 

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
              $scope.msg = 'Could not update speakerInfo into ldb';
              logger.error(value);
            }
          );
        }

        if (increment === 'return') {
          return tokensRead;
        }
      },
      function error(value){
        $scope.msg = 'Could not read tokensRead counter from ldb';
        logger.error(value);
      }

    );
  }

  function tokensRead(speaker) {
    // input is speaker fetched from ram

    var tokensRead;
    // get speakerInfo from ram
    var ramSpeakerInfo = dataService.get('speakerInfo');

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

  function displayQCReport() {
    $uibModal.open({
      // defined in app.js to simpliy gruntfile replace of rest of the views.
      templateUrl: CACHEBROKEN_REPORT, // e.g. 'views/report.2016-03-02-15-42.html'
      controller: 'ReportController',
      controllerAs: 'reportCtrl',
    }); 
  }

  function toggleActionBtn() {
    if (actionType === 'record') {
      actionType = 'stop';
      $scope.actionText = STOPTEXT;
      $scope.actionGlyph = STOPGLYPH;
      $scope.hide_playback = true;
    } else if (actionType === 'stop') {
      actionType = 'record';
      $scope.hide_playback = false;
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
   // console.info('QCReportS')
   /*
    if (dataService.get('QCReport')) {
      console.info(dataService.get('QCReport') + 'QC report');
    }*/
    

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

            // we may have gotten a deviceId and speakerId from server, in which case
            //   we handle that by setting it in RAM and local database, if it is different
            //   from the id's there.
            // response e.g.: { 'sessionId' : int, 'speakerId': int, 'deviceId' : int }

            var speakerId = response.data.speakerId;
            var deviceId = response.data.deviceId;
            if (deviceId) updateDevice(deviceId); 
            if (speakerId) updateSpeakerInfo(speakerId);

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

            // notify QC with last used session (should be same probably)
            //   and if non-existant, use the one we got now, and if non-existant don't move.
            var sessionIdToUse = oldSessionId || sessionId;
            //console.info(sessionId);
            //console.info(oldSessionId);
            if (sessionIdToUse) {
              qcService.notifySend(sessionIdToUse, dataService.get('speakerInfo').tokensRead || 0).then(
                function success(data){
                  //console.info('calling qcService');
                  // so long as the user is not in a recording
                  //   display QC report straight away
                  // otherwise, queue it for next stop click.
                  if (actionType === 'record') {
                    displayQCReport();
                  } else {
                    displayReport = true;
                  }
                },
                angular.noop);
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
    
    if (displayReport) {
      displayQCReport();
      displayReport = false;
    }

    recService.stop(valid);

    // whenever stopped is pressed from gui, it should mean a valid token read.
    if (valid) {
      $scope.tokensRead++; 
      // updating tokenRead in ldb and ram
      asyncTokenRead(speaker, $scope.tokensRead);
    }
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
        miscDbService.setDevice(device)
          .then(angular.noop, util.stdErrCallback);
      }
    } else {
      // no device in ram, check in local db
      miscDbService.getDevice().then(
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
          miscDbService.setDevice(device)
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
        miscDbService.setSpeaker(speakerName, speakerInfo)
          .then(angular.noop, util.stdErrCallback);
      }
    } else {
      // no speakerInfo in ram, check in local db
      miscDbService.getSpeaker(speakerName).then(
        function success(speakerInfo) {
          if (speakerInfo) {
            speakerInfo.speakerId = id;
            dataService.set('speakerInfo', speakerInfo);
            miscDbService.setSpeaker(speakerName, speakerInfo)
              .then(angular.noop, util.stdErrCallback);
          } else {
            logger.error('Speaker not in database, ' + speakerName + ', should not happen.');
          }
        },
        util.stdErrCallback
      );
    }
  }
}
}());
