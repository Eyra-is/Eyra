// main controller for application

'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$scope',
                          'deliveryService',
                          'localDbService',
                          'logger',
                          'recordingService',
                          'tokenService',
                          'utilityService'];

function MainController($scope, deliveryService, localDbService, logger, recordingService, tokenService, utilityService) {
  var mainCtrl = this;
  var recService = recordingService;
  var delService = deliveryService;
  var dbService = localDbService;
  var util = utilityService;

  mainCtrl.clearLocalDb = clearLocalDb;
  mainCtrl.getTokens = getTokens;
  mainCtrl.record = record;
  mainCtrl.stop = stop;
  mainCtrl.sync = sync;
  mainCtrl.test = test;

  mainCtrl.msg = ''; // single debug/information msg
  mainCtrl.curRec = recService.currentRecording;

  mainCtrl.recordBtnDisabled = false;
  mainCtrl.stopBtnDisabled = true;
  mainCtrl.syncBtnDisabled = false;

  var currentToken = {'id':0, 'token':'No token yet. Hit \'Record\' to start'};
  mainCtrl.displayToken = currentToken['token'];

  var start_time = new Date().toISOString(); // session start time
  var invalidTitle = util.getConstant('invalidTitle');

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
      mainCtrl.msg = 'Clearing entire local db...';
      tokenService.clearLocalDb();      
    }
  }

  function getTokens() {
    mainCtrl.msg = 'Getting tokens...';

    tokenService.getTokens(25);
  }

  function record() {
    mainCtrl.msg = 'Recording now...';

    mainCtrl.recordBtnDisabled = true;

    recService.record();

    mainCtrl.stopBtnDisabled = false;

    // show token on record/newToken button hit
    tokenService.nextToken().then(function(data){
      mainCtrl.displayToken = data['token'];
      currentToken = data;
    });
  }

  // function passed to our recording service, notified when a recording has been finished
  function recordingCompleteCallback() {   
    var end_time = new Date().toISOString();
    // these scope variables connected to user input obviously have to be sanitized.
    var sessionData =  {                                                                  
                      "type":'session', 
                      "data":
                      {
                        "speakerId"      : (mainCtrl.speakerId || 1),
                        "instructorId"   : (mainCtrl.instructorId || 1),
                        "deviceId"       : (mainCtrl.deviceId || 1),
                        "location"       : (mainCtrl.curLocation || 'unknown'),
                        "start"          : start_time,
                        "end"            : end_time,
                        "comments"       : (mainCtrl.comments || 'no comments'),
                        "recordingsInfo" : {}
                      }
                    };
    sessionData['data']['recordingsInfo']
                [mainCtrl.curRec[0].title] = { 'tokenId' : currentToken['id'] };

    send(sessionData); // attempt to send current recording
    // if unsuccessful, save it locally, see send()->delService.submit()

    mainCtrl.recordBtnDisabled = false;
  }

  function send(sessionData) {
    mainCtrl.msg = 'Sending recs...';

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
    delService.submitRecordings(sessionData, mainCtrl.curRec)
    .then(
      function success(response) {
        logger.log(response);
      }, 
      function error(response) {
        logger.log(response);

        // on unsuccessful submit to server, save recordings locally, if they are valid (non-empty)
        var rec = mainCtrl.curRec[0];
        var tokenId = sessionData['data']['recordingsInfo'][rec.title]['tokenId'];
        if (rec.title !== invalidTitle && tokenId !== 0) {
          mainCtrl.msg = 'Submitting recording to server was unsuccessful, saving locally...';
          // only need blob and title from recording
          dbService.saveRecording(sessionData, {'blob' : rec.blob, 'title' : rec.title });
        }
      }
    );
  }

  function stop() {
    mainCtrl.msg = 'Processing wav...';

    mainCtrl.stopBtnDisabled = true;
    
    recService.stop();
  }

  // sends all available sessions from local db to server, one session at a time
  // assumes internet connection
  function sync() {
    mainCtrl.msg = 'Syncing...';

    mainCtrl.syncBtnDisabled = true;

    delService.sendLocalSessions(syncDoneCallback);
  }

  // result is true if sync completed successfully
  function syncDoneCallback(result) {
    mainCtrl.syncBtnDisabled = false;
  }

  function test() {
    dbService.countAvailableSessions().then(function(value){
      if (value > 0)
        logger.log('Aw yeah, '+value);
      else
        logger.log('Nope');
    });

    logger.getLogs().then(function(logs){
      console.log(logs);
    });
  }

  function updateBindingsCallback() {
    $scope.$apply();
  }
}

