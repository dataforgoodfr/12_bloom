#! /bin/sh

source /home/bas/venv/bin/activate
cd $APP_FOLDER

python bloom/tasks/load_spire_data_from_api.py && \
flock bloom/tasks/clean_positions.py --command "
    python bloom/tasks/clean_positions.py && 
    python bloom/tasks/create_update_excursions_segments.py"