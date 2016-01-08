'use strict';

angular.module('daApp')
.controller('RecordingController', RecordingController);

RecordingController.$inject = ['$http', '$scope',  // DEBUG HTTP
                          'deliveryService',
                          'localDbService',
                          'logger',
                          'recordingService',
                          'tokenService',
                          'utilityService'];

function RecordingController($http, $scope, deliveryService, localDbService, logger, recordingService, tokenService, utilityService) {
  var recCtrl = this;
  var recService = recordingService;
  var delService = deliveryService;
  var dbService = localDbService;
  var util = utilityService;

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
  var invalidTitle = util.getConstant('invalidTitle');

  activate();

  //////////

  function activate() {
    // provide updateBindings function so recordingService can 
    // call that function when it needs to update bindings
    recService.setupCallbacks(updateBindingsCallback, recordingCompleteCallback);
    $scope.isLoaded = true; // is page loaded?  
  }

  // dev function, clear the entire local forage database
  function clearLocalDb() {
    if (confirm('Are you sure?\nThis will delete the entire local db, including tokens and recordings.')) {
      recCtrl.msg = 'Clearing entire local db...';
      dbService.clearLocalDb()
        .then(function(val){
          alert('Database cleared!');
          recCtrl.msg = 'Database cleared.';
        }, util.stdErrCallback);
    }
  }

  function getTokens() {
    recCtrl.msg = 'Getting tokens...';

    tokenService.getTokens(25).then(function(tokens){
      alert('Tokens acquired!');
      recCtrl.msg = 'Tokens acquired.';
    },
    util.stdErrCallback);
  }

  function record() {
    recCtrl.msg = 'Recording now...';

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
    var end_time = new Date().toISOString();
    // these scope variables connected to user input obviously have to be sanitized.
    var sessionData = {                                                                  
                        "type":'session', 
                        "data":
                        {
                          "speakerId"      : (recCtrl.speakerId || 1),
                          "instructorId"   : (recCtrl.instructorId || 1),
                          "deviceId"       : (recCtrl.deviceId || 1),
                          "location"       : (recCtrl.curLocation || 'Unknown.'),
                          "start"          : start_time,
                          "end"            : end_time,
                          "comments"       : (recCtrl.comments || 'No comments.'),
                          "recordingsInfo" : {}
                        }
                      };
    sessionData['data']['recordingsInfo']
                [recCtrl.curRec[0].title] = { 'tokenId' : currentToken['id'] };

    // attempt to send current recording
    send(sessionData)
    .then(
      function success(response) {
        logger.log(response); // DEBUG
      }, 
      function error(response) {
        // on unsuccessful submit to server, save recordings locally, if they are valid (non-empty)
        var rec = recCtrl.curRec[0];
        var tokenId = sessionData['data']['recordingsInfo'][rec.title]['tokenId'];
        if (rec.title !== invalidTitle && tokenId !== 0) {
          recCtrl.msg = 'Submitting recording to server was unsuccessful, saving locally...';
          // only need blob and title from recording
          dbService.saveRecording(sessionData, {'blob' : rec.blob, 'title' : rec.title });
        } else {
          logger.error('Invalid token in submission.');
        }

        util.stdErrCallback(response);
      }
    );

    recCtrl.recordBtnDisabled = false; // think about keeping record disabled until after send.
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
    return delService.submitRecordings(sessionData, recCtrl.curRec);
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
    recCtrl.msg = result ? 'Sync complete.' : 'Sync failed.';
    recCtrl.syncBtnDisabled = false;
  }

  function test() {
    /*dbService.countAvailableSessions().then(function(value){
      if (value > 0)
        logger.log('Aw yeah, '+value);
      else
        logger.log('Nope');
    });

    logger.getLogs().then(function(logs){
      console.log(logs);
    });*/

    /*$http.post(
      '//' + BACKENDURL + '/submit/session'
    ).then(function(response){
      console.log(response);
    },
    util.stdErrCallback);*/

    tokenService.countAvailableTokens().then(function(n){
      console.log(n);
    });
  }

  function updateBindingsCallback() {
    $scope.$apply();
  }
}

