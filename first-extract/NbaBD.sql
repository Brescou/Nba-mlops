CREATE TABLE "player" (
  "player_id" INTEGER PRIMARY KEY,
  "firstname" VARCHAR(100),
  "lastname" VARCHAR(100),
  "player_slug" VARCHAR(100),
  "team_id" INTEGER,
  "is_defunct" BOOLEAN,
  "jersey_number" INTEGER,
  "position" VARCHAR(50),
  "height" DECIMAL(5,2),
  "weight" DECIMAL(5,2),
  "college" VARCHAR(100),
  "country" VARCHAR(100),
  "draft_year" INTEGER,
  "draft_round" INTEGER,
  "draft_number" INTEGER,
  "roster_status" BOOLEAN,
  "points" DECIMAL(5,2),
  "rebounds" DECIMAL(5,2),
  "assists" DECIMAL(5,2),
  "stats_timeframe" VARCHAR(50),
  "from_year" INTEGER,
  "to_year" INTEGER
);

CREATE TABLE "team" (
  "team_id" INTEGER PRIMARY KEY,
  "name" VARCHAR(100),
  "city" VARCHAR(50),
  "abbreviation" VARCHAR(50),
  "slug" VARCHAR(100)
);

CREATE TABLE "game" (
  "game_id" INTEGER PRIMARY KEY,
  "season_year" VARCHAR(20),
  "date" DATE,
  "home_team_id" INTEGER,
  "away_team_id" INTEGER,
  "result" VARCHAR(20)
);

CREATE TABLE "player_boxscore" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "season_year" INTEGER,
  "player_id" INTEGER,
  "team_id" INTEGER,
  "game_id" INTEGER,
  "game_date" DATE,
  "matchup" VARCHAR(100),
  "wl" CHAR(1),
  "min" INTEGER
);

CREATE TABLE "player_boxscore_base" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "fgm" INTEGER,
  "fga" INTEGER,
  "fg_pct" DECIMAL(4,3),
  "fg3m" INTEGER,
  "fg3a" INTEGER,
  "fg3_pct" DECIMAL(4,3),
  "ftm" INTEGER,
  "fta" INTEGER,
  "ft_pct" DECIMAL(4,3),
  "oreb" INTEGER,
  "dreb" INTEGER,
  "reb" INTEGER,
  "ast" INTEGER,
  "tov" INTEGER,
  "stl" INTEGER,
  "blk" INTEGER,
  "blka" INTEGER,
  "pf" INTEGER,
  "pfd" INTEGER,
  "pts" INTEGER,
  "plus_minus" INTEGER,
  "dd2" BOOLEAN,
  "td3" BOOLEAN,
  "min_sec" VARCHAR(5)
);

CREATE TABLE "player_boxscore_advanced" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "e_off_rating" DECIMAL(5,2),
  "off_rating" DECIMAL(5,2),
  "sp_work_off_rating" DECIMAL(5,2),
  "e_def_rating" DECIMAL(5,2),
  "def_rating" DECIMAL(5,2),
  "sp_work_def_rating" DECIMAL(5,2),
  "e_net_rating" DECIMAL(5,2),
  "net_rating" DECIMAL(5,2),
  "sp_work_net_rating" DECIMAL(5,2),
  "ast_pct" DECIMAL(5,2),
  "ast_to" DECIMAL(5,2),
  "ast_ratio" DECIMAL(5,2),
  "oreb_pct" DECIMAL(5,2),
  "dreb_pct" DECIMAL(5,2),
  "reb_pct" DECIMAL(5,2),
  "tm_tov_pct" DECIMAL(5,2),
  "e_tov_pct" DECIMAL(5,2),
  "efg_pct" DECIMAL(5,2),
  "ts_pct" DECIMAL(5,2),
  "usg_pct" DECIMAL(5,2),
  "pace" DECIMAL(5,2),
  "pie" DECIMAL(5,2)
);

CREATE TABLE "player_boxscore_misc" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "pts_off_tov" INTEGER,
  "pts_2nd_chance" INTEGER,
  "pts_fb" INTEGER,
  "pts_paint" INTEGER,
  "opp_pts_off_tov" INTEGER,
  "opp_pts_2nd_chance" INTEGER,
  "opp_pts_fb" INTEGER,
  "opp_pts_paint" INTEGER,
  "blk" INTEGER,
  "blka" INTEGER,
  "pf" INTEGER,
  "pfd" INTEGER,
  "min_sec" VARCHAR(5)
);

CREATE TABLE "player_boxscore_scoring" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "pct_fga_2pt" DECIMAL(4,3),
  "pct_fga_3pt" DECIMAL(4,3),
  "pct_pts_2pt" DECIMAL(4,3),
  "pct_pts_2pt_mr" DECIMAL(4,3),
  "pct_pts_3pt" DECIMAL(4,3),
  "pct_pts_fb" DECIMAL(4,3),
  "pct_pts_ft" DECIMAL(4,3),
  "pct_pts_off_tov" DECIMAL(4,3),
  "pct_pts_paint" DECIMAL(4,3),
  "pct_ast_2pm" DECIMAL(4,3),
  "pct_uast_2pm" DECIMAL(4,3),
  "pct_ast_3pm" DECIMAL(4,3),
  "pct_uast_3pm" DECIMAL(4,3),
  "pct_ast_fgm" DECIMAL(4,3),
  "pct_uast_fgm" DECIMAL(4,3),
  "fgm" INTEGER,
  "fga" INTEGER,
  "fg_pct" DECIMAL(4,3),
  "min_sec" VARCHAR(5)
);

CREATE TABLE "player_boxscore_usage" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "usg_pct" DECIMAL(5,2),
  "pct_fgm" DECIMAL(5,2),
  "pct_fga" DECIMAL(5,2),
  "pct_fg3m" DECIMAL(5,2),
  "pct_fg3a" DECIMAL(5,2),
  "pct_ftm" DECIMAL(5,2),
  "pct_fta" DECIMAL(5,2),
  "pct_oreb" DECIMAL(5,2),
  "pct_dreb" DECIMAL(5,2),
  "pct_reb" DECIMAL(5,2),
  "pct_ast" DECIMAL(5,2),
  "pct_tov" DECIMAL(5,2),
  "pct_stl" DECIMAL(5,2),
  "pct_blk" DECIMAL(5,2),
  "pct_blka" DECIMAL(5,2),
  "pct_pf" DECIMAL(5,2),
  "pct_pfd" DECIMAL(5,2),
  "pct_pts" DECIMAL(5,2),
  "min_sec" VARCHAR(5)
);

CREATE TABLE "team_boxscore" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "season_year" INTEGER,
  "team_id" INTEGER,
  "game_id" INTEGER,
  "game_date" DATE,
  "matchup" VARCHAR(100),
  "wl" CHAR(1),
  "min" INTEGER
);

CREATE TABLE "team_boxscore_base" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "fgm" INTEGER,
  "fga" INTEGER,
  "fg_pct" DECIMAL(4,3),
  "fg3m" INTEGER,
  "fg3a" INTEGER,
  "fg3_pct" DECIMAL(4,3),
  "ftm" INTEGER,
  "fta" INTEGER,
  "ft_pct" DECIMAL(4,3),
  "oreb" INTEGER,
  "dreb" INTEGER,
  "reb" INTEGER,
  "ast" INTEGER,
  "tov" INTEGER,
  "stl" INTEGER,
  "blk" INTEGER,
  "blka" INTEGER,
  "pf" INTEGER,
  "pfd" INTEGER,
  "pts" INTEGER,
  "plus_minus" INTEGER
);

CREATE TABLE "team_boxscore_advanced" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "offensive_rating" DECIMAL(5,2),
  "defensive_rating" DECIMAL(5,2),
  "net_rating" DECIMAL(5,2),
  "ast_pct" DECIMAL(5,2),
  "ast_to" DECIMAL(5,2),
  "ast_ratio" DECIMAL(5,2),
  "oreb_pct" DECIMAL(5,2),
  "dreb_pct" DECIMAL(5,2),
  "reb_pct" DECIMAL(5,2),
  "tm_tov_pct" DECIMAL(5,2),
  "efg_pct" DECIMAL(5,2),
  "ts_pct" DECIMAL(5,2),
  "pace" DECIMAL(5,2),
  "pie" DECIMAL(5,2)
);

CREATE TABLE "team_boxscore_misc" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "pts_off_tov" INTEGER,
  "pts_2nd_chance" INTEGER,
  "pts_fb" INTEGER,
  "pts_paint" INTEGER,
  "opp_pts_off_tov" INTEGER,
  "opp_pts_2nd_chance" INTEGER,
  "opp_pts_fb" INTEGER,
  "opp_pts_paint" INTEGER
);

CREATE TABLE "team_boxscore_scoring" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "pct_fga_2pt" DECIMAL(4,3),
  "pct_fga_3pt" DECIMAL(4,3),
  "pct_pts_2pt" DECIMAL(4,3),
  "pct_pts_2pt_mr" DECIMAL(4,3),
  "pct_pts_3pt" DECIMAL(4,3),
  "pct_pts_fb" DECIMAL(4,3),
  "pct_pts_ft" DECIMAL(4,3),
  "pct_pts_off_tov" DECIMAL(4,3),
  "pct_pts_paint" DECIMAL(4,3),
  "pct_ast_2pm" DECIMAL(4,3),
  "pct_uast_2pm" DECIMAL(4,3),
  "pct_ast_3pm" DECIMAL(4,3),
  "pct_uast_3pm" DECIMAL(4,3),
  "pct_ast_fgm" DECIMAL(4,3),
  "pct_uast_fgm" DECIMAL(4,3)
);

CREATE TABLE "team_boxscore_four_factors" (
  "boxscore_id" INTEGER PRIMARY KEY,
  "efg_pct" DECIMAL(4,3),
  "fta_rate" DECIMAL(4,3),
  "tm_tov_pct" DECIMAL(4,3),
  "oreb_pct" DECIMAL(4,3),
  "opp_efg_pct" DECIMAL(4,3),
  "opp_fta_rate" DECIMAL(4,3),
  "opp_tov_pct" DECIMAL(4,3),
  "opp_oreb_pct" DECIMAL(4,3)
);

ALTER TABLE "player" ADD FOREIGN KEY ("team_id") REFERENCES "team" ("team_id");

ALTER TABLE "game" ADD FOREIGN KEY ("home_team_id") REFERENCES "team" ("team_id");

ALTER TABLE "game" ADD FOREIGN KEY ("away_team_id") REFERENCES "team" ("team_id");

ALTER TABLE "player_boxscore" ADD FOREIGN KEY ("player_id") REFERENCES "player" ("player_id");

ALTER TABLE "player_boxscore" ADD FOREIGN KEY ("team_id") REFERENCES "team" ("team_id");

ALTER TABLE "player_boxscore" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "player_boxscore_base" ADD FOREIGN KEY ("boxscore_id") REFERENCES "player_boxscore" ("boxscore_id");

ALTER TABLE "player_boxscore_advanced" ADD FOREIGN KEY ("boxscore_id") REFERENCES "player_boxscore" ("boxscore_id");

ALTER TABLE "player_boxscore_misc" ADD FOREIGN KEY ("boxscore_id") REFERENCES "player_boxscore" ("boxscore_id");

ALTER TABLE "player_boxscore_scoring" ADD FOREIGN KEY ("boxscore_id") REFERENCES "player_boxscore" ("boxscore_id");

ALTER TABLE "player_boxscore_usage" ADD FOREIGN KEY ("boxscore_id") REFERENCES "player_boxscore" ("boxscore_id");

ALTER TABLE "team_boxscore" ADD FOREIGN KEY ("team_id") REFERENCES "team" ("team_id");

ALTER TABLE "team_boxscore" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "team_boxscore_base" ADD FOREIGN KEY ("boxscore_id") REFERENCES "team_boxscore" ("boxscore_id");

ALTER TABLE "team_boxscore_advanced" ADD FOREIGN KEY ("boxscore_id") REFERENCES "team_boxscore" ("boxscore_id");

ALTER TABLE "team_boxscore_misc" ADD FOREIGN KEY ("boxscore_id") REFERENCES "team_boxscore" ("boxscore_id");

ALTER TABLE "team_boxscore_scoring" ADD FOREIGN KEY ("boxscore_id") REFERENCES "team_boxscore" ("boxscore_id");

ALTER TABLE "team_boxscore_four_factors" ADD FOREIGN KEY ("boxscore_id") REFERENCES "team_boxscore" ("boxscore_id");
