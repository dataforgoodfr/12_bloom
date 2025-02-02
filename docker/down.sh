#!/bin/sh
cd "$(dirname "$0")"/..
docker compose down $1 || read -p "[$?] Appuyer sur une pour continuer"
