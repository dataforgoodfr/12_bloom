VERSION ?= 1.0.0

BLOOM_DEV_DOCKER = docker run --name bloom-dev --mount type=bind,source="$(shell pwd)",target=/source_code --env-file /tmp/.env.docker.dev --network=bloom_net -e POSTGRES_PORT=5432 -p 8501:8501 -e APP_ENV=dev -v "$(shell pwd)/.env:/source_code/.env" -v "$(shell pwd)/.env.local:/source_code/.env.local" -v $(shell pwd)/.env.dev:/source_code/.env.dev -v $(shell pwd)/.env.dev.local:/source_code/.env.dev.local
BLOOM_PRODUCTION_DOCKER = docker run --add-host ${POSTGRES_HOSTNAME}:$${POSTGRES_IP} --mount type=bind,source="$(shell pwd)",target=/source_code --log-driver json-file --log-opt max-size=10M --log-opt max-file=3 --entrypoint /entrypoint.sh -e APP_ENV=prod -v $(shell pwd)/.env:/source_code/.env -v $(shell pwd)/.env.local:/source_code/.env.local -v $(shell pwd)/.env.prod:/source_code/.env.prod -v $(shell pwd)/.env.prod.local:/source_code/.env.prod.local

EXPORT_ENV_DEV = @export $(shell cat $(shell pwd)/.env | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.local | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.dev | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.dev.local | grep -v "#" | xargs -d '\r') >> /dev/null;
EXPORT_ENV_TEST = @export $(shell cat $(shell pwd)/.env | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.local | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.test | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.test.local | grep -v "#" | xargs -d '\r') >> /dev/null;
EXPORT_ENV_PROD = @export $(shell cat $(shell pwd)/.env | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.local | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.prod | grep -v "#" | xargs -d '\r') >> /dev/null && export $(shell cat $(shell pwd)/.env.prod.local | grep -v "#" | xargs -d '\r') >> /dev/null;

build:
	@docker build -t d4g/bloom:${VERSION} --platform linux/amd64  -f docker-env/Dockerfile .
	@docker tag d4g/bloom:${VERSION} d4g/bloom:latest

launch-dev-db:
	$(EXPORT_ENV_DEV) export APP_ENV=dev; docker compose -f docker-env/docker-compose-base.yaml up -d postgres
	$(EXPORT_ENV_DEV) export APP_ENV=dev; docker compose -f docker-env/docker-compose-base.yaml up -d app
	$(EXPORT_ENV_DEV) && docker compose -f docker-env/docker-compose-db.yaml up -d
	@sleep 20
	$(EXPORT_ENV_DEV) export APP_ENV=dev; docker compose -f docker-env/docker-compose-base.yaml exec app alembic upgrade head
	$(EXPORT_ENV_DEV) export APP_ENV=dev; docker compose -f docker-env/docker-compose-base.yaml exec app /venv/bin/python3 alembic/init_script/load_vessels_data.py

load-amp-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_amp_data.py

load-test-positions-data:
	$(EXPORT_ENV_DEV) $(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_positions_data.py

launch-dev-container:
	$(EXPORT_ENV_DEV) $(BLOOM_DEV_DOCKER) -dti  d4g/bloom:${VERSION} /bin/bash

launch-dev-app:
	$(EXPORT_ENV_DEV) $(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 app.py

launch-test:
	$(EXPORT_ENV_DEV) $(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} tox -vv

rm-dev-db:
	$(EXPORT_ENV_DEV) @docker compose -f docker-env/docker-compose-db.yaml stop
	$(EXPORT_ENV_DEV) @docker compose -f docker-env/docker-compose-db.yaml rm

rm-dev-env:
	@docker stop bloom-test
	@docker rm bloom-test

init-production:
	$(EXPORT_ENV_PROD) $(BLOOM_PRODUCTION_DOCKER) --name bloom-production-db-init --rm d4g/bloom:${VERSION} alembic upgrade head
	$(EXPORT_ENV_PROD) $(BLOOM_PRODUCTION_DOCKER) --name bloom-production-db-init --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_vessels_data.py

launch-production:
	$(EXPORT_ENV_PROD) $(BLOOM_PRODUCTION_DOCKER) --name bloom-production -d d4g/bloom:${VERSION} cron -f -L 2

launch-production-app:
	$(EXPORT_ENV_PROD) $(BLOOM_PRODUCTION_DOCKER) --name bloom-production-app --rm d4g/bloom:${VERSION} /venv/bin/python3 app.py

dump-dev-db:
	$(EXPORT_ENV_DEV) $(BLOOM_DEV_DOCKER) --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'

dump-db:
	$(EXPORT_ENV_DEV) $(EXPORT_ENV_DEV) && docker run --mount type=bind,source="$(shell pwd)",target=/source_code --network=bloom_net --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'

