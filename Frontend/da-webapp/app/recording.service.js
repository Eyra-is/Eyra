// service to handle recording and saving of data

'use strict';

angular.module('daApp')
  .factory('recordingService', recordingService);

recordingService.$inject = ['$http', 
                            '$localForage',
                            'deliveryService'];

function recordingService($http, $localForage, deliveryService) {
  var recHandler = {};
  var delService = deliveryService;

  recHandler.init = init;
  recHandler.record = record;
  recHandler.send = send;
  recHandler.stop = stop;


  var invalidTitle = 'no_data.wav';
  // for some reason, putting this in an array, makes angular updates this correctly
  recHandler.currentRecording = [{  "blob":new Blob(),
                                    "url":'',
                                    "title":invalidTitle}];

  // local variable definitions for service
  var start_time;
  var end_time;

  var audio_context;
  var recorder;

  return recHandler;

  //////////

  function init(updateBindingsCallback, recordingCompleteCallback) {
    recHandler.updateBindingsCallback = updateBindingsCallback;
    recHandler.recordingCompleteCallback = recordingCompleteCallback;

    start_time = new Date().toISOString();

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

  // attempt to send recording with session info (speakerId, etc.) to server
  function send(speakerId, instructorId, deviceId, curLocation, comments, tokenId) {    
    end_time = new Date().toISOString();
    var jsonData =  {                                                                  
                      "type":'session', 
                      "data":
                      {
                        "speakerId"      : (speakerId || 1),
                        "instructorId"   : (instructorId || 1),
                        "deviceId"       : (deviceId || 1),
                        "location"       : (curLocation || 'unknown'),
                        "start"          : start_time,
                        "end"            : end_time,
                        "comments"       : (comments || 'no comments'),
                        "recordingsInfo" : {}
                      }
                    };
    jsonData["data"]["recordingsInfo"]
                [recHandler.currentRecording[0].title] = { "tokenId" : tokenId };

    // and send it to remote server
    // test CORS is working
    delService.testServerGet()
    .then(function (response) {
      console.log(response);
    }, function (response) {
      console.log(response);
    });

    // plump out the recording!
    delService.submitRecordings(jsonData, recHandler.currentRecording, invalidTitle)
    .then(function (response) {
      console.log(response);
    }, function (response) {
      console.log(response);
    });
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