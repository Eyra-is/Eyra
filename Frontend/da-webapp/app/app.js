'use strict';

var app = angular.module('daApp', ['LocalForageModule']);

app.controller('RecordingController', function($scope, $http, $localForage) {
  var recordCtrl = this;

  $scope.msg = '';
  $scope.outputDesc = '';
  $scope.outputLink = '';

  var recordBtnDisabled = false;
  var stopBtnDisabled = true;

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

    recordBtnDisabled = true;
    stopBtnDisabled = false;
    $scope.msg = 'Recording now...';
    console.log('Recording...');
  };

  recordCtrl.stop = function() {
    $scope.msg = 'Handing off the file now...';

    recorder && recorder.stop();
    stopBtnDisabled = true;
    recordBtnDisabled = false;
    console.log('Stopped recording.');
    
    // create WAV download link using audio data blob
    sendWav();
    
    recorder.clear();
  };

  function sendWav() {
    recorder && recorder.exportWAV(function(blob) {
      var url = URL.createObjectURL(blob);
      var li = document.createElement('li');
      var au = document.createElement('audio');
      var hf = document.createElement('a');
      
      au.controls = true;
      au.src = url;
      hf.href = url;
      hf.download = new Date().toISOString() + '.wav';
      hf.innerHTML = hf.download;
      li.appendChild(au);
      li.appendChild(hf);
      recordingslist.appendChild(li);
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




