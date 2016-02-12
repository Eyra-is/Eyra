(function () {
// service for the volume meter, uses volume-meter.js. Code in part from
//   https://github.com/cwilso/volume-meter

'use strict';

angular.module('daApp')
  .factory('volumeMeterService', volumeMeterService);

volumeMeterService.$inject = ['logger'];

function volumeMeterService(logger) {
  var volHandler = {};

  volHandler.init = init;

  var canvas = document.getElementById('volume-meter');
  var canvasContext = canvas.getContext('2d');
  var WIDTH = canvas.attributes['width'].value;
  var HEIGHT = canvas.attributes['height'].value;
  var rafID;
  var meter;

  return volHandler;

  //////////

  function init(audioContext, mediaStreamSource) {
    if (!audioContext || !mediaStreamSource) {
      return false;
    }

    // Create a new volume meter and connect it.
    meter = createAudioMeter(audioContext);
    mediaStreamSource.connect(meter);
    // kick off the visual updating
    drawLoop();

    return true;
  }

  function drawLoop(time) {
    // clear the background
    canvasContext.clearRect(0,0,WIDTH,HEIGHT);

    // check if we're currently clipping
    if (meter.checkClipping())
        canvasContext.fillStyle = 'red';
    else
        canvasContext.fillStyle = 'green';

    // draw a bar based on the current volume
    canvasContext.fillRect(0, 0, meter.volume*WIDTH*1.4, HEIGHT);

    // set up the next visual callback
    rafID = window.requestAnimationFrame(drawLoop);
  }
}
}());
