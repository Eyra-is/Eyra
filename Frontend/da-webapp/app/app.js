'use strict';

var app = angular.module('daApp', ['LocalForageModule']);

app.config( [
      // make sure Angular doesn't prepend "unsafe:" to the blob: url
      '$compileProvider',
      function( $compileProvider )
      {   
          $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|blob):/);
      }
]);

app.filter("trustUrl", ['$sce', function ($sce) {
  return function (recordingUrl) {
    return $sce.trustAsResourceUrl(recordingUrl);
  };
}]);

app.controller('RecordingController', function($scope, $http, $localForage) {
  var recordCtrl = this;

  $scope.msg = ''; // single debug/information msg
  $scope.msg2 = '';
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

    $scope.recordBtnDisabled = true;
    $scope.stopBtnDisabled = false;
    $scope.saveBtnDisabled = true;
    $scope.msg = 'Recording now...';
    console.log('Recording...');
  };

  recordCtrl.stop = function() {
    $scope.msg = 'Handing off the file now...';

    recorder && recorder.stop();
    $scope.stopBtnDisabled = true;
    $scope.recordBtnDisabled = false;
    console.log('Stopped recording.');
    
    // create WAV download link using audio data blob and display on website
    displayWav();
    
    recorder.clear();
  };

  recordCtrl.save = function() {
    $scope.msg = 'Saving and sending recs...';

    $scope.saveBtnDisabled = true;
    
    end_time = new Date().toISOString();
    var jsonData = '{'+                                                                  
                     '  "type":"session",'+ 
                     '  "data":'+
                     '   {'+
                     '      "speakerId"      : '+ ($scope.speakerId || 1) +','+
                     '      "instructorId"   : '+ ($scope.instructorId || 1) +','+
                     '      "deviceId"       : '+ ($scope.deviceId || 1) +','+
                     '      "location"       : "'+ ($scope.curLocation || 'unknown') +'",'+
                     '      "start"          : "'+ start_time +'",'+
                     '      "end"            : "'+ end_time +'",'+
                     '      "comments"       : "'+ ($scope.comments || 'no comments') +'",'+
                     '      "recordingsInfo" :'+
                     '      {'+
                     '          "blob"                    : { "tokenId" : 5 }'+                        
                     '      }'+
                     '   }'+
                     '}';

    // and send it to remote server
    // test CORS is working
    $http({
      method: 'GET',
      url: 'http://127.0.0.1:5000/submit/session'
    })
    .success(function (data) {
      console.log(data);
    })
    .error(function (data, status) {
      console.log(data);
      console.log(status);
    });

    // send our recording/s, and metadata as json
    var rec = $scope.recordings[$scope.recordings.length-1];
    console.log(rec.blob);

    var fd = new FormData();
    fd.append('json', jsonData);
    fd.append('rec0', rec.blob);
    $http.post('http://127.0.0.1:5000/submit/session', fd, {
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

  function displayWav() {
    recorder && recorder.exportWAV(function(blob) {
      var url = URL.createObjectURL(blob);

      // display recordings on website
      $scope.recordings.push({"blob":blob,
                              "url":url,
                              "name":(new Date().toISOString() + '.wav')});
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
});




