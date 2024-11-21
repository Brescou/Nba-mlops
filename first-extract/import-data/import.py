import os
import pandas as pd
from db.DB import DB
import logging

logging.basicConfig(level=logging.INFO)

# Instance de la base de données
db_instance = DB()
db_instance.connect()


def clean_csv(file_path):
    df = pd.read_csv(file_path)
    df = df.where(pd.notnull(df), None)
    df['HEIGHT'] = df['HEIGHT'].apply(convert_height_to_inches)
    df['ROSTER_STATUS'] = df['ROSTER_STATUS'].apply(convert_roster_status)
    df['JERSEY_NUMBER'] = df['JERSEY_NUMBER'].apply(clean_jersey_number)
    return df


def clean_jersey_number(jersey_number):
    if isinstance(jersey_number, str) and '-' in jersey_number:
        return int(jersey_number.split('-')[0])
    elif str(jersey_number).isdigit():
        return int(jersey_number)
    return None


def convert_roster_status(value):
    if value == 'NaN' or pd.isna(value):
        return None
    elif value == 1.0 or value == 1:
        return True
    elif value == 0.0 or value == 0:
        return False
    return None


def convert_height_to_inches(height_str):
    if isinstance(height_str, str) and '-' in height_str:
        feet, inches = height_str.split('-')
        try:
            feet = int(feet)
            inches = int(inches)
            total_inches = feet * 12 + inches
            return total_inches
        except ValueError:
            return None
    return None


def load_player_data(file_path):
    data = clean_csv(file_path)
    players_df = data[[
        'PERSON_ID', 'PLAYER_FIRST_NAME', 'PLAYER_LAST_NAME', 'PLAYER_SLUG', 'TEAM_ID',
        'IS_DEFUNCT', 'JERSEY_NUMBER', 'POSITION', 'HEIGHT', 'WEIGHT', 'COLLEGE', 'COUNTRY',
        'DRAFT_YEAR', 'DRAFT_ROUND', 'DRAFT_NUMBER', 'ROSTER_STATUS', 'PTS', 'REB', 'AST',
        'STATS_TIMEFRAME', 'FROM_YEAR', 'TO_YEAR'
    ]]
    db_instance.insert_bulk_data(
        table="player",
        columns=[
            "player_id", "firstname", "lastname", "player_slug", "team_id", "is_defunct", "jersey_number",
            "position", "height", "weight", "college", "country", "draft_year", "draft_round",
            "draft_number", "roster_status", "points", "rebounds", "assists", "stats_timeframe",
            "from_year", "to_year"
        ],
        data=players_df.to_records(index=False)
    )
    logging.info("Les joueurs ont été insérés avec succès.")


def load_team_data(data):
    teams_df = data[['TEAM_ID', 'TEAM_NAME', 'TEAM_CITY', 'TEAM_ABBREVIATION', 'TEAM_SLUG']].drop_duplicates()
    db_instance.insert_bulk_data(
        table="team",
        columns=["team_id", "name", "city", "abbreviation", "slug"],
        data=teams_df.to_records(index=False)
    )
    logging.info("Les équipes ont été insérées avec succès.")


def load_game_data(file_path):
    df = pd.read_csv(file_path, dtype={'GAME_ID': str})
    df = df.where(pd.notnull(df), None)
    df['RESULT'] = df.apply(lambda row: 'HOME' if row['HOME_WL'] == 'W' else 'AWAY', axis=1)
    games_df = df[['GAME_ID', 'SEASON_YEAR', 'GAME_DATE', 'HOME_TEAM_ID', 'AWAY_TEAM_ID', 'RESULT']]
    db_instance.insert_bulk_data(
        table="game",
        columns=["game_id", "season_year", "date", "home_team_id", "away_team_id", "result"],
        data=games_df.to_records(index=False)
    )
    logging.info("Les matchs ont été insérés avec succès.")


def load_play_by_play_data():
    play_by_play_dir = "../data/game"
    for root, _, files in os.walk(play_by_play_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)
                df['game_id'] = os.path.splitext(file)[0]
                db_instance.load_data_from_dataframe("play_by_play", df)
                logging.info(f"Données de {file} insérées avec succès.")


if __name__ == "__main__":
    player_data = clean_csv("../data/player_bios.csv")
    load_player_data("../data/player_bios.csv")
    load_team_data(player_data)

    regular_games = pd.read_csv("../data/game/regular_season_game_logs.csv")
    playoff_games = pd.read_csv("../data/game/playoffs_game_logs.csv")
    load_game_data(pd.concat([regular_games, playoff_games], ignore_index=True))

    load_play_by_play_data()

    db_instance.close()
