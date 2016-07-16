var config   = require('../config');
var gulp     = require('gulp');
var exec     = require('child_process').exec;

var serverTask = function() {
    var proc = exec('python conditional config.json');
};

gulp.task('server', serverTask);
module.exports = serverTask;
