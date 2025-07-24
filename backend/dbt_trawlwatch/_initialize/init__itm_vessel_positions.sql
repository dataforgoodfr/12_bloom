/*
    Script : Crée ou met à jour la table `itm.itm_vessel_positions` avec un partitionnement **mensuel**.
    usage : "SELECT itm.manage_itm_vessel_positions_partitions(2024, 2026, false);" pour créer les partitions de 2024 à 2026 sans reconstruire la table.
    ATTENTION : si vous lancez la fonction avec `full_rebuild = TRUE`, la table sera supprimée puis recréée.
*/

----------------------------- FUNCTION: itm.manage_itm_vessel_positions_partitions(integer, integer, boolean) -----------------------------
/*
    Cette fonction gère les partitions mensuelles de la table de itm des positions navires.

    Paramètres :
        - start_year   : année de début du partitionnement (inclus).
        - end_year     : année de fin du partitionnement (inclus).
        - full_rebuild : TRUE  → drop + recréation complète ;
                         FALSE → création uniquement des partitions manquantes.

    Retour : void
*/
-- DROP FUNCTION IF EXISTS itm.manage_itm_vessel_positions_partitions(integer, integer, boolean);

/*  PG‑15 : un seul CREATE INDEX sur la table parent suffit ; les index enfants sont créés automatiquement. */
CREATE OR REPLACE FUNCTION itm.manage_itm_vessel_positions_partitions(
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
    base_table     TEXT := 'itm_vessel_positions';
    qualified      TEXT := 'itm.itm_vessel_positions';
BEGIN
    /* 1. (Re)création de la table parent ---------------------------------------------------------- */
    IF full_rebuild THEN
        RAISE NOTICE 'Full rebuild activé → DROP TABLE %', qualified;
        EXECUTE format('DROP TABLE IF EXISTS %s CASCADE;', qualified);
    END IF;

    EXECUTE format($ddl$
        CREATE TABLE IF NOT EXISTS %s (
            position_id                     VARCHAR          NOT NULL,
            position_id_prev                 INTEGER,
            position_timestamp              TIMESTAMPTZ,
            position_timestamp_prev         TIMESTAMPTZ,
            position_timestamp_day         DATE,
            position_timestamp_month     VARCHAR NOT NULL,

            position_mmsi                   INTEGER,
            vessel_id                       TEXT,
            position_latitude               DOUBLE PRECISION,
            position_longitude              DOUBLE PRECISION,
            position_rot                    DOUBLE PRECISION,
            position_speed                  DOUBLE PRECISION,
            position_course                 DOUBLE PRECISION,
            position_heading                DOUBLE PRECISION,
            
            

            is_last_position            BOOLEAN DEFAULT FALSE,
            is_first_position           BOOLEAN DEFAULT FALSE,

            is_same_position            BOOLEAN DEFAULT FALSE,

            is_in_port                  BOOLEAN DEFAULT FALSE,
            is_same_port                BOOLEAN DEFAULT FALSE,
            port_id                     TEXT,
            port_exited                 TEXT,

            position_status            TEXT DEFAULT 'unknown', -- Statut de la position courante 
            position_status_prev       TEXT DEFAULT 'unknown', -- Statut de la position précédente 
            is_excursion_start          BOOLEAN DEFAULT FALSE,
            is_excursion_end            BOOLEAN DEFAULT FALSE,

            time_diff_s numeric, -- Temps écoulé entre la position courante et la précédente (en secondes)
            time_diff_h numeric, -- Temps écoulé entre la position courante et la précédente (  en heures)
            distance_m numeric, -- Distance euclidienne entre la position courante et la précédente (en mètres)
            distance_km numeric, -- Distance euclidienne entre la position courante et la précédente (en kilomètres)
            distance_mi numeric, -- Distance euclidienne entre la position courante et la précédente (en milles marins)

            position GEOMETRY(Point,4326),
            position_prev GEOMETRY(Point,4326),
            nb_ais_messages INTEGER DEFAULT 1, -- Nombre de messages AIS reçus pour cette position

            CONSTRAINT %I_pkey PRIMARY KEY (position_id, position_timestamp_month)
        ) PARTITION BY LIST (position_timestamp_month);
    $ddl$, qualified, base_table);

    EXECUTE format('ALTER TABLE %s OWNER TO %I;', qualified, owner_name);
    EXECUTE format('GRANT ALL ON TABLE %s TO %I;', qualified, owner_name);

    /* 2. Index « parent »  (crée automatiquement les index enfants) ------------------------------ */
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_id                     ON '||qualified||' (position_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_vessel_id              ON '||qualified||' (vessel_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_mmsi                   ON '||qualified||' (position_mmsi)';
    

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_ts_day      ON '||qualified||' (position_timestamp_day)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_ts_brin         ON '||qualified||' USING brin(position_timestamp)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_vessel_ts              ON '||qualified||' (vessel_id, position_timestamp)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_vessel_ts_day              ON '||qualified||' (vessel_id, position_timestamp_day)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_geom                   ON '||qualified||' USING gist(position)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_position_ids                ON '||qualified||' USING btree(position_id, position_id_prev)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_is_last_position             ON '||qualified||' USING btree(is_last_position)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_is_excursion_start           ON '||qualified||' USING btree(is_excursion_start)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_is_excursion_end             ON '||qualified||' USING btree(is_excursion_end)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_port_id                   ON '||qualified||' USING btree(port_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_port_exited               ON '||qualified||' USING btree(port_exited)';

    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_position_status            ON '||qualified||' USING btree(position_status)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_position_status_prev       ON '||qualified||' USING btree(position_status_prev)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_itm_pos_position_status_evol       ON '||qualified||' USING btree(position_status_prev, position_status)';

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

ALTER FUNCTION itm.manage_itm_vessel_positions_partitions
    OWNER TO ulf7g0ewqes1svjic5qf;


------------------------- FUNCTION: itm.ensure_itm_vessel_positions_future_partitions() -------------------------
/*
    Assure que les partitions mensuelles de l’année courante et de l’année suivante existent.
    Appelée (hook) par le modèle itm.itm_vessel_positions.
*/
-- DROP FUNCTION IF EXISTS itm.ensure_itm_vessel_positions_future_partitions();

CREATE OR REPLACE FUNCTION itm.ensure_itm_vessel_positions_future_partitions()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    this_year INT := EXTRACT(YEAR FROM now());
BEGIN
    -- on crée/complète les partitions de l’année en cours et de l’année prochaine
    PERFORM itm.manage_itm_vessel_positions_partitions(this_year, this_year + 1, FALSE);
END;
$$;

ALTER FUNCTION itm.ensure_itm_vessel_positions_future_partitions()
    OWNER TO ulf7g0ewqes1svjic5qf;
