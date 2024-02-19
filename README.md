![banner](images/banner.png)

**[Trawl Watch](https://twitter.com/TrawlWatch)** is an initiative launched by the **[Bloom Association](https://www.bloomassociation.org/en/)** to track and expose the most destructive fishing vessels. Inspired by L’[Avion de Bernard](https://www.instagram.com/laviondebernard/), which monitors the movements of private jets, Trawl Watch aims to make visible the impact of these massive trawlers on our oceans. These vessels, often referred to as mégachalutiers, deploy gigantic nets that can engulf marine life from the surface down to the ocean floor. The consequences are both ecological—as they devastate crucial nursery and breeding areas for marine animals—and social, as they deprive artisanal fishermen of a healthy marine ecosystem. The solution proposed by Bloom is to dismantle these industrial fishing ships and redistribute their quotas to small-scale fishers. A petition has been launched, and Bloom continues to track these megatrawlers while awaiting action from European institutions12.

**Did you know that, in Europe, the largest fishing vessels, which represent 1% of the fleet, catch half of the fish?** These factory-vessels can measure up to 144 meters in length and catch 400,000 kilos of fish per day! This is as much as 1,000 small-scale fishing vessels in one day at sea.

**These veritable sea monsters are devastating Europe’s biodiversity and coastlines.** It is important to measure the scale of the damage: about 20 of these factory-vessels can obliterate hundreds of thousands of marine animals and biodiversity treasures in one day, including in the so-called ‘Marine Protected Areas’ of French territorial waters, which are not protected at all.

In addition, more and more ‘mega trawlers’ – vessels over 25 meters in length – come right up to the coast to fish, so close to the beaches that they can be observed from the shore. These industrial monsters were not designed to fish in coastal waters, where small artisanal fishers operate.

## Installing a Trawl Watch with `venv` and `poetry`

### Prerequisites:

1. Python (≥ `3.10`) installed on your system.
2. Ensure you have `venv` and [`poetry`](https://python-poetry.org/) installed. If not, you can install them using `pip`.

```bash
pip install poetry
```

### Steps:

1. **Clone the GitHub Repository:**

   Clone the GitHub repository you want to install locally using the `git clone` command.

   ```bash
   $ git clone https://github.com/dataforgoodfr/12_bloom.git
   ```

2. **Navigate to the Repository Directory:**

   Use the `cd` command to navigate into the repository directory.

   ```bash
   $ cd 12_bloom/
   ```

3. **Set Up a Virtual Environment using `venv`:**

Create a virtual environment using `venv` to isolate the dependencies for the project.

```bash
$ python -m venv venv
```

4. **Activate the Virtual Environment:**

   Activate the virtual environment to work within its isolated environment.

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

   On Unix or MacOS:

   ```bash
   source venv/bin/activate
   ```

5. **Install Project Dependencies using `poetry`:**

   Use `poetry` to install the project dependencies.

   ```bash
   poetry install
   ```

   This will read the `pyproject.toml` file in the repository and install all the dependencies specified.

6. **(Optional) Install Development Dependencies:**

   If there are separate dependencies for development, you can install them using:

   ```bash
   poetry install --dev
   ```

7. **Run the Project:**

   After installing the dependencies, you can run the project using the appropriate commands specified in the repository's documentation or README file.

   ```bash
   poetry run <command_to_run_project>
   ```

8. **Deactivate the Virtual Environment:**

   Once you're done working with the project, deactivate the virtual environment.

   ```bash
   deactivate
   ```

#### Additional Notes:

- Ensure you are using the correct Python version specified by the repository, especially if it's mentioned in the `pyproject.toml` file.
- Always refer to the repository's documentation or README file for any specific instructions or configurations required for setting up and running the project.

This documentation provides a general guideline for setting up a project from a GitHub repository using `venv` and `poetry`. Adjustments may be needed based on the specific requirements and configurations of the repository you are working with.

### Requirements

### FAQ

Suivre les trajectoires de milliers de bateaux de pêche en quasi temps réel afin de pouvoir analyser leurs pratiques de pêche dans des zones maritimes protégées (AMP) à partir de données GPS récupérées (via antennes satellites et/ou terrestres)

- https://www.un.org/sustainabledevelopment/economic-growth/
- https://www.un.org/sustainabledevelopment/climate-change/
- https://www.un.org/sustainabledevelopment/oceans/

- https://petitions.bloomassociation.org/en/stop-mega-trawlers/

## Setting up your local development environment

### FAQ

## bloom data source

## [Automatic identification system](https://en.wikipedia.org/wiki/Automatic_identification_system)

limits:

- out of range
- intense traffic area
- expensive

- https://spire.com/maritime/

## [Marine Protected Areas]

- https://www.cell.com/one-earth/fulltext/S2590-3322(20)30150-0

## [Shom](https://www.shom.fr/)

pour visualiser les droits miles nautique et les droits historiques

# Bloom Project

This project is maintained by D4G in order to gather vessels data.
A cron job is launched every 15min, does calls to API and save the data in a Postgresql database.

## About directory architecture

The domain directory ...
The infra directory ...

More information can be found there :

1. [Database initialisation and versioning](./documentation/database_init.md)
2. [Development environment](./documentation/dev_env.md)
3. [Useful SQL examples](./documentation/sql_examples.md)
4. [Data models](#todo)
