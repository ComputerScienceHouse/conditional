const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// yes I know this is awkward. I want to actually use the node libraries but that gets SUBSTANTIALLY easier when node and all the dependinces are updated
// So after I can update node and stuff I'll change this to do it in a sane way, probably in webpack

const loadPaths = [
  "./node_modules/csh-material-bootstrap/dist/css",
  "./node_modules/datatables.net-bs/css",
  "./node_modules/bootstrap-material-datetimepicker/css",
  "./node_modules/selectize-scss/src",
  "./node_modules/load-awesome/css",
  "./node_modules/reveal.js/css",
  "./node_modules",
  ".",
]

const loadPathCommands = loadPaths.map((string) => "-I " + string);

const loadPathString = loadPathCommands.join(" ");

function compileFile(file) {
  // you can use the node package but it doesn't like the version of node we're using for this rn fix later tm
  const cmd = "sass " + loadPathString + " " + "frontend/stylesheets/" + file + ".scss" + " conditional/static/css/" + file + ".css";
  
  exec(cmd, (error, stdout, stderr) => {
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
    if (error) {
      console.error(`exec error: ${error}`);
      throw error;
    }
  })
}

exec("pwd", (error, stdout, stderr) => {
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
  if (error) {
    console.error(`exec error: ${error}`);
    throw error;
  }
})

exec("mkdir -p " + path.resolve("conditional/static/css"))

compileFile("app")

compileFile("presentations")

