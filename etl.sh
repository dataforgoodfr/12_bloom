#! /bin/sh

python backend/bloom/tasks/load_spire_data_from_api.py && \
python backend/bloom/tasks/clean_positions.py && \
python backend/bloom/tasks/create_update_excursions_segments.py
