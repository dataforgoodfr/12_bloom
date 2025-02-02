#!/bin/sh
cd "$(dirname "$0")"/..
docker compose build $@ || read -p "[$?] Appuyer sur une pour continuer"
