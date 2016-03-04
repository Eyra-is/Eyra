(function () {
// service to handle all processing realted to the QC. Querying the server, processing the information for example.

'use strict';

angular.module('daApp')
  .factory('qcService', qcService);

qcService.$inject = ['dataService', 'logger', 'utilityService'];

function qcService(dataService, logger, utilityService) {
  var qcHandler = {};
  var util = utilityService;

  qcHandler.notifySend = notifySend;

  // counter to use for QC, counts how many recordings have been sent,
  //   since last reset of counter.
  var modSendCounter = 0;

  return qcHandler;

  //////////

  function notifySend() {
    modSendCounter++;

    if (modSendCounter >= (util.getConstant('QCFrequency') || 5)) {
      modSendCounter = 0;

      var oldSessionId = dataService.get('sessionId');
      var sessionId;

      // if no error, save sessionId to RAM to be used to identify session
      //   in later requests (e.g. QC reports)
      try {
        sessionId = response.data.sessionId;
        if (sessionId) {
          dataService.set('sessionId', sessionId); // set it in ram
        } else {
          $scope.msg = 'Something went wrong.';
        }
      } catch (e) {
        logger.error(e);
      }

      // query for QC report with last used session (should be same probably)
      //   and if non-existant, use the one we got now, and if non-existant don't move.
      var sessionIdToUse = oldSessionId || sessionId;
      if (sessionIdToUse) {
        delService.queryQC(sessionIdToUse)
        .then(function (response){
          logger.log(response);
        },
        util.stdErrCallback)
      }
    }

    var displayResults = true;
    if (displayResults) {
      return true;
    }
  }
}
}());
