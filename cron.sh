#! /bin/bash -l

source ${APP_HOME}/backend/.venv/bin/activate
# python ${APP_HOME}/backend/load_spire_data_from_api.py
# python -m bloom.usecase.create_kpler_ais_messages &&\
cd ${APP_HOME}/backend/dbt_trawlwatch &&\
dbt run --select observ_spire_ais_data_retrievals &&\
dbt run --select itm_vessel_last_raw_position &&\
dbt run --select mart_dim_vessels__last_positions
deactivate