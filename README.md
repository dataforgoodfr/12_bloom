# Bloom Project

This project is maintained by D4G in order to gather vessels data. 
A cron job is launched every 15min, does calls to API and save the data in a Postgresql database.

You can develop locally using Poetry and your own database but you can also use the Makefile to :
1) launch a local postgresql dockerized
2) launch a python environment dockerized

please note that every container use the .env.template file. You may want to modify it to access the dockrized db from you local python environment for exemple (using POSTGRES_HOSTNAME=localhost and POSTGRES_PORT=5480

If you work with Mac m1, the containers may not work as expected

## Poetry 


## Development Database

Launch the following command :
` make launch-dev-db `

Now, a postgresql db is available in your localhost, port 5480. And a pgadmin is available port 5080

You can remove it thanks to this command:
` make rm-db`

## Development environment

Launch the development environment :
` make launch-dev-container`

In order to acess the development environment :
` docker exec -ti blomm-test /bin/bash`

You know have a shell which can launch python command.

To delete the container:
` make rm-dev-env`



A second option is to launch directly the app.py command thanks to this command : (the container is automatically removed after)
` make launch-app`


## About Database schema
Don't be afraid to launch ` alembic upgrade head` in the root of the project in order to update the database schema to the last version.

Some initialisation files are also available in alembic/init_script

## About directory architecture
The domain directory ...
The infra directory ...

## tests & precommit hook
Please install the [precommit hook](https://pre-commit.com/) tool locally to avoid any issue with the CI/CD.

You may also want to launch tests :
` tox -vv`
..



