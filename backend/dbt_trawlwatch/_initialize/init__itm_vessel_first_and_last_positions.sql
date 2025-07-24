create table if not exists itm.itm_vessel_first_and_last_positions (
    vessel_id                      varchar primary key,
    first_position_timestamp       timestamptz not null,
    first_position_id              bigint      not null,
    first_position_ais_created_at  timestamptz not null,

    last_position_timestamp        timestamptz not null,
    last_position_id               bigint      not null,
    last_position_ais_created_at   timestamptz not null
);

create index if not exists itm_vfl_last_ingest_idx
    on itm.itm_vessel_first_and_last_positions(last_position_ais_created_at);
create index if not exists itm_vfl_vessel_first_pos_ts
    on itm.itm_vessel_first_and_last_positions(vessel_id, first_position_timestamp);
create index if not exists itm_vfl_vessel_last_pos_ts
    on itm.itm_vessel_first_and_last_positions(vessel_id, last_position_timestamp);
create index if not exists itm_vfl_first_pos_id
    on itm.itm_vessel_first_and_last_positions(vessel_id, first_position_id);
create index if not exists itm_vfl_last_pos_id
    on itm.itm_vessel_first_and_last_positions(vessel_id, last_position_id);

-- Rafraîchit les premières / dernières positions
-- pour les enregistrements dont AIS_created_at ∈ [_batch_start, _batch_end]
CREATE OR REPLACE FUNCTION itm.refresh_first_last_positions(
    _batch_start  timestamptz,   -- inclus
    _batch_end    timestamptz    -- inclus
) RETURNS boolean
LANGUAGE plpgsql
AS $func$
DECLARE
    _rows integer := 0;          -- facultatif : ROW_COUNT
BEGIN
    ------------------------------------------------------------------
    -- 1. Limite le périmètre aux positions du batch demandé
    ------------------------------------------------------------------
    WITH bounds AS (
        SELECT  vessel_id,
                first_position_ais_created_at,
                last_position_ais_created_at
        FROM    itm.itm_vessel_first_and_last_positions
    ),
    candidates AS (
        SELECT  p.vessel_id,
                p.position_timestamp,
                p.position_id,
                p.position_ais_created_at
        FROM    staging.stg_vessel_positions p
        LEFT JOIN bounds b USING (vessel_id)
        WHERE   p.position_ais_created_at BETWEEN _batch_start AND _batch_end
        AND    (b.vessel_id IS NULL                                    -- nouveau navire
                OR  p.position_ais_created_at < b.first_position_ais_created_at  -- repousse le min
                OR  p.position_ais_created_at > b.last_position_ais_created_at)  -- repousse le max
    ),
    ------------------------------------------------------------------
    -- 2a. plus ANCIENNE candidate par navire
    ------------------------------------------------------------------
    new_first AS (
        SELECT DISTINCT ON (vessel_id)
            vessel_id,
            position_timestamp,
            position_id,
            position_ais_created_at
        FROM   candidates
        ORDER  BY vessel_id,
                 position_timestamp,
                 position_id
    ),
    ------------------------------------------------------------------
    -- 2b. plus RÉCENTE candidate par navire
    ------------------------------------------------------------------
    new_last AS (
        SELECT DISTINCT ON (vessel_id)
            vessel_id,
            position_timestamp,
            position_id,
            position_ais_created_at
        FROM   candidates
        ORDER  BY vessel_id,
                 position_timestamp DESC,
                 position_id
    )
    ------------------------------------------------------------------
    -- 3. UPSERT conditionnel
    ------------------------------------------------------------------
    INSERT INTO itm.itm_vessel_first_and_last_positions AS tgt
        (vessel_id,
         first_position_timestamp, first_position_id, first_position_ais_created_at,
         last_position_timestamp,  last_position_id,  last_position_ais_created_at)
    SELECT
        COALESCE(f.vessel_id, l.vessel_id),
        COALESCE(f.position_timestamp,      tgt.first_position_timestamp),
        COALESCE(f.position_id,            tgt.first_position_id),
        COALESCE(f.position_ais_created_at, tgt.first_position_ais_created_at),
        COALESCE(l.position_timestamp,      tgt.last_position_timestamp),
        COALESCE(l.position_id,            tgt.last_position_id),
        COALESCE(l.position_ais_created_at, tgt.last_position_ais_created_at)
    FROM new_first f
    FULL JOIN new_last l USING (vessel_id)
    LEFT JOIN itm.itm_vessel_first_and_last_positions tgt USING (vessel_id)
    ON CONFLICT (vessel_id) DO UPDATE
        SET first_position_timestamp      = EXCLUDED.first_position_timestamp,
            first_position_id             = EXCLUDED.first_position_id,
            first_position_ais_created_at = EXCLUDED.first_position_ais_created_at,
            last_position_timestamp       = EXCLUDED.last_position_timestamp,
            last_position_id              = EXCLUDED.last_position_id,
            last_position_ais_created_at  = EXCLUDED.last_position_ais_created_at
        WHERE EXCLUDED.first_position_ais_created_at < tgt.first_position_ais_created_at
       OR EXCLUDED.last_position_ais_created_at  > tgt.last_position_ais_created_at;

    RETURN TRUE;
END;
$func$;

