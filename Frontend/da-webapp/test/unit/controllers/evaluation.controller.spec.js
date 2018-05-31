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

describe('evaluation controller', function(){
  beforeEach(module('daApp'));

  var $rootScope, $controller, $document, $httpBackend, $scope, evalCtrl;
  beforeEach(inject(function(_$rootScope_, _$controller_, _$document_, _$httpBackend_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    $rootScope = _$rootScope_;
    $controller = _$controller_;
    $document = _$document_;
    $httpBackend = _$httpBackend_;

    // same as in evaluation.service.spec.js
    $httpBackend.whenRoute('GET', '/backend/evaluation/set/:set/progress/:progress/count/:count')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        var set = params.set;
        var progress = Number(params.progress);
        var count = Number(params.count);

        //expect(testSets).toContain(set);
        expect(progress >= 0).toBe(true);
        expect(count).toBeGreaterThan(0);

        var partialSet = [];
        for (var i = 0; i < params.count; i++) {
          partialSet.push(['link','prompt']);
        }
        return [200, partialSet];
      });
    $httpBackend.whenRoute('GET', '/backend/evaluation/setinfo/:set')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        return [200, '{"count":50}'];
      });
    $httpBackend.whenRoute('GET', '/backend/evaluation/progress/user/:user/set/:set')
      .respond(function(method, url, data, headers, params) {
        // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
        return [200, '{"progress":2}'];
      });
    $httpBackend.whenRoute('GET', 'json/evaluation-comments.json')
    .respond(function(method, url, data, headers, params) {
      // for url of '/user/1234/article/567' params is {user: '1234', article: '567'}
      return [200, '["comment1", "comment2"]'];
    });

    $scope = {};
    $scope.$watch = function(){};

    evalCtrl = $controller('EvaluationController', { $scope: $scope });
    $httpBackend.flush(); // evalCtrl calls initSet which calls $http
  }));

  it('should initialize', function(){
    expect(typeof(evalCtrl.action)).toBe('function');
    expect(typeof(evalCtrl.skip)).toBe('function');
    expect(evalCtrl.actionBtnDisabled).toBeDefined();
    expect(evalCtrl.skipBtnDisabled).toBeDefined();
    expect(evalCtrl.undoBtnDisabled).toBeDefined();
    expect(typeof(evalCtrl.displayToken)).toBe('string');
    expect(typeof(evalCtrl.uttsGraded)).toBe('number');

    // wait for getProgress from server and addToBuffer
    setTimeout(function(){
      expect($rootScope.isLoaded).toBe(true);
    }, 50);
  });
});