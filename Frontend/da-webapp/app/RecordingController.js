// record and submit recordings/data to server

'use strict';

angular.module('daApp')
.controller('RecordingController', ['$scope',
                                    'recordingService',
                                    'tokenService',
                                    RecordingController]);

function RecordingController($scope, recordingService, tokenService) {
  var recCtrl = this; // record control
  var recService = recordingService;

  recCtrl.record = record;
  recCtrl.save = save;
  recCtrl.stop = stop;

  recCtrl.msg = ''; // single debug/information msg
  recCtrl.recordings = recService.recordings; // recordings so far

  recCtrl.recordBtnDisabled = false;
  recCtrl.saveBtnDisabled = true;
  recCtrl.stopBtnDisabled = true;


  recCtrl.getTokens = getTokens;

  var currentToken = {'id':0, 'token':'No token yet.'};

  // kick it off

  // provide updateBindings function so recordingService can call that function when it needs to update bindings
  recService.init(updateBindings);

  //////////

  function record() {
    recCtrl.msg = 'Recording now...';

    recService.record();

    // show token on record/newToken button hit
    tokenService.nextToken().then(function(data){
      recCtrl.displayToken = data['token'];
      currentToken = data;
    });

    recCtrl.recordBtnDisabled = true;
    recCtrl.stopBtnDisabled = false;
    recCtrl.saveBtnDisabled = true;
  }

  function save() {
    recCtrl.msg = 'Saving and sending recs...';
    recCtrl.saveBtnDisabled = true;

    // these scope variables connected to user input obviously have to be sanitized.
    recService.save(recCtrl.speakerId,
                    recCtrl.isntructorId,
                    recCtrl.deviceId,
                    recCtrl.curLocation,
                    recCtrl.comments);
  }

  function stop() {
    recCtrl.msg = 'Processing wav...';

    recCtrl.stopBtnDisabled = true;
    recCtrl.recordBtnDisabled = false;
    recCtrl.saveBtnDisabled = false;
    
    recService.stop();
  }

  function updateBindings() {
    $scope.$apply();
  }

  function getTokens() {
    tokenService.getTokens(25);
  };
}

