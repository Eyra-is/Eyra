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
// Service to notify user (e.g. during recording) with for example a popup on a certain amount of prompts read.

'use strict';

angular.module('daApp')
  .factory('notificationService', notificationService);

notificationService.$inject = ['dataService', 'logger', 'utilityService'];

function notificationService(dataService, logger, utilityService) {
  var notifHandler = {};
  var util = utilityService;

  notifHandler.notifySend = notifySend;

  // counter for the total times recording.controller.js 
  // has notified us of a prompt read during this session
  var totalNotifies = 0;

  // disabled gratulations on completed desired tokens
  var displayedGratulations = false;

  return notifHandler;

  //////////

  function notifySend(tokenCount) {
    // tokenCount is the total count of token reads by current speaker
    // if tokenCount === 0 it is a new speaker
    totalNotifies++;

    // if totalNotifies is higher than the token count, it probably means
    //   a new user is recording starting at 0 tokens read.
    if (totalNotifies > tokenCount) {
      totalNotifies = 1;
      displayedGratulations = false;
    }

    var report = {};
    var tokenAnnouncement = handleTokenAnnouncements(report);

    if (tokenAnnouncement) {
      // displayReport is in HTML
      var displayReport = prettify(report);
      dataService.set('DisplayReport', displayReport);
    }

    return tokenAnnouncement;
  }

  // like for example, display, good job! on each 50 tokens read.
  // adds key tokenCount and tokenCountMsg to report.
  function handleTokenAnnouncements(report) {
    
    // After 500 tokens read, display a special notification.
    var _totalNotifies;
    var tokensRead = dataService.get('speakerInfo').tokensRead;
    if (tokensRead){
      _totalNotifies = tokensRead;
    } else {
      _totalNotifies = totalNotifies;
    }

    var tokenCountGoal = util.getConstant('tokenCountGoal') || 500;
    // lets keep a small margin (+3) in case some error was made and user skips the exact tokenCountGoal number
    if (_totalNotifies >= tokenCountGoal && !(_totalNotifies > tokenCountGoal + 3) && !displayedGratulations) {
      report.tokenCountMsg = 'You have reached the set goal of '+tokenCountGoal+' prompts. Thank you very much for your contribution.';
      displayedGratulations = true;
      return true;
    }
    return false;
    /*var tokenAnnouncement = _totalNotifies > 0
                            && totalNotifies % util.getConstant('tokenAnnouncementFreq') === 0;

    var totalTokens = util.getConstant('tokenCountGoal') || 260;
    if (tokenAnnouncement) {
      report.tokenCount =  tokensRead;
      // some gamifying messages to pump up the speakers
      
      report.tokenCountMsg = 'Nice, '+util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens read, keep going.';
      if (totalNotifies >= 100 && totalNotifies < 200) {
        report.tokenCountMsg = 'Sweet, '+util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens.';
      }
      if (totalNotifies >= 200 && totalNotifies < 300) {
        report.tokenCountMsg = util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens? Wow.'
      }
      if (totalNotifies >= 300 && totalNotifies < 400) {
        report.tokenCountMsg = 'Awesome, '+util.percentage(t_otalNotifies, totalTokens, 2)+'% of the tokens. Just awesome';
      }
      
      var tokensLeftToRead = totalTokens - tokensRead;

      if (tokensLeftToRead > 0){
        report.tokensLeftToReadMsg = 'You have ' + tokensLeftToRead + ' tokens of ' + totalTokens + ' left to read.';
      }     
    }
    return tokenAnnouncement;*/
  }

  // parses the JSON object report into some prettified report to display in HTML
  function prettify(report) {
    var out = '';
    if (report.tokenCountMsg) {
      out += '<p class="message">'+report.tokenCountMsg+'</p>\n';
      
    }
    if (report.tokensLeftToReadMsg){
      out += '<p class="message">'+report.tokensLeftToReadMsg+'</p>\n';
    }
    
    return out;
  }
}
}());