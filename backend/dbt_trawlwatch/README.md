# Initialisation

## Principe général du workflow d'initialisation

1. Lancement de macros qui : 
    1. Détruisent (le cas échéant) et recréent les schémas définis dans `dbt_project.yml` par 
    `dbt_schemas_to_init: ['admin','itm','marts','observ','seeds','staging','utils']` 
    2. Recréent toutes les fonctions et procédures stockées utiles au projet, ainsi que quelques tables annexes
    3. Récréent la structure initiale des tables partitionnées
2. Rechargement des tables de dimensions en .CSV (seeds) par `dbt seed`
4. Run d’initialisation du workflow (1h + environ 8-9h par année d’historique de données sources AIS)
`dbt run --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'`
Avec l'augmentation de l'historique, il est possible de rencontrer un timeout sur certaines requêtes : segmenter alors le workflow en répétant la ligne ci-dessus avec un découpage `--event-time-start` et `--event-time-end` par année
5. Compte-tenu de la durée du run d’initialisation, lancement d’un second run incrémental permettant de rattraper le retard accumulé durant le run initial 
`dbt run --event-time-start "<<<remplacer par : today - 1day>>>" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'`
6. Lancement d’un dbt run classique pour terminer la syncrhonisation `dbt run`
7. Evaluation de l’ensemble des tests `dbt test`

## Script INIT intégral (à adapter avec la date courante)
⚠️ ATTENTION >>> Réinitialisation complète du projet !!!

### UNIX
```shell
cd ./12_bloom/backend/dbt_trawlwatch/
dbt run-operation __init_dbt_trawl_watch__init_all
dbt seed
# À remplacer dynamiquement ou manuellement
dbt run --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'
dbt run --event-time-start "<<<remplacer par : today - 1day>>>" --event-time-end "<<<remplacer par : today + 1day>>>" --vars '{default_microbatch_size: "day"}'
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


Avec l'augmentation de l'historique, il est possible de segmenter davantage les runs d'initialisation

## Reconstruire et tester seulement les tables de dimension
```shell
dbt build --select tag:dim 
```

# Run au fil de l'eau
```shell
dbt run
```
