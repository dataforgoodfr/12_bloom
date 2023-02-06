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
