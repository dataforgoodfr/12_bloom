# Liste et description des traitements batch

 * `src/bloom/tasks/load_spire_data_from_api.py`: Appel l'API Spire et enregistre les données AIS receuillies dans la table `spire_ais_data`
   * le paramètre `-d <dump_path>` permet de stocker la réponse SPIRE dans un fichier JSON. Dans ce cas la réponse n'est pas enregistrée en base. Cas d'usage: récupération de jeu de données SPIRE depuis la production.
 * `src/bloom/tasks/load_spire_data_from_json.py`: Lit un fichier JSON et enregistre les données AIS receuillies dans la table `spire_ais_data`
 * `src/bloom/tasks/load_port_data_from_csv.py`: Charge dans la table `dim_port` les données provenant d'un fichier csv au format `url;country;port;locode;latitude;longitude;geometry_point`
 *  `src/bloom/tasks/compute_port_geometry_buffer.py`: Calcule la zone tampon autour des ports stockées en base et pour lesquels cette zone n'est pas encore calculée
 * `src/bloom/tasks/convert_spire_vessels_to_spire_ais_data.py`: convertit les données de l'ancienne table `spire_vessel_positions` et les charge dans la table `spire_ais_data`.