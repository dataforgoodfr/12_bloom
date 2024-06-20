cd "$(dirname "$0")"/..
docker compose -f docker-compose.yaml -f docker-compose-load-data.yaml up || pause