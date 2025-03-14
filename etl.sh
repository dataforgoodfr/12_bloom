#! /bin/sh

cd /Users/marthevienne/12_bloom/backend
source .venv/bin/activate
sleep 90

python3 -m bloom.tasks.clean_positions 2>> logs.log && \
python3 -m bloom.tasks.create_update_excursions_segments 2>> logs.log