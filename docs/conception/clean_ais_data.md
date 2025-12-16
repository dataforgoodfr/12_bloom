
# Logique de traitement des nouvelles données AIS et création des positions

## Périodicité
* À chaque call API (toutes les 15 min)

## Description du processus

Ne traiter que les données Spire qui ont été mises à jour : spire_ais_data.position_update_timestamp > position_updates.point_in_time

```mermaid
graph LR;
    ISTART[START<br>**PROCESS <br>NEW SPIRE AIS DATA**]-->I000
    I000[New spire ais data <br>stg_spire_data]-->I001[Select essentiel info]
    I001-->I002[Drop duplicates]
    I002-->I003[Save positions]
    I003-->I004[Update <br>position_updates]
```
