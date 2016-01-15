module.exports = function(grunt) {
  var cache_breaker = '<%= grunt.template.today("yyyymmdd-HHMM") %>';
  var root = 'app/';
  var base = 'app';

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    appcache: {
      options: {
        basePath: base
      },
      all: {
        dest: root+'app.appcache',
        cache: {
          patterns: [
                      root+'min/script.*.min.js'
                    ],
          literals: [
                      'app.css', 
                      'index.html', 
                      'min/script.min.map' 
                    ]
        },
        network: '*'
      }
    },
    clean: {
      min_scripts: [root+'min/*.min.js'],
      temp: [root+'min/temp/']
    },
    jshint: {
      all: ['Gruntfile.js', root+'**/*.js']
    },
    ngAnnotate: {
        options: {
            singleQuotes: true,
        },
        app: {
            files: [{
                expand: true,
                src:  [
                        root+'app.js', 
                        root+'services/**/*.js',
                        root+'controllers/**/*.js', 
                      ],
                dest: root+'min/temp/'
            }]
        }
    },
    replace: {
      script_name: {
        options: {
          patterns: [
            {
              match: /script\..*\.min\.js/,
              replacement: 'script.'+cache_breaker+'.min.js'
            }
          ]
        },
        files: [
          {expand: true, flatten: true, src: [root+'index.html'], dest: root+''}
        ]
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - \
                 <%= grunt.template.today("yyyy-mm-dd") %> */',
        mangle: false,
        sourceMap: true,
        sourceMapName: root+'min/script.min.map'
      },
      minify: {
        files: [{
          src:  [
                  root+'bower_components/angular/angular.js',
                  root+'bower_components/angular-route/angular-route.js',

                  root+'bower_components/localforage/dist/localforage.js',
                  root+'bower_components/angular-localforage/dist/angular-localForage.js',
                  root+'bower_components/satellizer/satellizer.js',
                  root+'recorderjs/dist/recorderWorker.js',
                  root+'recorderjs/dist/recorder.js',

                  root+'min/temp/'+root+'app.js', 
                  root+'min/temp/'+root+'services/**/*.js',
                  root+'min/temp/'+root+'controllers/**/*.js'
                ],
          dest: root+'min/script.'+cache_breaker+'.min.js'
        }]
      }
    },
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-appcache');
  grunt.loadNpmTasks('grunt-ng-annotate');
  grunt.loadNpmTasks('grunt-replace');

  grunt.registerTask('default', []);
  grunt.registerTask('deploy',  [
                                  'ngAnnotate', // make sure angular scripts are ready for minification
                                  'clean:min_scripts', // delete previous script.DATA.min.js
                                  'uglify',
                                  'clean:temp', // delete the temp files from ngAnnotate 
                                  'replace', // replace previous script.DATA.min.js in index.html 
                                  'appcache'
                                ]);
};
