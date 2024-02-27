VERSION ?= 1.0.0

BLOOM_DEV_DOCKER = docker run --name bloom-dev  --mount type=bind,source="$(shell pwd)",target=/source_code --env-file /tmp/docker.dev --network=bloom_net -p ${POSTGRES_PORT}:8501
BLOOM_PRODUCTION_DOCKER = @docker run --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env --log-driver json-file --log-opt max-size=10M --log-opt max-file=3 --entrypoint /entrypoint.sh

EXPORT_ENV_DEV = @export $(shell cat /tmp/docker.dev | grep -v "#" | xargs -d '\r')
EXPORT_ENV_TEST = @export $(shell cat /tmp/docker.test | grep -v "#" | xargs -d '\r')
EXPORT_ENV_PROD = @export $(shell cat /tmp/docker.prod | grep -v "#" | xargs -d '\r')

UPDATE_ENV_DEV = @$(shell pwd)/scripts/update_env.sh dev /tmp/env.dev
UPDATE_ENV_TEST = @$(shell pwd)/scripts/update_env.sh test /tmp/env.test
UPDATE_ENV_PROD = @$(shell pwd)/scripts/update_env.sh prod /tmp/env.prod

build:
	@docker build -t d4g/bloom:${VERSION} --platform linux/amd64  -f docker-env/Dockerfile .
	@docker tag d4g/bloom:${VERSION} d4g/bloom:latest

launch-dev-db:
	$(UPDATE_ENV_DEV)
	$(EXPORT_ENV_DEV) && docker compose -f docker-env/docker-compose-db.yaml up -d
	@sleep 20
	$(EXPORT_ENV_DEV) && $(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} alembic upgrade head
	$(EXPORT_ENV_DEV) && $(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_vessels_data.py

load-amp-data:
	$(UPDATE_ENV_DEV)
	$(EXPORT_ENV_DEV) && $(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_amp_data.py

load-test-positions-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_positions_data.py

launch-dev-container:
	$(BLOOM_DEV_DOCKER) -dti  d4g/bloom:${VERSION} /bin/bash

launch-dev-app:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 app.py

launch-test:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} tox -vv

rm-dev-db:
	@docker-compose -f docker-env/docker-compose-db.yaml stop
	@docker-compose -f docker-env/docker-compose-db.yaml rm

rm-dev-env:
	@docker stop bloom-test
	@docker rm bloom-test

init-production:
	$(BLOOM_PRODUCTION_DOCKER) --name bloom-production-db-init --rm d4g/bloom:${VERSION} alembic upgrade head
	$(BLOOM_PRODUCTION_DOCKER) --name bloom-production-db-init --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_vessels_data.py

launch-production:
	$(BLOOM_PRODUCTION_DOCKER) --name bloom-production -d d4g/bloom:${VERSION} cron -f -L 2

launch-production-app:
	 $(BLOOM_PRODUCTION_DOCKER) --name bloom-production-app --rm d4g/bloom:${VERSION} /venv/bin/python3 app.py

dump-dev-db:
	$(BLOOM_DEV_DOCKER) --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'

dump-db:
	@docker run --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env.test --network=bloom_net --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'