// The meat in this Gruntfile is the renaming of files like bla.html -> bla.DATE.html
//   for the appcache. Also generates the appcache files itself.
// It's a bit daunting. Some explanations are in the 'deploy' task down below.

module.exports = function(grunt) {
  // be careful if compile time takes more than 1 minute, this might break since it's used in many places in the script
  var cache_breaker = '<%= grunt.template.today("yyyymmdd-HHMM") %>';
  var source = 'src/'; // source files
  var depl = 'app/'; // source files -> minified and renamed for cache breaking
  var base = 'app';

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    appcache: {
      options: {
        basePath: base
      },
      all: {
        dest: depl+'app.appcache',
        cache: {
          patterns: [
                      depl+'min/script.*.min.js',
                      depl+'min/script.min.*.map',
                      depl+'app.*.css', 
                      depl+'views/**'
                    ],
          literals: [
                      depl+'index.html'
                    ]
        },
        network: '*'
      }
    },
    clean: {
      old_scripts:  [
                      depl+'min/', 
                      depl+'views/', 
                      depl+'app.*.css', 
                      depl+'index.html'
                    ],
      temp: [depl+'app.js']
    },
    copy: {
      main: {
        files: [
          { expand: true, flatten: true, cwd: source,
            src: ['views/*.html'],
            dest: depl+'views/',
            rename: function(dest, src) {
              return dest + src.replace(/\.html$/, '.'+cache_breaker+'.html');
            }
          },
          { expand: true, cwd: source,
            src: ['app.css'],
            dest: depl,
            rename: function(dest, src) {
              return dest + src.replace(/\.css$/, '.'+cache_breaker+'.css');
            }
          },
          { expand: true, flatten: true, cwd: source,
            src: ['app.js', 'index.html'],
            dest: depl
          }
        ]
      }
    },
    jshint: {
      all: ['Gruntfile.js', source+'**/*.js']
    },
    ngAnnotate: {
        options: {
            singleQuotes: true,
        },
        app: {
            files: [{
                expand: true,
                src:  [
                        depl+'app.js', 
                        source+'services/**/*.js',
                        source+'controllers/**/*.js', 
                      ],
                dest: depl+'min/old/'
            }]
        }
    },
    replace: {
      script_name: {
        options: {
          patterns: [
            {
              match: 'script.min.js',
              replacement: 'script.'+cache_breaker+'.min.js'
            },
            {
              match: 'app.css',
              replacement: 'app.'+cache_breaker+'.css'
            }
          ]
        },
        files: [
          { 
            expand: true, flatten: true, cwd: depl,
            src: ['index.html'], 
            dest: depl
          }
        ]
      },
      views: {
        options: {
          patterns: [
            {
              match: /views\/(.*).html/g,
              replacement: 'views\/$1.'+cache_breaker+'.html'
            }
          ]
        },
        files: [
          { 
            expand: true, flatten: true, cwd: depl,
            src: ['app.js'], 
            dest: depl
          }
        ]
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - \
                 <%= grunt.template.today("yyyy-mm-dd") %> */',
        mangle: false,
        sourceMap: true,
        sourceMapName: depl+'min/script.min.'+cache_breaker+'.map'
      },
      minify: {
        files: [{
          src:  [
                  depl+'bower_components/angular/angular.js',
                  depl+'bower_components/angular-route/angular-route.js',

                  depl+'bower_components/localforage/dist/localforage.js',
                  depl+'bower_components/angular-localforage/dist/angular-localForage.js',
                  depl+'bower_components/satellizer/satellizer.js',
                  depl+'recorderjs/dist/recorderWorker.js',
                  depl+'recorderjs/dist/recorder.js',

                  depl+'min/old/'+depl+'app.js', 
                  depl+'min/old/'+source+'services/**/*.js',
                  depl+'min/old/'+source+'controllers/**/*.js'
                ],
          dest: depl+'min/script.'+cache_breaker+'.min.js'
        }]
      }
    },
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-appcache');
  grunt.loadNpmTasks('grunt-ng-annotate');
  grunt.loadNpmTasks('grunt-replace');

  grunt.registerTask('default', []);
  grunt.registerTask('deploy',  [
                                  'clean:old_scripts', // delete previous deploy scripts
                                  'copy:main', // copy everything not javascript to depl/ and rename with CACHEBREAKER
                                  'replace:script_name', // replace previous file.CACHEBREAKER.ext in index.CACHEBREAKER.html 
                                  'replace:views', // replace 'views/bla.CACHEBREAKER.html' to the new cachebreaker in the routes in app.js
                                  'ngAnnotate:app', // make sure angular scripts are ready for minification
                                  'uglify:minify', // min javascript
                                  'clean:temp', // delete the temp app.js used by ngAnnotate
                                  'appcache:all'
                                ]);
};
