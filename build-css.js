const { exec } = require('child_process');

// yes I know this is awkward. I want to actually use the node libraries but that gets SUBSTANTIALLY easier when node and all the dependinces are updated
// So after I can update node and stuff I'll change this to do it in a sane way, probably in webpack

exec("sass -I ./node_modules/csh-material-bootstrap/dist/css -I ./node_modules/datatables.net-bs/css -I ./node_modules/bootstrap-material-datetimepicker/css -I ./node_modules/selectize-scss/src -I ./node_modules/load-awesome/css -I ./node_modules/reveal.js/css -I . frontend/stylesheets/app.scss conditional/static/css/app.css")

exec("sass -I ./node_modules/csh-material-bootstrap/dist/css -I ./node_modules/datatables.net-bs/css -I ./node_modules/bootstrap-material-datetimepicker/css -I ./node_modules/selectize-scss/src -I ./node_modules/load-awesome/css -I ./node_modules/reveal.js/css -I . frontend/stylesheets/presentations.scss conditional/static/css/presentations.css")
