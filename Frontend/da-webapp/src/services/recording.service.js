/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

(function () {
// service to handle recording, basically a wrapper around recorderjs library

'use strict';

angular.module('daApp')
  .factory('recordingService', recordingService);

recordingService.$inject = ['$http', 'logger', 'utilityService'];

function recordingService($http, logger, utilityService) {
  var recHandler = {};
  var util = utilityService;

  recHandler.createWavFromBlob = createWavFromBlob; // exported for android audio recorder
  recHandler.getAudioContext = getAudioContext;
  recHandler.getStreamSource = getStreamSource;
  recHandler.init = init;
  recHandler.record = record;
  recHandler.setupCallbacks = setupCallbacks;
  recHandler.stop = stop;

  // local variable definitions for service
  var invalidTitle = util.getConstant('invalidTitle');
  
  // for some reason, putting this in an array, makes angular update this correctly
  recHandler.currentRecording = [{  "blob":new Blob(),
                                    "url":'',
                                    "title":invalidTitle}];

  var audio_context;
  var input;
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

  function getAudioContext() {
    return audio_context;
  }

  function getStreamSource() {
    return input;
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
    } else {
      logger.log('Token skipped, no recording made.');
    }
    
    recorder && recorder.clear();
  } 

  //////////

  function createWav() {
    recorder && recorder.exportWAV(function(blob) {
      createWavFromBlob(recHandler, blob); // calls the recording complete callback
    });
  }

  function createWavFromBlob(handler, blob) {
    var url = (window.URL || window.webkitURL).createObjectURL(blob);
    // workaround for mobile playback, where it didn't work on chrome/android.
    // fetch blob at url using xhr, and use url generated from that blob.
    // see issue: https://code.google.com/p/chromium/issues/detail?id=227476
    // thanks, gbrlg
    $http.get(url, {'responseType':'blob'}).then(
      function success(response) {
        var reBlob = response.data;
        if (reBlob) {
          url = (window.URL || window.webkitURL).createObjectURL(reBlob);
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
      handler.prevRecTitle = handler.currentRecording[0].title;
      // display recording on website
      handler.currentRecording[0] = { "blob":blob,
                                      "url":url,
                                      "title":(new Date().toISOString() + '.wav')};

      // notify main controller of completed recording
      handler.recordingCompleteCallback();
    }
  }

  function startUserMedia(stream) {
    input = audio_context.createMediaStreamSource(stream);
    // Fix for a firefox bug.
    // save a reference to the media stream source.
    // thanks, csch, http://stackoverflow.com/a/23486702/5272567
    window.source = input;
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
