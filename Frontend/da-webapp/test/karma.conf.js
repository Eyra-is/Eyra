module.exports = function(config){
  config.set({

    basePath : '../',

    files : [
      'src/bower_components/angular/angular.js',
      'src/bower_components/angular-route/angular-route.js',
      'src/bower_components/angular-mocks/angular-mocks.js',
      'src/bower_components/localforage/dist/localforage.js',
      'src/bower_components/angular-localforage/dist/angular-localForage.js',
      'src/bower_components/satellizer/satellizer.js',

      'src/bower_components/jquery/dist/jquery.js',
      'src/bower_components/bootstrap/dist/js/bootstrap.js',
      'src/bower_components/angular-bootstrap/ui-bootstrap-tpls.js',

      'src/recorderjs/dist/*.js',
      'src/volume_meter/volume-meter.js',

      'src/app.js',

      'src/controllers/*.js',
      'src/services/*.js',

      'src/views/*.html',

      'test/unit/**/*.spec.js'
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['chrome_webrtc'],//, 'Firefox'],

    customLaunchers: {
      chrome_webrtc: {
        base: 'Chrome',
        flags: ['--use-fake-ui-for-media-stream'],
        displayName: 'Chrome WebRTC'
      }
    },

    plugins : [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine',
            'karma-junit-reporter'
            ],

    junitReporter : {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }

  });
};
