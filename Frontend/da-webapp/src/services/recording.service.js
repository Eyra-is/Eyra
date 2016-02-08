(function () {
// service to handle recording, basically a wrapper around recorderjs

'use strict';

angular.module('daApp')
  .factory('recordingService', recordingService);

recordingService.$inject = ['$http', 'logger', 'utilityService'];

function recordingService($http, logger, utilityService) {
  var recHandler = {};
  var util = utilityService;

  recHandler.init = init;
  recHandler.record = record;
  recHandler.setupCallbacks = setupCallbacks;
  recHandler.stop = stop;

  // for some reason, putting this in an array, makes angular update this correctly
  recHandler.currentRecording = [{  "blob":new Blob(),
                                    "url":'',
                                    "title":invalidTitle}];

  // local variable definitions for service
  var invalidTitle = util.getConstant('invalidTitle');

  var audio_context;
  var recorder;

  return recHandler;

  //////////

  function init(initCompleteCallback) {
    recHandler.initCompleteCallback = initCompleteCallback;

    // kick it off
    try {
      // webkit shim
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia =  navigator.getUserMedia || navigator.webkitGetUserMedia ||
                                navigator.mozGetUserMedia || navigator.msGetUserMedia;
      window.URL = window.URL || window.webkitURL;
      
      audio_context = new AudioContext();
      logger.log('Audio context set up.');
      logger.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
    } catch (e) {
      alert('No web audio support in this browser!');
      logger.error(e);
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

  // setup callbacks for any controller which needs to use this service
  function setupCallbacks(recordingCompleteCallback) {
    recHandler.recordingCompleteCallback = recordingCompleteCallback;
  }

  function stop(valid) {
    recorder && recorder.stop();
    logger.log('Stopped recording.');

    if (valid) {
      // create WAV download link using audio data blob and display on website
      createWav();
    }
    
    recorder.clear();
  } 

  //////////

  function createWav() {
    recorder && recorder.exportWAV(function(blob) {
      var url = URL.createObjectURL(blob);
      // workaround for mobile playback, where it didn't work on chrome/android.
      // fetch blob at url using xhr, and use url generated from that blob.
      // see issue: https://code.google.com/p/chromium/issues/detail?id=227476
      // thanks, gbrlg
      $http.get(url, {'responseType':'blob'}).then(
        function success(response) {
          var reBlob = response.data;
          if (reBlob) {
            url = URL.createObjectURL(reBlob);
          }
          finishCreateWav();
        },
        function error(response) {
          logger.error(response);
          finishCreateWav();
        }
      );

      // just added because of the async nature of $http
      function finishCreateWav() {
        recHandler.prevRecTitle = recHandler.currentRecording[0].title;
        // display recording on website
        recHandler.currentRecording[0] = {  "blob":blob,
                                            "url":url,
                                            "title":(new Date().toISOString() + '.wav')};

        // notify main controller of completed recording
        recHandler.recordingCompleteCallback();
      }
    });
  }

  function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    logger.log('Media stream created.');
    // Uncomment if you want the audio to feedback directly
    //input.connect(audio_context.destination);
    //logger.log('Input connected to audio context destination.');
    
    recorder = new Recorder(input, { 'numChannels':1 });
    logger.log('Recorder initialised.');

    recHandler.initCompleteCallback(true);
  }
}
}());
