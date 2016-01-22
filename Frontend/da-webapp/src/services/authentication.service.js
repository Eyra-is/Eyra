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
