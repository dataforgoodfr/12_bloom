# Bloom_scrap

Scraper qui collecte les données de positions AIS pour une liste de bateau


Vous pouvez ajouter ces deux lignes à votre crontab pour lancer le job toutes les 15min
Attention il semblerait que &> ne fonctionnerait pas avec tous les bash

`DATEVAR=date +20%y%m%d_%H%M%S
*/15 * * * * /root/Bloom_scrap/bloom_scraper.sh &> /tmp/bloom_scraper_log_$($DATEVAR)`


Pour utiliser la nouvelle version du scraper, la commande python est :
```bash
python app.py
```
Pour l'exécuter en local, un paramètre supplémentaire est nécessaire :
```bash
python app.py -m local
```

Installation :

TODO

Après installation : `poetry run pre-commit install`


# Use app.py into a local docker container
In order to use of app.py as a cron job that run every 15 minutes into a docker container please follows those steps :
1) Navigate to docker-local-env repository with command : cd ./docker-local-env
2) Build docker compose file with : docker-compose build 
3) Run docker compose file with : docker-compose up
4) Enter into running container with : docker exec -it bloom_scraper /bin/bash

Please note: If you encounter a container build error, ensure you are using the following flag when building the Docker image: --platform linux/amd64. This is particularly important for computers with ARM architecture.