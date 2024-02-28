VERSION ?= 1.0.0

BLOOM_DEV_DOCKER = @docker run --name bloom-dev --mount type=bind,source="$(shell pwd)",target=/source_code --env-file /tmp/.env.docker.dev --network=bloom_net -e POSTGRES_PORT=5432 -p 8501:8501 -e APP_ENV=dev -v "$(shell pwd)/.env:/source_code/.env" -v "$(shell pwd)/.env.local:/source_code/.env.local" -v $(shell pwd)/.env.dev:/source_code/.env.dev -v $(shell pwd)/.env.dev.local:/source_code/.env.dev.local
BLOOM_PRODUCTION_DOCKER = @docker run --add-host ${POSTGRES_HOSTNAME}:$${POSTGRES_IP} --mount type=bind,source="$(shell pwd)",target=/source_code --env-file /tmp/.env.docker.prod --log-driver json-file --log-opt max-size=10M --log-opt max-file=3 --entrypoint /entrypoint.sh -e APP_ENV=prod -v $(shell pwd)/.env:/source_code/.env -v $(shell pwd)/.env.local:/source_code/.env.local -v $(shell pwd)/.env.prod:/source_code/.env.prod -v $(shell pwd)/.env.prod.local:/source_code/.env.prod.local

define mount_env_options
	OPTIONS=""
	files=".env .env.local .env.dev .env.test .env.prod .env.dev.local .env.test.local .env.prod.local"
	for file in $$files ;do 
		echo "Y"
	done
	echo $$OPTIONS
endef

MOUNT_ENV_OTPIONS = /bin/bash $(shell pwd)/scripts/env_mount.sh

EXPORT_ENV_DEV = @export $(shell cat /tmp/.env.docker.dev | grep -v "#" | xargs -d '\r')
EXPORT_ENV_TEST = @export $(shell cat /tmp/.env.docker.test | grep -v "#" | xargs -d '\r')
EXPORT_ENV_PROD = @export $(shell cat /tmp/.env.docker.prod | grep -v "#" | xargs -d '\r')

UPDATE_ENV_DEV = @$(shell pwd)/scripts/update_env.sh dev /tmp/.env.docker.dev
UPDATE_ENV_TEST = @$(shell pwd)/scripts/update_env.sh test /tmp/.env.docker.test
UPDATE_ENV_PROD = @$(shell pwd)/scripts/update_env.sh prod /tmp/.env.docker.prod

env-options:
	echo 	$(MOUNT_ENV_OPTIONS)

build:
	@docker build -t d4g/bloom:${VERSION} --platform linux/amd64  -f docker-env/Dockerfile .
	@docker tag d4g/bloom:${VERSION} d4g/bloom:latest

launch-dev-db:
	$(UPDATE_ENV_DEV)
	$(EXPORT_ENV_DEV) && docker compose -f docker-env/docker-compose-db.yaml up -d
	@sleep 20
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} alembic upgrade head
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_vessels_data.py

load-amp-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_amp_data.py

load-test-positions-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_positions_data.py

launch-dev-container:
	$(BLOOM_DEV_DOCKER) -dti  d4g/bloom:${VERSION} /bin/bash

launch-dev-app:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 app.py

launch-test:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} tox -vv

rm-dev-db:
	@docker compose -f docker-env/docker-compose-db.yaml stop
	@docker compose -f docker-env/docker-compose-db.yaml rm

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
	$(UPDATE_ENV_DEV)
	$(EXPORT_ENV_DEV) && docker run --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env.test --network=bloom_net --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /source_code/bloom_$(shell date +%Y%m%d_%H%M).dump'

