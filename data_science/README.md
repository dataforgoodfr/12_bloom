# Data Science stream for Bloom

## Data files and sources

### Structure

Relevant data or references to data sources are stored in the `data` folder.

The `data` folder is subdivided into a `raw` (for data directly obtained from outside sources and "re-hosted" on our repo) 
and a `processed` folder (for datasets we produce from `raw` data). 

Ideally, for tracability, processed data should be accompanied by the script used to generate it from raw data.

### Hosting/download large data files

To host or download large data files directly on/from github, use Git Large File Storage (https://git-lfs.com/). 

Make sure to track the extension of large data files as explained in point 2. of https://git-lfs.com/.

Here is a list of tracking commands for some large data formats currently hosted on GH:

`git lfs track "*.shp"`

### Documenting

Ideally, when hosting new data files (whether raw data or transforms), makes sure to document the new data file on https://www.notion.so/dataforgood/aec8be0483f74ebea6a1343604bf0fb6?v=81fd132a4e6f42bca41ae52d80f274c0.
