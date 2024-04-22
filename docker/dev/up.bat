cd %~dp0/../..
docker compose -f docker-compose.yaml -f docker-compose.override.dev.yaml up || pause