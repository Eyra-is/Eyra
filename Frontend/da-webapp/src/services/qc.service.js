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
  qcHandler.setupCallbacks = setupCallbacks;
  qcHandler.dataReady = function(){}; // needs to be set by calling controller

  // counter for the total times recording.controller.js 
  // has notified us of a send during this session
  var totalNotifies = 0;
  // counter to use for QC, counts how many recordings have been sent,
  //   since last reset of counter.
  var modSendCounter = 0;
  // {"module1" : id, ...} 
  var moduleRequestIds = {};

  // number of utterances currently included in report
  var lowerUtt = '?';
  var upperUtt = '?';
  var avgAcc = 1.0; // average accuracy of the recordings included in [lowerUtt, upperUtt]

  return qcHandler;

  //////////

  function setupCallbacks(dataReadyCallback) {
    qcHandler.dataReady = dataReadyCallback;
  }

  function notifySend(sessionId, tokenCount) {
    // tokenCount is the total count of token reads by current speaker
    // if tokenCount === 0 it is a new speaker
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

      if (sessionId) {
        delService.queryQC(sessionId)
        .then(handleQCReport, util.stdErrCallback);
      }
    }
  }

  function handleQCReport(response) {
    var report = response.data || {};
    
    //var result = updateModuleRequestIds(report); // do we have any new reports?

    if (report.status === 'processing') {
      // right now only uses MarosijoModule
      avgAcc = report.modules['MarosijoModule'].totalStats.avgAcc;
      lowerUtt = report.modules['MarosijoModule'].totalStats.lowerUtt;
      upperUtt = report.modules['MarosijoModule'].totalStats.upperUtt;

      qcHandler.dataReady({'avgAcc': avgAcc, 'lowerUtt': lowerUtt, 'upperUtt': upperUtt});
    }
  }

  function updateModuleRequestIds(report) {
    /*
      Updates this.moduleRequestIds, looks through the QC report
      and looks at module1.requestId and updates it here.

      :return: true if any requestId was updated
               false otherwise
    */
    var changed = false;
    for (var mod in report.modules) {
      if (!report.modules.hasOwnProperty(mod)) continue;

      if (moduleRequestIds[mod] !== report.modules[mod].requestId) {
        moduleRequestIds[mod] = report.modules[mod].requestId;
        changed = true;        
      }
    }
    return changed;
  }
}
}());