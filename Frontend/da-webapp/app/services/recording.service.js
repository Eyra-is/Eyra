// service to handle recording, basically a wrapper around recorderjs

'use strict';

angular.module('daApp')
  .factory('recordingService', recordingService);

recordingService.$inject = ['logger', 'utilityService'];

function recordingService(logger, utilityService) {
  var recHandler = {};
  var util = utilityService;

  recHandler.init = init;
  recHandler.record = record;
  recHandler.stop = stop;

  // for some reason, putting this in an array, makes angular updates this correctly
  recHandler.currentRecording = [{  "blob":new Blob(),
                                    "url":'',
                                    "title":invalidTitle}];

  // local variable definitions for service
  var invalidTitle = util.getConstant('invalidTitle');

  var audio_context;
  var recorder;

  return recHandler;

  //////////

  function init(initCompleteCallback, updateBindingsCallback, recordingCompleteCallback) {
    recHandler.updateBindingsCallback = updateBindingsCallback;
    recHandler.recordingCompleteCallback = recordingCompleteCallback;
    recHandler.initCompleteCallback = initCompleteCallback;

    // kick it off
    try {
      // webkit shim
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia =  navigator.getUserMedia || navigator.webkitGetUserMedia ||
                                navigator.mozGetUserMedia || navigator.msGetUserMedia;
      window.URL = window.URL || window.webkitURL;
      
      audio_context = new AudioContext;
      logger.log('Audio context set up.');
      logger.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
    } catch (e) {
      alert('No web audio support in this browser!');
    }
    
    navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
      logger.error('No live audio input: ' + e);

      recHandler.initCompleteCallback(false);
    });
  }

  function record() {
    logger.log('Recording...');
    recorder && recorder.record();
  }

  function stop() {
    recorder && recorder.stop();
    logger.log('Stopped recording.');
    
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
    logger.log('Media stream created.');
    // Uncomment if you want the audio to feedback directly
    //input.connect(audio_context.destination);
    //logger.log('Input connected to audio context destination.');
    
    recorder = new Recorder(input);
    logger.log('Recorder initialised.');

    recHandler.initCompleteCallback(true);
  }
}