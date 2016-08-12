var config = require('../config');
var compact = require('lodash/compact');

// Grouped by what can run in parallel
var initTasks = ['clean', 'csscomb'];
var linterTasks = ['pylint', 'eslint', 'sasslint'];
var assetTasks = ['fonts', 'images'];
var codeTasks = ['css', 'js'];

module.exports = function (env) {

    function matchFilter(task) {
        if (config.tasks[task]) {
            if (task === 'js') {
                task = env === 'production' ? 'webpack:production' : false
            }
            return task
        }
    }

    function exists(value) {
        return !!value
    }

    return {
        initTasks: compact(initTasks.map(matchFilter).filter(exists)),
        assetTasks: compact(assetTasks.map(matchFilter).filter(exists)),
        codeTasks: compact(codeTasks.map(matchFilter).filter(exists)),
        linterTasks: compact(linterTasks.map(matchFilter).filter(exists))
    }
}
