Yet another readme :D

Quickstart :

git clone https://github.com/dataforgoodfr/12_bloom.git

docker compose build

docker compose pull

copy and paste bloom/env.template at the same level than docker-compose.yaml and rename it .env

docker compose run --service-ports bloom /bin/bash

streamlit run Trawlwatcher.py

working mmsi : 261084090
