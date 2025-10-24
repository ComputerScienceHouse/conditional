var webpack = require("webpack")
var webpackConfig = require("./webpack.config")

webpack(webpackConfig, (err, stats) => {
  console.log("Done!")
  console.log(err, stats)
});
