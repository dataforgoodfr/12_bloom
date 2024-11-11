#! /bin/sh

exec 200>./var/lock/mylockfile
flock -n 200 || exit 1

/home/bas/venv/bin/python /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/load_spire_data_from_api.py && \
/home/bas/venv/bin/python /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/clean_positions.py && \
/home/bas/venv/bin/python /home/bas/app_7244f095-70bc-43c3-9950-d075c01af05f/backend/bloom/tasks/create_update_excursions_segments.py