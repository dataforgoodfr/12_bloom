-- trawl_watch_generate_all_pg_functions.sql
/*
    These 3 dbt macros are useful to initialize Trawl Watch dbt projet : 
        - __init_dbt_trawl_watch__init_all() : drop and creates the schemas required for the project, and grants all rights to the user defined in POSTGRES_USER environment variable.
          To call it : >> dbt run-operation __init_dbt_trawl_watch__init_all
        - _init_dbt_trawl_watch__generate_all_pg_functions() : creates in PostgreSQL all the functions and stored procedures required for the proper functioning of the project.
          To call it : >> dbt run-operation _init_dbt_trawl_watch__generate_all_pg_functions
        - _init_dbt_trawl_watch__enforce_incremental_tables_reset() : [USE WITH CAUTION] drop all incremental tables in the project + recreates partitionned tables
          To call it : >> dbt run-operation _init_dbt_trawl_watch__enforce_incremental_tables_reset
*/



{# macros/_init/_init_trawl_watch_generate_all_pg_functions.sql #}
{% macro _init_dbt_trawl_watch__generate_all_pg_functions() %}

    {% call statement('generate_partitionning_functions', fetch_result=False) %}
        {{ _init_generate_paritionning_functions() }}
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('...INIT >>> Partitionning functions created or updated', info=True) }}

    {% call statement('create_util_functions', fetch_result=False) %}
        {{ _init_create_util_functions() }}
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('...INIT >>> Utils functions created or updated', info=True) }}

    {% call statement('admin_tables', fetch_result=False) %}
        {{ _init_create_admin_tables() }}
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('...INIT >>> Admin schema & tables for database monitoring', info=True) }}

    {% call statement('initialize_incremental_tables', fetch_result=False) %}
        {{ _init_proc_incremental_tables() }}
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('...INIT >>> Useful functions and procedures for dbt_trawl_watch initialization.', info=True) }}

{% endmacro %}

{% macro _init_generate_paritionning_functions() %}
    /*************** [ CREATION DES FONCTIONS DE GESTION DES TABLES PARTITIONNEES ] ****************/
        -- staging.stg_vessel_positions
        {{ _init__manage_stg_vessel_positions() }}
        {{ _init__ensure_stg_vessel_positions_future_partitions() }}

        -- itm.itm_vessel_positions
        {{ _init__manage_itm_vessel_positions() }}
        {{ _init__ensure_itm_vessel_positions_future_partitions() }}

        -- itm.itm_vessel_segments
        {{ _init__manage_itm_vessel_segments() }}
        {{ _init__ensure_itm_vessel_segments_future_partitions() }}
 {% endmacro %}

{% macro _init_create_util_functions() %}
    /**************** [ FONCTIONS UTILITAIRES] ***********************/
        /* ---- utils.analyze_table_onlimit ---------------------------------------------------------- */
        {{ pguf__analyze_table_onlimit() }}
        /* ---- utils.array_diff ---------------------------------------------------- */
        {{ pguf__array_diff() }}
        /* ----- utils.array_distinct ------------------------------------------------- */ 
        {{ pguf__array_distinct() }}
        /* ----- utils.array_dmerge ------------------------------------------------- */ 
        {{ pguf__array_dmerge() }}
        /* ----- utils.array_in_both ------------------------------------------------- */
        {{ pguf__array_in_both() }}
        /* ----- utils.array_concat_uniq_agg ----------------------------------------- */
        {{ pguf__array_concat_uniq_agg() }}
        /* ---- utils.array_intersect_agg ---------------------------------------------------- */
        {{ pguf__array_intersect_agg() }}
        /* ---- utils.safe_between ---------------------------------------------------- */
        {{ pguf__safe_between() }}
        /* ---- utils.coalesce_json ---------------------------------------------------- */
        {{ pguf__jsonb_coalesce() }}
        /* ---- utils.count_rows ---------------------------------------------------- */
        {{ pguf__count_rows() }}
        /* ---- utils.get_excursion_details ---------------------------------------------------- */
        {{ pguf__get_excursion_details() }}
        
{% endmacro %}

{% macro _init_create_admin_tables() %}
        /* ---- create_admin_tables  ---------------------------------------------------- */
        {{ create_admin_tables() }}
{% endmacro %}

{% macro _init_proc_incremental_tables() %}
        {{ init__initialize_incremental_tables() }}
{% endmacro %}

