#! /bin/bash -l

source ${APP_HOME}/backend/.env
source ${APP_HOME}/backend/.venv/bin/activate

python -m bloom.usecase.create_kpler_ais_messages

cd ${APP_HOME}/backend/dbt_trawlwatch

# dbt deps
dbt run
