#!/bin/sh
cd "$(dirname "$0")"/..
docker compose up $1 || read -p "[$?] Appuyer sur une pour continuer"
