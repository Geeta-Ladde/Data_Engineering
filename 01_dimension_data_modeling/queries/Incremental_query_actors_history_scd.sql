
--5. Incremental query for actors_history_scd:

CREATE OR REPLACE FUNCTION load_actors_scd_year(p_year INT)
RETURNS void
LANGUAGE plpgsql AS
$$
BEGIN
  WITH
  this_year AS (
    SELECT a.actorid, a.actor, a.quality_class, a.is_active
    FROM actors a
    WHERE a.current_year = p_year
  ),
  last_segments AS (
    SELECT DISTINCT ON (actorid)
           actorid, actor, quality_class, is_active, start_year, end_year
    FROM actors_history_scd
    ORDER BY actorid, end_year DESC, start_year DESC
  ),
  unchanged AS (  -- extend the previous segment
    SELECT
      l.actorid, l.actor, l.quality_class, l.is_active,
      l.start_year,
      p_year AS end_year
    FROM last_segments l
    JOIN this_year t
      ON t.actorid = l.actorid
     AND t.quality_class = l.quality_class
     AND t.is_active     = l.is_active
  ),
  changed_close AS (  -- close old segment at year-1
    SELECT
      l.actorid, l.actor, l.quality_class, l.is_active,
      l.start_year,
      (p_year - 1) AS end_year
    FROM last_segments l
    JOIN this_year t
      ON t.actorid = l.actorid
     AND (t.quality_class IS DISTINCT FROM l.quality_class
          OR t.is_active  IS DISTINCT FROM l.is_active)
  ),
  changed_open AS (   -- open new segment starting this year
    SELECT
      t.actorid, t.actor, t.quality_class, t.is_active,
      p_year AS start_year,
      p_year AS end_year      -- use NULL if you prefer open-ended segments
    FROM this_year t
    JOIN last_segments l
      ON t.actorid = l.actorid
     AND (t.quality_class IS DISTINCT FROM l.quality_class
          OR t.is_active  IS DISTINCT FROM l.is_active)
  ),
  brand_new AS (      -- actors with no prior SCD rows
    SELECT
      t.actorid, t.actor, t.quality_class, t.is_active,
      p_year AS start_year,
      p_year AS end_year
    FROM this_year t
    LEFT JOIN last_segments l ON l.actorid = t.actorid
    WHERE l.actorid IS NULL
  ),
  -- do the two updates inside the same WITH (data-modifying CTEs)
  u1 AS (
    UPDATE actors_history_scd s
    SET end_year = u.end_year
    FROM unchanged u
    WHERE s.actorid = u.actorid
      AND s.start_year = u.start_year
    RETURNING 1
  ),
  u2 AS (
    UPDATE actors_history_scd s
    SET end_year = c.end_year
    FROM changed_close c
    WHERE s.actorid = c.actorid
      AND s.start_year = c.start_year
    RETURNING 1
  )
  -- and finish with the insert, still in the same statement
  INSERT INTO actors_history_scd (actorid, actor, quality_class, is_active, start_year, end_year)
  SELECT actorid, actor, quality_class, is_active, start_year, end_year
  FROM changed_open
  UNION ALL
  SELECT actorid, actor, quality_class, is_active, start_year, end_year
  FROM brand_new
  ON CONFLICT (actorid, start_year) DO NOTHING;
END;
$$;


SELECT load_actors_scd_year(y)
FROM generate_series(1970, 2021) AS g(y);
