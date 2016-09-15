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

"use strict";

// create a special global needed for androidRecording service, pretty messy
var AndroidRecorder = {};
AndroidRecorder.startRecording = jasmine.createSpy('startRecording');
AndroidRecorder.stopRecording = jasmine.createSpy('stopRecording').and.returnValue('[]');

describe('android recording service', function(){
  beforeEach(module('daApp'));
  
  var recordingCompleteCallback = jasmine.createSpy('recordingCompleteCallback');
  var $httpBackend, androidRecordingService;
  beforeEach(inject(function(_$httpBackend_, _androidRecordingService_){
    $httpBackend = _$httpBackend_;
    androidRecordingService = _androidRecordingService_;
    androidRecordingService.setupCallbacks(recordingCompleteCallback);

    // mock the workaround with mobile where we use xhr to request a blob we should already have
    // see src/services/recording.service.js:createWavFromBlob
    $httpBackend.whenRoute('GET', ':url')
      .respond(function(method, url, data, headers, params) {
        return [200, new Blob()]; // return empty blob for mock purposes
      });
  }));

  afterEach(function() {
   $httpBackend.verifyNoOutstandingExpectation();
   $httpBackend.verifyNoOutstandingRequest();
  });

  it('should initialize', function(){
    var initCallback = jasmine.createSpy('initCallback');
    androidRecordingService.init(initCallback);
    expect(initCallback).toHaveBeenCalled();
  });

  it('should call stop and start recording and recording complete callback', function(done){
    // try recording a couple of times (literally hehe)
    var T = 2;
    for (var i = 0; i < T; i++) {
      androidRecordingService.record();
      androidRecordingService.stop(true);
      $httpBackend.flush(1);
    }

    expect(AndroidRecorder.startRecording).toHaveBeenCalledTimes(T);
    expect(AndroidRecorder.stopRecording).toHaveBeenCalledTimes(T);
    setTimeout(function(){
      expect(recordingCompleteCallback).toHaveBeenCalledTimes(T);
      done(); 
    }, 10);
  });
});
