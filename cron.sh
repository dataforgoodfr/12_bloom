#! /bin/bash -l

source ${APP_HOME}/backend/.env
source ${APP_HOME}/backend/.venv/bin/activate

python -m bloom.usecase.create_kpler_ais_messages

cd ${APP_HOME}/backend/dbt_trawlwatch

yesterday="$(date -v-1d +%Y-%m-%d)"
tomorrow="$(date -v+1d +%Y-%m-%d)"

dbt deps
dbt run --select observ_kpler_ais_data_retrievals 
dbt run --select itm_vessel_last_raw_position
dbt run --select mart_dim_vessels__last_positions
dbt seed 
dbt run --event-time-start ${yesterday} --event-time-end ${tomorrow} --vars '{default_microbatch_size: "day"}'
