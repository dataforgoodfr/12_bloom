You can develop locally using Poetry and your own database but you can also use the Makefile to :

1. launch a local postgresql dockerized
2. launch a python environment dockerized

If you work with Mac m1, the containers may not work as expected

## Local Database

You will need to source the .env.template file but before you should modify it according to your local configuration, for example using POSTGRES_HOSTNAME=localhost

## Development Database

First, you need to create an .env.test file, you can use the .env.template file :
` cp .env.template .env.test`

Next, you have to set the SPIRE_TOKEN variable. You can ask for it.

Launch the following command :
`make launch-dev-db`

Now, a postgresql db is available in your localhost, port 5480. And a pgadmin is available port 5080

You can remove it thanks to this command:
` make rm-db`

TIPS : you can use the following command to launch the psql client :
`docker exec -ti postgres_bloom psql -d bloom_db -U bloom_user`

## Development environment

Launch the development environment :
` make launch-dev-container`

In order to access the development environment :
` docker exec -ti bloom-test /bin/bash`

You know have a shell which can launch python command.

To delete the container:
` make rm-dev-env`

A second option is to launch directly the app.py command thanks to this command : (the container is automatically removed after)
` make launch-app`

## tests & precommit hook

Please install the [precommit hook](https://pre-commit.com/) tool locally to avoid any issue with the CI/CD.

You may also want to launch tests :
` tox -vv`
