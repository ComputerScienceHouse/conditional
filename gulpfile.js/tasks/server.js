var config = require('../config');
var gulp = require('gulp');
var gutil = require('gulp-util');
var spawn = require('child_process').spawn;

var serverTask = function () {
    var server = spawn(config.tasks.server.command, config.tasks.server.arguments);

    server.stdout.on('data', function (data) {
        gutil.log(gutil.colors.blue(data));
    });

    server.stderr.on('data', function (data) {
        gutil.log(gutil.colors.blue(data));
    });

    server.on('exit', function (code) {
        gutil.log(gutil.colors.red('Python server stopped: child process exited with code ' + code));
    });
};

gulp.task('server', serverTask);
module.exports = serverTask;
