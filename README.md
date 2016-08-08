Conditional
===========

A comprehensive membership evaluations solution for Computer Science House.

Development
-----------

To run the application, you must have the latest version of [Python 3](https://www.python.org/downloads/) and [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) installed. Once you have those installed, create a new virtualenv and install the Python dependencies:

```
virtualenv .conditionalenv -p `which python3`
source .conditionalenv/bin/activate
pip install -r requirements.txt
```

In addition, you must have the latest stable version of Node, the corresponding version of NPM, and the latest version of Gulp installed to properly execute the asset pipeline. If you don't have Node installed, we recommending installing with [NVM](https://github.com/creationix/nvm):

```
nvm install stable
nvm use stable
npm install -g gulp
```

Then, install the pipeline and frontend dependencies:

```
npm install
```

You must create `config.json` in the top-level directory with the appropriate credentials for the application to run. See `config_sample.json` for an example. To perform the initial database migration, run the following commands before starting the application:

```
pip install pymysql
python conditional/zoo_migrate.py config.json
```

Once you have all of the dependencies installed, simply run `npm start` to run the asset pipeline, start the Python server, and start BrowserSync. Your default web browser will open automatically. If it doesn't, navigate to `http://127.0.0.1:3000`. Any changes made to the frontend files in `frontend` or the Jinja templates in `conditional/templates` will cause the browser to reload automatically.