var config = require('../config');
var gulp = require('gulp');
var path = require('path');
var watch = require('gulp-watch');
var browserSync = require('browser-sync');

var watchTask = function () {
    var watchableTasks = config.tasks.watch.tasks;
    var additionalPaths = config.tasks.watch.paths;

    watchableTasks.forEach(function (taskName) {
        var task = config.tasks[taskName];
        if (task) {
            var glob = path.join(config.root.src, task.src, '**/*.{' + task.extensions.join(',') + '}');
            watch(glob, function () {
                require('./' + taskName)()
            });
        }
    });

    additionalPaths.forEach(function (addPath) {
        var glob = path.join(addPath, '**');
        watch(glob, function () {
            browserSync.reload();
        });
    });
}

gulp.task('watch', ['browserSync'], watchTask);
module.exports = watchTask;
