
--4. Backfill query for actors_history_scd

-- 4a) Materialize per-actor per-year status derived from the rules
WITH all_years AS (
  SELECT generate_series(MIN(year), MAX(year)) AS yr
  FROM actor_films
),
actors AS (
  SELECT DISTINCT actorid, actor FROM actor_films
),
actor_years AS (
  SELECT a.actorid, a.actor, y.yr AS year
  FROM actors a CROSS JOIN all_years y
),
last_active_year AS (
  SELECT actorid, year,
         MAX(year) OVER (PARTITION BY actorid
                         ORDER BY year
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS last_year_played
  FROM actor_years
),
avg_at_last_year AS (
  SELECT ay.actorid,
         ay.year,
         COALESCE((
           SELECT AVG(rating)
           FROM actor_films af
           WHERE af.actorid = ay.actorid
             AND af.year    = lay.last_year_played
         ), 0) AS avg_rating_last,
         EXISTS (
           SELECT 1
           FROM actor_films af
           WHERE af.actorid = ay.actorid
             AND af.year    = ay.year
         ) AS is_active
  FROM actor_years ay
  JOIN last_active_year lay
    ON lay.actorid = ay.actorid
   AND lay.year    = ay.year
),
status_per_year AS (
  SELECT
    ay.actorid,
    (SELECT MIN(actor) FROM actor_films f WHERE f.actorid = ay.actorid) AS actor,
    ay.year,
    (CASE
       WHEN avg_rating_last > 8 THEN 'star'
       WHEN avg_rating_last > 7 THEN 'good'
       WHEN avg_rating_last > 6 THEN 'average'
       ELSE 'bad'
     END)::quality_class_enum AS quality_class,
    is_active
  FROM avg_at_last_year ay
),

-- 4b) Turn per-year status into SCD2 ranges via "islands"
marked AS (
  SELECT
    spy.*,
    LAG(quality_class, 1) OVER (PARTITION BY actorid ORDER BY year)  AS prev_qc,
    LAG(is_active, 1)     OVER (PARTITION BY actorid ORDER BY year)  AS prev_active
  FROM status_per_year spy
),
grouped AS (
  SELECT
    actorid,
    MIN((SELECT MIN(actor) FROM actor_films f WHERE f.actorid = actorid)) AS actor,
    quality_class,
    is_active,
    MIN(year) AS start_year,
    MAX(year) AS end_year
  FROM (
    SELECT
      m.*,
      -- start a new group when either attribute changes
      SUM( CASE WHEN (prev_qc IS DISTINCT FROM quality_class)
                     OR (prev_active IS DISTINCT FROM is_active)
                THEN 1 ELSE 0 END
         ) OVER (PARTITION BY actorid ORDER BY year) AS grp
    FROM marked m
  ) x
  GROUP BY actorid, quality_class, is_active, grp
)

INSERT INTO actors_history_scd (actorid, actor, quality_class, is_active, start_year, end_year)
SELECT actorid, actor, quality_class, is_active, start_year, end_year
FROM grouped
ON CONFLICT (actorid, start_year) DO NOTHING;