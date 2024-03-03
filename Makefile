VERSION ?= 1.0.0

BLOOM_DEV_DOCKER = @docker run --name bloom-test  --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env.test --network=bloom_net -p 8501:8501
BLOOM_PRODUCTION_DOCKER = @docker run --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env --log-driver json-file --log-opt max-size=10M --log-opt max-file=3 --entrypoint /entrypoint.sh

build:
	@docker compose -f docker-env/docker-compose.yaml build

start-db-dev: 
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml up db-dev -d
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml up dbadmin-dev -d

start-app-dev:
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml up init-dev -d
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml up app-dev -d

stop-db-dev:
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml down db-dev 
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml down dbadmin-dev 
stop-app-dev:
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml down app-dev

connect-app-dev:
	@if [ -f $$(pwd)/.env.dev ]; then ln -sf $$(pwd)/.env.dev $$(pwd)/.env; else ( echo "ERROR: No file $$(pwd)/.env.dev"; exit 1) ; fi
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml exec app-dev bash

load-amp-data-dev:
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml exec app-dev /venv/bin/python3 alembic/init_script/load_amp_data.py

load-positions-data-dev:
	@docker compose --env-file .env.dev -f docker-env/docker-compose.yaml exec app-dev /venv/bin/python3 alembic/init_script/load_positions_data.py

dump-dev-db:
	$(BLOOM_DEV_DOCKER) --rm db:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'

dump-db:
	@docker run --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env.test --network=bloom_net --rm db:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'
