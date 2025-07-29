{% macro _init__manage_stg_vessel_positions() %}
----------------------------- FUNCTION: staging.manage_stg_vessel_positions_partitions(integer, integer, boolean) -----------------------------
        /*
            Cette fonction gère les partitions mensuelles de la table de staging des positions navires.

            Paramètres :
                - start_year   : année de début du partitionnement (inclus).
                - end_year     : année de fin du partitionnement (inclus).
                - full_rebuild : TRUE  → drop + recréation complète ;
                                FALSE → création uniquement des partitions manquantes.

            Retour : void

            Contexte : Crée les partitions de `staging.stg_vessel_positions` pour la période entre les 2 années (comprises) passées en paramètres.
            usage : "SELECT staging.manage_stg_vessel_positions_partitions(2024, 2026, false);" pour créer les partitions de 2024 à 2026 sans reconstruire la table.
            Attention : si vous lancez la fonction avec `full_rebuild = TRUE`, la table sera supprimée puis recréée.
        */
        DROP FUNCTION IF EXISTS staging.manage_stg_vessel_positions_partitions(integer, integer, boolean);

        /*  PG‑15 : un seul CREATE INDEX sur la table parent suffit ; les index enfants sont créés automatiquement. */
        CREATE OR REPLACE FUNCTION staging.manage_stg_vessel_positions_partitions(
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
                base_table     TEXT := 'stg_vessel_positions';
                qualified      TEXT := 'staging.stg_vessel_positions';
            BEGIN
                /* 1. (Re)création de la table parent ---------------------------------------------------------- */
                IF full_rebuild THEN
                    RAISE NOTICE 'Full rebuild activé → DROP TABLE %', qualified;
                    EXECUTE format('DROP TABLE IF EXISTS %s CASCADE;', qualified);
                END IF;

                EXECUTE format($ddl$
                    CREATE TABLE IF NOT EXISTS %s (
                            position_id                     VARCHAR NOT NULL,
                            position_timestamp              TIMESTAMPTZ,
                            position_mmsi                   INTEGER,
                            vessel_id                       TEXT,
                            position_latitude               DOUBLE PRECISION,
                            position_longitude              DOUBLE PRECISION,
                            position_speed                  DOUBLE PRECISION,
                            position_heading                DOUBLE PRECISION,
                            position_course                 DOUBLE PRECISION,
                            position_rot                    DOUBLE PRECISION,
                            position_timestamp_month   VARCHAR NOT NULL,
                            position_timestamp_day     DATE,
                            position_ais_created_at_min         TIMESTAMPTZ,
                            position_ais_created_at_max         TIMESTAMPTZ,
                            position_stg_created_at TIMESTAMPTZ, -- Date de création de la position dans la base de données (staging)
                            position_point                        GEOMETRY(Point,4326),
                            CONSTRAINT %I_pkey PRIMARY KEY (vessel_id, position_id, position_timestamp_month)
                        ) PARTITION BY LIST (position_timestamp_month);
                    $ddl$, qualified, base_table);

                    EXECUTE format('ALTER TABLE %s OWNER TO %I;', qualified, owner_name);
                    EXECUTE format('GRANT ALL ON TABLE %s TO %I;', qualified, owner_name);

                    /* 2. Index « parent »  (crée automatiquement les index enfants) ------------------------------ */
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_id                     ON '||qualified||' (position_id)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_vessel_id              ON '||qualified||' (vessel_id)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_mmsi                   ON '||qualified||' (position_mmsi)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_vessel_ts              ON '||qualified||' (vessel_id, position_timestamp)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_vessel_ts_day          ON '||qualified||' (vessel_id, position_timestamp_day)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_stg_created_at         ON '||qualified||' (position_stg_created_at)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_timestamp_brin         ON '||qualified||' USING brin(position_timestamp)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_timestamp_brin         ON '||qualified||' USING brin(position_timestamp_day)';
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_geom                   ON '||qualified||' USING gist(position_point)';
            
            /* 3. Création des partitions manquantes ------------------------------------------------------ */
            FOR y IN start_year..end_year LOOP
                FOR m IN 1..12 LOOP
                    partition_name := format('%s_%s%s', base_table, y, lpad(m::text, 2, '0'));  -- ex. stg_vessel_positions_202401
                    value_label    := format('%s%s', y, lpad(m::text, 2, '0'));                 -- ex. 202401

                    EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS staging.%I
                            PARTITION OF %s
                            FOR VALUES IN (%L);',
                    partition_name, qualified, value_label);

                    EXECUTE format('ALTER TABLE staging.%I OWNER TO %I;', partition_name, owner_name);
                END LOOP;
            END LOOP;
        END;
        $$;

        ALTER FUNCTION staging.manage_stg_vessel_positions_partitions
            OWNER TO ulf7g0ewqes1svjic5qf;
{% endmacro%}

{% macro _init__ensure_stg_vessel_positions_future_partitions() %}
------------------------- FUNCTION: staging.ensure_stg_vessel_positions_future_partitions() -------------------------
        /*
            Assure que les partitions mensuelles de l’année courante et de l’année suivante existent.
            Appelée (hook) par le modèle staging.stg_vessel_positions.
        */
                
        DROP FUNCTION IF EXISTS staging.ensure_stg_vessel_positions_future_partitions();

        CREATE OR REPLACE FUNCTION staging.ensure_stg_vessel_positions_future_partitions()
        RETURNS void
        LANGUAGE plpgsql
        AS $$
        DECLARE
            this_year INT := EXTRACT(YEAR FROM now());
        BEGIN
            -- on crée/complète les partitions de l’année en cours et de l’année prochaine
            PERFORM staging.manage_stg_vessel_positions_partitions(this_year, this_year + 1, FALSE);
        END;
        $$;

        ALTER FUNCTION staging.ensure_stg_vessel_positions_future_partitions()
            OWNER TO ulf7g0ewqes1svjic5qf;
{% endmacro %}