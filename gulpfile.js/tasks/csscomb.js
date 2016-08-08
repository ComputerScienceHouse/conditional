var config = require('../config');
if (!config.tasks.csscomb) return;

var csscomb = require('gulp-csscomb');
var gulp = require('gulp');
var path = require('path');
var _ = require('lodash')

var csscombTask = function () {
    var globs = [path.join(config.root.src, config.tasks.csscomb.src, '/**/*.{' + config.tasks.csscomb.extensions + '}')];

    if (!_.isUndefined(config.tasks.csscomb.exclude) && _.isArray(config.tasks.csscomb.exclude) && config.tasks.csscomb.exclude.length > 0) {
        for (var i = 0; i < config.tasks.csscomb.exclude.length; i++) {
            var excludePath = '!' + path.join(config.root.src, config.tasks.csscomb.src, config.tasks.csscomb.exclude[i]);
            globs.push(excludePath);
        }
    }

    return gulp.src(globs)
        .pipe(csscomb())
        .pipe(gulp.dest(path.join(config.root.src, config.tasks.csscomb.src)))
};

gulp.task('csscomb', csscombTask);
module.exports = csscombTask;