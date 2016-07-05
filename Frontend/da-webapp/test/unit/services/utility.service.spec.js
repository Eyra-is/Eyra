"use strict";

describe('utility service', function(){
  beforeEach(module('daApp'));

  var util;
  beforeEach(inject(function(_utilityService_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    util = _utilityService_;
  }));

  describe('getIdxFromPath', function(){
    it('should correctly extract id', function() {
      var paths = ['localDb/sessions/0', 
                   'localDb/sessions/102', 
                   'localDb/sessions/-1', 
                   'localDb/sessions/0/blobs/6',
                   'localDb/sessions/100/blobs/70',
                   ['should produce an error since it\'s an array']
                  ];
      var expectedIdxs = [0, 102, -1, 6, 70, -1];

      expect(paths.length).toEqual(expectedIdxs.length);

      for (var i = 0; i < paths.length; i++) {
        var idx = util.getIdxFromPath(paths[i]);
        expect(idx).toEqual(expectedIdxs[i]);
      }
    });
  });

  describe('getConstant', function(){
    it('should return correct constants/types', function(){
      var currentKeys = [ 
        'invalidTitle',
        'tokenThreshold', 
        'tokenGetCount', 
        'QCAccThreshold',
        'QCFrequency',
        'QCInitRecThreshold',
        'tokenAnnouncementFreq',
        'tokenCountGoal',
        'syncRecCountPerSend'
      ];
      var valueTypes = [
        'string',
        'number',
        'number',
        'number',
        'number',
        'number',
        'number',
        'number',
        'number'
      ];

      expect(currentKeys.length).toEqual(valueTypes.length);

      for (var i = 0; i < currentKeys.length; i++) {
        var constant = util.getConstant(currentKeys[i]);
        expect(typeof(constant)).toEqual(valueTypes[i]);
      }
    });
  });

  describe('percentage', function(){
    it('should return correct numbers', function(){
      var args = [
        [3,9,2],
        [5,10,3]
      ];
      var expected = [
        33.33,
        50
      ];

      expect(args.length).toEqual(expected.length);

      for (var i = 0; i < args.length; i++) {
        var pr = util.percentage.apply(this, args[i]);
        expect(pr).toEqual(expected[i]);
      }
    });
  });

  describe('stdErrCallback', function(){
    it('should be defined', function(){
      expect(util.stdErrCallback).toBeDefined();
    });
  });
});