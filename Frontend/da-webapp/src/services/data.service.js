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
}());
