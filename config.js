module.exports = {
  root: {
    src: "./frontend",
    dest: "./conditional/static",
    templates: "./conditional/templates",
    publicPath: "static"
  },

  tasks: {
    static: {
      src: "static",
      dest: "./"
    },

    js: {
      src: "javascript",
      dest: "js",
      entries: {
        app: ["./app.js"]
      },
      extensions: ["js", "json"],
      babel: {
        presets: ["es2015", "stage-1"],
        plugins: []
      },
      extractSharedJs: false
    },

    eslint: {
      "src": "javascript",
      "extensions": ["js", "json"]
    },
    
    "sasslint": {
      "src": "stylesheets",
      "exclude": ["components/sweet-alert/**", "components/_datatables.scss"],
      "extensions": ["sass", "scss"]
    },
    
    "csscomb": {
      "src": "stylesheets",
      "extensions": ["sass", "scss"]
    },

    "css": {
      "src": "stylesheets",
      "dest": "css",
      "autoprefixer": {
        "browsers": ["last 3 version"]
      },
      "sass": {
        "includePaths": [
          "./node_modules/csh-material-bootstrap/dist/css",
          "./node_modules/datatables.net-bs/css",
          "./node_modules/bootstrap-material-datetimepicker/css",
          "./node_modules/selectize-scss/src",
          "./node_modules/load-awesome/css",
          "./node_modules/reveal.js/css"
        ]
      },
      "extensions": ["sass", "scss", "css"]
    },

    "fonts": {
      "src": "fonts",
      "dest": "fonts",
      "vendor": ["./node_modules/csh-material-bootstrap/dist/fonts"],
      "extensions": ["woff2", "woff", "eot", "ttf", "svg"]
    },

    "images": {
      "src": "images",
      "dest": "images",
      "extensions": ["jpg", "png", "svg", "gif"]
    },

    production : {
      rev: true
    }
  }
}
