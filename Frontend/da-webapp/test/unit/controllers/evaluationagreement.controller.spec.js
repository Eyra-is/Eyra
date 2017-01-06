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

This file is very similar to recordingagreement.controller.spec.js (not very DRY)
*/

"use strict";

describe('evaluation agreement controller', function(){
  beforeEach(module('daApp'));

  var $rootScope, $controller, $scope, $location, agrCtrl, dataService;
  beforeEach(inject(function(_$rootScope_, _$controller_, _$location_, _dataService_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    $rootScope = _$rootScope_;
    $controller = _$controller_;
    $location = _$location_;
    $location.path = jasmine.createSpy('$location.path');
    dataService = _dataService_;

    $scope = {};
    $scope.$watch = function(){};
    agrCtrl = $controller('EvaluationAgreementController', { $scope: $scope });
  }));

  it('should initialize', function(){
    expect(typeof(agrCtrl.submit)).toBe('function');

    setTimeout(function(){
      expect($rootScope.isLoaded).toBe(true);
    }, 50);
  });

  it('should display error message if name or email not filled out', function(){
    var oldMessage = $scope.msg;
    agrCtrl.submit();
    var newMessage = $scope.msg;

    expect(newMessage).not.toBe(oldMessage);

    // now try if one of them is filled out
    $scope.msg = oldMessage;
    agrCtrl.email = 'only@email.com';
    agrCtrl.submit();
    var newMessage = $scope.msg;
    
    expect(newMessage).not.toBe(oldMessage);
  });

  it('should not redirect if agreement declined, and display error message', function(){
    var oldMessage = $scope.msg;
    agrCtrl.submit('decline');
    var newMessage = $scope.msg;

    expect(newMessage).not.toBe(oldMessage);

    expect($location.path).not.toHaveBeenCalled();
  });

  it('should redirect if agreement accepted, set fullName/email\
      in dataService and set $rootScope.evalAgreementSigned to true', function(){
    var fullName = 'Warner Bro';
    var email = 'warner@bros.com';
    agrCtrl.fullName = fullName;
    agrCtrl.email = email;

    agrCtrl.submit('accept');

    expect($rootScope.evalAgreementSigned).toBe(true);
    expect($location.path).toHaveBeenCalledWith('/evaluation');
    expect(dataService.get('evalFullName')).toEqual(fullName);
    expect(dataService.get('evalEmail')).toEqual(email);
  });
});