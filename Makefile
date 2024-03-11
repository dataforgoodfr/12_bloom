VERSION ?= 1.0.0

#BLOOM_DEV_DOCKER = @docker run --name bloom-test  --mount type=bind,source="$(shell pwd)",target=/project --env-file ./.env.test --network=bloom_net -p 8501:8501
BLOOM_DEV_DOCKER = @docker run --name bloom-test -v "$(shell pwd)/data:/data" -v "$(shell pwd)/:/project" --env-file ./.env.template --network=bloom_net -p 8501:8501
BLOOM_PRODUCTION_DOCKER = @docker run -v "$(shell pwd)/data:/data" -v "$(shell pwd)/:/project" --env-file ./.env --log-driver json-file --log-opt max-size=10M --log-opt max-file=3 --entrypoint /entrypoint.sh

build:
	@docker build -t d4g/bloom:${VERSION} --platform linux/amd64  -f docker/Dockerfile .
	@docker tag d4g/bloom:${VERSION} d4g/bloom:latest

launch-dev-db:
	@docker compose -f docker/docker-compose-db.yaml up -d
	@sleep 10
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} alembic upgrade head
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 src/alembic/init_script/load_vessels_data.py

load-ports-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 alembic/init_script/load_ports_data.py

load-amp-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 src/alembic/init_script/load_amp_data.py

load-test-positions-data:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 src/alembic/init_script/load_positions_data.py

launch-dev-container:
	$(BLOOM_DEV_DOCKER) -dti  d4g/bloom:${VERSION} /bin/bash

launch-dev-app:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} /venv/bin/python3 src/app.py

launch-test:
	$(BLOOM_DEV_DOCKER) --rm d4g/bloom:${VERSION} tox -vv

rm-dev-db:
	@docker compose -f docker/docker-compose-db.yaml stop
	@docker compose -f docker/docker-compose-db.yaml rm

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
	$(BLOOM_DEV_DOCKER) --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /project/bloom_$(shell date +%Y%m%d_%H%M).dump'

dump-db:
	@docker run --mount type=bind,source="$(shell pwd)",target=/project --env-file ./.env.test --network=bloom_net --rm postgres:latest sh -c 'export PGPASSWORD=$$POSTGRES_PASSWORD && pg_dump -Fc $$POSTGRES_DB -h $$POSTGRES_HOSTNAME -p $$POSTGRES_PORT -U $$POSTGRES_USER> /project/bloom_$(shell date +%Y%m%d_%H%M).dump'
