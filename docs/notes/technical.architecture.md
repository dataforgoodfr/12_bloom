## Components

#todo

## Data models

- SQL Alchemy is used to map infra [SQL models](see [infra/database](../../src/bloom/infra/database/))
- A mapping is done to map infra models with domain
- For the front-end application pydantic is used (see [domain](../../src/bloom/domain/))

## Worflows

- Every 15 minutes, latest vessels positions are scrap from spire api [app.py](../../src/app.py)
- Every 15 minutes, new alerts are sent to slack [app.py](../../src/app.py)

## Versionning

- Code : github
- Database schema : alembic

The command ` alembic upgrade head` can be used in the root of the project in order to update the database schema to the last version.
For further usages check [alembic documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html) (ex : create or running migrations)

## Quality

- Tests with Tox, see Makefile for run command

## Monitoring

- logs with logging package

## Deployment

#todo

## Domain glossary

See [here](https://www.notion.so/dataforgood/6a8d74632b0c45ebb0990c2e75147f57?v=a61dbe31b01a47149974e3bb5e9a3c16)