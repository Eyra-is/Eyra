(function () {
// service to handle all processing realted to the QC. Querying the server, processing the information for example.

'use strict';

angular.module('daApp')
  .factory('qcService', qcService);

qcService.$inject = ['$q', 'dataService', 'deliveryService', 'logger', 'utilityService'];

function qcService($q, dataService, deliveryService, logger, utilityService) {
  var qcHandler = {};
  var delService = deliveryService;
  var util = utilityService;

  qcHandler.notifySend = notifySend;

  // counter for the total times recording.controller.js has notified us of a send
  var totalNotifies = 0;
  // counter to use for QC, counts how many recordings have been sent,
  //   since last reset of counter.
  var modSendCounter = 0;

  return qcHandler;

  //////////

  function notifySend(sessionId) {
    totalNotifies++;
    modSendCounter++;

    if (modSendCounter >= (util.getConstant('QCFrequency' || 5))
       && totalNotifies >= (util.getConstant('QCInitRecThreshold') || 10)) {
      modSendCounter = 0;

      
      return delService.queryQC(sessionId)
      .then(function (response){
        console.log(response);
        var report = response.data;

        var tokenAnnouncement = totalNotifies % util.getConstant('TokenAnnouncementFreq') === 0;
        if (tokenAnnouncement) {
          report.tokenCount = totalNotifies;
        }

        dataService.set('QCReport', report);
        // message to send back to recording.controller.js notifying that we wish
        //   results to be displayed.
        var displayResults = tokenAnnouncement
                             || report.totalStats.accuracy < util.getConstant('QCAccThreshold');
        if (displayResults) {
          return $q.when(true);
        } else {
          return $q.reject(false);
        }
      },
      util.stdErrCallback);
    }
    return $q.when(true); //debug
  }
}
}());
