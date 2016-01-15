module.exports = function(grunt) {
  var cache_breaker = '<%= grunt.template.today("yyyymmdd-HHMM") %>';

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    appcache: {
      options: {
        basePath: 'app'
      },
      all: {
        dest: 'app/app.appcache',
        cache: 'app/**/*',
        network: '*'
      }
    },
    clean: {
      min_scripts: ['app/min/*.min.js'],
      temp: ['app/min/temp/']
    },
    jshint: {
      all: ['Gruntfile.js', 'app/**/*.js']
    },
    ngAnnotate: {
        options: {
            singleQuotes: true,
        },
        app: {
            files: [{
                expand: true,
                src:  [
                        'app.js', 
                        'app/services/**/*.js',
                        'app/controllers/**/*.js', 
                      ],
                dest: 'app/min/temp/'
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
          {expand: true, flatten: true, src: ['app/index.html'], dest: 'app/'}
        ]
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - \
                 <%= grunt.template.today("yyyy-mm-dd") %> */',
        mangle: false,
        sourceMap: true,
        sourceMapName: 'sourceMap.map'
      },
      minify: {
        files: [{
          src:  [
                  'app/min/temp/app/app.js', 
                  'app/min/temp/app/services/**/*.js',
                  'app/min/temp/app/controllers/**/*.js'
                ],
          dest: 'app/min/script.'+cache_breaker+'.min.js'
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
                                  'ngAnnotate', 
                                  'clean:min_scripts', // delete previous script.DATA.min.js
                                  'uglify',
                                  'clean:temp', // delete the temp files from ngAnnotate 
                                  'replace', // replace previous script.DATA.min.js in index.html 
                                  'appcache'
                                ]);
};
