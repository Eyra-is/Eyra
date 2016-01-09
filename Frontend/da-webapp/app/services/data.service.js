// send data from one pageview to the next by injecting this service on both sides, 
// and using get/set with strings as keys.

'use strict';

angular.module('daApp')
  .factory('dataService', dataService);

//dataService.$inject = [];

function dataService() {
  var dataHandler = {};

  dataHandler.set = set;
  dataHandler.get = get;

  var data = {};

  return dataHandler;

  //////////

  function set(key, value) {
    if (typeof key !== 'string') return false;
    data[key] = value;
    return true;
  }

  function get(key) {
    if (typeof key !== 'string') return false;
    return data[key];
  }
}