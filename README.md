Conditional
===========

[![Build Status](https://travis-ci.org/ComputerScienceHouse/conditional.svg)](https://travis-ci.org/ComputerScienceHouse/conditional)

A comprehensive membership evaluations solution for Computer Science House.

Development
-----------

### Config

You must create `config.py` in the top-level directory with the appropriate credentials for the application to run. See `config.env.py` for an example.

#### Add OIDC Config
Reach out to an RTP to get OIDC credentials that will allow you to develop locally behind OIDC auth
```py
# OIDC Config
OIDC_ISSUER = "https://sso.csh.rit.edu/auth/realms/csh"
OIDC_CLIENT_CONFIG = {
    'client_id': '',
    'client_secret': '',
    'post_logout_redirect_uris': ['http://0.0.0.0:6969/logout']
}
```

#### Database 
You can either develop using the dev database, or use the local database provided in the docker compose file

Using the local database is detailed below, but both options will require the dev database password, so you will have to ask an RTP for this too

### Run (Without Docker)

To run the application without using containers, you must have the latest version of [Python 3](https://www.python.org/downloads/) and [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) installed. Once you have those installed, create a new virtualenv and install the Python dependencies:

```sh
virtualenv .conditionalenv -p `which python3`
source .conditionalenv/bin/activate
pip install -r requirements.txt
```

In addition, you must have Node, NPM, and Weback CLI installed to properly execute the asset pipeline. If you don't have Node installed, we recommending installing with [NVM](https://github.com/creationix/nvm):

```sh
nvm install
nvm use
npm install -g webpack
```

Then, install the pipeline and frontend dependencies: (do this in the `frontend` directory)

```sh
npm install
```

Once you have all of the dependencies installed, run

```sh
npm webpack
```

This will build the frontend assets and put them in the correct place for use with flask

Finally, start the flask app with `gunicorn`

```sh
gunicorn
```

or 

```sh
python -m gunicorn
```

### Run (containerized)

It is likely easier to use containers like `podman` or `docker` or the corresponding compose file

With podman, I have been using 

```sh
podman compose up --force-recreate --build
```

Which can be restarted every time changes are made

### Dependencies

To add new dependencies, add them to `requirements.in` and then run `pip-compile requirements.in` to produce a new locked `requirements.txt`. Do not edit `requirements.txt` directly as it will be overwritten by future PRs.

### Local database

You can run the database locally using the docker compose

To populate it with dev data for example, you can use the command

```sh
PGPASSWORD='[DB PASSWORD]' pg_dump -h postgres.csh.rit.edu -p 5432 -U conditionaldev conditionaldev |  PGPASSWORD='fancypantspassword' psql -h localhost -p 5432 -U conditional conditional
```

This can be helpful for changing the database schema

To run migration commands in the local database, you can run the commands inside the docker container. Any migrations created will also be in the local repository since migrations are mounted in the docker compose
```sh
podman exec conditional flask db upgrade
```

### Database Migrations

If the database schema is changed after initializing the database, you must migrate it to the new schema by running:

```
flask db upgrade
```

At the same time, if you change the database schema, you must generate a new migration by running:

```
flask db migrate
```

The new migration script in `migrations/versions` should be verified before being committed, as Alembic may not detect every change you make to the models.

For more information, refer to the [Flask-Migrate](https://flask-migrate.readthedocs.io/) documentation.

### Old Evals DB Migration

Conditional includes a utility to facilitate data migrations from the old Evals DB. This isn't necessary to run Conditional. To perform this migration, run the following commands before starting the application:

```
pip install pymysql
flask zoo
```
