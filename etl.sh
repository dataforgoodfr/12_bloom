#! /bin/sh

/home/bas/venv/bin/python /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/load_spire_data_from_api.py && \
flock /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/clean_positions.py --command "
    /home/bas/venv/bin/python /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/clean_positions.py && 
    /home/bas/venv/bin/python /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/create_update_excursions_segments.py"