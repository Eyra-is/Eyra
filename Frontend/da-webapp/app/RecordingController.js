// record and submit recordings/data to server

'use strict';

angular.module('daApp')
.controller('RecordingController', ['$http',
                                    '$localForage',
                                    '$scope',
                                    'tokenService',
                                    function($http, $localForage, $scope, tokenService) {
  var recordCtrl = this;

  //tokenService.getTokens(10);
  var currentToken = {'id':0, 'token':'No token yet.'};

  $scope.msg = ''; // single debug/information msg
  $scope.recordings = []; // recordings so far

  // these button things don't work yet
  $scope.recordBtnDisabled = false;
  $scope.stopBtnDisabled = true;
  $scope.saveBtnDisabled = true;

  var start_time = new Date().toISOString();
  var end_time;

  var audio_context;
  var recorder;
  function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    console.log('Media stream created.');
    // Uncomment if you want the audio to feedback directly
    //input.connect(audio_context.destination);
    //console.log('Input connected to audio context destination.');
    
    recorder = new Recorder(input);
    console.log('Recorder initialised.');
  }

  // controller functions
  recordCtrl.record = function() {
    recorder && recorder.record();
    $scope.msg = 'Recording now...';
    console.log('Recording...');

    // 
    tokenService.nextToken().then(function(data){
      $scope.displayToken = data['token'];
      currentToken = data;
    });

    $scope.recordBtnDisabled = true;
    $scope.stopBtnDisabled = false;
    $scope.saveBtnDisabled = true;
  };

  recordCtrl.stop = function() {
    $scope.msg = 'Processing wav...';

    recorder && recorder.stop();
    $scope.stopBtnDisabled = true;
    $scope.recordBtnDisabled = false;
    $scope.saveBtnDisabled = false;
    console.log('Stopped recording.');
    
    // create WAV download link using audio data blob and display on website
    createWav();
    
    recorder.clear();
  };

  recordCtrl.save = function() {
    $scope.msg = 'Saving and sending recs...';

    $scope.saveBtnDisabled = true;
    
    // these scope variables connected to user input obviously have to be sanitized.
    end_time = new Date().toISOString();
    var jsonData =  {                                                                  
                      "type":'session', 
                      "data":
                      {
                         "speakerId"      : ($scope.speakerId || 1),
                         "instructorId"   : ($scope.instructorId || 1),
                         "deviceId"       : ($scope.deviceId || 1),
                         "location"       : ($scope.curLocation || 'unknown'),
                         "start"          : start_time,
                         "end"            : end_time,
                         "comments"       : ($scope.comments || 'no comments'),
                         "recordingsInfo" : {}
                      }
                    };
    // update start time for next session
    start_time = new Date().toISOString();

    // and send it to remote server
    // test CORS is working
    $http({
      method: 'GET',
      url: '//'+BACKENDURL+'/submit/session'
    })
    .success(function (data) {
      console.log(data);
    })
    .error(function (data, status) {
      console.log(data);
      console.log(status);
    });

    // send our recording/s, and metadata as json
    var fd = new FormData();
    for (var i = 0; i < $scope.recordings.length; i++)
    {
      var rec = $scope.recordings[i];
      fd.append('rec'+i, rec.blob, rec.title);
      // all recordings get same tokenId for now
      jsonData["data"]["recordingsInfo"][rec.title] = { "tokenId" : 5 };
    }
    fd.append('json', JSON.stringify(jsonData));

    $http.post('http://'+BACKENDURL+'/submit/session', fd, {
      // this is so angular sets the correct headers/info itself
      transformRequest: angular.identity,
      headers: {'Content-Type': undefined}
    })
    .success(function (data) {
      console.log(data);
    })
    .error(function (data, status) {
      console.log(data);
      console.log(status);
    });
  };

  function createWav() {
    recorder && recorder.exportWAV(function(blob) {
      var url = URL.createObjectURL(blob);

      // display recordings on website
      $scope.recordings.push({"blob":blob,
                              "url":url,
                              "title":(new Date().toISOString() + '.wav')});
      $scope.saveBtnDisabled = false;

      $scope.$apply(); // update our bindings
    });
  }

  // kick it off
  try {
    // webkit shim
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia =  navigator.getUserMedia || navigator.webkitGetUserMedia ||
                              navigator.mozGetUserMedia || navigator.msGetUserMedia;
    window.URL = window.URL || window.webkitURL;
    
    audio_context = new AudioContext;
    console.log('Audio context set up.');
    console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    alert('No web audio support in this browser!');
  }
  
  navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
    console.log('No live audio input: ' + e);
  });
}]);

