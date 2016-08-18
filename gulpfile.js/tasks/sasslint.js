var config = require('../config');
if (!config.tasks.sasslint) return;

var sassLint = require('gulp-sass-lint');
var gulp = require('gulp');
var path = require('path');
var _ = require('lodash');

var sasslintTask = function () {
    var globs = [path.join(config.root.src, config.tasks.sasslint.src, '/**/*.{' + config.tasks.sasslint.extensions + '}')];

    if (!_.isUndefined(config.tasks.sasslint.exclude) && _.isArray(config.tasks.sasslint.exclude) && config.tasks.sasslint.exclude.length > 0) {
        for (var i = 0; i < config.tasks.sasslint.exclude.length; i++) {
            var excludePath = '!' + path.join(config.root.src, config.tasks.sasslint.src, config.tasks.sasslint.exclude[i]);
            globs.push(excludePath);
        }
    }

    return gulp.src(globs)
        .pipe(sassLint())
        .pipe(sassLint.format());
};

gulp.task('sasslint', sasslintTask);
module.exports = sasslintTask;