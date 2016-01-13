'use strict';

angular.module('daApp')
.controller('LoginController', LoginController);

LoginController.$inject = ['$location', '$scope', 'authenticationService', 'logger'];

function LoginController($location, $scope, authenticationService, logger) {
  var loginCtrl = this;
  var authService = authenticationService;
  
  loginCtrl.submit = submit;

  loginCtrl.email = '';
  loginCtrl.password = '';
  $scope.isLoaded = true;

  
  //////////

  function submit() {
    authService.login({'email':loginCtrl.email, 'password':loginCtrl.password}).then(
        function success(res) {
            console.log(res);
            alert('Logged in successfully!');
            $location.path('/more');
        },
        function error(res) {
            $scope.msg = 'Failed to login.';
            logger.error(res); // DEBUG ONLY 
        }
    );
  }
}
