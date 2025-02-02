#!/bin/sh
cd "$(dirname "$0")"/..
docker compose build $1 || read -p "[$?] Appuyer sur une pour continuer"
