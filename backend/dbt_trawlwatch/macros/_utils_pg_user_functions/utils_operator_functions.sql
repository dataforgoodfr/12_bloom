/* ---- utils.safe_between ---------------------------------------------------- */
{% macro pguf__safe_between() %}
    DROP FUNCTION IF EXISTS utils.safe_between(TIMESTAMPTZ, TIMESTAMPTZ, TIMESTAMPTZ);

    CREATE OR REPLACE FUNCTION utils.safe_between(
        -- RETURNS TRUE IF : (start_ts=NULL, end_ts=NULL) | (start_ts=NULL,<=end_ts) | (>=start_ts, end_ts=NULL) | (>=start_ts, <=end_ts)
        value_ts TIMESTAMPTZ,
        start_ts TIMESTAMPTZ,
        end_ts TIMESTAMPTZ
    )
    RETURNS BOOLEAN AS $$
    DECLARE
        adjusted_end_ts TIMESTAMPTZ;
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

    ALTER FUNCTION utils.safe_between(TIMESTAMPTZ, TIMESTAMPTZ, TIMESTAMPTZ)
        OWNER TO ulf7g0ewqes1svjic5qf;
    -- utils.safe_between TS ---------------------------------------------------- */
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
{% endmacro %}

{% macro pguf__jsonb_coalesce() %}
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
{% endmacro %}