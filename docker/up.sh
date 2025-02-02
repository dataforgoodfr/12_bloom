#!/bin/sh
cd "$(dirname "$0")"/..
docker compose up $@ || read -p "[$?] Appuyer sur une pour continuer"
