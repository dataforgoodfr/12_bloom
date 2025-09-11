#! /bin/sh

cd "$(dirname "$0")" || exit 1
source /Users/marthevienne/12_bloom/backend/.venv/bin/activate
[ ! -f /Users/marthevienne/12_bloom/backend/.env ] || export $(grep -v '^#' /Users/marthevienne/12_bloom/backend/.env | xargs)
cd ./backend/dbt_trawlwatch

sleep 60

dbt run --select observ_spire_ais_data_retrievals
dbt run --select itm_vessel_last_raw_position
dbt run --select mart_dim_vessels__last_positions