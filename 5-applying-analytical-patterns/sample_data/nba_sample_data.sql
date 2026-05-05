-- Sample data for testing analytical pattern queries
-- Load this into PostgreSQL before running the queries

-- game_details sample data
CREATE TABLE IF NOT EXISTS game_details (
    game_id     INTEGER,
    team_id     INTEGER,
    team_abbreviation VARCHAR(10),
    player_name VARCHAR(100),
    pts         INTEGER,
    reb         INTEGER,
    ast         INTEGER
);

INSERT INTO game_details VALUES
(1, 1, 'LAL', 'LeBron James',   28, 8, 10),
(1, 1, 'LAL', 'Anthony Davis',  26, 14,  3),
(1, 2, 'GSW', 'Stephen Curry',  35,  5,  7),
(1, 2, 'GSW', 'Klay Thompson',  22,  3,  2),
(2, 1, 'LAL', 'LeBron James',   32,  7, 12),
(2, 1, 'LAL', 'Anthony Davis',  18, 11,  2),
(2, 3, 'BOS', 'Jayson Tatum',   30,  9,  4),
(2, 3, 'BOS', 'Jaylen Brown',   24,  6,  3),
(3, 2, 'GSW', 'Stephen Curry',  43,  4,  6),
(3, 2, 'GSW', 'Klay Thompson',  19,  4,  1),
(3, 3, 'BOS', 'Jayson Tatum',   27,  8,  5),
(3, 3, 'BOS', 'Jaylen Brown',   21,  5,  2),
(4, 1, 'LAL', 'LeBron James',   12,  6,  9),
(4, 1, 'LAL', 'Anthony Davis',  33, 15,  1),
(4, 2, 'GSW', 'Stephen Curry',  38,  3,  8),
(5, 1, 'LAL', 'LeBron James',    8,  5,  7),
(5, 3, 'BOS', 'Jayson Tatum',   22,  7,  4),
(6, 1, 'LAL', 'LeBron James',   25,  9,  8),
(6, 2, 'GSW', 'Stephen Curry',  29,  4,  5),
(7, 1, 'LAL', 'LeBron James',   33, 11,  9);

-- player_seasons sample data
CREATE TABLE IF NOT EXISTS player_seasons (
    player_name VARCHAR(100),
    season      INTEGER,
    pts         FLOAT,
    ast         FLOAT,
    reb         FLOAT,
    weight      FLOAT
);

INSERT INTO player_seasons VALUES
('LeBron James',  2020, 25.3, 7.8, 7.4, 250),
('LeBron James',  2021, 28.4, 8.2, 7.5, 250),
('LeBron James',  2022, 30.3, 6.2, 8.2, 250),
('Stephen Curry', 2020, 23.5, 4.8, 4.2, 185),
('Stephen Curry', 2021, 32.0, 5.8, 5.5, 185),
('Jayson Tatum',  2021, 26.9, 4.4, 8.0, 210),
('Jayson Tatum',  2022, 30.1, 4.7, 8.8, 210),
('Anthony Davis', 2021, 24.8, 3.1, 10.2, 253),
('Klay Thompson', 2020, 19.6, 2.4, 3.4, 215);

-- players_scd sample data
CREATE TABLE IF NOT EXISTS players_scd (
    player_name  VARCHAR(100),
    scoring_class VARCHAR(20),
    is_active    BOOLEAN,
    start_season INTEGER,
    end_season   INTEGER,
    current_season INTEGER
);

INSERT INTO players_scd VALUES
('LeBron James',  'star', TRUE,  2003, NULL, 2022),
('Stephen Curry', 'star', TRUE,  2009, NULL, 2022),
('Kobe Bryant',   'star', TRUE,  1996, 2016, 2022),
('Jayson Tatum',  'good', TRUE,  2017, NULL, 2022),
('Retired Player','good', FALSE, 2010, 2019, 2022);
