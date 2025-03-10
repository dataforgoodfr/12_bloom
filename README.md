![banner](docs/images/banner.png)

## What is Trawl Watch

**[Trawl Watch](https://twitter.com/TrawlWatch)** is an initiative launched by
**[BLOOM Association](https://www.bloomassociation.org/en/)** to track and expose the most destructive EU fishing vessels.
Inspired by l’[Avion de Bernard](https://www.instagram.com/laviondebernard/), which monitors the movements of private
jets, **Trawl Watch** aims to make visible the impact of the fishing vessels, mostly trawlers or senners on our oceans.

**These veritable sea monsters are devastating Europe’s biodiversity and coastlines.** It is important to measure the
scale of the damage: about 20 of these factory-vessels can obliterate hundreds of thousands of marine animals and
biodiversity treasures in one day, including in the so-called ‘Marine Protected Areas’ of French territorial waters,
which are not protected at all.

## What is BLOOM Association

**BLOOM** is a non-profit organization founded in 2005 that works to preserve the marine environment and species from
unnecessary destruction and to increase social benefits in the fishing sector. **BLOOM** wages awareness and advocacy
campaigns in order to accelerate the adoption of concrete solutions for the ocean, humans and the climate. **BLOOM**
carries out scientific research projects, independent studies and evaluations that highlight crucial and unaddressed
issues such as the financing mechanisms of the fishing sector. **BLOOM**’s actions are meant for the general public as
well as policy-makers and economic stakeholders.

**Table of contents**

- [Requirements](#requirements)
- [Getting started](#getting-started)
    - [Clone repo](#clone-trawl-watch-repository)
    - [Installation with Docker/Docker Compose stack (Recommended)](#installation-with-docker-docker-compose-stack-recommended)
    - [Installation on local machine](#installation-on-local-machine)
    - [Database migration](#database-migration)
    - [Use Trawl Watch](#use-trawl-watch)


## Requirements

Trawl Watch is tested with:

|            | Main version (dev) | Stable version (1.0.0) |
|------------|--------------------|------------------------|
| Python     | 3.11               | 3.11                   |
| Platform   | AMD64/ARM64(\*)    | AMD64/ARM64(\*)        |
| Docker     | 24                 | 24                     |
| PostgreSQL | 14                 | 14                     |

## Getting started

### Clone Trawl Watch repository

```bash
    # clone git repository
    git clone https://github.com/dataforgoodfr/12_bloom.git
    # change to project root directory
    cd 12_bloom
```

### Installation with Docker/Docker Compose stack (Recommended)

#### Prerequisites

* **Docker Engine** (version >= **18.06.0**) with **Compose** plugin

#### Building image

```bash
    docker compose build
```

> When official Docker image will be available, the building step could be optionnal for user as docker compose up will
> pull official image from repository

#### Starting the application

```bash
    docker compose up
```

#### Load demonstration data

To use Trawl Watch application, some data have to be initialy loaded for demonstration. As these data are protected and
can't be publicly published, you just have to contact the Trawl Watch application team. Informations
on [Who maintains Trawl Watch?](#who-maintains-trawl-watch)

List of required files:
- zones.zip
    - french_metropolitan_mpas.csv
    - fishing_coastal_waters.csv
    - territorial_seas.csv
    - clipped_territorial_seas.csv
- spire_positions_subset.csv

Load all files in data folder.

Then launch docker compose stack using docker compose file extension to add loading data service

    docker compose -f docker-compose.yaml -f docker-compose-load-data.yaml up

You can now jump to [Use Trawl Watch](#use-trawl-watch)

### Installation on local machine

#### Prerequistes

* **Python**: 3.11
* **Python-pip**: >=20
* **Postgresql**: 14, 15, 16

You must have a functionnal PostgreSQL instance with connexion informations (database server hostname or ip, user,
password, database name, port to use)

See [development environment](./docs/notes/development.environment.md) for more information on required environment variables

#### Install Backend Application with Poetry

```bash
    # From project diretory
    cd ./backend
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Install project and dependencies
    uv sync
```

#### Initial configuration

```bash
    # From project root diretory
    # Create initial configuration
    cp .env.template .env
    # Edit .env file
```

#### Loading initial data for backend

```bash
    # From project root diretory
    cd ./backend
    # Check if database is up to date with alembic revisions
    alembic upgrade head
    # If upgrade is successful you can load the data
    # Demonstration data must be recovered from TrawlWatch Project Team
    # and put in <project>/data/ folder with correct names
        - french_metropolitan_mpas.csv
        - fishing_coastal_waters.csv
        - territorial_seas.csv
        - clipped_territorial_seas.csv
        - spire_positions_subset.csv
    $ python3 bloom/tasks/load_dim_vessel_from_csv.py
    $ python3 bloom/tasks/load_dim_port_from_csv.py
    $ python3 bloom/tasks/load_dim_zone_amp_from_csv.py
    $ python3 bloom/tasks/compute_port_geometry_buffer.py
    $ python3 bloom/tasks/load_spire_data_from_csv.py
```

#### Starting the application

```
//TO UPDATE
```

You can now jump to [Use Trawl Watch](#use-trawl-watch)

### Database migration

Trawl Watch DB model has been refactored during DataForGood season 12. If you run a version of Trawl Wach using the old
model follow next steps to upgrade.

- Upgrade DB model:

```
$ alembic upgrade head
```

- Run data conversion from the old model to the new model (actually copy data from `spire_vessel_positions`
  to `spire_ais_data`). This may take long if you have a long positions history:

```
$ python backend/bloom/tasks/convert_spire_vessels_to_spire_ais_data.py
```

- Load new references data (zones, ports, vessels):

```
$ /venv/bin/python3 backend/bloom/tasks/load_dim_vessel_from_csv.py 
$ /venv/bin/python3 backend/bloom/tasks/load_dim_port_from_csv.py
$ /venv/bin/python3 backend/bloom/tasks/load_dim_zone_amp_from_csv.py
$ /venv/bin/python3 backend/bloom/tasks/compute_port_geometry_buffer.py
```

- If you feel it, drop old tables:

```
DROP TABLE mpa_fr_with_mn;
DROP TABLE spire_vessel_positions;
DROP TABLE vessels;
```

### Use Trawl Watch

Launch backend:
```bash
fastapi run backend/bloom/app.py
```

Open [http://0.0.0.0:8000/docs#/](http://0.0.0.0:8000/docs#/)

Launch frontend:
```bash
cd frontend
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000)

## Official source code

You can find official source code on [Github Repository](https://github.com/dataforgoodfr/12_bloom/)

Official Docker (container) images for Trawl Watch are described
in [images](https://github.com/dataforgoodfr/12_bloom/tree/main/docker/).

### Who maintains Trawl Watch
**Marthe Vienne** (marthevienne@bloomassociation.org) is the administrator of Trawl Watch.
