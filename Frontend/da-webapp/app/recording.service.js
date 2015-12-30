// service to handle recording, basically a wrapper around recorderjs

'use strict';

angular.module('daApp')
  .factory('recordingService', recordingService);

//recordingService.$inject = [];

function recordingService() {
  var recHandler = {};

  recHandler.init = init;
  recHandler.record = record;
  recHandler.stop = stop;

  // give caller info on what is the title sentinel value
  recHandler.invalidTitle = 'no_data.wav';
  // for some reason, putting this in an array, makes angular updates this correctly
  recHandler.currentRecording = [{  "blob":new Blob(),
                                    "url":'',
                                    "title":recHandler.invalidTitle}];

  // local variable definitions for service
  var audio_context;
  var recorder;

  return recHandler;

  //////////

  function init(updateBindingsCallback, recordingCompleteCallback) {
    recHandler.updateBindingsCallback = updateBindingsCallback;
    recHandler.recordingCompleteCallback = recordingCompleteCallback;

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
  }

  function record() {
    console.log('Recording...');
    recorder && recorder.record();
  }

  function stop() {
    recorder && recorder.stop();
    console.log('Stopped recording.');
    
    // create WAV download link using audio data blob and display on website
    createWav();
    
    recorder.clear();
  } 

  //////////

  function createWav() {
    recorder && recorder.exportWAV(function(blob) {
      var url = URL.createObjectURL(blob);

      recHandler.prevRecTitle = recHandler.currentRecording[0].title;
      // display recording on website
      recHandler.currentRecording[0] = {  "blob":blob,
                                          "url":url,
                                          "title":(new Date().toISOString() + '.wav')};

      // angular didn't update bindings on that recordings push, so we do it manually
      // through this callback function from the controller
      recHandler.updateBindingsCallback();
      // notify main controller of completed recording
      recHandler.recordingCompleteCallback();
    });
  }

  function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    console.log('Media stream created.');
    // Uncomment if you want the audio to feedback directly
    //input.connect(audio_context.destination);
    //console.log('Input connected to audio context destination.');
    
    recorder = new Recorder(input);
    console.log('Recorder initialised.');
  }
}