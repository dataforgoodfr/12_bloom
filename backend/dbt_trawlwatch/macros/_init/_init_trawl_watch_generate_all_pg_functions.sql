-- trawl_watch_generate_all_pg_functions.sql
/*
    These 2 dbt macros are useful to initialize Trawl Watch dbt projet : 
        - _init_dbt_trawl_watch__generate_all_pg_functions() : creates in PostgreSQL all the functions and stored procedures required for the proper functioning of the project.
          To call it : >> dbt run-operation _init_dbt_trawl_watch__generate_all_pg_functions
        - _init_dbt_trawl_watch__enforce_incremental_tables_reset() : [USE WITH CAUTION] drop all incremental tables in the project + recreates partitionned tables
          To call it : >> dbt run-operation _init_dbt_trawl_watch__enforce_incremental_tables_reset
*/

{# macros/_init/_init_trawl_watch_generate_all_pg_functions.sql #}
{% macro _init_dbt_trawl_watch__generate_all_pg_functions() %}

    {% call statement('generate_partitionning_functions', fetch_result=False) %}

    -- Schéma utilitaire -----------------------------------------------------------------
    CREATE SCHEMA IF NOT EXISTS utils;

    /*************************************************** [ CREATION DES FONCTIONS DE GESTION DES TABLES PARTITIONNEES ] ***************************************************/


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
                            position                        GEOMETRY(Point,4326),
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
                    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stg_pos_geom                   ON '||qualified||' USING gist(position)';
            
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

        ----------------------------- FUNCTION: itm.manage_itm_vessel_positions_partitions(integer, integer, boolean) -----------------------------
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
                    position_id_prev                 VARCHAR,
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
                    position_itm_created_at TIMESTAMPTZ DEFAULT now(), -- Date de création de la position dans la base de données (cette table)

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



        ----------------------------- FUNCTION: itm.manage_itm_vessel_segments_partitions(integer, integer, boolean) -----------------------------
        /*
            Cette fonction gère les partitions mensuelles de la table de itm des segments construits à partir des positions successives des navires en excursion.

            Paramètres :
                - start_year   : année de début du partitionnement (inclus).
                - end_year     : année de fin du partitionnement (inclus).
                - full_rebuild : TRUE  → drop + recréation complète ;
                                FALSE → création uniquement des partitions manquantes.

            Retour : void

            Contexte : Crée les partitions de `itm.manage_itm_vessel_segments` pour la période entre les 2 années (comprises) passées en paramètres.
            usage : "SELECT itm.manage_itm_vessel_segments_partitions(2023, 2026, false);" pour créer les partitions de 2023 à 2026 sans reconstruire la table.
            Attention : si vous lancez la fonction avec `full_rebuild = TRUE`, la table sera supprimée puis recréée.

        */
        DROP FUNCTION IF EXISTS itm.manage_itm_vessel_segments_partitions(integer, integer, boolean);

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
        DROP FUNCTION IF EXISTS itm.ensure_itm_vessel_segments_future_partitions();

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

    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT >>> Partitionning functions created or updated', info=True) }}



    /*************************************************************** [ FONCTIONS UTILITAIRES] *************************************************/
    {% call statement('create_util_fonctions', fetch_result=False) %}

    /* ---- utils.analyze_table_onlimit ---------------------------------------------------------- */
    DROP FUNCTION IF EXISTS utils.analyze_table_onlimit(text, text, integer);
    CREATE OR REPLACE FUNCTION utils.analyze_table_onlimit(
        in_schema_name text,
        in_table_name text,
        row_limit integer)
        RETURNS TABLE(schema_name text, table_name text, total_execution_time_ms double precision, estimated_total_cost_ms double precision, analyze_json json) 
        LANGUAGE 'plpgsql'
        COST 100
        VOLATILE PARALLEL UNSAFE
        ROWS 1000

    AS $BODY$
    DECLARE
        explain_result json;
    BEGIN
        -- Exécuter l'explain analyze en format JSON avec LIMIT paramétré
        EXECUTE format(
            'EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM %I.%I LIMIT %s',
            in_schema_name,
            in_table_name,
            row_limit
        )
        INTO explain_result;

        -- Retourner le résultat
        RETURN QUERY
        SELECT
            in_schema_name::text as schema_name,
            in_table_name::text as table_name,
            (explain_result->0->>'Execution Time')::double precision,
            (explain_result->0->'Plan'->>'Total Cost')::double precision,
            explain_result;
    END;
    $BODY$;

    ALTER FUNCTION utils.analyze_table_onlimit(text, text, integer)
        OWNER TO ulf7g0ewqes1svjic5qf;

    /* ---- utils.array_diff ---------------------------------------------------- */
    DROP FUNCTION IF EXISTS utils.array_diff(anyarray, anyarray);
    CREATE OR REPLACE FUNCTION utils.array_diff(
        a1 anyarray,
        a2 anyarray)
        RETURNS anyarray
        LANGUAGE 'sql'
        COST 100
        IMMUTABLE PARALLEL UNSAFE
    AS $BODY$
        SELECT ARRAY(
            SELECT unnest(a1)
            EXCEPT
            SELECT unnest(a2)
        )
    $BODY$;

    ALTER FUNCTION utils.array_diff(anyarray, anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf;

    /* ----- utils.array_distinct ------------------------------------------------- */ 
    DROP FUNCTION IF EXISTS utils.array_distinct(anyarray);
    CREATE FUNCTION utils.array_distinct(anyarray) RETURNS anyarray AS $f$
        SELECT array_agg(DISTINCT x) FROM unnest($1) t(x);
    $f$ LANGUAGE SQL IMMUTABLE;
    ALTER FUNCTION utils.array_distinct(anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf; 

    /* ----- utils.array_dmerge ------------------------------------------------- */ 
    DROP FUNCTION IF EXISTS utils.array_dmerge(anyarray, anyarray);
    CREATE OR REPLACE FUNCTION utils.array_dmerge(
        a1 anyarray,
        a2 anyarray)
        RETURNS anyarray AS $f$
        
            SELECT utils.array_distinct( array_cat( a1, a2) )
    $f$ LANGUAGE 'sql'
    COST 100
    IMMUTABLE PARALLEL UNSAFE;
    ALTER FUNCTION utils.array_dmerge(anyarray, anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf;  
    /* ----- utils.array_in_both ------------------------------------------------- */
    DROP FUNCTION IF EXISTS utils.array_in_both(anyarray, anyarray);
    CREATE OR REPLACE FUNCTION utils.array_in_both(
        a1 anyarray,
        a2 anyarray)
        RETURNS boolean
        LANGUAGE 'sql'
        COST 100
        IMMUTABLE PARALLEL UNSAFE
    AS $BODY$
        SELECT EXISTS (
            SELECT 1
            FROM unnest(a1) AS x
            WHERE x = ANY(a2)
        );
    $BODY$;
    ALTER FUNCTION utils.array_in_both(anyarray, anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf;

    /* ----- utils.array_concat_uniq_agg ----------------------------------------- */
    DROP AGGREGATE IF EXISTS utils.array_concat_uniq_agg(anyarray);
    DROP FUNCTION IF EXISTS utils.array_concat_uniq_agg_transfn(anyarray, anyarray);
    CREATE OR REPLACE FUNCTION utils.array_concat_uniq_agg_transfn(acc anyarray, val anyarray)
    RETURNS anyarray
    LANGUAGE SQL
    AS $$
    SELECT array_agg(DISTINCT e)
    FROM unnest(COALESCE(acc, '{}') || COALESCE(val, '{}')) AS t(e)
    $$;

    CREATE AGGREGATE utils.array_concat_uniq_agg(anyarray) (
    SFUNC = utils.array_concat_uniq_agg_transfn,
    STYPE = anyarray,
    INITCOND = '{}'
    );
    ALTER AGGREGATE utils.array_concat_uniq_agg(anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf;

    /* ---- utils.safe_between ---------------------------------------------------- */
    DROP FUNCTION IF EXISTS utils.safe_between(TIMESTAMP, TIMESTAMP, TIMESTAMP);

    CREATE OR REPLACE FUNCTION utils.safe_between(
        -- RETURNS TRUE IF : (start_ts=NULL, end_ts=NULL) | (start_ts=NULL,<=end_ts) | (>=start_ts, end_ts=NULL) | (>=start_ts, <=end_ts)
        value_ts TIMESTAMP,
        start_ts TIMESTAMP,
        end_ts TIMESTAMP
    )
    RETURNS BOOLEAN AS $$
    DECLARE
        adjusted_end_ts TIMESTAMP;
    BEGIN
        -- Ajuste end_ts si l'utilisateur a passé un "end of day" implicite (ex : '2025-07-31'::date)
        IF end_ts IS NOT NULL AND end_ts::time = '00:00:00' THEN
            adjusted_end_ts := end_ts + interval '1 day' - interval '1 microsecond';
        ELSE
            adjusted_end_ts := end_ts;
        END IF;

        IF start_ts IS NULL AND adjusted_end_ts IS NULL THEN
            RETURN TRUE;
        ELSIF start_ts IS NULL THEN
            RETURN value_ts <= adjusted_end_ts;
        ELSIF adjusted_end_ts IS NULL THEN
            RETURN value_ts >= start_ts;
        ELSE
            RETURN value_ts BETWEEN start_ts AND adjusted_end_ts;
        END IF;
    END;
    $$ LANGUAGE plpgsql;

    ALTER FUNCTION utils.safe_between(TIMESTAMP, TIMESTAMP, TIMESTAMP)
        OWNER TO ulf7g0ewqes1svjic5qf;

    /* ---- utils.coalesce_json ---------------------------------------------------- */
    DROP FUNCTION IF EXISTS utils.jsonb_coalesce(json, json);
    CREATE OR REPLACE FUNCTION utils.jsonb_coalesce(priority_json JSONB, fallback_json JSONB)
    RETURNS JSONB AS $$
    DECLARE
        merged_json JSONB;
        key TEXT;
    BEGIN
        merged_json = fallback_json;
        FOR key IN SELECT jsonb_object_keys(priority_json)
        LOOP
            merged_json = merged_json || jsonb_build_object(key, priority_json->>key);
        END LOOP;
        RETURN merged_json;
    END;
    $$ LANGUAGE plpgsql;
    ALTER FUNCTION utils.jsonb_coalesce(JSONB, JSONB)
        OWNER TO ulf7g0ewqes1svjic5qf;

    /* ---- utils.count_rows ---------------------------------------------------- */
    CREATE OR REPLACE FUNCTION utils.count_rows(
        schema_name text,
        table_name text)
        RETURNS bigint
        LANGUAGE 'plpgsql'
        COST 100
        VOLATILE PARALLEL UNSAFE
    AS $BODY$
    DECLARE
        result bigint;
    BEGIN
        EXECUTE format('SELECT COUNT(*) FROM %I.%I', schema_name, table_name) INTO result;
        RETURN result;
    END;
    $BODY$;

    ALTER FUNCTION utils.count_rows(text, text)
        OWNER TO ulf7g0ewqes1svjic5qf;

    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT >>> Utils functions created or updated', info=True) }}

    {% call statement('admin_tables', fetch_result=False) %}
            /* -------------------------------------------------------------------------
        Vue : admin.heaviest_objects
        - Détail : toutes les partitions, indexes, TOAST…
        - Agrégats : taille cumulée d’une table partitionnée (+ indexes),
                        taille cumulée d’un index partitionné.
        ------------------------------------------------------------------------- */
        create schema if not exists admin;

        create or replace view admin.heaviest_objects as
        with relsizes as (
            /* Taille de chaque relation utilisateur (octets) */
            select
                c.oid,
                n.nspname                as schema_name,
                c.relname                as object_name,
                c.relkind,
                pg_total_relation_size(c.oid) as total_bytes
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where n.nspname not in ('pg_catalog','information_schema')
        ),

        /* --------------------------------------------------------------------- *
        * 1. Lignes DÉTAILLÉES : chaque partition, index, toast, etc.           *
        * --------------------------------------------------------------------- */
        details as (
            select
                case
                    when relkind = 'p'            then 'table_parent'
                    when relkind = 'r'            then 'table_partition_or_simple'
                    when relkind = 'i'            then 'index'
                    when relkind = 'I'            then 'index_parent'
                    when relkind = 't'            then 'toast'
                    else relkind::text
                end                             as object_type,
                schema_name,
                object_name,
                pg_size_pretty(total_bytes)     as total_size,
                total_bytes
            from relsizes
        ),

        /* --------------------------------------------------------------------- *
        * 2. Agrégat TABLE partitionnée  (relkind = 'p')                        *
        *    somme = toutes les partitions + leurs indexes + toast éventuels    *
        * --------------------------------------------------------------------- */
        table_agg as (
            select
                'partitioned_table'           as object_type,
                parent.schema_name,
                parent.object_name,
                pg_size_pretty(sum(child.total_bytes)) as total_size,
                sum(child.total_bytes)         as total_bytes
            from relsizes parent
            join pg_inherits    i  on i.inhparent = parent.oid          -- enfant → table
            join relsizes child on child.oid   = i.inhrelid
            where parent.relkind = 'p'
            group by parent.schema_name, parent.object_name
        ),

        /* --------------------------------------------------------------------- *
        * 3. Agrégat INDEX partitionné (relkind = 'I')                          *
        *    somme = tous les index-fils physiques                              *
        * --------------------------------------------------------------------- */
        index_agg as (
            select
                'partitioned_index'           as object_type,
                parent.schema_name,
                parent.object_name,
                pg_size_pretty(sum(child.total_bytes)) as total_size,
                sum(child.total_bytes)         as total_bytes
            from relsizes parent
            join pg_inherits    i  on i.inhparent = parent.oid          -- enfant → index
            join relsizes child on child.oid   = i.inhrelid
            where parent.relkind = 'I'         -- racine d’index partitionné
            group by parent.schema_name, parent.object_name
        )
        select * from (
            select * from details
            union all
            select * from table_agg
            union all
            select * from index_agg
            order by total_bytes desc
        ) a  where total_bytes > 261000000 -- env. 250 Mo
        order by total_bytes desc;
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT >>> Admin schema & tables for database monitoring', info=True) }}

    {% call statement('initialize_incremental_tables', fetch_result=False) %}
    -- Création d'une procédure pour réinitialiser les tables incrémentales
    DROP PROCEDURE IF EXISTS utils.dbt_initialize_incremental_tables();

    CREATE OR REPLACE PROCEDURE utils.dbt_initialize_incremental_tables()
    LANGUAGE plpgsql
    AS $$
    BEGIN
        ----------------------------------------------------------------
        -- 1) Tables incrémentales non partitionnées
        ----------------------------------------------------------------
        RAISE NOTICE 'Suppression des tables non partitionnées…';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_positions_x_zones CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_excursions CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_excursions_details CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_zones_x_excursions_list CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_segments_by_date CASCADE;';

        ----------------------------------------------------------------
        -- 2) Tables partitionnées : appel aux fonctions de gestion
        ----------------------------------------------------------------
        RAISE NOTICE 'Réinitialisation des partitions…';
        PERFORM staging.manage_stg_vessel_positions_partitions(2024, 2026, true);
        PERFORM itm.manage_itm_vessel_positions_partitions(2023, 2026, true);
        PERFORM itm.manage_itm_vessel_segments_partitions(2023, 2026, true);

        
    END;
    $$;
    ALTER PROCEDURE utils.dbt_initialize_incremental_tables()
        OWNER TO ulf7g0ewqes1svjic5qf;

    
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT >>> Useful functions and procedures for dbt_trawl_watch initialized.', info=True) }}

{% endmacro %}

------------------------------------------------------------------------------------------

{% macro _init_dbt_trawl_watch__enforce_incremental_tables_reset() %}
    {% call statement('reset_incremental_tables', fetch_result=False) %}

    -- Réinitialisation des tables incrémentales
    CALL utils.dbt_initialize_incremental_tables();

    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT >>> Incremental tables reset completed.', info=True) }}
{% endmacro %}

-------------------------------------------------------------------------------------------
