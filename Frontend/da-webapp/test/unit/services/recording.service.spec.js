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

// NOTE: this file is similar to androidRecording.service.spec.js

"use strict";

describe('recording service', function(){
  beforeEach(module('daApp'));
  
  var $httpBackend, recordingService;
  beforeEach(inject(function(_$httpBackend_, _recordingService_){
    $httpBackend = _$httpBackend_;
    recordingService = _recordingService_;

    // mock the workaround with mobile where we use xhr to request a blob we should already have
    // see src/services/recording.service.js:createWavFromBlob
/*    $httpBackend.whenRoute('GET', ':url')
      .respond(function(method, url, data, headers, params) {
        return [200, new Blob()]; // return empty blob for mock purposes
      });*/
  }));

/*  afterEach(function() {
   $httpBackend.verifyNoOutstandingExpectation();
   $httpBackend.verifyNoOutstandingRequest();
  });*/

  // initialize recorder
  beforeEach(function(done){
    var initCallback = jasmine.createSpy('initCallback').and.callFake(done);
    recordingService.init(initCallback);
  });
  // setup
  var recordingCompleteCallback;
  beforeEach(function(){
    recordingCompleteCallback = jasmine.createSpy('recordingCompleteCallback');
    recordingService.setupCallbacks(recordingCompleteCallback);
  });

  it('should return an audio_context and a stream source', function(){
    // a way to get the e.g. [object Array], [object AudioContext]
    // see: http://javascript.info/tutorial/type-detection
    var toClass = {}.toString;
    expect(toClass.call(recordingService.getAudioContext())).toBe('[object AudioContext]');
    expect(toClass.call(recordingService.getStreamSource())).toBe('[object MediaStreamAudioSourceNode]');
  });

  // TODO actually test the recorderjs functionality. Right now this appears
  // to be hard due to window.postMessage usage. Something in this direction:
/*  it('should call recording complete callback appropriately', function(done){
    // try recording a couple of times (literally hehe)
    var T = 1;
    for (var i = 0; i < T; i++) {
      recordingService.record();
      recordingService.stop(true);
      $httpBackend.flush(1);
    }

    // should not call recording complete callback with .stop(falsy)
    recordingService.record();
    recordingService.stop(false);

    setTimeout(function(){
      expect(recordingCompleteCallback).toHaveBeenCalledTimes(T);

      expect(typeof(recordingService.currentRecording)).toEqual('object');
      expect(typeof(recordingService.currentRecording[0])).toEqual('object');
      expect(typeof(recordingService.currentRecording[0].blob)).toEqual('object');
      expect(typeof(recordingService.currentRecording[0].url)).toEqual('string');
      expect(typeof(recordingService.currentRecording[0].title)).toEqual('string');

      done();
    }, 500);
  });*/
});
