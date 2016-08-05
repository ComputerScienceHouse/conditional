var config = require('../config');
if (!config.tasks.eslint) return;

var eslint = require('gulp-eslint');
var gulp = require('gulp');
var path = require('path');

var eslintTask = function () {
    return gulp.src(path.join(config.root.src, config.tasks.eslint.src, '/**/*.js'))
        .pipe(eslint(config.tasks.eslint.options))
        .pipe(eslint.format())
        .pipe(eslint.failAfterError());
};

gulp.task('eslint', eslintTask);
module.exports = eslintTask;