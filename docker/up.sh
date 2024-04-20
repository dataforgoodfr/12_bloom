cd "$(dirname "$0")"/..
docker compose -f docker-compose.yaml up || read -p "Error. Press any key to continue"