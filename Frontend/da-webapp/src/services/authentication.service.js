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
// right now pretty useless to have it as a special service, but if authentication scheme
//   is ever changed or modified, it might be nice, so why not have it?

'use strict';

angular.module('daApp')
  .factory('authenticationService', authenticationService);

authenticationService.$inject = ['$auth'];

function authenticationService($auth) {
  var authHandler = {};

  authHandler.loggedIn = loggedIn;
  authHandler.login = login;
  authHandler.logout = logout;

  return authHandler;

  //////////

  function login(user) {
    return $auth.login(user);
  }

  function loggedIn() {
    return $auth.isAuthenticated();
  }

  function logout() {
    $auth.logout();
  }
}
}());
