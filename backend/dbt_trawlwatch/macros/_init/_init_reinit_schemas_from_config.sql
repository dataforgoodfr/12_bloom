{% macro reinit_schemas_with_grants(cascade=true) %}
  {% set schemas = var('dbt_schemas_to_init', []) %}
  {% set grantee = env_var('POSTGRES_USER', 'ulf7g0ewqes1svjic5qf') %}

  {% set statements = [] %}

  {% for schema in schemas %}
    {% set drop_stmt = "drop schema if exists " ~ schema ~ (" cascade" if cascade else "") ~ ";" %}
    {% set create_stmt = "create schema if not exists " ~ schema ~ ";" %}
    {% set grant_stmt = "grant all on schema " ~ schema ~ " to " ~ grantee ~ ";" %}

    {% do statements.append(drop_stmt) %}
    {% do statements.append(create_stmt) %}
    {% do statements.append(grant_stmt) %}
  {% endfor %}

  {{ return(statements | join('\n')) }}
{% endmacro %}
