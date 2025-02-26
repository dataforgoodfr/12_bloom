# Logique de traitement des positions pour la création des segments, des excursions et calcul des métriques

**ATTENTION : dans cette logique, on ne prend pas en compte un recalcul des excursions sur la base de `dim_vessel_source_mapping`.
À modifier par la suite en se basant sur [#428](https://github.com/dataforgoodfr/12_bloom/pulls/428)**

## Périodicité
* À chaque call API (toutes les 15 min)
* pour recalcul des trajectoires :
    - par `vessel_id`
    - par batch temporel

## Description du processus par vessel_id

```mermaid
graph TD;
    ISTART[START<br>**PROCESS NEW VESSEL POSITION**]-->I000
    I000[New vessel position stg_vessel_position]-->I001{If stg_vessel_position in port}
    I001-->|Yes|I002{If last excursion is closed}
    I002-->|Yes|I004[Ignore stg_vessel_position]
    I002-->|No|I005[Update <br>last excursion]
    I001-->|No|I006{If last excursion is closed}
    I007[Associate excursion id to stg_vessel_position]
    I005-->I007
    I006-->|No|I007
    I006-->|Yes|I008[Create new excursion]-->I007
    I007-->I009[Add stg_vessel_position to batch stg_vessel_positions]
```

