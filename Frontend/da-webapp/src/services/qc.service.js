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

  function notifySend(sessionId, tokenCount) {
    totalNotifies++;
    modSendCounter++;

    // if totalNotifies is higher than the token count, it probably means
    //   a new user is recording starting at 0 tokens read.
    if (totalNotifies > tokenCount) {
      totalNotifies = 1;
      modSendCounter = 1;
    }

    if (modSendCounter >= (util.getConstant('QCFrequency' || 5))
       && totalNotifies >= (util.getConstant('QCInitRecThreshold') || 10)) {
      modSendCounter = 0;

      return delService.queryQC(sessionId)
      .then(handleQCReport, util.stdErrCallback);
    } else {
      return $q.reject(false);
    }
  }

  function handleQCReport(response) {
    var report = response.data || {};
    var tokenAnnouncement = handleTokenAnnouncements(report);
    var displayReport = prettify(report);

    dataService.set('QCReport', displayReport);

    // message to send back to recording.controller.js notifying that we wish
    //   results to be displayed.
    var displayResults = tokenAnnouncement
                         || report.totalStats.accuracy < util.getConstant('QCAccThreshold');
    if (displayResults) {
      return $q.when(true);
    } else {
      return $q.reject(false);
    }
  }

  // like for example, display, good job! on each 50 tokens read.
  // adds key tokenCount and tokenCountMsg to report.
  function handleTokenAnnouncements(report) {
    var tokenAnnouncement = totalNotifies > 0
                            && totalNotifies % util.getConstant('TokenAnnouncementFreq') === 0;
    var totalTokens = util.getConstant('TokenCountGoal') || 260;
    if (tokenAnnouncement) {
      report.tokenCount = totalNotifies;
      // some gamifying messages to pump up the speakers
      report.tokenCountMsg = 'Nice, '+util.percentage(totalNotifies, totalTokens, 2)+'% of the tokens read, keep going.';
      if (totalNotifies >= 100) {
        report.tokenCountMsg = 'Sweet, '+util.percentage(totalNotifies, totalTokens, 2)+'% of the tokens.';
      }
      if (totalNotifies >= 200) {
        report.tokenCountMsg = util.percentage(totalNotifies, totalTokens, 2)+'% of the tokens? Wow.'
      }
      if (totalNotifies >= 300) {
        report.tokenCountMsg = 'Awesome, '+util.percentage(totalNotifies, totalTokens, 2)+'% of the tokens. Just awesome';
      }
      if (totalNotifies >= 400) {
        report.tokenCountMsg = 'You are a god: '+util.percentage(totalNotifies, totalTokens, 2)+'% of the tokens.';
      }
    }
    return tokenAnnouncement;
  }

  // parses the JSON object report into some prettified report to display in HTML
  function prettify(report) {
    var out = '';
    if (report.tokenCountMsg) {
      out += '<p class="message">'+report.tokenCountMsg+'</p>\n';
    }
    if (report.totalStats) {
      out += '<p class="message">Average accuracy: '+util.percentage(report.totalStats.accuracy, 1, 3)+'%</p>';
    }
    if (report.perRecordingStats) {
      out += '<h3>More stats</h3>';
      out += '<ul>';
      for (var i = 0; i < report.perRecordingStats.length; i++) {
        var acc = report.perRecordingStats[i].stats.accuracy;
        out += '    <li>Rec. '+i+', accuracy: '+util.percentage(acc, 1, 3)+'%</li>';
      }
      out += '</ul>';
    }
    return out;
  }
}
}());
