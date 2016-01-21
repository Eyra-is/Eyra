// The meat in this Gruntfile is the renaming of files like bla.html -> bla.DATE.html
//   for the appcache. Also generates the appcache files itself.
// It's a bit daunting. Some explanations are in the 'deploy' task down below.
//
// This file is sort of caveman-like, on a number of changes including but not limited to
//   additional content added to the site which needs to be cached, this file needs to be updated
//   in accordance with that.

'use strict';

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
                      depl+'css/**',
                      depl+'views/**',
                      depl+'img/**',
                      // be careful, if these files (recorderjs/) are ever changed, 
                      // it might not reflect on client end if he has this cached. 
                      // This is not cache-broken. 
                      depl+'recorderjs/dist/*' 
                    ],
          literals: [
                      'index.html'
                    ]
        },
        network: '*'
      }
    },
    clean: {
      old_files:  [
                    depl+'min/', 
                    depl+'views/', 
                    depl+'css/**',
                    depl+'sass/**',
                    depl+'index.html',
                    depl+'img/**'
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
            src: ['css/**'],
            dest: depl,
            rename: function(dest, src) {
              return dest + src.replace(/\.css$/, '.'+cache_breaker+'.css');
            }
          },
          { expand: true, cwd: source,
            src: ['img/**'],
            dest: depl,
            rename: function(dest, src) {
              return dest + src.replace(/\.(jpg|png|gif)$/, '.'+cache_breaker+'.$1');
            }
          },
          { expand: true, cwd: source,
            src: ['app.js', 'index.html', 'sass/**'],
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
      },
      imgs: {
        options: {
          patterns: [
            {
              match: /src=\"img\/(.*)\.(jpg|png|gif)\"/g,
              replacement: 'src="img\/$1.'+cache_breaker+'.$2"'
            }
          ]
        },
        files: [
          { 
            expand: true, cwd: depl,
            src: ['views/**/*.html', 'index.html'], 
            dest: depl
          }
        ]
      }
    },
    sass: {
      options: {
        sourceMap: true,
        expand: true,
        flatten: true
      },
      main: {
        files: [{
          dest: source+'css/app.css',
          src: source+'sass/app.scss'
        }]
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - \
                 <%= grunt.template.today("yyyy-mm-dd") %> */',
        mangle: false,
        sourceMap: true,
        sourceMapName: depl+'min/script.min.js.map'
      },
      minify: {
        files: [{
          src:  [
                  depl+'bower_components/angular/angular.js',
                  depl+'bower_components/angular-route/angular-route.js',

                  depl+'bower_components/localforage/dist/localforage.js',
                  depl+'bower_components/angular-localforage/dist/angular-localForage.js',
                  depl+'bower_components/satellizer/satellizer.js',
                  // must not be minified as they use window.postMessage. U
                  //   until code is changed or we use ES6 commit of recorderjs
                  //   this has to be non-minified.
                  //depl+'recorderjs/dist/recorderWorker.js',
                  //depl+'recorderjs/dist/recorder.js',

                  depl+'min/old/'+depl+'app.js', 
                  depl+'min/old/'+source+'services/**/*.js',
                  depl+'min/old/'+source+'controllers/**/*.js'
                ],
          dest: depl+'min/script.'+cache_breaker+'.min.js'
        }]
      }
    },
    watch: {
      scripts: {
        files: [source+'**/*.js', source+'**/*.html', source+'**/*.css'],
        tasks: ['deploy'],
        options: { spawn: false }
      },
      sass: {
        files: [source+'**/*.scss'],
        tasks: ['sass'],
        options: { spawn: false }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-appcache');
  grunt.loadNpmTasks('grunt-ng-annotate');
  grunt.loadNpmTasks('grunt-replace');
  grunt.loadNpmTasks('grunt-sass');

  grunt.registerTask('default', ['watch:scripts']);
  grunt.registerTask('dev', ['watch:sass']);
  grunt.registerTask('deploy',  [
                                  'clean:old_files', // delete previous deploy scripts
                                  'sass', // compile scss to css file/s in source
                                  'copy:main', // copy everything not javascript from source to depl and rename with CACHEBREAKER
                                  'replace:script_name', // replace previous file.CACHEBREAKER.ext in index.CACHEBREAKER.html 
                                  'replace:views', // replace 'views/bla.CACHEBREAKER.html' to the new cachebreaker in the routes in app.js
                                  'replace:imgs', // replace all 'src="img/i.(jpg|png|gif)' imgs with cachebroken versions in the .html files
                                  'ngAnnotate:app', // make sure angular scripts are ready for minification
                                  'uglify:minify', // min javascript
                                  'clean:temp', // delete the temp app.js used by ngAnnotate
                                  'appcache:all'
                                ]);
};
