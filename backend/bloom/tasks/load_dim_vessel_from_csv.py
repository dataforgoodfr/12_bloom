from pathlib import Path
from time import perf_counter

import pandas as pd
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.infra.database.errors import DBException
from bloom.logger import logger
from pydantic import ValidationError


def map_to_domain(row: pd.Series) -> Vessel:
    isna = row.isna()
    return Vessel(
        id=int(row["id"]) if not isna["id"] else None,
        mmsi=int(row["mmsi"]) if not isna["mmsi"] else None,
        ship_name=row["ship_name"],
        width=int(row["width"]) if not isna["width"] else None,
        length=int(row["length"]) if not isna["length"] else None,
        country_iso3=row["country_iso3"] if not isna["country_iso3"] else "XXX",
        type=row["type"],
        imo=row["imo"] if not isna["imo"] else None,
        cfr=row["cfr"] if not isna["cfr"] else None,
        external_marking=row["external_marking"] if not isna["external_marking"] else None,
        ircs=row["ircs"] if not isna["ircs"] else None,
        tracking_activated=row["tracking_activated"],
        tracking_status=row["tracking_status"] if not isna["tracking_status"] else None,
        details=row["details"] if not isna["details"] else None,
        length_class=row["length_class"] if not isna["length_class"] else None,
        check=row["check"] if not isna["length_class"] else None,
    )


def run(csv_file_name: str) -> None:
    use_cases = UseCases()
    db = use_cases.db()

    inserted_ports = []
    deleted_ports = []
    try:
        df = pd.read_csv(csv_file_name, sep=",")
        vessels = df.apply(map_to_domain, axis=1)
        with db.session() as session:
            vessel_repository = use_cases.vessel_repository(session)
            ports_inserts = []
            ports_updates = []
            # Pour chaque enregistrement du fichier CSV
            for vessel in vessels:
                if vessel.id and vessel_repository.get_by_id(vessel.id):
                    # si la valeur du champ id n'est pas vide:
                    #     rechercher l'enregistrement correspondant dans la table dim_vessel
                    #     mettre à jour l'enregistrement à partir des données CSV.
                    ports_updates.append(vessel)
                else:
                    # sinon:
                    #     insérer les données CSV dans la table dim_vessel;
                    ports_inserts.append(vessel)
            # Insertions / MAJ en batch
            inserted_ports = vessel_repository.add(ports_inserts)
            vessel_repository.List(ports_updates)

            # En fin de traitement:
            # les enregistrements de la table dim_vessel pourtant un MMSI absent du fichier CSV sont mis à jour
            # avec la valeur tracking_activated=FALSE
            csv_mmsi = list(df['mmsi'])
            deleted_ports = list(
                filter(lambda v: v.mmsi not in csv_mmsi, vessel_repository.list()))
            vessel_repository.set_tracking([v.id for v in deleted_ports], False,
                                           "Suppression logique suite import nouveau fichier CSV")
            # le traitement vérifie qu'il n'existe qu'un seul enregistrement à l'état tracking_activated==True
            # pour chaque valeur distincte de MMSI.
            integrity_errors = vessel_repository.check_mmsi_integrity()
            if not integrity_errors:
                session.commit()
            else:
                logger.error(
                    f"Erreur d'intégrité fonctionnelle, plusieurs bateaux actifs avec le même MMSI: {integrity_errors}")
                session.rollback()
    except ValidationError as e:
        logger.error("Erreur de validation des données de bateau")
        logger.error(e.errors())
    except DBException:
        logger.error("Erreur d'insertion en base")
    logger.info(f"{len(inserted_ports)} bateau(x) créés")
    logger.info(f"{len(ports_updates)} bateau(x) mise à jour ou inchangés")
    logger.info(f"{len(deleted_ports)} bateau(x) désactivés")


if __name__ == "__main__":
    time_start = perf_counter()
    file_name = Path(settings.data_folder).joinpath("./updated_vessels_table.csv")
    logger.info(f"DEBUT - Chargement des données de bateaux depuis le fichier {file_name}")
    run(file_name)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données de bateaux en {duration:.2f}s")
