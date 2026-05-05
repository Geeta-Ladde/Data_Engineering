
--2. Year-by-year,  one click (function + generate_series)
CREATE OR REPLACE FUNCTION load_actors_year(p_year INT)
RETURNS void
LANGUAGE plpgsql AS
$$
BEGIN
  WITH
  this_year AS (
    SELECT actor, actorid, film, votes, rating, filmid
    FROM actor_films
    WHERE year = p_year
  ),
  last_active_year AS (
    SELECT actorid, MAX(year) AS last_year
    FROM actor_films
    WHERE year <= p_year
    GROUP BY actorid
  ),
  latest_year_avg AS (
    SELECT af.actorid, AVG(af.rating) AS avg_rating
    FROM actor_films af
    JOIN last_active_year lay
      ON af.actorid = lay.actorid
     AND af.year    = lay.last_year
    GROUP BY af.actorid
  ),
  latest_prior_row AS (
    SELECT DISTINCT ON (actorid) *
    FROM actors
    WHERE current_year < p_year
    ORDER BY actorid, current_year DESC
  ),
  year_films_as_array AS (
    SELECT
      actorid,
      MIN(actor) AS actor,
      COALESCE(
        ARRAY_AGG(ROW(film, votes, rating, filmid)::film_info ORDER BY rating DESC),
        ARRAY[]::film_info[]
      ) AS films_this_year
    FROM this_year
    GROUP BY actorid
  ),
  upsert_rows AS (
    SELECT
      COALESCE(y.actor,   lpr.actor)   AS actor,
      COALESCE(y.actorid, lpr.actorid) AS actorid,
      CASE
        WHEN lpr.actorid IS NULL
          THEN COALESCE(y.films_this_year, ARRAY[]::film_info[])
        ELSE COALESCE(lpr.films, ARRAY[]::film_info[]) || COALESCE(y.films_this_year, ARRAY[]::film_info[])
      END AS films,
      (CASE
         WHEN ly.avg_rating > 8 THEN 'star'
         WHEN ly.avg_rating > 7 THEN 'good'
         WHEN ly.avg_rating > 6 THEN 'average'
         ELSE 'bad'
       END)::quality_class_enum AS quality_class,
      (y.actorid IS NOT NULL) AS is_active,
      p_year AS current_year
    FROM latest_prior_row lpr
    FULL JOIN year_films_as_array y
      ON y.actorid = lpr.actorid
    LEFT JOIN latest_year_avg ly
      ON ly.actorid = COALESCE(y.actorid, lpr.actorid)
  )
  INSERT INTO actors (actor, actorid, films, quality_class, is_active, current_year)
  SELECT actor, actorid, films, quality_class, is_active, current_year
  FROM upsert_rows
  ON CONFLICT (actorid, current_year)
  DO UPDATE SET
    actor         = EXCLUDED.actor,
    films         = EXCLUDED.films,
    quality_class = EXCLUDED.quality_class,
    is_active     = EXCLUDED.is_active;
END;
$$;

--Run it for every year in one shot (1970 → 2021):
SELECT load_actors_year(y)
FROM generate_series(1970, 2021) AS g(y)