create database nba_db with owner postgres;

create table public.team
(
    team_id      integer not null primary key,
    name         varchar(100),
    city         varchar(50),
    abbreviation varchar(50),
    slug         varchar(100)
);

alter table public.team owner to postgres;

create table public.game
(
    game_id integer not null primary key,
    season_year  varchar(20),
    date  date,
    home_team_id integer references public.team,
    away_team_id integer references public.team,
    result varchar(20)
);

alter table public.game owner to postgres;

create table public.player
(
    player_id       integer not null primary key,
    firstname       varchar(100),
    lastname        varchar(100),
    player_slug     varchar(100),
    team_id         integer references public.team,
    is_defunct      boolean,
    jersey_number   integer,
    position        varchar(50),
    height          numeric(5, 2),
    weight          numeric(5, 2),
    college         varchar(100),
    country         varchar(100),
    draft_year      integer,
    draft_round     integer,
    draft_number    integer,
    roster_status   boolean,
    points          numeric(5, 2),
    rebounds        numeric(5, 2),
    assists         numeric(5, 2),
    stats_timeframe varchar(50),
    from_year       integer,
    to_year         integer
);

alter table public.player owner to postgres;

create table public.player_boxscore
(
    boxscore_id varchar(225) not null primary key,
    season_year varchar(20),
    player_id   integer references public.player,
    team_id     integer references public.team,
    game_id     integer references public.game,
    game_date   date,
    matchup     varchar(100),
    wl          char,
    min         integer,
    is_playoff  boolean default false,
    constraint unique_player_game unique (player_id, game_id)
);

alter table public.player_boxscore owner to postgres;

create table public.player_boxscore_advanced
(
    boxscore_id        varchar(225) not null primary key references public.player_boxscore,
    e_off_rating       numeric(5, 2),
    off_rating         numeric(5, 2),
    sp_work_off_rating numeric(5, 2),
    e_def_rating       numeric(5, 2),
    def_rating         numeric(5, 2),
    sp_work_def_rating numeric(5, 2),
    e_net_rating       numeric(5, 2),
    net_rating         numeric(5, 2),
    sp_work_net_rating numeric(5, 2),
    ast_pct            numeric(5, 2),
    ast_to             numeric(5, 2),
    ast_ratio          numeric(5, 2),
    oreb_pct           numeric(5, 2),
    dreb_pct           numeric(5, 2),
    reb_pct            numeric(5, 2),
    tm_tov_pct         numeric(5, 2),
    e_tov_pct          numeric(5, 2),
    efg_pct            numeric(5, 2),
    ts_pct             numeric(5, 2),
    usg_pct            numeric(5, 2),
    pace               numeric(5, 2),
    pie                numeric(5, 2)
);

alter table public.player_boxscore_advanced owner to postgres;

create table public.player_boxscore_base
(
    boxscore_id varchar(225) not null primary key references public.player_boxscore,
    fgm         integer,
    fga         integer,
    fg_pct      numeric(4, 3),
    fg3m        integer,
    fg3a        integer,
    fg3_pct     numeric(4, 3),
    ftm         integer,
    fta         integer,
    ft_pct      numeric(4, 3),
    oreb        integer,
    dreb        integer,
    reb         integer,
    ast         integer,
    tov         integer,
    stl         integer,
    blk         integer,
    blka        integer,
    pf          integer,
    pfd         integer,
    pts         integer,
    plus_minus  integer,
    dd2         boolean,
    td3         boolean,
    min_sec     varchar(5)
);

alter table public.player_boxscore_base owner to postgres;

create table public.player_boxscore_misc
(
    boxscore_id        varchar(225) not null primary key references public.player_boxscore,
    pts_off_tov        integer,
    pts_2nd_chance     integer,
    pts_fb             integer,
    pts_paint          integer,
    opp_pts_off_tov    integer,
    opp_pts_2nd_chance integer,
    opp_pts_fb         integer,
    opp_pts_paint      integer,
    blk                integer,
    blka               integer,
    pf                 integer,
    pfd                integer,
    min_sec            varchar(5)
);

alter table public.player_boxscore_misc owner to postgres;

create table public.player_boxscore_scoring
(
    boxscore_id     varchar(225) not null primary key references public.player_boxscore,
    pct_fga_2pt     numeric(4, 3),
    pct_fga_3pt     numeric(4, 3),
    pct_pts_2pt     numeric(4, 3),
    pct_pts_2pt_mr  numeric(4, 3),
    pct_pts_3pt     numeric(4, 3),
    pct_pts_fb      numeric(4, 3),
    pct_pts_ft      numeric(4, 3),
    pct_pts_off_tov numeric(4, 3),
    pct_pts_paint   numeric(4, 3),
    pct_ast_2pm     numeric(4, 3),
    pct_uast_2pm    numeric(4, 3),
    pct_ast_3pm     numeric(4, 3),
    pct_uast_3pm    numeric(4, 3),
    pct_ast_fgm     numeric(4, 3),
    pct_uast_fgm    numeric(4, 3),
    fgm             integer,
    fga             integer,
    fg_pct          numeric(4, 3),
    min_sec         varchar(5)
);

alter table public.player_boxscore_scoring owner to postgres;

create table public.player_boxscore_usage
(
    boxscore_id varchar(225) not null primary key references public.player_boxscore,
    usg_pct     numeric(5, 2),
    pct_fgm     numeric(5, 2),
    pct_fga     numeric(5, 2),
    pct_fg3m    numeric(5, 2),
    pct_fg3a    numeric(5, 2),
    pct_ftm     numeric(5, 2),
    pct_fta     numeric(5, 2),
    pct_oreb    numeric(5, 2),
    pct_dreb    numeric(5, 2),
    pct_reb     numeric(5, 2),
    pct_ast     numeric(5, 2),
    pct_tov     numeric(5, 2),
    pct_stl     numeric(5, 2),
    pct_blk     numeric(5, 2),
    pct_blka    numeric(5, 2),
    pct_pf      numeric(5, 2),
    pct_pfd     numeric(5, 2),
    pct_pts     numeric(5, 2),
    min_sec     varchar(5)
);

alter table public.player_boxscore_usage owner to postgres;

create table public.team_boxscore
(
    boxscore_id varchar(225) not null primary key,
    season_year  varchar(20),
    team_id     integer references public.team,
    game_id     integer references public.game,
    game_date   date,
    matchup     varchar(100),
    wl          char,
    min         integer
);

alter table public.team_boxscore owner to postgres;

create table public.team_boxscore_advanced
(
    boxscore_id      varchar(225) not null primary key references public.team_boxscore,
    off_rating       numeric(5, 2),
    def_rating       numeric(5, 2),
    net_rating       numeric(5, 2),
    ast_pct          numeric(5, 2),
    ast_to           numeric(5, 2),
    ast_ratio        numeric(5, 2),
    oreb_pct         numeric(5, 2),
    dreb_pct         numeric(5, 2),
    reb_pct          numeric(5, 2),
    tm_tov_pct       numeric(5, 2),
    efg_pct          numeric(5, 2),
    ts_pct           numeric(5, 2),
    pace             numeric(5, 2),
    pie              numeric(5, 2)
);

alter table public.team_boxscore_advanced owner to postgres;

create table public.team_boxscore_base
(
    boxscore_id varchar(225) not null primary key references public.team_boxscore,
    fgm         integer,
    fga         integer,
    fg_pct      numeric(4, 3),
    fg3m        integer,
    fg3a        integer,
    fg3_pct     numeric(4, 3),
    ftm         integer,
    fta         integer,
    ft_pct      numeric(4, 3),
    oreb        integer,
    dreb        integer,
    reb         integer,
    ast         integer,
    tov         integer,
    stl         integer,
    blk         integer,
    blka        integer,
    pf          integer,
    pfd         integer,
    pts         integer,
    plus_minus  integer
);

alter table public.team_boxscore_base owner to postgres;

create table public.team_boxscore_four_factors
(
    boxscore_id  varchar(225) not null primary key references public.team_boxscore,
    efg_pct      numeric(4, 3),
    fta_rate     numeric(4, 3),
    tm_tov_pct   numeric(4, 3),
    oreb_pct     numeric(4, 3),
    opp_efg_pct  numeric(4, 3),
    opp_fta_rate numeric(4, 3),
    opp_tov_pct  numeric(4, 3),
    opp_oreb_pct numeric(4, 3)
);

alter table public.team_boxscore_four_factors owner to postgres;

create table public.team_boxscore_misc
(
    boxscore_id        varchar(225) not null primary key references public.team_boxscore,
    pts_off_tov        integer,
    pts_2nd_chance     integer,
    pts_fb             integer,
    pts_paint          integer,
    opp_pts_off_tov    integer,
    opp_pts_2nd_chance integer,
    opp_pts_fb         integer,
    opp_pts_paint      integer
);

alter table public.team_boxscore_misc owner to postgres;

create table public.team_boxscore_scoring
(
    boxscore_id     varchar(225) not null primary key references public.team_boxscore,
    pct_fga_2pt     numeric(4, 3),
    pct_fga_3pt     numeric(4, 3),
    pct_pts_2pt     numeric(4, 3),
    pct_pts_2pt_mr  numeric(4, 3),
    pct_pts_3pt     numeric(4, 3),
    pct_pts_fb      numeric(4, 3),
    pct_pts_ft      numeric(4, 3),
    pct_pts_off_tov numeric(4, 3),
    pct_pts_paint   numeric(4, 3),
    pct_ast_2pm     numeric(4, 3),
    pct_uast_2pm    numeric(4, 3),
    pct_ast_3pm     numeric(4, 3),
    pct_uast_3pm    numeric(4, 3),
    pct_ast_fgm     numeric(4, 3),
    pct_uast_fgm    numeric(4, 3)
);

alter table public.team_boxscore_scoring owner to postgres;

