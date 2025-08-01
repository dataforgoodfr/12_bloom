# Initialisation

## Principe général du workflow d'initialisation

1. Lancement de macros qui : 
    1. Détruisent (le cas échéant) et recréent les schémas définis dans `dbt_project.yml` par 
    `dbt_schemas_to_init: ['admin','itm','marts','observ','seeds','staging','utils']` 
    2. Recréent toutes les fonctions et procédures stockées utiles au projet, ainsi que quelques tables annexes
    3. Récréent la structure initiale des tables partitionnées
2. Rechargement des tables de dimensions en .CSV (seeds) par `dbt seed`
4. Run d’initialisation du workflow (1h + environ 10h par année d’historique de données sources AIS)
`dbt run --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'`
Avec l'augmentation de l'historique, il est possible de rencontrer un timeout sur certaines requêtes : segmenter alors le workflow en répétant la ligne ci-dessus avec un découpage `--event-time-start` et `--event-time-end` par année
5. Compte-tenu de la durée du run d’initialisation, lancement d’un second run incrémental "de rattrapage" permettant de récupérer les données remontées durant l'exécution du run initial (durée : environ 15')
`dbt run --event-time-start "<<<remplacer par : today - 1 day>>>" --event-time-end "<<<remplacer par : today + 1 day >>>" --vars '{default_microbatch_size: "day"}'`
5. (suite) Si, ce qui ne devrait pas être le cas, le run de rattrapage (5) a duré plus de 1h, lancer un second run de rattrapage seulement sur la journée en cours : 
`dbt run --event-time-start "<<<remplacer par : today>>>" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'`
6. Lancement d’un dbt run classique pour terminer la syncrhonisation `dbt run`. Le microbatch par défaut étant 'hour', ce run traite les données de l'heure en cours et de l'heure précédente.
7. Evaluation de l’ensemble des tests `dbt test`

## Script INIT intégral (à adapter avec la date courante)
⚠️ ATTENTION >>> Réinitialisation complète du projet !!!

### UNIX
```shell
cd ./12_bloom/backend/dbt_trawlwatch/
dbt run-operation __init_dbt_trawl_watch__init_all
dbt seed
# À remplacer dynamiquement ou manuellement
dbt run --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'
dbt run --event-time-start "<<<remplacer par : today - 1 day>>>" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'
dbt run
dbt test
```

### WINDOWS
```powershell
cd .\12_bloom\backend\dbt_trawlwatch\
dbt run-operation __init_dbt_trawl_watch__init_all
dbt seed
dbt run --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'
dbt run --event-time-start "<<<remplacer par : today - 1day>>>" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'
dbt run 
dbt test
```


Avec l'augmentation de l'historique, il est possible de segmenter davantage les runs d'initialisation, exemple : 
```shell
cd ./12_bloom/backend/dbt_trawlwatch/
dbt run-operation __init_dbt_trawl_watch__init_all
dbt seed
# À remplacer dynamiquement ou manuellement
dbt run --event-time-start "2024-05-01" --event-time-end "2025-01-01" --vars '{default_microbatch_size: "day"}'
dbt run --event-time-start "2025-01-01" --event-time-end "2026-01-01" --vars '{default_microbatch_size: "day"}'
#... (ajouter une ligne par année terminée)
dbt run --event-time-start "<<<remplacer par : today - 1day>>>" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'
dbt run
dbt test
```

## Reconstruire et tester seulement les tables de dimension
```shell
dbt build --select tag:dim 
```

# Run au fil de l'eau
```shell
dbt run
```

# Mettre à jour seulement "itm_vessel_last_raw_position "
Il faut mettre à jour également les modèles situés en amont (< 15") : 
`dbt run --select +itm_vessel_last_raw_position` 