### Prerequisites:

1. Ensure [Docker](https://docs.docker.com/get-docker/) is installed.
2. Ask for zones data subset and saves it into data folder as zones_subset.csv
3. Ask for spire positions data subset and saves it into data folder as spire_positions_subset.csv


### Steps:

1. **Launch development database**

    ```bash
    make launch-dev-db
    ```

    It consists in 3 steps :
    1. create database with docker compose (docker-compose-db.yaml)
    2. upgrade to last schema version with alembic
    3. load chalutiers_palagiques.csv into vessels table

2. **Load amp data subset**

    ```bash
    make load-amp-data
    ```

    It consists in loading zones_subset.csv into mpa_fr_with_mn table.

3. **Load spire positions data**

    ```bash
    make load-test-positions-data
    ```

    It consists in loading spire_positions_subset.csv into spire_vessel_positions table.


### Notes:

- If you have an empty table for alerts, it's normal since it's the application that generates these data.
- You may not have all vessels from vessels table with data in the spire_vessel_positions, so make sure to select mmsi with positions in your subset if you want to test the application.
