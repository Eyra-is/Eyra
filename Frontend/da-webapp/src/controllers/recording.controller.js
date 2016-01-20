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
                                'utilityService'];

function RecordingController($rootScope, $scope, dataService, deliveryService, localDbService, logger, recordingService, sessionService, tokenService, utilityService) {
  var recCtrl = this;
  var recService = recordingService;
  var delService = deliveryService;
  var dbService = localDbService;
  var util = utilityService;

  recCtrl.record = record;
  recCtrl.stop = stop;

  $scope.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.recordBtnDisabled = false;
  recCtrl.stopBtnDisabled = true;

  var currentToken = {'id':0, 'token':'No token yet. Hit \'Record\' to start.'};
  recCtrl.displayToken = currentToken['token'];

  sessionService.setStartTime(new Date().toISOString());
  var invalidTitle = util.getConstant('invalidTitle');

  activate();

  //////////

  function activate() {
    // provide updateBindings function so recordingService can 
    // call that function when it needs to update bindings
    recService.setupCallbacks(updateBindingsCallback, recordingCompleteCallback);
    $rootScope.isLoaded = true; // is page loaded?  
  }

  function record() {
    $scope.msg = 'Recording now...';

    recCtrl.recordBtnDisabled = true;

    recService.record();

    recCtrl.stopBtnDisabled = false;

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

    recCtrl.recordBtnDisabled = false; // think about keeping record disabled until after send.
  }

  // oldCurRec is a reference to the possibly previous recCtrl.curRec, because
  //   it might have changed when it is sent (although almost impossible atm)
  function send(sessionData, oldCurRec) {
    $scope.msg = 'Sending recs...';

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

  function stop() {
    $scope.msg = 'Processing wav...';

    recCtrl.stopBtnDisabled = true;
    
    recService.stop();
  }

  function updateBindingsCallback() {
    $scope.$apply();
  }
}
}());
