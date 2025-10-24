var config = require('./config');
if (!config.tasks.js) return;

var path = require('path');
var pathToUrl = require('./gulpfile.js/lib/pathToUrl');
var webpack = require('webpack');
var webpackManifest = require('./gulpfile.js/lib/webpackManifest');

var jsSrc = path.resolve(config.root.src, config.tasks.js.src);
var jsDest = path.resolve(config.root.dest, config.tasks.js.dest);
var publicPath = pathToUrl(config.root.publicPath, config.tasks.js.dest, '/');

var extensions = config.tasks.js.extensions.map(function(extension) {
  return '.' + extension;
});

var rev = config.tasks.production.rev;
var filenamePattern = rev ? '[name]-[hash].js' : '[name].js';

var webpackConfig = {
  context: jsSrc,
  plugins: [],
  optimization: {
    emitOnErrors: true,
  },
  // module: {
  //   loaders: [
  //     {
  //       test: /\.js$/,
  //       loader: 'babel-loader',
  //       exclude: /node_modules/,
  //       query: config.tasks.js.babel
  //     },
  //     {
  //       test: require.resolve("jquery"),
  //       loader: 'expose?$!expose?jQuery'
  //     },
  //     {
  //       test: /bootstrap-material-datetimepicker/,
  //       loader: 'imports?moment'
  //     },
  //     {
  //       test: /bootstrap-sweetalert.*$/,
  //       loader: 'babel-loader',
  //       query: config.tasks.js.babel
  //     }
  //   ]
  // }
};

// Karma doesn't need entry points or output settings
webpackConfig.entry = config.tasks.js.entries;

webpackConfig.output = {
  path: path.normalize(jsDest),
  filename: filenamePattern,
  publicPath: publicPath
};

if (config.tasks.js.extractSharedJs) {
  // Factor out common dependencies into a shared.js
  webpackConfig.plugins.push(
    new webpack.optimize.CommonsChunkPlugin({
      name: 'shared',
      filename: filenamePattern
    })
  )
}

webpackConfig.plugins.push(
  new webpack.DefinePlugin({
    'process.env': {
      'NODE_ENV': JSON.stringify('production')
    }
  })
)

module.exports = webpackConfig;
