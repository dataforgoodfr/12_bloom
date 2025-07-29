{% macro __init_dbt_trawl_watch__init_all() %}

    {{ log('INIT >>> Running macro: _init_reinit_schemas_from_config', info=True) }}
    {% call statement('init_schemas', fetch_result=False) %}
        {{ reinit_schemas_with_grants(cascade=true) }} 
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT <<< _init_reinit_schemas_from_config DONE', info=True) }}


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


    {{ log('INIT >>> Running macro: _init_dbt_trawl_watch__enforce_incremental_tables_reset', info=True) }}
    {% call statement('enforce_incremental_tables_reset', fetch_result=False) %}
        -- Réinitialisation des tables incrémentales
        CALL utils.dbt_initialize_incremental_tables();
    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT <<< _init_dbt_trawl_watch__enforce_incremental_tables_reset DONE', info=True) }}
    
{% endmacro %}
