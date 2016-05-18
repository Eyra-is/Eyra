(function () {
// simple wrapper for the angular-localForage library.
// does nothing except keep a single boolean whether there are any indexed db operations
//   still ongoing
//
// WARNING only implements the functions currently used in the app
//         if any other functions are used, they need to be added here manually

'use strict';

angular.module('daApp')
  .factory('myLocalForageService', myLocalForageService);

myLocalForageService.$inject = ['$localForage'];

function myLocalForageService($localForage) {
  var lfHandler = {};

  lfHandler.inProgress = inProgress;

  lfHandler.clear = clear;
  lfHandler.getItem = getItem;
  lfHandler.keys = keys;
  lfHandler.pull = pull;
  lfHandler.removeItem = removeItem;
  lfHandler.setItem = setItem;

  // THE BOOLEAN
  // are there lf operations ongoing?
  var lfInProgress = false;

  return lfHandler;

  //////////

  function inProgress() {
    return lfInProgress;
  }

  // calls fn with rest of arguments supplied in that order
  //   and expects fn to return a promise, and attaches
  //   a lfInProgress = true until the promise
  //   is resolved or rejected, then lfInProgress = false
  //
  // Usage: generalWrapper(fn [, arg1 [, arg2] etc.])
  function generalWrapper(fn) {
    lfInProgress = true;
    // can't use slice, remove first element from the arguments array (which should be fn)
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/arguments
    var args = [];
    for (var i = 1; i < arguments.length; i++) {
      args.push(arguments[i]);
    }
    return fn.apply($localForage, args).then(
      function (val) {
        lfInProgress = false;
        return val;
      },
      function (error) {
        lfInProgress = false;
        return error;
      }
    );
  }

  // LOCALFORAGE FUNCTIONS

  function clear() {
    return generalWrapper($localForage.clear);
  }

  function getItem(key) {
    return generalWrapper($localForage.getItem, key);
  }

  function keys() {
    return generalWrapper($localForage.keys);
  }

  function pull(key) {
    return generalWrapper($localForage.pull, key);
  }

  function removeItem(key) {
    return generalWrapper($localForage.removeItem, key);
  }

  function setItem(key, value) {
    return generalWrapper($localForage.setItem, key, value);
  }
}
}());
