{% macro init__initialize_incremental_tables() %}    
    -- Création d'une procédure pour réinitialiser les tables incrémentales
    DROP PROCEDURE IF EXISTS utils.dbt_initialize_incremental_tables();

    CREATE OR REPLACE PROCEDURE utils.dbt_initialize_incremental_tables()
    LANGUAGE plpgsql
    AS $$
    BEGIN
        ----------------------------------------------------------------
        -- 1) Tables incrémentales non partitionnées
        ----------------------------------------------------------------
        RAISE NOTICE 'Suppression des tables incrémentales non partitionnées…';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_positions_x_zones CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_excursions CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_excursions_details CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_zones_x_excursions_list CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_segments_by_date CASCADE;';
        EXECUTE 'DROP TABLE IF EXISTS itm.itm_vessel_last_raw_position CASCADE;';

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
{% endmacro %}
