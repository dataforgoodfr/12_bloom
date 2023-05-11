VERSION ?= 1.0.0

build:
	@docker build -t d4g/bloom:${VERSION} --platform linux/amd64  -f docker-env/Dockerfile .
	@docker tag d4g/bloom:${VERSION} d4g/bloom:latest

launch-dev-container:
	@docker run -d -ti --name blomm-dev  --mount type=bind,source="$(shell pwd)",target=/source_code d4g/bloom:${VERSION}  /bin/bash

launch-app:
	@docker run --rm --name blomm-test  --mount type=bind,source="$(shell pwd)",target=/source_code --env-file ./.env.template d4g/bloom:${VERSION} /venv/bin/python3 app.py
