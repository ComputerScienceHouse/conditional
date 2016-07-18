var config = require('../config');
var gulp = require('gulp');
var exec = require('child_process').exec;

var serverTask = function () {
    var proc = exec('python conditional config.json', (error, stdout, stderr) => {
        if (error) {
            console.error(`Unable to start Python server: ${error}`);
            return;
        }
        console.log(`${stdout}`);
        console.log(`${stderr}`);
    });
};

gulp.task('server', serverTask);
module.exports = serverTask;
