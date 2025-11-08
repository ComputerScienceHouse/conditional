const webpack = require('webpack');
const CopyPlugin = require('copy-webpack-plugin')
const path = require('path');
const sass = require('sass');

var jsSrc = path.resolve('./frontend');
var jsDest = path.resolve('./conditional/static');
var publicPath = 'static/js';

var babelQuery = {
  "presets": ["@babel/preset-env"],
  "plugins": []
}

var webpackConfig = {
  context: jsSrc,
  entry: ["./javascript/app.js"],
  output: {
    path: path.normalize(jsDest),
    filename: 'js/app.js',
    publicPath: publicPath,
    clean: true,
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
    new CopyPlugin({
      patterns: [
        { from: "images", to: "images" },
      ],
    })
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
      {
        test: /\.s[ac]ss$/i,
        loader: "sass-loader",
        type: "asset/resource",
        generator: {
          filename: "css/[name].css",
        },
        options: {
          sassOptions: {
            loadPaths: [
              "./node_modules/csh-material-bootstrap/dist",
              "./node_modules/csh-material-bootstrap/dist/css",
              "./node_modules/datatables.net-bs/css",
              "./node_modules/bootstrap-material-datetimepicker/css",
              "./node_modules/load-awesome/css",
              "./node_modules/reveal.js/css",
              "./node_modules",
              ".",
            ],
            importers: [
              new sass.NodePackageImporter()
            ],
          }
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: "asset/resource",
        generator: {
          filename: "fonts/[name][ext]",
        },
      }
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
