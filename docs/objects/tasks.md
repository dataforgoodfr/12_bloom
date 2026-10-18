# Liste et description des traitements batch

Liste et description des traitements disponibles dans le répertoire `src/bloom/tasks/`:

* `load_spire_data_from_api.py`: Appel l'API Spire et enregistre les données AIS recueillies dans la
  table `spire_ais_data`
    * le paramètre `-d <dump_path>` permet de stocker la réponse SPIRE dans un fichier JSON. Dans ce cas la réponse
      n'est pas enregistrée en base. Cas d'usage: récupération de jeu de données SPIRE depuis la production.
* `load_spire_data_from_json.py`: Lit un fichier JSON et enregistre les données AIS recueillies dans la
  table `spire_ais_data`
* `load_dim_port_from_csv.py`: Charge dans la table `dim_port` les données provenant d'un fichier csv au
  format `url;country;port;locode;latitude;longitude;geometry_point`
* `compute_port_geometry_buffer.py`: Calcule la zone tampon autour des ports stockées en base et pour lesquels cette
  zone n'est pas encore calculée
* `convert_spire_vessels_to_spire_ais_data.py`: convertit les données de l'ancienne table `spire_vessel_positions` et
  les charge dans la table `spire_ais_data`.
* `load_dim_vessel_from_csv.py`: Charge le contenu d'un fichier CSV dans la table `dim_vessel`. Le format du fichier CSV
  attendu
  est `country_iso3;cfr;IMO;registration_number;external_marking;ship_name;ircs;mmsi;loa;type;mt_activated;comment`
* `load_dim_zone_amp_from_csv.py`: Charge le contenu d'un fichier CSV des AMP dans la table `dim_zone`. Le format
  attendu
  est `"index","WDPAID","name","DESIG_ENG","DESIG_TYPE","IUCN_CAT","PARENT_ISO","ISO3","geometry","Benificiaries"`.
* `update_vessel_data_voyage.py`: alimente les tables des données statiques (`vessel_data`) et de
  voyage (`vessel_voyage`) à partir des données AIS.
* `clean_positions.py` : filtre les données ajoutées dans `spire_ais_data `depuis la dernière exécution et alimente
  la table des positions (`vessel_positions`). Par défaut le traitement traite les données SPIRE ajoutées sur une
  période  
  de 7 jours depuis la dernière exécution. Il est possible de modifier cet interval avec l'argument -b suivi d'un
  nombre de jours. Les données spire sont nettoyées et stockées dans la table `vessel_positions`.
* `create_update_excursions_segments.py`: traite les données ajoutées dans la table `vessel_positions` depuis la
  dernière exécution.
    * le traitement détecte les excursions et créé les segments à partir des positions.
    * le traitement créé une association avec chaque zone (AMP, ...) avec laquelle le segment a une intersection
    * met à jour les indicateurs du segment indiquant s'il est dans une AMP, zone cotière ou eaux territoriales
    * met à jour l'ensemble des durées de chaque excursions.