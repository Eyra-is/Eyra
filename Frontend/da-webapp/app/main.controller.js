// main controller for application

'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$scope',
                          'deliveryService',
                          'invalidTitle',
                          'localDbService',
                          'logger',
                          'recordingService',
                          'tokenService'];

function MainController($scope, deliveryService, invalidTitle, localDbService, logger, recordingService, tokenService) {
  var recCtrl = this; // record control
  var recService = recordingService;
  var delService = deliveryService;
  var dbService = localDbService;

  recCtrl.clearLocalDb = clearLocalDb;
  recCtrl.getTokens = getTokens;
  recCtrl.record = record;
  recCtrl.stop = stop;
  recCtrl.sync = sync;
  recCtrl.test = test;

  recCtrl.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.recordBtnDisabled = false;
  recCtrl.stopBtnDisabled = true;
  recCtrl.syncBtnDisabled = false;

  var currentToken = {'id':0, 'token':'No token yet. Hit \'Record\' to start'};
  recCtrl.displayToken = currentToken['token'];

  var start_time = new Date().toISOString(); // session start time
  var end_time;

  activate();

  //////////

  function activate() {
    // provide updateBindings function so recordingService can 
    // call that function when it needs to update bindings
    recService.init(updateBindingsCallback, recordingCompleteCallback);    
  }

  // dev function, clear the entire local forage database
  function clearLocalDb() {
    if (confirm('Are you sure?\nThis will delete the entire local db, including tokens and recordings.')) {
      recCtrl.msg = 'Clearing entire local db...';
      tokenService.clearLocalDb();      
    }
  }

  function getTokens() {
    recCtrl.msg = 'Getting tokens...';

    tokenService.getTokens(25);
  }

  function record() {
    recCtrl.msg = 'Recording now...';

    recCtrl.recordBtnDisabled = true;

    recService.record();

    recCtrl.stopBtnDisabled = false;

    // show token on record/newToken button hit
    tokenService.nextToken().then(function(data){
      recCtrl.displayToken = data['token'];
      currentToken = data;
    });
  }

  // function passed to our recording service, notified when a recording has been finished
  function recordingCompleteCallback() {   
    end_time = new Date().toISOString();
    // these scope variables connected to user input obviously have to be sanitized.
    var sessionData =  {                                                                  
                      "type":'session', 
                      "data":
                      {
                        "speakerId"      : (recCtrl.speakerId || 1),
                        "instructorId"   : (recCtrl.instructorId || 1),
                        "deviceId"       : (recCtrl.deviceId || 1),
                        "location"       : (recCtrl.curLocation || 'unknown'),
                        "start"          : start_time,
                        "end"            : end_time,
                        "comments"       : (recCtrl.comments || 'no comments'),
                        "recordingsInfo" : {}
                      }
                    };
    sessionData['data']['recordingsInfo']
                [recCtrl.curRec[0].title] = { 'tokenId' : currentToken['id'] };

    send(sessionData); // attempt to send current recording
    // if unsuccessful, save it locally, see send()->delService.submit()

    recCtrl.recordBtnDisabled = false;
  }

  function send(sessionData) {
    recCtrl.msg = 'Sending recs...';

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
    delService.submitRecordings(sessionData, recCtrl.curRec)
    .then(
      function success(response) {
        logger.log(response);
      }, 
      function error(response) {
        logger.log(response);

        // on unsuccessful submit to server, save recordings locally, if they are valid (non-empty)
        var rec = recCtrl.curRec[0];
        var tokenId = sessionData['data']['recordingsInfo'][rec.title]['tokenId'];
        if (rec.title !== invalidTitle && tokenId !== 0) {
          recCtrl.msg = 'Submitting recording to server was unsuccessful, saving locally...';
          // only need blob and title from recording
          dbService.saveRecording(sessionData, {'blob' : rec.blob, 'title' : rec.title });
        }
      }
    );
  }

  function stop() {
    recCtrl.msg = 'Processing wav...';

    recCtrl.stopBtnDisabled = true;
    
    recService.stop();
  }

  // sends all available sessions from local db to server, one session at a time
  // assumes internet connection
  function sync() {
    recCtrl.msg = 'Syncing...';

    recCtrl.syncBtnDisabled = true;

    delService.sendLocalSessions(syncDoneCallback);
  }

  // result is true if sync completed successfully
  function syncDoneCallback(result) {
    recCtrl.syncBtnDisabled = false;
  }

  function test() {
    dbService.countAvailableSessions().then(function(value){
      if (value > 0)
        logger.log('Aw yeah, '+value);
      else
        logger.log('Nope');
    });

    logger.getLogs().then(function(logs){
      logger.log(logs);
    });
  }

  function updateBindingsCallback() {
    $scope.$apply();
  }
}

