var webpack = require("webpack")
var path = require('path');

var jsSrc = path.resolve('./frontend/javascript');
var jsDest = path.resolve('./conditional/static/js');
var publicPath = 'static/js';

var babelQuery = {
  "presets": ["es2015", "stage-1"],
  "plugins": []
}

var webpackConfig = {
  context: jsSrc,
  entry: ["./app.js"],
  output: {
    path: path.normalize(jsDest),
    filename: '[name].js',
    publicPath: publicPath
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.NoErrorsPlugin()
  ],
  resolve: {
    root: jsSrc,
    extensions: ['', '.js']
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: babelQuery
      },
      {
        test: require.resolve("jquery"),
        loader: 'expose?$!expose?jQuery'
      },
      {
        test: /bootstrap-material-datetimepicker/,
        loader: 'imports?moment'
      },
      {
        test: /bootstrap-sweetalert.*$/,
        loader: 'babel-loader',
        query: babelQuery
      },
    ]
  },
};

webpack(webpackConfig, (err, stats) => {
  console.log("Done!")
  console.log(err, stats)
});
