var webpack = require("webpack")
var path = require('path');

var jsSrc = path.resolve('./frontend/javascript');
var jsDest = path.resolve('./conditional/static/js');
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
    filename: '[name].js',
    publicPath: publicPath
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
  ],
  resolve: {
    modules: [
      path.join(__dirname, "frontend/javascript"),
      path.join(__dirname, "frontend/node_modules"),
    ],
  },
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          query: babelQuery
        }
      },
      {
        test: require.resolve("jquery"),
        use: {
          loader: 'expose-loader'
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
  optimization: {
    emitOnErrors: true,
  }
};

webpack(webpackConfig, (err, stats) => {
  console.log("Done!")
  console.log(err, stats)
});
