#!/bin/sh
cd "$(dirname "$0")"/..
docker compose down $@ || read -p "[$?] Appuyer sur une pour continuer"
