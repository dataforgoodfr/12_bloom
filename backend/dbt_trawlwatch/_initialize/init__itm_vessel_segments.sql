/*
    Script : Crée ou met à jour la table `itm.itm_vessel_segments` avec un partitionnement **mensuel**.
    usage : "SELECT itm.manage_itm_vessel_segments_partitions(2023, 2026, false);" pour créer les partitions de 2023 à 2026 sans reconstruire la table.
    ATTENTION : si vous lancez la fonction avec `full_rebuild = TRUE`, la table sera supprimée puis recréée.
*/

----------------------------- FUNCTION: itm.manage_itm_vessel_segments_partitions(integer, integer, boolean) -----------------------------
/*
    Cette fonction gère les partitions mensuelles de la table de itm des segments construits à partir des positions successives des navires en excursion.

    Paramètres :
        - start_year   : année de début du partitionnement (inclus).
        - end_year     : année de fin du partitionnement (inclus).
        - full_rebuild : TRUE  → drop + recréation complète ;
                         FALSE → création uniquement des partitions manquantes.

    Retour : void
*/
-- DROP FUNCTION IF EXISTS itm.manage_itm_vessel_segments_partitions(integer, integer, boolean);

/*  PG‑15 : un seul CREATE INDEX sur la table parent suffit ; les index enfants sont créés automatiquement. */
CREATE OR REPLACE FUNCTION itm.manage_itm_vessel_segments_partitions(
        start_year   INT,
        end_year     INT,
        full_rebuild BOOLEAN DEFAULT FALSE)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    y  INT;
    m  INT;
    partition_name TEXT;
    value_label    TEXT;
    owner_name     TEXT := 'ulf7g0ewqes1svjic5qf';
    base_table     TEXT := 'itm_vessel_segments';
    qualified      TEXT := 'itm.itm_vessel_segments';
BEGIN
    /* 1. (Re)création de la table parent ---------------------------------------------------------- */
    IF full_rebuild THEN
        RAISE NOTICE 'Full rebuild activé → DROP TABLE %', qualified;
        EXECUTE format('DROP TABLE IF EXISTS %s CASCADE;', qualified);
    END IF;

    EXECUTE format($ddl$
        CREATE TABLE IF NOT EXISTS %s (
            segment_id VARCHAR NOT NULL,
            excursion_id VARCHAR NOT NULL,
            vessel_id VARCHAR NOT NULL,

            segment_start_at TIMESTAMPTZ,
            segment_end_at TIMESTAMPTZ,

            segment_duration INTERVAL,
            segment_duration_s BIGINT,
            segment_duration_h DOUBLE PRECISION,

            segment_course DOUBLE PRECISION,
            segment_distance_m DOUBLE PRECISION,
            segment_distance_nm DOUBLE PRECISION,

            segment_average_speed DOUBLE PRECISION,
            segment_course_speed DOUBLE PRECISION,

            segment_type VARCHAR,

            zone_ids VARCHAR[],
            zone_categories VARCHAR[],
            zone_sub_categories VARCHAR[],

            zone_ids_prev VARCHAR[],
            zone_categories_prev  VARCHAR[],
            zone_sub_categories_prev  VARCHAR[],
            
            zones_entered  VARCHAR[],
            zones_exited VARCHAR[],
            zones_crossed VARCHAR[],

            is_in_amp_zone BOOLEAN DEFAULT NULL,
            is_in_territorial_waters BOOLEAN DEFAULT NULL,
            is_in_zone_with_no_fishing_rights  BOOLEAN DEFAULT NULL,

            is_last_vessel_segment BOOLEAN DEFAULT NULL,
                        
            segment_speed_at_start DOUBLE PRECISION,
            segment_speed_at_end DOUBLE PRECISION,

            segment_heading_at_start DOUBLE PRECISION,
            segment_heading_at_end DOUBLE PRECISION,

            segment_course_at_start DOUBLE PRECISION,
            segment_course_at_end DOUBLE PRECISION,

            segment_rot_at_start DOUBLE PRECISION, -- Taux de rotation AIS à la position de début du segment
            segment_rot_at_end DOUBLE PRECISION, -- Taux de rotation AIS à la position de

            segment_ends_at_month VARCHAR NOT NULL,
            segment_ends_at_day DATE NOT NULL,
            segment_created_at TIMESTAMPTZ DEFAULT now(),
            position_ais_created_at TIMESTAMPTZ, -- Date de création de la dernière position AIS à l'origine du segment, utilisée par les modèles microbatch

            segment_position_start GEOMETRY(Point, 4326),
            segment_position_end GEOMETRY(Point, 4326),
            segment_line GEOMETRY(LineString, 4326),

            CONSTRAINT %I_pkey PRIMARY KEY (segment_id, segment_ends_at_month)
        ) PARTITION BY LIST (segment_ends_at_month);
    $ddl$, qualified, base_table);

    EXECUTE format('ALTER TABLE %s OWNER TO %I;', qualified, owner_name);
    EXECUTE format('GRANT ALL ON TABLE %s TO %I;', qualified, owner_name);

    /* 2. Index « parent »  (crée automatiquement les index enfants) ------------------------------ */
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_seg_id                     ON '||qualified||' (segment_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_excursion_id               ON '||qualified||' (excursion_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_vessel_id                  ON '||qualified||' (vessel_id)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_start_at           ON '||qualified||' USING brin(segment_start_at)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_end_at             ON '||qualified||' (segment_end_at)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_duration           ON '||qualified||' (segment_duration)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_ends_at_day      ON '||qualified||' USING brin(segment_ends_at_day)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_type               ON '||qualified||' (segment_type)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_zone_ids          ON '||qualified||' (zone_ids)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_zone_categories   ON '||qualified||' (zone_categories)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_zone_sub_categories ON '||qualified||' (zone_sub_categories)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_is_in_amp_zone    ON '||qualified||' (is_in_amp_zone)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_is_in_territorial_waters ON '||qualified||' (is_in_territorial_waters)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_is_in_zone_with_no_fishing_rights ON '||qualified||' (is_in_zone_with_no_fishing_rights)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_is_last_vessel_segment ON '||qualified||' (is_last_vessel_segment)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_position_start ON '||qualified||'  USING gist(segment_position_start)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_position_end ON '||qualified||'  USING gist(segment_position_end)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_segment_line ON '||qualified||'  USING gist(segment_line)';

    /* 3. Création des partitions manquantes ------------------------------------------------------ */
    FOR y IN start_year..end_year LOOP
        FOR m IN 1..12 LOOP
            partition_name := format('%s_%s%s', base_table, y, lpad(m::text, 2, '0'));  -- ex. itm_vessel_positions_202401
            value_label    := format('%s%s', y, lpad(m::text, 2, '0'));                 -- ex. 202401

            EXECUTE format(
              'CREATE TABLE IF NOT EXISTS itm.%I
                     PARTITION OF %s
                     FOR VALUES IN (%L);',
              partition_name, qualified, value_label);

            EXECUTE format('ALTER TABLE itm.%I OWNER TO %I;', partition_name, owner_name);
        END LOOP;
    END LOOP;
END;
$$;

ALTER FUNCTION itm.manage_itm_vessel_segments_partitions
    OWNER TO ulf7g0ewqes1svjic5qf;


------------------------- FUNCTION: itm.ensure_itm_vessel_segments_future_partitions() -------------------------
/*
    Assure que les partitions mensuelles de l’année courante et de l’année suivante existent.
    Appelée (hook) par le modèle itm.itm_vessel_positions.
*/
-- DROP FUNCTION IF EXISTS itm.ensure_itm_vessel_segments_future_partitions();

CREATE OR REPLACE FUNCTION itm.ensure_itm_vessel_segments_future_partitions()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    this_year INT := EXTRACT(YEAR FROM now());
BEGIN
    -- on crée/complète les partitions de l’année en cours et de l’année prochaine
    PERFORM itm.manage_itm_vessel_segments_partitions(this_year, this_year + 1, FALSE);
END;
$$;

ALTER FUNCTION itm.ensure_itm_vessel_segments_future_partitions()
    OWNER TO ulf7g0ewqes1svjic5qf;
