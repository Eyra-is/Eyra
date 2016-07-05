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
// service to handle recording through the android WebView.
// called in exactly the same way as recording.service.js, must therefore export same functions. 

// assumes interface from WebView, AndroidRecorder

'use strict';

angular.module('daApp')
  .factory('androidRecordingService', androidRecordingService);

androidRecordingService.$inject = ['logger', 'recordingService', 'utilityService'];

function androidRecordingService(logger, recordingService, utilityService) {
  var recHandler = {};
  var recService = recordingService;
  var util = utilityService;

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
  try {
    recorder = AndroidRecorder; // set recorder to be the recorder JS interface with android app
  } catch (e) {
    return {}; // this should never happen
  }
  return recHandler;

  //////////

  function init(initCompleteCallback) {
    recHandler.initCompleteCallback = initCompleteCallback;

    logger.log('In android recorder.');

    initCompleteCallback(true);
  }

  function getAudioContext() {
    return audio_context;
  }

  function getStreamSource() {
    return input;
  }

  function record() {
    logger.log('Android recording...');
    recorder.startRecording();
  }

  // setup callbacks for any controller which needs to use this service
  function setupCallbacks(recordingCompleteCallback) {
    recHandler.recordingCompleteCallback = recordingCompleteCallback;
  }

  function stop(valid) {
    var data = recorder.stopRecording();
    logger.log('Android stopped recording.');

    if (valid) {
      data = JSON.parse(data);
      data = new Uint8Array(data);
      var blob = new Blob([data], { type: 'audio/wav' });
      // display recording on website
      recService.createWavFromBlob(recHandler, blob);
    } else {
      logger.log('Token skipped, no recording made.');
    }
  } 
}
}());
