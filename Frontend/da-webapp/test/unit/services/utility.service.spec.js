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
        'syncRecCountPerSend',
        'evalBufferSize'
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

  describe('generateUUID', function(){
    it('should generate uuid on rfc4122 version 4 format', function(){
      var uuid = util.generateUUID();
      // match RFC 4122: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
      // https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_.28random.29
      //[0-9A-Fa-f]{6}
      expect(uuid.match(/^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/)).toBeTruthy();
    });

    it('should not be the same if repeated many times', function(){
      var REPEAT = 300; // lets not go overboard here.
      var uuids = [];
      for (var i = 0; i < REPEAT; i++) {
        uuids.push(util.generateUUID());
        for (var j = 0; j < i; j++) {
          expect(uuids[j]).not.toEqual(uuids[i]);
        }
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