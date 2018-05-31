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
// service with utility functions for the app and for now, contains many configurable aspects, see also app.js.

'use strict';

angular.module('daApp')
  .factory('utilityService', utilityService);

utilityService.$inject = ['logger'];

function utilityService(logger) {
  var utilityHandler = {};

  utilityHandler.getConstant = getConstant;
  utilityHandler.getIdxFromPath = getIdxFromPath;
  utilityHandler.generateUUID = generateUUID;
  utilityHandler.percentage = percentage;
  utilityHandler.stdErrCallback = stdErrCallback;

  var CONSTANTS = { 
    //To change to English you must modify these files:

    //-must change "label" in "speaker-info-format.json" to the correct translation

    //-must change evalueation-comments.json:
      //1. change EVALUATIONCOMMENTSURL in evaluation.controller.js from 'json/evaluation-comments.json' to 'json/evaluation-comments-isl.json'
      //2. in Gruntfil.js change:
        //"match: /json\/evaluation-comments-isl\.json/g, 
         //replacement: 'json/evaluation-comments-isl.'+cache_breaker+'.json'"
         //to
         // "match: /json\/evaluation-comments\.json/g,
         // replacement: 'json/evaluation-comments.'+cache_breaker+'.json'"

    //-must change index page: nav bar and loading msg


    'invalidTitle' : 'no_data.wav', // sentinel value for invalid recordings
    'tokenThreshold' : 5, 
    'tokenGetCount' : 10, 
    'QCAccThreshold' : 0.2, // if accuracy falls below this, meter will display red
    'QCFrequency' : 5, // per sessions sent
    'QCInitRecThreshold' : 5, // recording count before QC can report, adjustment period for speaker
    'QCHighThreshold' : 0.7, // if accuracy falls below this, meter will display yellow instead of green
    'tokenAnnouncementFreq' : 500,
    'tokenCountGoal' : 500, // how many prompts should a user read?
    'syncRecCountPerSend' : 5, // recs to send each transmission to server during a Sync operation,
    'evalBufferSize' : 5, // number of prompts and/or recs to fetch and keep in memory during evaluation
    'evalSubmitFreq' : 5, // per utterance graded, after X send to server
    'RECAGREEMENT' : true, // include the recording participant agreement
    //language specific constants
    //evaluation login
    'ENTERINFO' : 'Fylltu inn þínar upplýsingar', //'Enter your info',
    'SETTEXT' : 'Sett', //'Set',
    'NAMEPLACEHOLDERTEXT' : 'Anna4',  //'Jane4',
    //evaluation 
    'PLAYTEXT' : 'Spila', //'Play',
    'PAUSETEXT' : 'Stoppa', //'Pause',
    'NOTOKENTEXT' : 'Textabrot enn ósótt.',  //'No prompt yet.',
    'GRADECOMPLETETEXT' : 'Einkunnagjöf fyrir sett lokið. Kærar þakkir.',  //'Grading set complete. Thank you.',
    'GRADETEXT' : 'Einkunn',  //'Grade',
    'COMMENTTEXT' : 'Athugasemd',  //'Comment',
    'UNDOTEXT' : 'Afturkalla',  //'Undo',
    'AUTOPLAYTEXT' : 'Sjálfvirk spilun',  //'Autoplay',
    'UTTGRADEDTEXT' : 'Frasar yfirfarnir',  //'Utterances graded',
    'USERTEXT' : 'Notandi',  //'User',
    'SETTEXTMIN' : 'sett',  //'set',
    //info
    'VERSIONTEXT' : 'Útgáfa',  //'Version',
    //login
    'LOGINTEXT' : 'Innskráning',  //'Login',
    'PASSWORDTEXT' : 'Lykilorð',  //'Password',
    //main
    'STARTTEXT' : 'Byrja',  //'Begin',
    //more
    'ADDSPEAKERTEXT' : 'Bæta við ræðumanni',  //'Add speaker',
    'SETINSTRUCTORTEXT' : 'Bæta við leiðbeinanda',  //'Set instructor',
    'REGISTERDEVICETEXT' : 'Skrá tæki',  //'Register device',
    'LOGOUTTEXT' : 'Útskráning',  //'Logout',
    'GETTOKENTEXT' : 'Sækja textabrot (dev)',  //'Get tokens (dev)',
    'CLEARDBTEXT' : 'Hreinsa staðbundin gögn (dev)',  //'Clear local db (dev)',
    'CLEARTOKENSDBTEXT' : 'Hreinsa öll textabrot (dev)',  //'Clear all tokens (dev)',
    'PRINTLOGSTEXT' : 'Skrifa út atburðaskrár (dev)',  //'Print logs (dev)',
    'CONFIRMMSG' : 'Ertu viss?\nÞetta mun eyða öllu staðbundna gagnasafninu, textabrotum og upptökum.',  //'Are you sure?\nThis will delete the entire local db, including tokens and recordings.',
    'CLEARINGDBMSG' : 'Hreinsa allt staðbundna gagnasafnið...',  //'Clearing entire local db...',
    'DBCLEAREDALERT' : 'Gagnasafn hreinsað!',  //'Database cleared!',
    'DBCLEAREDMSG' : 'Gagnasafn hreinsað.',  //'Database cleared.',
    'CLEARINGTOKENSMSG' : 'Hreinsa textabrot...',  //'Clearing tokens...',
    'TOKENSCLEARSALERT' : 'Öll textabrot farin!',  //'All tokens gone!',
    'TOKENSCLEARSMSG' : 'Textabrotum eytt.',  //'Tokens deleted.',
    'GETTINGTOKENSMSG' : 'Sæki textabrot...',  //'Getting tokens...',
    'TOKENSACQUIREDALERT' : 'Textabrot sótt!',  //'Tokens acquired!',
    'TOKENSACQUIREDMSG' : 'Textabrot sótt.',  //'Tokens acquired.',
    'SYNCINGMSG' : 'Samstilli gögn - vinsamlegst bíðið',  //'Syncing - please wait',
    'SYNCCOMPLETEMSG' : 'Samstillingu lokið.',  //'Sync complete.',
    'SYNCFAILEDMSG' : 'Textabrot sótt.',  //'Tokens acquired.',
    //recording agreement
    'FULLNAMETEXT' : 'Fullt nafn',  //'Full name',
    'EMAILTEXT' : 'Netfang',  //'Email',
    'ACCEPTTEXT' : 'Samþykkja',   //'Accept', 
    'DECLINETEXT' : 'Hafna',  //'Decline',
    //speaker info
    'INFOHEADINGTEXT' : 'Vinsamlegast veldu þá möguleika sem eiga við þig',  //'Enter your info',
    //start
    'STARTHEADINGTEXT' : 'Vinsamlegast fylltu inn þá möguleika sem eiga við þig',  //'Enter your info',
    'USERNAMETEXT' : 'Notendanafn',  //'Username',
    'DONEBEFORETEXT' : 'Ég hef notað Eyra áður',  //'Done this before?', 
    //recording
     'RECTEXT' : 'Taka upp', //'Rec', //text under rec button
     'STOPTEXT' : 'Stopp',  //'Stop',
     'SKIPTEXT' : 'Sleppa',  //'Skip',
     'PROMPTSREADTEXT' : 'Lesnir textar:',  //'Prompts read',
     'UTTQUALITYTEXT' : 'Gæði lesinna frasa',  //'Quality of utts',
     'UTTUPLOADEDTEXT' : 'Frösum hlaðið upp',  //'Utterances uploaded',
     'INITTOKENTEXT' : 'Smelltu á \'Taka upp\' til að fá textabrot',  //'Hit \'Rec\' for prompt',
     'RECORDINGNOWTEXT' : 'Tek upp...',  //'Recording now...',
     'WAITINGFORTOKENTEXT' : 'Bíð eftir nýju textabroti...',  //'Waiting for new token...',
     'TOKENSKIPPEDTEXT' : 'Textabroti sleppt',  //'Token skipped',
     'STOPPEDTEXT' : 'Stöðvað',  //'Stopped',
     'NOMORETOKENSTEXT' : 'Engin fleiri textabrot. Endurræstu forritið með nettengingu fyrir fleiri.',  //'No more tokens. Restart app with internet connection for more.',
     //register device
     'IMEIDEVICETEXT' : 'IMEI/Device ID',  //'IMEI/Device ID',
     'DEVICEINFOALERT' : 'Upplýsingar tækis skráðar!',  //'Device info submitted!',
     'DEVICESUBMITERRORMSG' : 'Villa við að skrá tæki.',  //'Error submitting device.',
     //report
     'REPORTTEXT' : 'Tilkynna',  //'Report',
     'CLICKTOCONTINUETEXT' : 'smelltu fyrir neðan til að halda áfram',  //'click below to continue',
     //set instructor
     'NEWINSTRUCTORTEXT' : 'Nýr leiðbeinandi',  //'New instructor',
     'PHONETEXT' : 'Sími',  //'Phone',
     'ADRESSTEXT' : 'Heimilisfang',  //'Address',
     'IDLABELTEXT' : 'ID',  //'ID',
     'EXISTINGINSTRUCTORTEXT' : 'Leiðbeinandi þegar skráður',  //'Existing instructor',
     'FULLNAMEPLACEHOLDERTEXT' : 'Jón Jónsson',  //'Jane Doe',
     'EMAILPLACEHOLDERTEXT' : 'postur@netfang.is',  //'email@example.com',
     'PHONEPLACEHOLDER' : '7777777',  //'7777777',
     'ADRESSPLACEHOLDER' : 'Aðalgata 11',  //'21 Example Lane',
     'INSTRUCTORSUBMITALERT' : 'Leiðbeinandi skráður í gagnagrunn!',  //'Instructor submitted to database!',
    //sync
    'SYNCTEXT' : 'Samstilla',  //'Sync',
    'BACKTORECTEXT' : 'Til baka í upptöku',  //'Back to recording',
    'UTTRECTEXT' : 'Frasar hljóðritaðir',  //'Utterances recorded',
    'UTTUPLTEXT' : 'Frasar hlaðnir upp',  //'Utterances uploaded',
    'UTTRECNOTUPLTEXT' : 'Frasar hljóðritaðir & ekki hlaðnir upp',  //'Utterances recorded &amp; not uploaded',
    'PROMPTSDOWNLTEXT' : 'Sótt textabrot',  //'Prompts downloaded:',
     //error messages\
    'SPEAKEREXISTSERRORMSG' : 'Ræðumaður þegar í gagnagrunni. Veldu annað nafn, nema þú hafir gert þetta áður á þessu tæki, hakaðu þá í boxið.',  //'Speaker already in database. Choose a different name, unless you have done this before on this device, then tick the box.',
    'ACCEPTPARTICIPATIONMSG' : 'Eitthvað fór úrskeiðis, samþykktir þú skilmála?',  // 'Something is wrong, did you accept the participant agreement?',
    'RENDERPAGEERRORMSG' : 'Villa við að birta síðu.',  //'Error rendering page.',
    'SUBMITINSTRUCTORERRORMSG' : 'Villa við að skrá gögn leiðbeinanda.',  //'Error submitting instructor data.',
    'SPEAKERINFOERRORMSG' : 'Gat ekki uppfært speakerInfo í ldb',  //'Could not update speakerInfo into ldb',
    'TOKENSREADERRORMSG' : 'Gat ekki lesið tokensRead teljara frá ldb',  //'Could not read tokensRead counter from ldb',
    'COMMENTMISSINGMSG' : 'Vinsamlegast gerðu grein fyrir einkunnagjöfinni.',  //'Please comment on your grade.',
    'LISTENMSG' : 'Vinsamlegast hlýddu á upptökuna.', //'Please listen to the recording.',
    'FETCHERRORMSG' : 'Gat ekki fundið laus sett. Ertu með nettengingu?', //'Couldn\'t grab available sets. Are you online?',
    'USERNAMEERRORMSG' : 'Vinsamlegast fylltu inn notendanafn.',  //'Please type a username.',
    'SETERRORMSG' : 'Vinsamlegast veldu sett.',  //'Please select a set.',
    'USERSETERRORMSG' : 'Fylltu inn notendanafn og veldu sett',  //'Type a username and select a set',
    'APPINITIALIZATIONFAILMSG' : 'Forrit tókst ekki að ræsa. Reyndu að endurhlaða síðunni og athuga nettengingu',  //'App failed to initialize. Try refreshing the page and check your connection.',
    'GETPROMPTSMSGTEXT' : 'Sæki textabrot  - Vinsamlegast bíðið',  //'Getting prompts  - Please wait',
    'WAITINGTEXT' : 'Vinsamlegast bíðið',  //'Please wait',
    'FAILEDTOGETTOKENS' : 'Tókst ekki að sækja textabrot',  //'Failed to get tokens',
    'PLAYBACKERRORMSG' : 'Eitthvað fór úrskeiðis við spilun hljóðs.',  //'Something went wrong with the audio playback.',
    'SOMETINGWRONGERRORMSG' : 'Eitthvað fór úrskeiðis.',  //'Something went wrong.',
    'FETCHCOMMENTERRORMSG' : 'Eitthvað fór úrskeiðis við að sækja athugasemdir frá netþjóni',  //'Something went wrong grabbing comments from server.',
    'LOGINERRORMSG' : 'Villa við innskráningu',  //'Failed to login',
    'NAMEANDEMAILMISSINGMSG' : 'Vinsamlegast skráðu nafn og netfang.',  //'Please type your name and email.',
    'MUSTACCEPTMSG' : 'Þú verður að samþykkja skilmála til að halda áfram.',  //'You have to accept the agreement to continue.',
  };
  

  return utilityHandler;

  //////////

  function getConstant(constant) {
    return CONSTANTS[constant];
  }

  // e.g if path === 'localDb/sessions/blob/5'
  // this will return 5
  // returns -1 on error
  function getIdxFromPath(path) {
    var idx = -1;
    try {
      var tokens = path.split('/');
      idx = parseInt(tokens[tokens.length - 1]);
      if (!idx && idx !== 0) idx = -1; // allow 0 as index
    } catch (e) {
      logger.error(e);
    }
    return idx;
  }

  function generateUUID() {
    // Thanks, broofa, http://stackoverflow.com/a/2117523/5272567
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
      return v.toString(16);
    });
  }

  // part=3, whole=9, accuracy=2 would result in 33.33
  function percentage(part, whole, accuracy) {
    return Math.round(part/whole*100 * Math.pow(10, accuracy)) / Math.pow(10, accuracy);
  }

  // standard error function to put as callback for rejected promises
  function stdErrCallback(arg) {
    logger.error(arg);
  }
}
}());
