{% macro _init_dbt_trawl_watch__enforce_incremental_tables_reset() %}
{# Réinitialise des tables incrémentales #}
    {% call statement('reset_incremental_tables', fetch_result=False) %}

    -- Réinitialisation des tables incrémentales
    CALL utils.dbt_initialize_incremental_tables();

    {% endcall %}
    {% do adapter.commit() %} 
    {{ log('INIT >>> Incremental tables reset completed.', info=True) }}
{% endmacro %}