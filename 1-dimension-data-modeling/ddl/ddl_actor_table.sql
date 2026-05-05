
-- Array element type for "films"
CREATE TYPE film_info AS (
  film   TEXT,
  votes  INTEGER,
  rating REAL,
  filmid TEXT
);

-- Quality band
CREATE TYPE quality_class_enum AS ENUM ('star','good','average','bad');

---1. DDL for actors table
CREATE TABLE actor_films (
  actor   TEXT,
  actorid TEXT,
  film    TEXT,
  year    INTEGER,
  votes   INTEGER,
  rating  REAL,
  filmid  TEXT,
  PRIMARY KEY (actorid, filmid)
);