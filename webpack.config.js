var webpack = require('webpack');
var path = require('path');

var jsSrc = path.resolve('./frontend/javascript');
var jsDest = path.resolve('./conditional/static');
var publicPath = 'static/js';

var babelQuery = {
  "presets": ["@babel/preset-env"],
  "plugins": []
}

var webpackConfig = {
  context: jsSrc,
  entry: ["./app.js"],
  output: {
    path: path.normalize(jsDest),
    filename: 'js/app.js',
    publicPath: publicPath
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
  ],
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: babelQuery
      },
      {
        test: require.resolve("jquery"),
        loader: 'expose-loader',
        options: {
          exposes: ["$", "jQuery"],
        },
      },
      {
        test: /bootstrap-material-datetimepicker/,
        loader: 'imports-loader',
        options: {
          imports: [
            {
              syntax: 'default',
              moduleName: 'moment',
              name: 'moment',
            },
          ],
        },
      },
      {
        test: /bootstrap-sweetalert.*$/,
        loader: 'babel-loader',
        options: babelQuery
      },
    ]
  },
  optimization: {
    emitOnErrors: true,
  }
};

module.exports = webpackConfig;
//
// webpack(webpackConfig, (err, stats) => {
//   console.log("Done!")
//   console.log(err, stats)
// });
