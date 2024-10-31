-- Création de la table Player
CREATE TABLE player (
    player_id INTEGER PRIMARY KEY,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    position VARCHAR(50),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    birthdate DATE,
    player_team_id INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (player_team_id) REFERENCES team (team_id)
);

-- Création de la table Team
CREATE TABLE team (
    team_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(100),
    coach VARCHAR(100),
    conference VARCHAR(50),
    division VARCHAR(50),
    created_at TIMESTAMP
);

-- Création de la table Game
CREATE TABLE game (
    game_id INTEGER PRIMARY KEY,
    date DATE,
    home_team_id INT,
    away_team_id INT,
    result VARCHAR(20),
    created_at TIMESTAMP,
    FOREIGN KEY (home_team_id) REFERENCES team (team_id),
    FOREIGN KEY (away_team_id) REFERENCES team (team_id)
);

-- Création de la table Player_Statistic (table associative entre Player et Game)
CREATE TABLE player_statistic (
    game_id INT,
    player_id INT,
    points INT,
    assists INT,
    minutes_played DECIMAL(4,2),
    PRIMARY KEY (game_id, player_id),
    FOREIGN KEY (game_id) REFERENCES game (game_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id)
);

-- Création de la table Team_Statistic (table associative entre Team et Game)
CREATE TABLE team_statistic (
    game_id INT,
    team_id INT,
    points_scored INT,
    rebounds INT,
    assists INT,
    PRIMARY KEY (game_id, team_id),
    FOREIGN KEY (game_id) REFERENCES game (game_id),
    FOREIGN KEY (team_id) REFERENCES team (team_id)
);

-- Création de la table Player_Event (table associative entre Player et Game)
CREATE TABLE player_event (
    player_id INT,
    game_id INT,
    description VARCHAR(255),
    event_start DATE,
    event_end DATE,
    PRIMARY KEY (player_id, game_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (game_id) REFERENCES game (game_id)
);
