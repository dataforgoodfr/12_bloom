cd "$(dirname "$0")"/../..
docker compose -f docker-compose.yaml -f docker-compose.override.dev.yaml up || read -p "Error. Press any key to continue"