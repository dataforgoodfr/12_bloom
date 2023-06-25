# Database initialisation and versioning


## Database initialisation

First you need to run scripts which are in alembic/init_script :
- the load_vessels_data.py script will load vessels metadata from the data/chalutier_pelagique.csv file.
- the load_geometry_data.py file will load shape data from the Nonterrestrial_WDPA_Jan2023.shp file. This file is not included in this github project but you can ask for it. It's only used for the alerting part.

The second step is to load the [distance-from-port-v20201104.tiff](https://globalfishingwatch.org/data-download/datasets/public-distance-from-port-v1) and [distance-from-shore.tif](https://globalfishingwatch.org/data-download/datasets/public-distance-from-shore-v1) files. They are only used for the alerting part.
- install psql and raster2pgsql.
- install raster type in db with postgis-raster using `create extension postgis_raster`
- adapt this command for each file :  `raster2pgsql -t auto -I -C -M /PATH_TO/distance-from-shore.tif public.distance_shore | PGPASSWORD='POSTGRES_PASSWORD' psql -h POSTGRES_HOSTNAME -d POSTGRES_DB -U POSTGRES_USER -p POSTGRES_PORT`

## Database versioning
The command ` alembic upgrade head` can be used in the root of the project in order to update the database schema to the last version.