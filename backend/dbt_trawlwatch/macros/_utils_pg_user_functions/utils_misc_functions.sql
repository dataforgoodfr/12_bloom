/* ---- utils.count_rows ---------------------------------------------------- */
{% macro pguf__count_rows() %}
    -- Compte le nombre de lignes dans une table spécifiée par son schéma et son nom
    DROP FUNCTION IF EXISTS utils.count_rows(text, text);
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
{% endmacro %}

/* ---- utils.analyze_table_onlimit ---------------------------------------------------------- */
{% macro pguf__analyze_table_onlimit() %}
    -- Exécute un EXPLAIN ANALYZE sur une table avec un LIMIT paramétré
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
{% endmacro %}

{% macro pguf__get_excursion_details() %}
drop function if exists utils.get_excursion_details( varchar, timestamptz, timestamptz);
create or replace function utils.get_excursion_details(
    _vessel_id varchar,
    _start_ts timestamptz,
    _end_ts timestamptz
)
returns table (
    position_ids varchar[],
    positions_count int,
    last_position_checked timestamptz,
    excursion_line geometry,
    excursion_line_metrics geometry
)
language sql
as
$$
    select 
        array_agg(position_id order by position_timestamp),
        count(*)::int,
        max(position_timestamp),
        st_makeline(array_agg(position_point order by position_timestamp)),
        st_transform(st_makeline(array_agg(position_point order by position_timestamp)), 3857)
    from itm.itm_vessel_positions
    where vessel_id = _vessel_id
      and position_timestamp between _start_ts and _end_ts
      and position_point is not null;
$$;
ALTER FUNCTION utils.get_excursion_details(varchar, timestamptz, timestamptz)
        OWNER TO ulf7g0ewqes1svjic5qf;
{% endmacro %}