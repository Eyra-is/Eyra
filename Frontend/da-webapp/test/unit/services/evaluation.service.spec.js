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

describe('evaluation service', function(){
  beforeEach(module('daApp'));
  // TODO handle more than one set
  var testSets = ['Random'];
  // TODO handle more than evalBufferSize TESTNEXTS
  var TESTNEXTS = 4; // test getNext X times.
  var evalBufferSize = 5; // should be same as in utilityService

  var $httpBackend, evalService;
  beforeEach(inject(function(_$httpBackend_, _evaluationService_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    $httpBackend = _$httpBackend_;
    evalService = _evaluationService_;

    $httpBackend.whenRoute('GET', '/backend/evaluation/set/:set/progress/:progress/count/:count')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        var set = params.set;
        var progress = Number(params.progress);
        var count = Number(params.count);

        expect(testSets).toContain(set);
        expect(progress >= 0).toBe(true);
        expect(count).toBeGreaterThan(0);

        var partialSet = [];
        for (var i = 0; i < params.count; i++) {
          partialSet.push(['link'+i,'prompt'+i]);
        }
        return [200, partialSet];
      });
    $httpBackend.whenRoute('POST', '/backend/evaluation/submit/:set')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        var set = params.set;

        expect(testSets).toContain(set);

        return 200;
      });
    $httpBackend.whenRoute('GET', '/backend/evaluation/setinfo/:set')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        var set = params.set;

        expect(testSets).toContain(set);

        return [200, '{"count":50}'];
      });
    $httpBackend.whenRoute('GET', '/backend/evaluation/progress/user/:user/set/:set')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        var set = params.set;
        var user = params.user;

        expect(testSets).toContain(set);

        return [200, '{"progress":541}'];
      });
  }));

  afterEach(function() {
   $httpBackend.verifyNoOutstandingExpectation();
   $httpBackend.verifyNoOutstandingRequest();
  });

  it('should initialize sets, and be able to grab nexts', function(){
    testSet(testSets[0]);

    // this is real messy
    // thanks, hansmaad, http://stackoverflow.com/a/37750595/5272567
    try { $httpBackend.flush(99); }  // resolve all the possible requests my service might have to do
    catch(e) {}

    function testSet(set) {
      var promise = evalService.initSet(set);
      $httpBackend.flush();
      promise.then(function(){
        for (var j = 0; j < TESTNEXTS; j++) {
          var next = j === 0 ? evalService.getNext('initial') : evalService.getNext(4);

          expect(typeof(next[0])).toBe('string');
          expect(typeof(next[1])).toBe('string');
        }
      }, function(){
        fail('Error in initSet.');
      });
    }
  });

  it('should correctly undo and be able to click next afterwards', function(){
    var promise = evalService.initSet(testSets[0]);
    $httpBackend.flush();
    promise.then(function(){
      evalService.getNext('initial');
      // prompt is short for recnprompt
      var oldPrompt = evalService.getNext(4);
      var newPrompt = evalService.getNext(4);
      var undoPrompt = evalService.undo();
      expect(oldPrompt).toBe(undoPrompt);
      var afterUndoPrompt = evalService.getNext(4);
      expect(newPrompt).toBe(afterUndoPrompt);
    }, function(){
      fail('Error in initSet.');
    });
  });
});