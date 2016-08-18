var config = require('../config');
if (!config.tasks.eslint) return;

var eslint = require('gulp-eslint');
var gulp = require('gulp');
var path = require('path');
var _ = require('lodash')

var eslintTask = function () {
    var globs = [path.join(config.root.src, config.tasks.eslint.src, '/**/*.{' + config.tasks.eslint.extensions + '}')];

    if (!_.isUndefined(config.tasks.eslint.exclude) && _.isArray(config.tasks.eslint.exclude) && config.tasks.eslint.exclude.length > 0) {
        for (var i = 0; i < config.tasks.eslint.exclude.length; i++) {
            var excludePath = '!' + path.join(config.root.src, config.tasks.eslint.src, config.tasks.eslint.exclude[i]);
            globs.push(excludePath);
        }
    }
    
    return gulp.src(globs)
        .pipe(eslint(config.tasks.eslint.options))
        .pipe(eslint.format());
};

gulp.task('eslint', eslintTask);
module.exports = eslintTask;