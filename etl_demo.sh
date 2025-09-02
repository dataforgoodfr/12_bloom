#! /bin/sh

cd "$(dirname "$0")" || exit 1
source backend/.venv/bin/activate    
cd $APP_FOLDER/dbt_trawlwatch

sleep 60

dbt run --select observ_spire_ais_data_retrievals
dbt run --select itm_vessel_last_raw_position
dbt run --select mart_dim_vessels__last_positions