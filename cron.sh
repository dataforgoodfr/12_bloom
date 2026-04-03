#! /bin/bash -l

source ${APP_HOME}/.venv/bin/activate
python -m bloom.usecase.create_kpler_ais_messages
deactivate