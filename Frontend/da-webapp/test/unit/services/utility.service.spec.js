"use strict";

describe('utility service', function() {
  beforeEach(module('daApp'));

  var utilityService;
  beforeEach(inject(function(_utilityService_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    utilityService = _utilityService_;
  }));

  describe('getIdxFromPath', function() {
    it('should correctly extract id', function() {
      var util = utilityService;

      var paths = ['localDb/sessions/0', 
                   'localDb/sessions/102', 
                   'localDb/sessions/-1', 
                   'localDb/sessions/0/blobs/6',
                   'localDb/sessions/100/blobs/70'
                  ];
      var expectedIdxs = [0, 102, -1, 6, 70];

      expect(paths.length).toEqual(expectedIdxs.length);

      for (var i = 0; i < paths.length; i++) {
        var idx = util.getIdxFromPath(paths[i]);
        expect(idx).toEqual(expectedIdxs[i]);
      }
    });
  });
});