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
'use strict';

angular.module('daApp')
.controller('LoginController', LoginController);

LoginController.$inject = ['$http', '$location', '$rootScope', '$scope', 'authenticationService', 'logger', 'utilityService'];

function LoginController($http, $location, $rootScope, $scope, authenticationService, logger, utilityService) {
  var loginCtrl = this;
  var authService = authenticationService;
  var util = utilityService;

  loginCtrl.submit = submit;

  $scope.email = '';
  $scope.password = '';
  $rootScope.isLoaded = true;

  
  $scope.loginText = util.getConstant('LOGINTEXT');
  $scope.emailText = util.getConstant('EMAILTEXT');
  $scope.passwordText = util.getConstant('PASSWORDTEXT');
  $scope.emailPlaceholder = util.getConstant('EMAILPLACEHOLDERTEXT');
  
  //////////

  function submit() {
    /*$http({
        method:'POST',
        url:BACKENDURL+'/auth/login',
        data:'{"email":email, "password":password}',
        json:{"email":email, "password":password},
        headers: {'Content-Type': 'application/json'}
    }).then(function(val){
        console.log(val);
    },
    function (error){
        console.log(error);
    });*/ // <--- this works
    authService.login({'email':$scope.email, 'password':$scope.password}).then(
        function success(res) {
            $location.path('/more');
        },
        function error(res) {
            $scope.msg =  util.getConstant('LOGINERRORMSG');
            logger.error(res); // DEBUG ONLY 
        }
    );
  }
}
}());
