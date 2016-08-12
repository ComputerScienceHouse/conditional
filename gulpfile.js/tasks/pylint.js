var config = require('../config');
if (!config.tasks.pylint) return;

var gulp = require('gulp');
var exec = require('child_process').exec;

var pylintTask = function (cb) {
    exec('pylint ' + config.tasks.pylint.module, function (err, stdout, stderr) {
        console.log(stdout);
        console.log(stderr);
        cb(err);
    });
}

gulp.task('pylint', pylintTask);
module.exports = pylintTask;