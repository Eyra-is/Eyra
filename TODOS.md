# Eyra TODOS

[FE] - Frontend  
[BE] - Backend  
[AA] - Android app  
[O] - None of the above

## High priority

* **Sync doesn't work properly on many many phones (older os's it seems) [BUG] [FE]**
    * Mismatch between tokens read and utts uploaded and utts read & not uploaded. (big mismatch, like e.g. 200)
* **Always save recordings even if not inserted into mysql database [BE]**
    * Change code in `Backend/server-interface/db_handler.py` to always save recordings even if not inserted into mysql database. Add to e.g. lost dir or something. In order to not lose data.
* **Add mod_status and any other tools to be able to monitor apache [BE]**

## Medium priority

* **Playback doesn't work in Android 4 [BUG] [FE]**
* **Site doesn't update in Firefox (some appcache thing) [BUG] [FE]**
    * Does it too in chrome unless there are certificates? (green lock)  
      Seems to do it in galaxy S6 (android 5.1.1) as well unfrotunately. (using webview which is based on chrome)
* **Make people able to access the app without acquiring tokens (e.g. the sync option) [FE]**
* **Separate logic to display popups to QC and other. [FE]**
    * For example, put the 'Thank you for your contribution' or 'Good job on reading X prompts' in a separate service from the QC service which deals with the server QC only.
* **Replace appcache with service workers [FE]**
    * Appcache is deprecated, should be replaced with service workers. This is a big task though.
* **Look into disabling Stop button when it does take a long time (for some reason it's not disabled) [FE]**
    * Stop button is not disabled on low end phones, causing people to be able to click multiple times and send multiple requests to our server in doing so.
* **Make sync feature more robust. [FE]**
    * I.e. if it fails sending 5 sessions, put them at the back of a queue and try sending the next 5 etc.
* **Make tests [FE][BE]**
    * Unit tests, end-to-end tests, you name it. Currently there are none.
* **Fix volume meter in webview. [AA]**
* **Serve index.html and more with cache headers with expiration for appcache [BE]**
    * Just to be safe, e.g. [appcache is a douche](http://alistapart.com/article/application-cache-is-a-douchebag)
    * Actually, appcache should be replaced by Service Workers.
* **Add diagnostics to see recorded data etc, to see if phones have issues recording. [BE]**
    * To be used live by the people conducting the collection, some kind of dashboard.
* **Figure out some system for the different languages (the data kept) e.g. icelandic and javanese. [O]**
    * Language specific data that is. Organize the files, make it ready for other languages.

## Low priority

* **Fix audio playback issue. On some phones volume is extremely low through the android app. [FE]**
    * Here is an idea: Some phones simply have poor playback unrelated to any app. Letting the app fix things is a bit heavy handed. Might it not be better to attempt to fix these issues by other means first, such as:https://www.androidpit.com/improve-the-sound-and-volume-quality-on-android - Sveinn
    * What phones? Has it been established that this is not a phone issue. How was this issue established. Need a phone that works well and a phone that performs below standard. Does this issue affect recording, thus impairing data quality? Is user experience sufficiently impaired - is it affected? - Sveinn
* **Combine start and speaker-info page if possible. [FE]**
* **Add maxlength on javascript side using database limits and display an error. [FE]**
* **Consider removing logging to local database from logger. [FE]**
    * Never used through the android app, rarely useful otherwise, uses up processing time.
* **In production, the logger.error should NOT LOG ANYTHING and CHANGE some ERRORS to LOGS for prod. [FE]**
* **Instant QC. [FE]**
    * Look into what can be done about Quality Control on the frontend. (e.g. detect volume, clipping..)
* **Create js/ folder for js. [FE]**
    * Volume meter, recorderjs, services, controllers, etc. etc.
* **Write info page. [FE]**
* **Make all english directions a variable that can be changed (for example by a json file) [FE]**
    * To ease translation if needed of the user interface.
* **Remove alerts [FE]**
* **Add developer options, to show that the phone is ready for recording. [FE]**
    * Depending on what needs to be done for a phone to be ready (get tokens, register imei) this can be useful or not.
* **Make config vars for app out of hardcoded constants. [FE]**
    * Add to util.py for example, or even better a separate file.
* **Rename minFreeTokenIdx to highest used token idx [FE]**
* **Fix volume meter on back click. [FE]**
* **Think about adding underscore for service private functions. [FE]**
* **Simplify the Gruntfile.js to copy everything (not just specific parts) from src/. [FE]**
* **Use jshint on all javascript [FE]**
* **Create pull request on recorderjs about the mozilla bug (window.source) [FE]**
    * [http://stackoverflow.com/questions/22860468/html5-microphone-capture-stops-after-5-seconds-in-firefox](http://stackoverflow.com/questions/22860468/html5-microphone-capture-stops-after-5-seconds-in-firefox)
* **Fix loading for sites [FE]**
    * $rootScope.isLoaded = true  
       right now stays true after the first view you visit. Originally it was $scope.isLoaded and therefore worked as intended, to show the loading screen on long angular processing pages.
* **Simplify message to users not clicking 'Done this before?' and being already in the database. [FE]**
* **Improve documentation on the Frontend [FE]**
    * Describe functions, layout of local db perhaps, etc.
* **Get rid of auto-accept all https in android app [AA]**
    * In AndroidApp/Eyra/app/src/main/java/is/eyra/eyra/EyraWebViewClient.java 
* **Add Android app to play store to simplify the process to the user [AA]**
* **Graceful crash or warning in android app when phone is out of memory (see fabric crash reports) [AA]**
    * Fatal Exception: java.lang.OutOfMemoryError  
      java.util.ArrayList.add (ArrayList.java:118)  
      is.eyra.eyra.Recorder$1.run (Recorder.java:50)  
      java.lang.Thread.run (Thread.java:841)  
* **Make server add timestamps to e.g. recordings [BE]**
    * Change databse schema for this.
* **Generalize the 'if in database, return that id, otherwise insert' [BE]**
    * The processData functions.
    * Basically, just clean up the messy non-DRY code in DBHANDLER - Matthias
* **Only update end time in processSession if end-time is greater than prevous end time [BE]**
    * Otherwise, it probably means, we got synced session.
* **Remove Flask-MySQLdb [BE]**
    * Remove Flask-MySQLdb and simply use MySQLdb, no need for the flask extension (low usage on github) I think.
* **Add an ID to each device which can be used for troubleshooting. [O]**
    * For example add a column in the device table, where you could put, phone A or something like that. Easier than having that cumbersome imei.
    * Until this is implemented, a simple sticker on the phones goes a long way. - Matthias
* **Convert TODOS which are issues, into issues on github [O]**
