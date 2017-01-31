"use strict";

describe('notification service', function(){
  beforeEach(module('daApp'));

  var notificationService, dataService, util;
  beforeEach(inject(function(_notificationService_, _dataService_, _utilityService_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    notificationService = _notificationService_;
    dataService = _dataService_;
    util = _utilityService_;
  }));

  it('should set display report in dataService after tokenCountGoal notifies', function() {
    var tokenCountGoal = 5;

    util.getConstant = jasmine.createSpy('util.getConstant').and.callFake(function(value){
      if (value === 'tokenCountGoal') {
        return tokenCountGoal;
      } else {
        return 'You need to program more return values.';
      }
    });

    dataService.set('speakerInfo', {});

    expect(dataService.get('DisplayReport')).toBe(undefined);

    var announcement = false;
    for (var i = 1; i <= tokenCountGoal; i++) {
      announcement = notificationService.notifySend(i);
      if (i !== tokenCountGoal) {
        expect(announcement).toBe(false);
      } else {
        expect(announcement).toBe(true);
      }
    }
    expect(dataService.get('DisplayReport').length).toBeGreaterThan(0);
  });
});