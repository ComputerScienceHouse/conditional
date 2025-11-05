const { exec } = require('child_process');
const path = require('path');
const sass = require('sass');
const fs = require('node:fs');

// yes I know this is awkward. I want to actually use the node libraries but that gets SUBSTANTIALLY easier when node and all the dependinces are updated
// So after I can update node and stuff I'll change this to do it in a sane way, probably in webpack

const loadPaths = [
  "./node_modules/csh-material-bootstrap/dist",
  "./node_modules/csh-material-bootstrap/dist/css",
  "./node_modules/datatables.net-bs/css",
  "./node_modules/bootstrap-material-datetimepicker/css",
  "./node_modules/load-awesome/css",
  "./node_modules/reveal.js/css",
  "./node_modules",
  ".",
]

function compileFile(file) {
  const result = sass.compile("frontend/stylesheets/" + file + ".scss", {
    loadPaths: loadPaths,
    importers: [
      new sass.NodePackageImporter()
    ],
  })

  fs.writeFileSync("conditional/static/css/" + file + ".css", result.css);
}

exec("mkdir -p " + path.resolve("conditional/static/css"))

compileFile("app")

compileFile("presentations")

