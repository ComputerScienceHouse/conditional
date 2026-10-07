const globals = require('globals');
let customConfig = [];
let hasIgnoresFile = false;
try {
  require.resolve('./eslint.ignores.js');
  hasIgnoresFile = true;
} catch {
  // eslint.ignores.js doesn't exist
}

if (hasIgnoresFile) {
  const ignores = require('./eslint.ignores.js');
  customConfig = [{ignores}];
}

module.exports = [
  ...customConfig,
  {
    files: ['frontend/javascript/**/*.js'],
    languageOptions: {
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.jquery,
      },
    },
  },
  {
    files: ['frontend/javascript/modules/index.js'],
    languageOptions: {
      sourceType: 'commonjs',
      globals: {...globals.browser},
    },
  },
  {
    files: ['webpack.config.js'],
    languageOptions: {
      sourceType: 'commonjs',
      globals: {...globals.node},
    },
  },
  {
    files: ['frontend/javascript/app.js'],
    languageOptions: {
      sourceType: 'module',
      globals: {...globals.node, ...globals.browser},
    },
  },
  ...require('gts'),
];
