(function () {
'use strict';

angular.module('daApp')
.controller('SyncController', SyncController);

SyncController.$inject = ['$rootScope', 
                          '$scope', 
                          'dataService',
                          'deliveryService', 
                          'localDbMiscService', 
                          'logger', 
                          'tokenService', 
                          'utilityService'];

function SyncController($rootScope, $scope, dataService, deliveryService, localDbMiscService, logger, tokenService, utilityService) {
  var syncCtrl = this;
  var dbService = localDbMiscService;
  var delService = deliveryService;
  var util = utilityService;
  
  syncCtrl.sync = sync;

  $rootScope.isLoaded = true;
  $scope.hide_recording = true;
  $scope.hide_sync = false;
  $scope.hide_wifi_msg = true;

  $scope.tokensRead = 0;
  $scope.recsDelivered = 0;
  $scope.recsSaved = 0;

  activate();
  
  //////////

  function activate() {
    // TODO move this token logic to a service, as well as logic in rec controller

    // get tokensRead
    var speakerInfo = dataService.get('speakerInfo');
    if (speakerInfo) {
      var tokensRead = speakerInfo.tokensRead;
      if (!tokensRead) {
        // get from ldb
        dbService.getSpeaker(dataService.get('speakerName')).then(function(speaker){
          if (speaker) {
            tokensRead = speaker.tokensRead;
            $scope.tokensRead = tokensRead || $scope.tokensRead;
          }
        },
        util.stdErrCallback);
      } else {
        $scope.tokensRead = tokensRead;
      }
    }

    // get recsDelivered
    var recsDelivered = dataService.get('recsDelivered');
    if (!recsDelivered) {
      dbService.getSpeaker(dataService.get('speakerName')).then(function(speaker){
        if (speaker) {
          $scope.recsDelivered = speaker.recsDelivered || $scope.recsDelivered;
        }
      },
      util.stdErrCallback);
    } else {
      $scope.recsDelivered = recsDelivered;
    }

    // get tokens saved locally, changes $scope.recsSaved
    updateRecsSaved();
  }

  function updateRecsSaved() {
    dbService.getRecsSaved().then(
      function success(count) {
        $scope.recsSaved = count || 0;
      },
      function error(error) {
        $scope.recsSaved = 0;
        logger.error(error);
      }
    );    
  }

  // sends all available sessions from local db to server, one session at a time
  // assumes internet connection
  function sync() {
    $scope.hide_sync = true;

    $scope.msg = 'Syncing - please wait';

    delService.sendLocalSessions(syncDoneCallback);
  }

  // result is true if sync completed successfully
  function syncDoneCallback(result) {
    $scope.msg = result ? 'Sync complete.' : 'Sync failed.';
    $scope.hide_sync = false;
    $scope.recsDelivered = dataService.get('recsDelivered') || $scope.recsDelivered || 0;
    updateRecsSaved();
    
    if (!result){
      $scope.wifi_msg = 'Please connect device to wifi or ethernet.';
      $scope.hide_recording = true;
      $scope.hide_wifi_msg = false;
    } else {
      // sync success
      $scope.hide_recording = false;
      $scope.hide_wifi_msg = true;
    }
  }
}
}());
