var config = require('../config');
var gulp = require('gulp');
var gulpSequence = require('gulp-sequence');
var getEnabledTasks = require('../lib/getEnabledTasks');

var productionTask = function (cb) {
    global.production = true;
    var tasks = getEnabledTasks('production');
    gulpSequence(tasks.initTasks, tasks.linterTasks, tasks.assetTasks, tasks.codeTasks, config.tasks.production.rev ? 'rev' : false, 'size-report', 'static', cb);
}

gulp.task('production', productionTask);
module.exports = productionTask;
