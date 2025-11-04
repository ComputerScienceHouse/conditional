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
    modules: [
      path.join(__dirname, "frontend/javascript"),
      path.join(__dirname, "frontend/node_modules"),
    ],
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          // exclude: /node_modules/,
          query: babelQuery
        }
      },
      {
        test: require.resolve("jquery"),
        use: {
          loader: 'expose?$!expose?jQuery'
        }
      },
      {
        test: /bootstrap-material-datetimepicker/,
        use: {
          loader: 'imports?moment'
        }
      },
      {
        test: /bootstrap-sweetalert.*$/,
        use: {
          loader: 'babel-loader',
          query: {
            query: babelQuery
          }
        }
      },
    ]
  },
};

webpack(webpackConfig, (err, stats) => {
  console.log("Done!")
  console.log(err, stats)
});
