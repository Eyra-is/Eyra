// handles http post and get requests to server
// "implements" the Client-Server API

'use strict';

angular.module('daApp')
  .factory('deliveryService', deliveryService);

deliveryService.$inject = ['$http'];

function deliveryService($http) {
  var reqHandler = {};



  return reqHandler;

  //////////

  // submit session with 1 or more recordings, 
  function submitSession(jsonData, recordings) {

  }
}