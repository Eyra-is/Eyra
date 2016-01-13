// service to log errors/console output. Also saves it to localForage, with key 'logs' as one big string.

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