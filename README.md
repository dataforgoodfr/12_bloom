# Bloom Project

This project is maintained by D4G in order to gather vessels data. 
A cron job is launched every 15min, does calls to API and save the data in a Postgresql database.

You can develop locally using Poetry and your own database but you can also use the Makefile to :
1) launch a local postgresql dockerized
2) launch a python environment dockerized

please note that every container use the .env.template file. You may want to modify it to access the dockrized db from you local python environment for exemple (using POSTGRES_HOSTNAME=localhost and POSTGRES_PORT=5480

## Development Database

Launch the following command :
` make launch-dev-db `

Now, a postgresql db is available in your localhost, port 5480. And a pgadmin is available port 5080

## Development environment

Launch the following command to launch the development environment :
` make launch-dev-container`

In order to use the development environment, you will need to do a ` docker ps` to find the container_id and do a scd command :
` docker exec -ti DOCKER_ID /bin/bash`

You know have a shell which can launch python command.

A second option is to launch directly the app.py command thanks to this command :
` launch-app`

## About Database schema
Don't be afraid to launch ` alembic upgrade head` in the root of the project in order to update the database schema to the last version.

Some initialisation files are also available in alembic/init_script

## About directory architecture
The domain directory ...
The infra directory ...

## test & precommit hook
Please install the [precommit hook](https://pre-commit.com/) tool locally to avoid any issue with the CI/CD.

You may also want to launch tests :
` tox -vv`
..



