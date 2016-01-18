(function () {
'use strict';

angular.module('daApp')
.controller('LoginController', LoginController);

LoginController.$inject = ['$http', '$location', '$scope', 'authenticationService', 'logger'];

function LoginController($http, $location, $scope, authenticationService, logger) {
  var loginCtrl = this;
  var authService = authenticationService;
  
  loginCtrl.submit = submit;

  $scope.email = '';
  $scope.password = '';
  $scope.isLoaded = true;

  
  //////////

  function submit() {
    /*$http({
        method:'POST',
        url:'//'+BACKENDURL+'/auth/login',
        data:'{"email":"rooney", "password":"suchPass"}',
        json:{"email":"rooney", "password":"suchPass"},
        headers: {'Content-Type': 'application/json'}
    }).then(function(val){
        console.log(val);
    },
    function (error){
        console.log(error);
    });*/ // <--- this works
    authService.login({'email':$scope.email, 'password':$scope.password}).then(
        function success(res) {
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
}());
