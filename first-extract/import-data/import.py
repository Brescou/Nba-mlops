import os
from datetime import timedelta

import pandas as pd
from db.DB import DB
import logging

logging.basicConfig(level=logging.INFO)


def parse_clock_to_time(clock_str):
    try:
        time_part = clock_str[2:].split("M")
        minutes = int(time_part[0]) if len(time_part) > 0 else 0
        seconds = float(time_part[1].replace("S", "")) if len(time_part) > 1 else 0
        return f"{minutes:02}:{int(seconds):02}"
    except Exception as e:
        logging.error(f"Error parsing clock: {clock_str} - {e}")
        return None


def parse_elapsed_to_interval(clock_value):
    try:
        minutes, seconds = map(int, clock_value.split(":"))
        return f"{minutes} minutes {seconds} seconds"
    except Exception as e:
        logging.error(f"Error parsing elapsed: {clock_value} - {e}")
        return None


def load_play_by_play_data(seasons=[]):
    base_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/data/game/"
    db_instance = DB()
    db_instance.connect()
    if not os.path.exists(base_path):
        logging.error("Base path does not exist.")
        return
    try:
        for season in seasons:
            season_path = os.path.join(base_path, season)
            if not os.path.exists(season_path):
                logging.warning(f"Season path does not exist: {season_path}")
                continue
            for subfolder in ["playoffs", "regular_season"]:
                subfolder_path = os.path.join(season_path, subfolder)
                if not os.path.exists(subfolder_path):
                    logging.warning(f"Subfolder path does not exist: {subfolder_path}")
                    continue
                for root, _, files in os.walk(subfolder_path):
                    for file in files:
                        if file.endswith(".csv"):
                            csv_path = os.path.join(root, file)
                            logging.info(f"Processing file: {csv_path}")
                            game_id = str(file.split(".")[0])
                            df = pd.read_csv(csv_path)
                            df["game_id"] = game_id
                            df["clock"] = df["clock"].apply(parse_clock_to_time)
                            df["elapsed"] = df["clock"].apply(parse_elapsed_to_interval)
                            df.rename(columns={
                                "actionId": "action_id",
                                "actionNumber": "action_number",
                                "period": "period",
                                "teamId": "team_id",
                                "personId": "player_id",
                                "xLegacy": "x_legacy",
                                "yLegacy": "y_legacy",
                                "shotDistance": "shot_distance",
                                "isFieldGoal": "is_field_goal",
                                "scoreHome": "score_home",
                                "scoreAway": "score_away",
                                "pointsTotal": "points_total",
                                "location": "location",
                                "description": "description",
                                "actionType": "action_type",
                                "subType": "sub_type",
                                "shotValue": "shot_value"
                            }, inplace=True)

                            df["is_field_goal"] = df["is_field_goal"].apply(
                                lambda x: bool(x) if pd.notnull(x) else None)

                            df["player_id"] = df["player_id"].apply(lambda x: None if x == 0 else x)
                            df["team_id"] = df["team_id"].apply(lambda x: None if x == 0 else x)
                            df['player_id'] = df['player_id'].astype(float).astype('Int64')
                            df['team_id'] = df['team_id'].astype(float).astype('Int64')
                            # if action_type is TimeOut, then team_id = player_id and player_id = None
                            timeout_condition = df["action_type"] == "Timeout"
                            df.loc[timeout_condition, "team_id"] = df.loc[timeout_condition, "player_id"]
                            df.loc[timeout_condition, "player_id"] = None

                            #  get team_id
                            team_id = df["team_id"].dropna().unique()
                            # when team_id is null , but player_id is not but have one of the team_id , put it in team_id and do player_id = None
                            df.loc[
                                df["team_id"].isnull() & df["player_id"].notnull() & df["player_id"].isin(team_id),
                                "team_id"
                            ] = df.loc[
                                df["team_id"].isnull() & df["player_id"].notnull() & df["player_id"].isin(team_id),
                                "player_id"
                            ]
                            df.loc[
                                df["team_id"].notnull() & df["player_id"].isin(team_id),
                                "player_id"
                            ] = None

                            df.drop(
                                columns=["teamTricode", "playerName", "playerNameI", "videoAvailable", "shotResult"],
                                inplace=True)
                            db_instance.load_data_from_dataframe("play_by_play", df)

    except Exception as e:
        logging.error(f"Error loading play-by-play data: {e}")
    finally:
        db_instance.close()


if __name__ == "__main__":
    load_play_by_play_data(['2021-22', '2022-23', '2023-24'])
