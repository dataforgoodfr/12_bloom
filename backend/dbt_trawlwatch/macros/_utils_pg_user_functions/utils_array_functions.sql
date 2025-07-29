
/* ---- utils.array_diff ---------------------------------------------------- */
{% macro pguf__array_diff() %}
    -- Calcule la différence entre deux tableaux en PostgreSQL (sur une dimension en profondeur)
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
{% endmacro %}

/* ----- utils.array_distinct ------------------------------------------------- */
{% macro pguf__array_distinct() %}
    -- Renvoie les éléments distincts d'un tableau en PostgreSQL
    DROP FUNCTION IF EXISTS utils.array_distinct(anyarray);
    CREATE FUNCTION utils.array_distinct(anyarray) RETURNS anyarray AS $f$
        SELECT array_agg(DISTINCT x) FROM unnest($1) t(x);
    $f$ LANGUAGE SQL IMMUTABLE;
    ALTER FUNCTION utils.array_distinct(anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf; 
{% endmacro %}

/* ----- utils.array_dmerge ------------------------------------------------- */
{% macro pguf__array_dmerge() %}
    -- Fusionne deux tableaux en PostgreSQL, en supprimant les doublons
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
{% endmacro %}

/* ----- utils.array_in_both ------------------------------------------------- */
{% macro pguf__array_in_both() %}
    -- Renvoie l'intersection de 2 tableaux (les éléments présents dans les 2 tableaux).
    DROP FUNCTION IF EXISTS utils.array_in_both(anyarray, anyarray);

    CREATE OR REPLACE FUNCTION utils.array_in_both(
        a1 anyarray,
        a2 anyarray
    )
    RETURNS anyarray
    LANGUAGE sql
    IMMUTABLE
    AS $$
        SELECT
            CASE
                WHEN a1 IS NULL OR a2 IS NULL THEN NULL
                ELSE ARRAY(
                    SELECT DISTINCT e
                    FROM unnest(a1) AS e
                    WHERE e = ANY(a2)
                )
            END
    $$;
    ALTER FUNCTION utils.array_in_both(anyarray, anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf;
{% endmacro %}

/* ----- utils.array_concat_uniq_agg ----------------------------------------- */
{% macro pguf__array_concat_uniq_agg() %}
    -- Permet de concaténer des tableaux présents dans plusieurs lignes en éliminant les doublons.
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
{% endmacro %}

/* ---- utils.array_intersect_agg ---------------------------------------------------- */
{% macro pguf__array_intersect_agg() %}
-- Permet de calculer l'intersection de tableaux présents dans plusieurs lignes (détecter les valeurs présentes partout)
    DROP AGGREGATE IF EXISTS utils.array_intersect_agg(anyarray);
    DROP FUNCTION IF EXISTS utils.array_intersect_agg_transfn(anyarray, anyarray);
    CREATE OR REPLACE FUNCTION utils.array_intersect_agg_transfn(acc anyarray, val anyarray)
    RETURNS anyarray
    LANGUAGE SQL
    AS $$
        SELECT
            CASE
                WHEN val IS NULL THEN acc
                WHEN acc IS NULL THEN val
                ELSE (
                    SELECT array_agg(DISTINCT e)
                    FROM unnest(acc) AS t(e)
                    WHERE e = ANY(val)
                )
            END
    $$;
    CREATE OR REPLACE AGGREGATE utils.array_intersect_agg(anyarray) (
        SFUNC = utils.array_intersect_agg_transfn,
        STYPE = anyarray,
        INITCOND = '{}',
        FINALFUNC_MODIFY = READ_ONLY,
        MFINALFUNC_MODIFY = READ_ONLY
    );
    ALTER AGGREGATE utils.array_intersect_agg(anyarray)
        OWNER TO ulf7g0ewqes1svjic5qf;
{% endmacro %}
