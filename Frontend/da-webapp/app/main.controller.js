// main controller for application

'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$scope',
                          'deliveryService',
                          'recordingService',
                          'tokenService'];

function MainController($scope, deliveryService, recordingService, tokenService) {
  var recCtrl = this; // record control
  var recService = recordingService;
  var delService = deliveryService;

  recCtrl.clearLocalDb = clearLocalDb;
  recCtrl.getTokens = getTokens;
  recCtrl.record = record;
  recCtrl.stop = stop;

  recCtrl.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.recordBtnDisabled = false;
  recCtrl.stopBtnDisabled = true;

  var currentToken = {'id':0, 'token':'No token yet. Hit \'Record\' to start'};
  recCtrl.displayToken = currentToken['token'];

  var invalidTitle = recService.invalidTitle; // sentinel value for title of recording
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
    if (confirm('Are you sure?\nThis will delete the entire local db, including tokens and recordings.'))
    {
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
    var jsonData =  {                                                                  
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
    jsonData["data"]["recordingsInfo"]
                [recCtrl.curRec[0].title] = { "tokenId" : currentToken['id'] };

    send(jsonData); // attempt to send current recording
    // TODO if unsuccessful, save it locally

    recCtrl.recordBtnDisabled = false;
  }

  function send(jsonData) {
    recCtrl.msg = 'Sending recs...';

    // and send it to remote server
    // test CORS is working
    delService.testServerGet()
    .then(
      function success(response) {
        console.log(response);
      }, 
      function error(response) {
        console.log(response);
      }
    );

    // plump out the recording!
    delService.submitRecordings(jsonData, recCtrl.curRec, invalidTitle)
    .then(
      function success(response) {
        console.log(response);
      }, 
      function error(response) {
        console.log(response);
      }
    );
  }

  function stop() {
    recCtrl.msg = 'Processing wav...';

    recCtrl.stopBtnDisabled = true;
    
    recService.stop();
  }

  function updateBindingsCallback() {
    $scope.$apply();
  }
}

