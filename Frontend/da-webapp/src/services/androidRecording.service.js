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
